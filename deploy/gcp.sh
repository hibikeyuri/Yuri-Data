#!/usr/bin/env bash
# GCP deployment of the separate, read-only v2 candidate.
# This script never modifies the original production Compose or database volume.
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE="$ROOT/deploy/compose.gcp.yml"
STATE_DIR="${YURI_DEPLOY_STATE_DIR:-$HOME/.local/share/yuri-deploy}"
NGINX_CONF="${YURI_NGINX_CONF:-$HOME/nginx/default.conf}"
CATALOG_DEFAULT="$HOME/yuri-private/catalog.json"
YURI_CATALOG_FILE="${YURI_CATALOG_FILE:-$CATALOG_DEFAULT}"
CONTAINER="yuri-catalog-preview"
ORIGINAL="yuriweb:5000"
CANDIDATE="$CONTAINER:8000"

say() { printf '[yuri-deploy] %s\n' "$*"; }
fail() { printf '[yuri-deploy] ERROR: %s\n' "$*" >&2; exit 1; }
usage() {
  cat <<'EOF'
Usage: bash deploy/gcp.sh {preflight|preview|status|promote|rollback|logs}
  preflight  Verify Docker, current origin and disk; no changes.
  preview    Build the new site separately, bind to 127.0.0.1:18000, test data.
  status     Show preview and original container status.
  promote    Switch ONLY the existing Nginx upstream after checks/backup.
  rollback   Restore the Nginx config backed up by promote.
  logs       Show the preview container's recent logs.

Private input: ${YURI_CATALOG_FILE:-$HOME/yuri-private/catalog.json}
No command touches the original MySQL volume or production Compose.
EOF
}
require_tools() {
  command -v docker >/dev/null || fail "Docker is missing."
  command -v python3 >/dev/null || fail "Python 3 is missing."
  command -v curl >/dev/null || fail "curl is missing."
  docker info >/dev/null 2>&1 || fail "Docker daemon inaccessible; use an account with Docker permission."
  docker compose version >/dev/null 2>&1 || fail "Docker Compose v2 is required."
}
require_branch() {
  local current
  current="$(git -C "$ROOT" branch --show-current 2>/dev/null || true)"
  [[ "$current" == 'deploy/gcp-one-command-20261023' ]] ||
    fail "Run from the deployment branch checkout, not main. Current: ${current:-unknown}"
}
network_names() {
  docker inspect -f '{{range $name, $_ := .NetworkSettings.Networks}}{{println $name}}{{end}}' "$1"
}
detect_network() {
  docker inspect yuringinx >/dev/null 2>&1 || fail "Original Nginx container not found."
  docker inspect yuriweb >/dev/null 2>&1 || fail "Original Flask container not found."
  local net
  while IFS= read -r net; do
    [[ -n "$net" ]] || continue
    if network_names yuriweb | grep -Fxq "$net"; then
      YURI_ORIGIN_NETWORK="$net"
      export YURI_ORIGIN_NETWORK
      return
    fi
  done < <(network_names yuringinx)
  fail "No network shared by original Nginx and Flask. No changes made."
}
compose() { docker compose -p yuri-catalog-preview -f "$COMPOSE" "$@"; }
show_resources() {
  local available
  available="$(df -Pk "$ROOT" | awk 'NR==2 {print $4}')"
  [[ "$available" =~ ^[0-9]+$ ]] && (( available >= 1800000 )) ||
    say "WARNING: less than ~1.8 GB disk available; image build may fail."
  if command -v free >/dev/null; then free -m | head -3; fi
}
validate_catalog() {
  [[ -f "$YURI_CATALOG_FILE" ]] ||
    fail "Missing private catalog. Create $CATALOG_DEFAULT from your private source (see docs/DEPLOY_GCP.md)."
  YURI_CATALOG_FILE="$(realpath "$YURI_CATALOG_FILE")"
  [[ "$YURI_CATALOG_FILE" != "$ROOT/"* ]] ||
    fail "Move the private catalog OUTSIDE the public repository checkout."
  [[ -r "$YURI_CATALOG_FILE" ]] || fail "Private catalog is not readable."
  export YURI_CATALOG_FILE
  # The catalogue is mode 0600 on the host; run the container as its non-root owner.
  YURI_HOST_UID="$(stat -c '%u' "$YURI_CATALOG_FILE")"
  YURI_HOST_GID="$(stat -c '%g' "$YURI_CATALOG_FILE")"
  [[ "$YURI_HOST_UID" != '0' ]] || fail "Private catalog must be owned by a non-root user."
  export YURI_HOST_UID YURI_HOST_GID
  CATALOG_COUNT="$(PYTHONPATH="$ROOT" python3 - "$YURI_CATALOG_FILE" <<'PY'
import sys
from modern.catalog import load_catalog
items = load_catalog(sys.argv[1])
if not items:
    raise SystemExit('catalog is empty')
print(len(items))
PY
)" || fail "Private catalog validation failed."
  say "Validated ${CATALOG_COUNT} allowed records (no record contents logged)."
}
wait_for_preview() {
  local i actual
  for i in $(seq 1 25); do
    actual="$(curl --fail --silent --max-time 3 'http://127.0.0.1:18000/api/v1/works' |
      python3 -c 'import sys,json; print(json.load(sys.stdin)["count"])' 2>/dev/null)" || true
    if [[ "$actual" == "$CATALOG_COUNT" ]]; then
      docker exec yuringinx wget -q -O /dev/null "http://$CANDIDATE/healthz" >/dev/null 2>&1 ||
        fail "Preview is NOT reachable from the current Nginx container."
      say "Preview ready at http://127.0.0.1:18000 (loopback only, not public)."
      return
    fi
    sleep 2
  done
  compose logs --tail=40 preview >&2 || true
  fail "Preview did not return the expected private dataset count."
}
ensure_config_mount() {
  [[ -f "$NGINX_CONF" ]] || fail "Existing Nginx config missing: $NGINX_CONF"
  NGINX_CONF="$(realpath "$NGINX_CONF")"
  local d mounts
  d="$(dirname "$NGINX_CONF")"
  mounts="$(docker inspect -f '{{range .Mounts}}{{printf "%s|%s\n" .Source .Destination}}{{end}}' yuringinx)"
  if ! printf '%s\n' "$mounts" | grep -Fxq "$NGINX_CONF|/etc/nginx/conf.d/default.conf" &&
     ! printf '%s\n' "$mounts" | grep -Fxq "$d|/etc/nginx/conf.d"; then
    fail "Nginx configuration is not confirmed as a live bind mount; refusing automatic switch."
  fi
}
count_upstream() { grep -Ec "^[[:space:]]*server[[:space:]]+$1;" "$NGINX_CONF" || true; }
rewrite_upstream() {
  python3 - "$NGINX_CONF" "$1" "$2" <<'PY'
import pathlib, re, sys
path, source, target = pathlib.Path(sys.argv[1]), sys.argv[2], sys.argv[3]
text = path.read_text()
pattern = r'(?m)^(\s*server\s+)' + re.escape(source) + r'(;)'
updated, count = re.subn(pattern, lambda m: m[1] + target + m[2], text)
if count != 1:
    raise SystemExit(f'Expected exactly one {source} upstream, got {count}')
path.write_text(updated)
PY
}
reload_nginx() {
  docker exec yuringinx nginx -t >/dev/null &&
  docker exec yuringinx nginx -s reload >/dev/null
}
check_preview() {
  validate_catalog
  [[ "$(curl -fsS --max-time 3 'http://127.0.0.1:18000/api/v1/works' |
    python3 -c 'import sys,json; print(json.load(sys.stdin)["count"])')" == "$CATALOG_COUNT" ]] ||
    fail "Preview missing or serving unexpected data; run preview first."
  docker exec yuringinx wget -q -O /dev/null "http://$CANDIDATE/healthz" >/dev/null 2>&1 ||
    fail "Nginx container cannot reach preview."
}
do_promote() {
  [[ "${YURI_CONFIRM_PROMOTE:-}" == 'YES' ]] ||
    fail "Explicit confirmation needed: YURI_CONFIRM_PROMOTE=YES bash deploy/gcp.sh promote"
  check_preview
  ensure_config_mount
  [[ "$(count_upstream "$ORIGINAL")" == '1' ]] ||
    fail "Unexpected production upstream (perhaps already switched); refusing to change it."
  mkdir -p "$STATE_DIR"
  chmod 700 "$STATE_DIR"
  local backup="$STATE_DIR/nginx-before-$(date -u +%Y%m%dT%H%M%SZ).conf"
  cp -p "$NGINX_CONF" "$backup"
  chmod 600 "$backup"
  rewrite_upstream "$ORIGINAL" "$CANDIDATE"
  if ! reload_nginx; then
    cp -p "$backup" "$NGINX_CONF"
    reload_nginx || say "CRITICAL: Nginx reload failed after restoring backup. Investigate manually."
    fail "Promotion failed; restored previous configuration."
  fi
  printf '%s\n' "$backup" > "$STATE_DIR/last-backup-path"
  chmod 600 "$STATE_DIR/last-backup-path"
  say "Promotion complete. Old app and database are still running; verify public URL manually."
  say "Rollback: bash deploy/gcp.sh rollback"
}
do_rollback() {
  ensure_config_mount
  local pointer="$STATE_DIR/last-backup-path" backup
  [[ -f "$pointer" ]] || fail "No saved promotion backup."
  backup="$(cat "$pointer")"
  [[ -f "$backup" ]] || fail "Backup no longer exists."
  [[ "$(count_upstream "$CANDIDATE")" == '1' ]] ||
    fail "Current upstream is not the preview; refusing to overwrite unrelated changes."
  [[ "$(grep -Ec "^[[:space:]]*server[[:space:]]+$ORIGINAL;" "$backup" || true)" == '1' ]] ||
    fail "Backup doesn't contain the expected original upstream."
  local current="$STATE_DIR/nginx-before-rollback-$(date -u +%Y%m%dT%H%M%SZ).conf"
  cp -p "$NGINX_CONF" "$current"
  cp -p "$backup" "$NGINX_CONF"
  if ! reload_nginx; then
    cp -p "$current" "$NGINX_CONF"
    reload_nginx || say "CRITICAL: Manual inspection of Nginx is needed."
    fail "Rollback failed; prior config restored."
  fi
  rm -f "$pointer"
  say "Previous production upstream restored. Preview container remains available."
}
command_name="${1:-}"
case "$command_name" in
  preflight)
    require_tools; require_branch; detect_network; show_resources
    say "Network found. No changes made."
    ;;
  preview)
    require_tools; require_branch; detect_network; validate_catalog; show_resources
    compose up --build --detach --force-recreate preview
    wait_for_preview
    ;;
  status)
    require_tools; detect_network
    docker ps --filter 'name=^(yuringinx|yuriweb|yuridb|yuri-catalog-preview)$' \
      --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
    curl -fsS --max-time 3 http://127.0.0.1:18000/healthz || true
    ;;
  promote)
    require_tools; require_branch; detect_network; do_promote
    ;;
  rollback)
    require_tools; detect_network; do_rollback
    ;;
  logs)
    require_tools; detect_network; compose logs --tail=70 preview
    ;;
  *)
    usage
    [[ -z "$command_name" ]] && exit 0 || exit 2
    ;;
esac

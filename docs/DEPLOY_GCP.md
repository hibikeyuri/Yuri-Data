# GCP deployment (opt-in, zero changes to the current stack until promotion)

The existing production app, database, volumes, Nginx and Cloudflare records are not modified by `preflight` or `preview`.
This branch builds a *separate* minimal Flask/Gunicorn candidate and mounts one privately generated, allowlisted catalogue file. No original database or raw input is mounted.

## 0. Know the limits

- This candidate is not yet functionally equivalent to the legacy site. Author/genre **numeric detail routes**, publisher routes, full catalogue metadata, covers and links are not migrated.
- It is not ready to replace a production website until a complete private catalogue has been exported and all relevant routes/records have been tested.
- The GCP VM previously had about 1 GiB RAM, 1 GiB swap and 4 GiB available disk. Building a second Python image may run out of resources; check `free -h` / `df -h` before proceeding.
- Cloudflare and Nginx remain responsible for the existing public hostname and TLS. Never upload origin certificates, SSH credentials or original private configuration into the repository.
- No GitHub-hosted/self-hosted runner is required for the VM deployment. CI here checks the code but does not access the VM.

## 1. Separate checkout (leave your current source/main alone)

Run on the GCP VM as the existing non-root user, **without sudo for the whole script**. The account needs Docker permission.

```bash
cd "$HOME"
git clone --branch deploy/gcp-one-command-20261023 --single-branch \
  https://github.com/hibikeyuri/Yuri-Data.git Yuri-Deploy
cd "$HOME/Yuri-Deploy"
bash deploy/gcp.sh preflight
```

This is a separate directory from your current production project. The script refuses to run `preview` / `promote` if checked out on main.

## 2. Prepare the private data locally on the VM

The script REQUIRES a private sanitized JSON list at `$HOME/yuri-private/catalog.json`. This JSON is NOT committed to GitHub or packed into the Docker image.

Example **only if** you already have a local, legitimate historical raw JSON file in the converter's expected list format:

```bash
install -d -m 700 "$HOME/yuri-private"
python3 modern/tools/export_catalog.py /PRIVATE/PATH/yuri_raw_plus.json \
  --output "$HOME/yuri-private/catalog.json"
chmod 600 "$HOME/yuri-private/catalog.json"
```

Keep the private directory mode 0700 and its JSON mode 0600. The deployment script runs the isolated container with the non-root UID/GID of that one bound file, avoiding the need to make data world-readable. The file must not be owned by root.

If the only complete records are in MySQL, **do not assume** the sample data is the complete site: export and sanitize your own authorized records first, without adding source credentials or the raw SQL dump to Git. The exporter intentionally strips all fields except ID (new row number), title, author, genres and status. Check the produced record count and ID differences before going live.

You may set `YURI_CATALOG_FILE=/absolute/private/path/catalog.json` if your sanitized file has another location. It must be outside the public checkout.

## 3. One-command preview

```bash
cd "$HOME/Yuri-Deploy"
bash deploy/gcp.sh preview
```

The script:
1. Detects the Docker network shared by the existing Nginx and Flask containers.
2. Checks and validates the private JSON without printing records.
3. Builds the separate image and starts `yuri-catalog-preview`.
4. Verifies the preview returns the expected record count and that existing Nginx can reach it.
5. Opens only `127.0.0.1:18000` on the VM. There is **no public DNS change**.

Check on the VM:

```bash
curl -fsS http://127.0.0.1:18000/healthz
curl -fsS http://127.0.0.1:18000/yuris >/dev/null
bash deploy/gcp.sh status
```

From a desktop computer, you can preview with an SSH local forward (replace `VM_HOST` and `VM_USER` on your own machine):

```bash
ssh -N -L 18000:127.0.0.1:18000 VM_USER@VM_HOST
```

Then open `http://127.0.0.1:18000` in your local browser. Do not change your existing Cloudflare DNS yet.

## 4. Explicit public switch (optional, only after verifying parity)

```bash
cd "$HOME/Yuri-Deploy"
YURI_CONFIRM_PROMOTE=YES bash deploy/gcp.sh promote
```

The script requires the existing Nginx config to be bind-mounted at the expected location; otherwise it **refuses** the switch. It makes a restricted backup in `$HOME/.local/share/yuri-deploy/`, changes ONLY the single upstream `yuriweb:5000` to `yuri-catalog-preview:8000`, runs `nginx -t` and reloads Nginx. On failure it restores the previous config. It never edits `docker-compose.prod.yml`, MySQL or certificates.

Keep the old Flask container running for rollback. Verify the live site through Cloudflare yourself after switching. This procedure assumes the host's existing `nginx/default.conf` is exactly what the running Nginx container uses; if the layout changed, deployment will fail closed.

## 5. One-command rollback

```bash
cd "$HOME/Yuri-Deploy"
bash deploy/gcp.sh rollback
```

The script restores the previous Nginx configuration from the private backup and reloads Nginx, retaining the preview instance for debugging. To inspect:

```bash
bash deploy/gcp.sh logs
bash deploy/gcp.sh status
```

## 6. Updating this branch

```bash
cd "$HOME/Yuri-Deploy"
git pull --ff-only
bash deploy/gcp.sh preview
```

For an already promoted installation, `preview` rebuilds the running candidate and may briefly interrupt requests. Roll back to the original first if zero-downtime updates are needed.

## Privacy and operational checks

- Nothing is pushed from the VM by this script. It only reads a sanitized catalogue and pulls/builds source already public in this branch.
- Never place `config.py`, `yuri.json`, SQL dumps, `cert.pem`, `key.pem` or .env files in any public branch, GitHub Actions artifact or deploy log.
- The exported **allowlisted metadata served to browsers is public** by design; keeping the JSON outside Git does not make its served entries confidential.
- Old credentials present in earlier public Git history must be rotated if active; a new branch cannot erase Git history.
- Before making any public cutover, validate catalogue completeness, routes, redirects, images, Cloudflare SSL/TLS Full (strict), and your actual ability to roll back.

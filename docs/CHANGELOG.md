# Work log

## 2026-10-21 — v2 proof of concept, new branch
- Inspected private archive locally; deliberately did not publish credentials, Cloudflare Origin key, SSH/GCP/Codex state, original database or raw external descriptions.
- Confirmed original architecture, old Flask debug/WSGI problem, and hardcoded credential in historical public Compose.
- Left main untouched and recorded its immutable historical commit for easy comparison.
- Replaced dangerous development Compose on this branch with local-only single Flask container; no MySQL/phpMyAdmin.
- Added Flask 3.1.3, Gunicorn 26.2.0, read-only local catalogue, retro-inspired responsive templates, basic security headers and safe metadata export.
- Added six historical metadata-only demo records, automated unit/smoke tests and CI workflow.
- Deferred full 229-record public release, publisher/legacy numeric ID parity, static Astro experiment, dependency audit/visual regression, and any GCP deployment.

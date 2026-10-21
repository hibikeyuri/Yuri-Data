# Architecture and decisions

## Original production architecture (2026-10-21 inspection)
Visitor → Cloudflare → GCP Debian 12 VM → Nginx Alpine (443, Cloudflare Origin CA cert) → Flask 2.1.2 built-in server at TCP 5000 → MySQL 8.0 Docker volume. The formal production configuration, docker-compose.prod.yml, was on the VM; it was distinct from the historical tracked development Compose file.

Historical scripts crawlyuri.py (Requests/BeautifulSoup) → yuri_raw_plus.json → throwcomic.py and related scripts → MySQL. Legacy pages covered /, /test, /yuris, /yuris/{id}, /authors, /authors/{id}, /genres, /genres/{id}, /publishers, /publishers/{id}.

The legacy version started with debug enabled: do not deploy it publicly unchanged. Main branch and immutable commit eeb56d9ec189e2abf12ba416fd84bc858d2d3ae3 preserve the handmade UI and old source without creating another asset copy containing secrets.

## v2 candidate in this branch
Visitor → Flask 3.1.3 + Gunicorn 26.2.0 (single small container) → local, allowlisted JSON catalogue; Jinja server-rendered pages with local CSS.

No MySQL, phpMyAdmin, live crawling, CDN scripts, external images or hotlinks. Root docker-compose.yml on this branch now binds to 127.0.0.1:8000, not to the public Internet. Production TLS/Cloudflare and a new public hosting destination are intentionally not auto-configured.

- modern/catalog.py: validates and filters local records.
- modern/app.py: read-only catalogue/author/genre/detail HTML and read-only API.
- modern/templates and modern/static: visual refresh retaining Japanese catalogue feel.
- modern/tools/export_catalog.py: offline converter from historical JSON; explicitly strips URLs, cover images, descriptions, purchasing links and all nonallowlisted fields.
- modern/data/catalog.sample.json: six original bibliographic entries for demo only.
- tests/: basic functional and data safety regression tests.

## Known limitations
- New demo has six sample records, not all 229 historic records. Full sanitized export remains local/gitignored until metadata publication rights and quality are reviewed.
- Legacy numeric author/genre IDs, publishers, book volumes, purchase links, and detailed synopsis have not been ported. Stable v2 IDs follow old snapshot row order rather than necessarily matching MySQL IDs. Do not claim 100% parity.
- Live production domain not updated and GCP has not been touched.
- FastAPI+Vue would add separate frontend/API runtime for little benefit while the domain model is being cleaned. Static Astro is a reasonable subsequent stage if hosting with no VM is desired.

## Rollback and migration
Main remains untouched. The candidate is opt-in only: test locally, verify snapshot and routes, back up DB, then decide whether to deploy the lightweight Flask container or replace it with a static generator. Always prove backups restore before decommissioning GCP.

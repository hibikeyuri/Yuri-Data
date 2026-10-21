# Yuri-Data / ユリデータ

A small handmade yuri bibliography. The original Flask + MySQL version is preserved on main, including the immutable [historical snapshot](https://github.com/hibikeyuri/Yuri-Data/tree/eeb56d9ec189e2abf12ba416fd84bc858d2d3ae3). This is an opt-in MODERNIZATION BRANCH, not a deployed replacement.

## Why v2?
The legacy site served Japanese bibliography records through Flask 2.1 + MySQL + a custom crawler, Nginx and Cloudflare. This first step uses modern Flask + Gunicorn and local JSON data instead. It keeps the personal, slightly retro catalogue feeling without a permanently running SQL database, live scraping or external cover/CDN requests.

## Run on Linux
Requires Python 3.12 or newer.

    python -m venv .venv
    . .venv/bin/activate
    python -m pip install -r modern/requirements.txt
    gunicorn --workers 1 --threads 2 --bind 127.0.0.1:8000 modern.app:app

Open http://127.0.0.1:8000. On Windows for local development only: python -m modern.app (debug remains False).

## Docker, localhost only

    docker compose up --build -d
    docker compose ps

Only 127.0.0.1:8000 is published; there is no MySQL container. Do NOT point your production domain to this without planning a secured reverse proxy or static hosting.

## Import existing data without a crawler
Only six historical metadata entries are committed for the demonstration. To privately export all 229 old records, retain your local yuri_raw_plus.json and run:

    python modern/tools/export_catalog.py /path/to/yuri_raw_plus.json --output modern/data/catalog.json

For local Gunicorn, set YURI_CATALOG=modern/data/catalog.json. For Docker, mount the generated file read-only into /app/modern/data/catalog.sample.json or make a reviewed private image. Do not publicly commit data you lack permission to republish. The exporter never fetches external websites; all image URLs, introductions and purchase links are discarded.

## Tests

    python -m pip install -r modern/requirements.txt
    python -m unittest discover -s tests -v

## Notes
- [Architecture](docs/ARCHITECTURE.md)
- [Security and Cloudflare](docs/SECURITY.md)
- [Changes and pending work](docs/CHANGELOG.md)

New UI supports home/work listing, search, genre/author indexes, detail pages and read-only JSON endpoints. Legacy publisher pages, numeric author/genre pages, richer relational fields and full record publication are not yet migrated. Original main remains unchanged. No GCP or DNS actions have been performed.

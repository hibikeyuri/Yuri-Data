"""Server-rendered Flask site. Production runs under Gunicorn; debug disabled."""
from __future__ import annotations
import os
from pathlib import Path
from flask import Flask, abort, jsonify, render_template, request
from modern.catalog import facets, filter_catalog, load_catalog

app = Flask(__name__)
app.config.update(DEBUG=False, TESTING=False)
PATH = Path(os.environ.get("YURI_CATALOG", Path(__file__).resolve().parent / "data" / "catalog.sample.json"))
CATALOG = load_catalog(PATH)

@app.after_request
def security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = "default-src 'self'; img-src 'self' data:; script-src 'self'; style-src 'self'; base-uri 'self'; object-src 'none'; frame-ancestors 'self'"
    return response

@app.get("/healthz")
def healthz():
    return jsonify(status="ok")

@app.get("/")
@app.get("/yuris")
def works():
    query = request.args.get("q", "")[:120]
    genre = request.args.get("genre", "")[:80]
    author = request.args.get("author", "")[:120]
    try:
        page = max(1, int(request.args.get("page", "1")))
    except ValueError:
        page = 1
    matched = filter_catalog(CATALOG, query, genre, author)
    size = 24
    total_pages = max(1, (len(matched) + size - 1) // size)
    page = min(page, total_pages)
    return render_template(
        "index.html", title="作品目録",
        items=matched[(page-1)*size:page*size], count=len(matched),
        page=page, total_pages=total_pages, query=query, genre=genre, author=author,
        genre_facets=facets(CATALOG, "genres"))

@app.get("/yuris/<int:work_id>")
def work_detail(work_id):
    item = next((x for x in CATALOG if x["id"] == work_id), None)
    if item is None: abort(404)
    return render_template("detail.html", item=item, title=item["title"])

@app.get("/genres")
def genres():
    return render_template("facets.html", title="Genres", groups=facets(CATALOG, "genres"), kind="genre")

@app.get("/authors")
def authors():
    return render_template("facets.html", title="Authors", groups=facets(CATALOG, "authors"), kind="author")

@app.get("/api/v1/works")
def works_api():
    matched = filter_catalog(CATALOG, request.args.get("q", "")[:120],
                             request.args.get("genre", "")[:80],
                             request.args.get("author", "")[:120])
    return jsonify(count=len(matched), items=matched[:100], truncated=len(matched)>100)

@app.get("/api/v1/works/<int:work_id>")
def work_api(work_id):
    item = next((x for x in CATALOG if x["id"] == work_id), None)
    if item is None: abort(404)
    return jsonify(item)

@app.errorhandler(404)
def not_found(error):
    return render_template("404.html", title="Not found"), 404

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=False)

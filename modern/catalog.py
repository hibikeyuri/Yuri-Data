"""Read-only, network-free bibliography catalogue."""
from __future__ import annotations
import json
from pathlib import Path

DEFAULT_CATALOG = Path(__file__).resolve().parent / "data" / "catalog.sample.json"

def load_catalog(path: str | Path = DEFAULT_CATALOG) -> list[dict]:
    content = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(content, list):
        raise ValueError("catalog must be an array")
    results, seen = [], set()
    for raw in content:
        if not isinstance(raw, dict):
            raise ValueError("catalog item must be an object")
        ident = raw.get("id")
        if type(ident) is not int or ident < 1 or ident in seen:
            raise ValueError("catalog ids must be unique positive integers")
        seen.add(ident)
        item = {"id": ident}
        for key in ("title", "author", "status"):
            value = raw.get(key, "")
            if not isinstance(value, str):
                raise ValueError(f"{key} must be text")
            item[key] = value.strip()[:300]
        genres = raw.get("genres", [])
        if not isinstance(genres, list) or any(not isinstance(g, str) for g in genres):
            raise ValueError("genres must be an array of text")
        item["genres"] = [g.strip()[:80] for g in genres if g.strip()][:20]
        results.append(item)
    return sorted(results, key=lambda item: item["id"])

def filter_catalog(items: list[dict], query: str = "", genre: str = "", author: str = "") -> list[dict]:
    q, g, a = query.casefold().strip()[:120], genre.casefold().strip()[:80], author.casefold().strip()[:120]
    return [item for item in items
            if (not q or q in (item["title"] + " " + item["author"]).casefold())
            and (not g or any(x.casefold() == g for x in item["genres"]))
            and (not a or a in item["author"].casefold())]

def facets(items: list[dict], key: str) -> list[tuple[str, int]]:
    counts: dict[str, int] = {}
    for item in items:
        values = item["genres"] if key == "genres" else [item["author"]]
        for value in values:
            if value:
                counts[value] = counts.get(value, 0) + 1
    return sorted(counts.items(), key=lambda pair: (-pair[1], pair[0]))

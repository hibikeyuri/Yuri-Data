"""Offline-only importer; republishes only allowlisted bibliography metadata."""
from __future__ import annotations
import argparse
import json
from pathlib import Path

def transform(records: list[dict]) -> list[dict]:
    if not isinstance(records, list):
        raise ValueError("expected a JSON list")
    result = []
    for index, record in enumerate(records, start=1):
        if not isinstance(record, dict):
            raise ValueError("each entry must be an object")
        genres = record.get("genre") or []
        if not isinstance(genres, list):
            genres = []
        result.append({
            "id": index,
            "title": str(record.get("title") or "").strip()[:300],
            "author": str(record.get("author") or "").strip()[:300],
            "genres": [g.strip()[:80] for g in genres if isinstance(g, str) and g.strip()][:20],
            "status": str(record.get("yuri status") or "").strip()[:300],
        })
    return result

def main():
    parser = argparse.ArgumentParser(description="Convert old JSON snapshot WITHOUT making network requests")
    parser.add_argument("source", type=Path, help="Existing local yuri_raw_plus.json")
    parser.add_argument("--output", type=Path, default=Path("modern/data/catalog.json"))
    args = parser.parse_args()
    records = json.loads(args.source.read_text(encoding="utf-8"))
    items = transform(records)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(items, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Exported {len(items)} bibliographic metadata records. No URLs/images/introductions.")

if __name__ == "__main__":
    main()

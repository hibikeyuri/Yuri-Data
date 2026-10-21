import json
import tempfile
import unittest
from pathlib import Path
from modern.catalog import facets, filter_catalog, load_catalog
from modern.tools.export_catalog import transform

class CatalogTests(unittest.TestCase):
    def test_sample_and_filters(self):
        catalog = load_catalog()
        self.assertEqual(len(catalog), 6)
        self.assertEqual(len(filter_catalog(catalog, query="SAL")), 1)
        self.assertTrue(filter_catalog(catalog, genre="恋愛"))
        self.assertTrue(facets(catalog, "genres"))

    def test_safe_offline_export(self):
        raw = [{"title":"Test", "author":"Person", "genre":["yuri"],
                "yuri status":"ok", "comic page":"https://example.invalid",
                "introduction":["external copyrighted prose"], "secret":"should-not-publish"}]
        result = transform(raw)
        self.assertEqual(set(result[0]), {"id", "title", "author", "genres", "status"})
        self.assertNotIn("https:", json.dumps(result))
        self.assertNotIn("should-not-publish", json.dumps(result))

    def test_duplicate_id_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "catalog.json"
            path.write_text('[{"id":1},{"id":1}]')
            with self.assertRaises(ValueError):
                load_catalog(path)

    def test_flask_smoke(self):
        from modern.app import app
        client = app.test_client()
        for url in ["/", "/yuris", "/authors", "/genres", "/yuris/1", "/healthz"]:
            self.assertEqual(client.get(url).status_code, 200, url)
        self.assertEqual(client.get("/yuris/999999").status_code, 404)
        self.assertEqual(client.get("/api/v1/works?q=SAL").json["count"], 1)
        self.assertFalse(app.debug)
        self.assertEqual(client.get("/").headers["X-Content-Type-Options"], "nosniff")

if __name__ == "__main__":
    unittest.main()

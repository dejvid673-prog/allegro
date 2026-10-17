"""Regression tests for deterministic Allegro catalog diff."""
import unittest

from scripts.compare_api_catalogs import compare_catalogs, render_markdown


class DiffTests(unittest.TestCase):
    def test_add_removed_and_updated(self):
        before = [
            {"method": "GET", "path": "/offers", "scopes": ["one"], "deprecated": False},
            {"method": "GET", "path": "/removed"},
        ]
        after = [
            {"method": "GET", "path": "/offers", "scopes": ["two"], "deprecated": True},
            {"method": "GET", "path": "/added"},
        ]
        result = compare_catalogs(before, after)
        self.assertEqual(result["added"], ["GET /added"])
        self.assertEqual(result["removed"], ["GET /removed"])
        self.assertEqual(len(result["changed"]), 1)
        self.assertEqual(set(result["changed"][0]["fields"]), {"scopes", "deprecated"})
        self.assertIn("schema", render_markdown(result).lower())

    def test_order_independent_and_duplicate_fail_closed(self):
        source = [{"method": "GET", "path": "/a"}, {"method": "POST", "path": "/b"}]
        result = compare_catalogs(source, list(reversed(source)))
        self.assertFalse(result["added"] or result["removed"] or result["changed"])
        with self.assertRaises(ValueError):
            compare_catalogs(source, source + [source[0]])

    def test_response_codes_change(self):
        old = [{"method": "GET", "path": "/x", "responseCodes": ["200"]}]
        new = [{"method": "GET", "path": "/x", "responseCodes": ["200", "403"]}]
        result = compare_catalogs(old, new)
        self.assertIn("responseCodes", result["changed"][0]["fields"])


if __name__ == "__main__":
    unittest.main()

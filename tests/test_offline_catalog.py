"""Offline tests for Allegro knowledge MCP business functions."""
import unittest

from allegro_mcp.offline_catalog import (
    _read_operations,
    catalog_status,
    find_read_endpoints,
    get_read_endpoint,
)


class OfflineCatalogTests(unittest.TestCase):
    def test_status_is_explicitly_offline_and_stale(self):
        result = catalog_status()
        self.assertFalse(result["allegro_connected"])
        self.assertFalse(result["live_api_verified"])
        self.assertEqual(result["mode"], "OFFLINE_READ_ONLY")
        self.assertIn("HOLD", result["snapshot_status"])
        self.assertGreater(result["operation_count"], 0)

    def test_catalog_is_get_only(self):
        ops = _read_operations()
        self.assertGreater(len(ops), 0)
        self.assertTrue(all(item["method"] == "GET" for item in ops))

    def test_find_get_never_returns_write_methods(self):
        result = find_read_endpoints("offer", 30)
        self.assertGreater(result["total_matches"], 0)
        self.assertTrue(all(item["method"] == "GET" for item in result["returned"]))

    def test_find_limit_and_validation(self):
        result = find_read_endpoints("sale", 1)
        self.assertLessEqual(len(result["returned"]), 1)
        for bad in ("", "  ", "x" * 121):
            with self.assertRaises(ValueError):
                find_read_endpoints(bad)
        for bad in (0, -1, 31, True, "5"):
            with self.assertRaises(ValueError):
                find_read_endpoints("offer", bad)

    def test_get_exact_path_from_catalog(self):
        path = _read_operations()[0]["path"]
        result = get_read_endpoint(path)
        self.assertEqual(result["method"], "GET")
        self.assertEqual(result["path"], path)
        self.assertEqual(result["snapshot_status"], "STALE_UNVERIFIED")

    def test_reject_url_unknown_and_write_only_paths(self):
        for path in ("https://api.allegro.pl/sale/offers", "/not-a-real-resource"):
            with self.assertRaises(ValueError):
                get_read_endpoint(path)

    def test_no_live_client_or_import_side_effect(self):
        # Importing knowledge functions must never require Allegro credentials.
        from allegro_mcp import offline_catalog
        self.assertFalse(hasattr(offline_catalog, "ACCESS_TOKEN"))


if __name__ == "__main__":
    unittest.main()

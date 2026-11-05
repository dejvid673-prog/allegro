"""Offline safety and math tests for the normalized Allegro Ads snapshot CLI."""
from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from scripts.ads_profit_snapshot import audit, number, ratio


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "templates" / "ads-audit-import.synthetic.example.json"


class AdsProfitSnapshotTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_fixture_exact_economics(self):
        result = audit(self.data)
        self.assertEqual(result["status"], "PASS", result["errors"])
        self.assertEqual(result["totals"]["spend"], "100")
        self.assertEqual(result["metrics"]["ctr"], "0.02")
        self.assertEqual(result["metrics"]["avg_cpc"], "0.5")
        self.assertEqual(result["metrics"]["cvr"], "0.05")
        self.assertEqual(result["metrics"]["roas"], "10")
        self.assertEqual(result["metrics"]["acos"], "0.1")
        self.assertEqual(result["attributed_contribution_before_ads"], "180")
        self.assertEqual(result["attributed_contribution_after_ads"], "80")

    def test_missing_cost_status_holds_profit(self):
        self.data["costs"][0]["cost_items"] = self.data["costs"][0]["cost_items"][:-1]
        result = audit(self.data)
        self.assertEqual(result["status"], "HOLD_DATA")
        self.assertIsNone(result["attributed_contribution_after_ads"])
        self.assertTrue(any("missing cost statuses" in msg for msg in result["errors"]))

    def test_unknown_cost_is_not_zero(self):
        self.data["costs"][0]["cost_items"][0]["status"] = "UNKNOWN"
        self.data["costs"][0]["cost_items"][0]["value"] = None
        result = audit(self.data)
        self.assertEqual(result["status"], "HOLD_DATA")
        self.assertIsNone(result["attributed_contribution_after_ads"])

    def test_duplicate_report_rows_block_totals_as_profit(self):
        self.data["ads_rows"].append(copy.deepcopy(self.data["ads_rows"][0]))
        result = audit(self.data)
        self.assertEqual(result["status"], "HOLD_DATA")
        self.assertTrue(any("duplicate source grain" in msg for msg in result["errors"]))

    def test_open_seven_day_window_provisional(self):
        self.data["manifest"]["attribution_maturity"] = "OPEN_7D_WINDOW"
        result = audit(self.data)
        self.assertEqual(result["status"], "PROVISIONAL")
        self.assertTrue(result["notes"])

    def test_refund_requires_source_reconciliation(self):
        self.data["order_lines"][0]["refund_amount"] = 25
        result = audit(self.data)
        self.assertEqual(result["status"], "HOLD_DATA")
        self.assertTrue(any("refund present" in msg for msg in result["errors"]))

    def test_mixed_cost_and_spend_basis_blocks_profit(self):
        self.data["costs"][0]["cost_items"][0]["basis"] = "NET"
        result = audit(self.data)
        self.assertEqual(result["status"], "HOLD_DATA")

    def test_zero_denominators_report_null(self):
        row = self.data["ads_rows"][0]
        row.update(impressions=0, clicks=0, spend=0, attributed_revenue=0, attributed_orders=0)
        for line in self.data["order_lines"]:
            line["ads_attributed"] = False
        result = audit(self.data)
        self.assertEqual(result["status"], "PASS", result["errors"])
        self.assertIsNone(result["metrics"]["avg_cpc"])
        self.assertIsNone(result["metrics"]["roas"])
        self.assertIsNone(result["metrics"]["cvr"])
        self.assertIsNone(result["metrics"]["acos"])
        self.assertEqual(result["attributed_contribution_after_ads"], "0")

    def test_two_attributed_items_in_one_order_do_not_double_count_orders(self):
        extra = copy.deepcopy(self.data["order_lines"][0])
        extra["line_item_id"] = "SYNTHETIC-ADDITIONAL-LINE"
        extra["quantity"] = 1
        extra["sale_amount"] = 100
        self.data["order_lines"].append(extra)
        self.data["ads_rows"][0]["attributed_revenue"] = 1100
        result = audit(self.data)
        self.assertEqual(result["status"], "PASS", result["errors"])
        self.assertEqual(result["attributed_contribution_before_ads"], "198")
        self.assertEqual(result["attributed_contribution_after_ads"], "98")
        self.assertEqual(result["metrics"]["cvr"], "0.05")

    def test_duplicate_row_suppresses_unreliable_kpis(self):
        self.data["ads_rows"].append(copy.deepcopy(self.data["ads_rows"][0]))
        result = audit(self.data)
        self.assertEqual(result["status"], "HOLD_DATA")
        self.assertIsNone(result["metrics"])

    def test_input_bool_and_negative_rejected(self):
        with self.assertRaises(ValueError):
            number(True, "cost")
        with self.assertRaises(ValueError):
            number(-1, "cost")
        self.assertIsNone(ratio(number(5, "num"), number(0, "den")))

    def test_unknown_ads_attribution_holds(self):
        self.data["order_lines"][0]["ads_attributed"] = None
        result = audit(self.data)
        self.assertEqual(result["status"], "HOLD_DATA")
        self.assertTrue(any("unknown line-item attribution" in msg for msg in result["errors"]))


if __name__ == "__main__":
    unittest.main()

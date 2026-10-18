"""Offline contract regression: no network calls or merchant writes."""
import copy
import unittest

from allegro_domain.shipments import audit_shipment_plan
from allegro_domain.costs import audit_cost_snapshot, COST_FIELDS


def order():
    return {
        "status": "READY_FOR_PROCESSING",
        "items": [
            {"sku": "chalk-24", "kind": "CHALK_BAG", "quantity": 2},
            {"sku": "can-5l", "kind": "CANISTER_5L", "quantity": 4},
        ],
        "service": {"max_weight_grams": 31500, "supports_cod": True, "verified": True},
        "cod_required": False,
        "cod_amount_gross": None,
        "shipment_status": "NOT_CREATED",
        "first_scan_at": None,
    }


def parcels():
    return [
        {"items": [{"sku": "chalk-24", "quantity": 1}], "packed_weight_grams": 24200, "verified": True},
        {"items": [{"sku": "chalk-24", "quantity": 1}], "packed_weight_grams": 24200, "verified": True},
        {"items": [{"sku": "can-5l", "quantity": 2}], "packed_weight_grams": 10500, "verified": True},
        {"items": [{"sku": "can-5l", "quantity": 2}], "packed_weight_grams": 10500, "verified": True},
    ]


def snapshot():
    return {
        "currency": "PLN", "taxBasis": "NET", "complete": True,
        "salesPriceGross": "123.00", "salesRevenueNet": "100.00",
        "minimumContributionMarginNet": "10.00",
        **{key: {
            "value": "0.00", "status": "ZERO_CONFIRMED",
            "sourceRef": "ledger:0", "effectiveAt": "2026-10-18T12:00:00Z",
        } for key in COST_FIELDS},
    }


class ShipmentPreflightTests(unittest.TestCase):
    def test_sufficient_packages_pass(self):
        r = audit_shipment_plan(order(), parcels())
        self.assertEqual(r["status"], "PASS")
        self.assertEqual(r["parcel_count"], 4)
        self.assertFalse(r["handover_confirmed"])

    def test_missing_chalk_package_is_blocked(self):
        p = parcels(); p.pop(1)
        r = audit_shipment_plan(order(), p)
        self.assertEqual(r["status"], "BLOCK")
        self.assertIn("MISSING_ITEM_ALLOCATION", r["findings"])

    def test_two_chalk_bags_same_package_are_blocked(self):
        p = parcels(); p[0]["items"][0]["quantity"] = 2; p.pop(1)
        self.assertIn("CHALK_ONE_BAG_PER_PARCEL", audit_shipment_plan(order(), p)["findings"])

    def test_mixed_chalk_canisters_blocked(self):
        p = parcels(); p[0]["items"].append({"sku": "can-5l", "quantity": 1})
        p[2]["items"][0]["quantity"] = 1
        r = audit_shipment_plan(order(), p)
        self.assertEqual(r["status"], "BLOCK")
        self.assertIn("MIXED_CHALK_LIQUID", r["findings"])

    def test_four_canisters_split_three_and_one_requires_review(self):
        p = parcels(); p[2]["items"][0]["quantity"] = 3
        p[3]["items"][0]["quantity"] = 1
        r = audit_shipment_plan(order(), p)
        self.assertEqual(r["status"], "HUMAN_REQUIRED")
        self.assertIn("CANISTER_FOUR_REQUIRES_TWO_PLUS_TWO", r["findings"])

    def test_more_than_four_canisters_requires_human(self):
        o = order(); o["items"][1]["quantity"] = 5
        p = parcels(); p[3]["items"][0]["quantity"] = 3
        self.assertEqual(audit_shipment_plan(o, p)["status"], "HUMAN_REQUIRED")

    def test_canister_package_more_than_three_blocked(self):
        p = parcels(); p[2]["items"][0]["quantity"] = 4; p.pop()
        self.assertIn("TOO_MANY_CANISTERS", audit_shipment_plan(order(), p)["findings"])

    def test_unverified_weight_requires_human(self):
        p = parcels(); p[0]["verified"] = False
        self.assertEqual(audit_shipment_plan(order(), p)["status"], "HUMAN_REQUIRED")

    def test_missing_or_zero_weight_requires_human(self):
        p = parcels(); p[0]["packed_weight_grams"] = 0
        self.assertIn("MISSING_PACKED_WEIGHT", audit_shipment_plan(order(), p)["findings"])

    def test_weight_exceeds_verified_carrier_limit_blocked(self):
        p = parcels(); p[0]["packed_weight_grams"] = 32000
        self.assertIn("CARRIER_WEIGHT_LIMIT", audit_shipment_plan(order(), p)["findings"])

    def test_unknown_carrier_limits_requires_human(self):
        o = order(); o["service"]["verified"] = False
        self.assertEqual(audit_shipment_plan(o, parcels())["status"], "HUMAN_REQUIRED")

    def test_cod_pallet_without_cod_support_blocked(self):
        o = order(); o["cod_required"] = True
        o["cod_amount_gross"] = "300.00"
        o["service"]["supports_cod"] = False
        o["service"]["max_weight_grams"] = 300000
        o["items"] = [{"sku": "pallet", "kind": "PALLET", "quantity": 1}]
        p = [{"items": [{"sku": "pallet", "quantity": 1}],
              "packed_weight_grams": 200000, "verified": True}]
        r = audit_shipment_plan(o, p)
        self.assertIn("PALLET_COD_MISMATCH", r["findings"])
        self.assertEqual(r["status"], "BLOCK")

    def test_pallet_always_manual(self):
        o = order()
        o["items"] = [{"sku": "pallet", "kind": "PALLET", "quantity": 1}]
        o["service"]["max_weight_grams"] = 300000
        p = [{"items": [{"sku": "pallet", "quantity": 1}],
              "packed_weight_grams": 200000, "verified": True}]
        self.assertEqual(audit_shipment_plan(o, p)["status"], "HUMAN_REQUIRED")

    def test_wrong_order_status_blocks(self):
        o = order(); o["status"] = "CANCELLED"
        self.assertIn("ORDER_NOT_READY", audit_shipment_plan(o, parcels())["findings"])

    def test_first_scan_proves_handover_but_label_does_not(self):
        o = order(); o["shipment_status"] = "LABEL_CREATED"
        self.assertFalse(audit_shipment_plan(o, parcels())["handover_confirmed"])
        o["first_scan_at"] = "2026-10-18T10:00:00Z"
        self.assertTrue(audit_shipment_plan(o, parcels())["handover_confirmed"])

    def test_duplicate_and_unexpected_sku_blocked(self):
        p = parcels(); p[0]["items"].append({"sku": "unknown", "quantity": 1})
        self.assertIn("UNKNOWN_SKU", audit_shipment_plan(order(), p)["findings"])
        o = order(); o["items"].append(copy.deepcopy(o["items"][0]))
        self.assertIn("DUPLICATE_ORDER_SKU", audit_shipment_plan(o, parcels())["findings"])

    def test_invalid_user_input_fails_closed(self):
        with self.assertRaises(ValueError):
            audit_shipment_plan({"items": "not-a-list"}, [])
        with self.assertRaises(ValueError):
            audit_shipment_plan(order(), "not-a-list")
        p = parcels(); p[0]["items"][0]["quantity"] = True
        with self.assertRaises(ValueError):
            audit_shipment_plan(order(), p)
        o = order(); o["items"][0]["quantity"] = -1
        with self.assertRaises(ValueError):
            audit_shipment_plan(o, parcels())


class CostPreflightTests(unittest.TestCase):
    def test_precise_decimal_margin(self):
        s = snapshot()
        s["purchaseNet"] = {
            "value": "60.11", "status": "KNOWN",
            "sourceRef": "invoice:1", "effectiveAt": "2026-10-18T12:00:00Z",
        }
        r = audit_cost_snapshot(s)
        self.assertEqual(r["status"], "PASS")
        self.assertEqual(r["totalVariableCostNet"], "60.11")
        self.assertEqual(r["contributionMarginNet"], "39.89")
        self.assertEqual(r["contributionMarginPct"], "39.89")

    def test_unknown_cost_blocks_no_false_margin(self):
        s = snapshot()
        s["smartContributionNet"]["status"] = "UNKNOWN"
        s["smartContributionNet"]["value"] = None
        r = audit_cost_snapshot(s)
        self.assertEqual(r["status"], "BLOCK")
        self.assertIsNone(r["contributionMarginNet"])
        self.assertIn("UNKNOWN_COST:smartContributionNet", r["findings"])

    def test_missing_required_cost_blocks(self):
        s = snapshot(); del s["carrierBaseNet"]
        self.assertIn("UNKNOWN_COST:carrierBaseNet", audit_cost_snapshot(s)["findings"])

    def test_zero_confirmed_without_source_blocks(self):
        s = snapshot(); s["purchaseNet"]["sourceRef"] = None
        self.assertIn("MISSING_COST_EVIDENCE:purchaseNet", audit_cost_snapshot(s)["findings"])

    def test_mixed_gross_net_blocks(self):
        s = snapshot(); s["taxBasis"] = "MIXED_REQUIRES_REVIEW"
        self.assertEqual(audit_cost_snapshot(s)["status"], "BLOCK")

    def test_incomplete_flag_blocks(self):
        s = snapshot(); s["complete"] = False
        self.assertEqual(audit_cost_snapshot(s)["status"], "BLOCK")

    def test_below_minimum_margin_blocks(self):
        s = snapshot(); s["minimumContributionMarginNet"] = "125.00"
        r = audit_cost_snapshot(s)
        self.assertEqual(r["status"], "BLOCK")
        self.assertEqual(r["contributionMarginNet"], "100.00")
        self.assertFalse(r["meetsMinimum"])

    def test_gross_to_net_is_not_guessed(self):
        s = snapshot(); del s["salesRevenueNet"]
        r = audit_cost_snapshot(s)
        self.assertEqual(r["status"], "BLOCK")
        self.assertIsNone(r["contributionMarginNet"])

    def test_reject_float_nan_bool_negative_and_bad_status(self):
        for val in (True, -1, float("nan"), float("inf"), "bad"):
            s = snapshot(); s["purchaseNet"]["value"] = val
            with self.subTest(value=repr(val)), self.assertRaises(ValueError):
                audit_cost_snapshot(s)
        s = snapshot(); s["purchaseNet"]["status"] = "WRONG"
        with self.assertRaises(ValueError):
            audit_cost_snapshot(s)

    def test_known_requires_evidence_and_nonzero(self):
        s = snapshot()
        s["purchaseNet"]["status"] = "KNOWN"
        s["purchaseNet"]["value"] = "0.00"
        self.assertIn("INCONSISTENT_COST_STATE:purchaseNet", audit_cost_snapshot(s)["findings"])

    def test_not_applicable_must_have_evidence(self):
        s = snapshot()
        s["codFeeNet"] = {
            "value": None, "status": "NOT_APPLICABLE",
            "sourceRef": "no-cod", "effectiveAt": "2026-10-18T12:00:00Z",
        }
        self.assertEqual(audit_cost_snapshot(s)["status"], "PASS")
        s["codFeeNet"]["sourceRef"] = None
        self.assertIn("MISSING_COST_EVIDENCE:codFeeNet", audit_cost_snapshot(s)["findings"])

    def test_no_mutation_of_input(self):
        s = snapshot(); original = copy.deepcopy(s)
        audit_cost_snapshot(s)
        self.assertEqual(s, original)


if __name__ == "__main__":
    unittest.main()

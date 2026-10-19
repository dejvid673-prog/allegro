"""Contract/regression tests for proposed offline Allegro commerce operations."""
import copy
from datetime import datetime, timedelta, timezone
import unittest

from allegro_domain.assortment import audit_assortment_snapshot
from allegro_domain.repricing import propose_price_change
from allegro_domain.market import compare_market_snapshots
from allegro_domain.shipment_monitor import audit_shipment_events
from allegro_domain.costs import COST_FIELDS


def master():
    return [{
        "sku": "CHALK-25", "gtin": "5901234123457",
        "expected_stock_by_connection": {"account-a": 4, "account-b": 2},
        "expected_price_by_connection": {"account-a": "55.00", "account-b": "57.00"},
    }]


def offer(account="account-a", oid="1001", stock=4, price="55.00"):
    return {
        "connection_id": account, "offer_id": oid, "sku": "CHALK-25",
        "gtin": "5901234123457", "stock": stock,
        "price_gross": price, "status": "ACTIVE",
    }


def costs():
    return {
        "currency": "PLN", "taxBasis": "NET", "complete": True,
        "salesPriceGross": "60.00", "salesRevenueNet": "48.78",
        "minimumContributionMarginNet": "5.00",
        **{name: {"status": "ZERO_CONFIRMED", "value": "0.00",
                  "sourceRef": "test-invoice", "effectiveAt": "2026-10-19T01:00:00Z"}
           for name in COST_FIELDS},
    }


def own():
    return [{
        "connection_id": "account-a", "offer_id": "1001",
        "sku": "CHALK-25", "gtin": "5901234123457",
        "net_weight_grams": 25000, "units_per_offer": 1,
        "condition": "NEW", "price_gross": "55.00", "shipping_gross": "12.00",
    }]


def competitor(*, price="50.00", shipping="14.00", weight=25000):
    return {
        "source_type": "USER_PROVIDED_EXPORT",
        "source_ref": "export:competitors.csv#1",
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "offer_ref": "market-1", "gtin": "5901234123457",
        "net_weight_grams": weight, "units_per_offer": 1, "condition": "NEW",
        "price_gross": price, "shipping_gross": shipping,
    }


def shipment(**kw):
    s = {
        "connection_id": "account-a", "order_id": "order-1",
        "shipment_id": "ship-1", "tracking_number": "TRACK-1",
        "status": "LABEL_CREATED", "label_created_at": "2026-10-18T10:00:00Z",
        "first_scan_at": None, "first_scan_verified": False,
        "cod_required": False,
    }
    s.update(kw)
    return s


class AssortmentTests(unittest.TestCase):
    def test_clean_two_account_snapshot(self):
        r = audit_assortment_snapshot(
            [offer(), offer("account-b", "2001", stock=2, price="57.00")], master()
        )
        self.assertEqual(r["status"], "PASS")
        self.assertEqual(r["offer_count"], 2)
        self.assertFalse(r["writes_performed"])

    def test_stock_and_price_drift_are_reported_per_connection(self):
        r = audit_assortment_snapshot([offer(stock=3, price="54.00")], master())
        codes = {f["code"] for f in r["findings"]}
        self.assertIn("STOCK_DRIFT", codes)
        self.assertIn("PRICE_DRIFT", codes)
        self.assertEqual(r["status"], "REVIEW")

    def test_unknown_stock_expectation_is_not_zero(self):
        m = master()
        m[0]["expected_stock_by_connection"] = {}
        r = audit_assortment_snapshot([offer()], m)
        self.assertIn("STOCK_EXPECTATION_UNKNOWN", {f["code"] for f in r["findings"]})

    def test_missing_sku_and_gtin_mismatch(self):
        a = offer()
        a["sku"] = "OTHER"
        r = audit_assortment_snapshot([a], master())
        self.assertIn("SKU_MISSING_IN_MASTER", {f["code"] for f in r["findings"]})
        a = offer()
        a["gtin"] = "000"
        r = audit_assortment_snapshot([a], master())
        self.assertIn("GTIN_MISMATCH", {f["code"] for f in r["findings"]})

    def test_three_same_sku_active_offers_only_flag_possible_duplicate(self):
        offers = [offer("account-a", "1001"), offer("account-a", "1002"),
                  offer("account-b", "2001", 2, "57.00")]
        r = audit_assortment_snapshot(offers, master())
        self.assertIn("POSSIBLE_MULTI_ACCOUNT_DUPLICATE",
                      {f["code"] for f in r["findings"]})

    def test_duplicate_identity_fails_closed(self):
        with self.assertRaises(ValueError):
            audit_assortment_snapshot([offer(), offer()], master())

    def test_invalid_types_rejected_and_input_untouched(self):
        a, m = [offer()], master()
        old_a, old_m = copy.deepcopy(a), copy.deepcopy(m)
        audit_assortment_snapshot(a, m)
        self.assertEqual((a, m), (old_a, old_m))
        a[0]["stock"] = True
        with self.assertRaises(ValueError):
            audit_assortment_snapshot(a, m)


class RepricingTests(unittest.TestCase):
    def test_proposal_is_nonexecuting_and_keeps_expected_state(self):
        r = propose_price_change(offer(), "60.00", costs())
        self.assertEqual(r["status"], "DRAFT")
        self.assertEqual(r["delta_gross"], "5.00")
        self.assertEqual(r["expected_price_gross"], "55.00")
        self.assertEqual(r["contribution_margin_net"], "48.78")
        self.assertFalse(r["writes_performed"])

    def test_unknown_smart_cost_blocks_price(self):
        snap = costs()
        snap["smartContributionNet"]["status"] = "UNKNOWN"
        snap["smartContributionNet"]["value"] = None
        r = propose_price_change(offer(), "60.00", snap)
        self.assertEqual(r["status"], "BLOCK")
        self.assertIn("UNKNOWN_COST:smartContributionNet", r["findings"])

    def test_mismatched_projected_price_blocks(self):
        r = propose_price_change(offer(), "61.00", costs())
        self.assertEqual(r["status"], "BLOCK")
        self.assertIn("PROPOSED_PRICE_COST_SNAPSHOT_MISMATCH", r["findings"])

    def test_below_minimum_margin_blocks(self):
        snap = costs()
        snap["minimumContributionMarginNet"] = "60.00"
        self.assertEqual(propose_price_change(offer(), "60.00", snap)["status"], "BLOCK")

    def test_money_rejects_float_and_negative(self):
        for value in (12.01, "-1", True, "NaN"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                propose_price_change(offer(), value, costs())


class MarketSnapshotTests(unittest.TestCase):
    def test_compares_full_delivered_price_and_same_pack(self):
        r = compare_market_snapshots(own(), [competitor()])
        self.assertEqual(r["status"], "DRAFT")
        self.assertEqual(r["comparisons"][0]["own_delivered_gross"], "67.00")
        self.assertEqual(r["comparisons"][0]["competitor_delivered_gross"], "64.00")
        self.assertEqual(r["comparisons"][0]["own_minus_competitor_gross"], "3.00")
        self.assertFalse(r["market_data_verified"])

    def test_different_weight_is_not_comparable(self):
        r = compare_market_snapshots(own(), [competitor(weight=24000)])
        self.assertEqual(r["comparisons"], [])
        self.assertIn("NO_EXACT_COMPARISON", r["findings"])

    def test_missing_source_blocks_comparison(self):
        c = competitor()
        c["source_ref"] = ""
        r = compare_market_snapshots(own(), [c])
        self.assertEqual(r["status"], "BLOCK")
        self.assertEqual(r["comparisons"], [])

    def test_stale_source_is_not_competitive_signal(self):
        c = competitor()
        c["observed_at"] = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
        r = compare_market_snapshots(own(), [c])
        self.assertEqual(r["comparisons"], [])
        self.assertIn("STALE_MARKET_OBSERVATION", r["findings"])

    def test_gtin_is_not_guessed_from_name(self):
        c = competitor()
        c["gtin"] = "000"
        r = compare_market_snapshots(own(), [c])
        self.assertEqual(r["comparisons"], [])

    def test_float_money_rejected(self):
        c = competitor()
        c["price_gross"] = 50.11
        with self.assertRaises(ValueError):
            compare_market_snapshots(own(), [c])


class ShipmentMonitorTests(unittest.TestCase):
    AS_OF = "2026-10-19T15:00:00Z"

    def test_old_label_without_first_scan_requires_review(self):
        r = audit_shipment_events([shipment()], as_of=self.AS_OF)
        self.assertEqual(r["status"], "REVIEW")
        self.assertIn("LABEL_OLDER_THAN_24H_NO_FIRST_SCAN", {f["code"] for f in r["findings"]})
        self.assertEqual(r["confirmed_handover_count"], 0)

    def test_first_scan_requires_verification_flag(self):
        s = shipment(first_scan_at="2026-10-18T12:00:00Z")
        r = audit_shipment_events([s], as_of=self.AS_OF)
        self.assertEqual(r["confirmed_handover_count"], 0)
        s["first_scan_verified"] = True
        r = audit_shipment_events([s], as_of=self.AS_OF)
        self.assertEqual(r["confirmed_handover_count"], 1)

    def test_claimed_handover_without_scan_blocked(self):
        r = audit_shipment_events([shipment(status="HANDED_OVER")], as_of=self.AS_OF)
        self.assertEqual(r["status"], "BLOCK")
        self.assertIn("FALSE_HANDOVER_STATUS", {f["code"] for f in r["findings"]})

    def test_cod_discrepancy_blocked(self):
        s = shipment(cod_required=True, cod_amount_gross="100.00",
                     carrier_cod_amount_gross="0.00")
        r = audit_shipment_events([s], as_of=self.AS_OF)
        self.assertIn("COD_AMOUNT_MISMATCH", {f["code"] for f in r["findings"]})

    def test_duplicate_tracking_different_order_blocked(self):
        a = shipment()
        b = shipment(order_id="order-2", shipment_id="ship-2")
        r = audit_shipment_events([a, b], as_of=self.AS_OF)
        self.assertIn("TRACKING_ASSIGNED_TO_MULTIPLE_ORDERS",
                      {f["code"] for f in r["findings"]})

    def test_fresh_label_not_flagged_as_late(self):
        s = shipment(label_created_at="2026-10-19T14:00:00Z")
        r = audit_shipment_events([s], as_of=self.AS_OF)
        self.assertNotIn("LABEL_OLDER_THAN_24H_NO_FIRST_SCAN",
                         {f["code"] for f in r["findings"]})

    def test_zero_cod_amount_blocked(self):
        s = shipment(cod_required=True, cod_amount_gross="0.00",
                     carrier_cod_amount_gross="0.00")
        r = audit_shipment_events([s], as_of=self.AS_OF)
        self.assertEqual(r["status"], "BLOCK")
        self.assertIn("COD_AMOUNT_ZERO", {f["code"] for f in r["findings"]})

    def test_label_from_future_flagged(self):
        s = shipment(label_created_at="2026-10-20T12:00:00Z")
        r = audit_shipment_events([s], as_of=self.AS_OF)
        self.assertEqual(r["status"], "BLOCK")
        self.assertIn("LABEL_FROM_FUTURE", {f["code"] for f in r["findings"]})

    def test_created_label_without_timestamp_requires_review(self):
        s = shipment(label_created_at=None)
        r = audit_shipment_events([s], as_of=self.AS_OF)
        self.assertEqual(r["status"], "REVIEW")
        self.assertIn("MISSING_LABEL_TIMESTAMP", {f["code"] for f in r["findings"]})

    def test_bad_timestamp_fails_closed(self):
        with self.assertRaises(ValueError):
            audit_shipment_events([shipment()], as_of="2026-10-19")


if __name__ == "__main__":
    unittest.main()

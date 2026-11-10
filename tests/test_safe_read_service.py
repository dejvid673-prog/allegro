"""Synthetic integration tests: READ -> trusted gate -> PII-safe projection."""
import json
import unittest

from allegro_api.read_client import (
    AllegroReadClient, Connection, ConnectionRegistry,
    ConnectionAccessDenied, MissingScope, Response,
)
from allegro_api.safe_read_service import (
    SafeAllegroReadService, SellerIdentityNotVerified,
)

OID = "29738e61-7f6a-11e8-ac45-09db60ede9d6"
LID = "31896450-2de1-11e9-bced-352ab82ad9cd"
PII = "PRIVATE-BUYER-PII"
OFFER_SCOPE = "allegro:api:sale:offers:read"
ORDER_SCOPE = "allegro:api:orders:read"


class Transport:
    def __init__(self):
        self.calls = []

    def __call__(self, url, headers, timeout):
        self.calls.append((url, headers["Authorization"]))
        if "/order/checkout-forms" in url:
            payload = {"checkoutForms": [{
                "id": OID, "status": "READY_FOR_PROCESSING",
                "buyer": {"email": PII, "phoneNumber": PII, "firstName": PII},
                "delivery": {"address": {"street": PII},
                             "cost": {"amount": "5.00", "currency": "PLN"}},
                "summary": {"totalToPay": {"amount": "45.00", "currency": "PLN"}},
                "lineItems": [{"id": LID, "quantity": 1, "offer": {"id": "555"},
                               "price": {"amount": "40.00", "currency": "PLN"}}],
            }]}
            if not url.endswith("limit=20&offset=0"):
                payload = payload["checkoutForms"][0]
        else:
            payload = {"offers": [{
                "id": "555", "buyer": {"email": PII}, "stock": {"available": 5},
                "sellingMode": {"price": {"amount": "40.00", "currency": "PLN"}},
            }]}
            if "/product-offers/" in url:
                payload = payload["offers"][0]
        return Response(200, {}, json.dumps(payload).encode())


class ServiceTests(unittest.TestCase):
    def setUp(self):
        self.reg = ConnectionRegistry([
            Connection("account_a", "seller-111", "production",
                       frozenset({"owner"}), frozenset({OFFER_SCOPE, ORDER_SCOPE})),
            Connection("account_b", "seller-222", "production",
                       frozenset({"other"}), frozenset({OFFER_SCOPE})),
        ])
        self.token_reads = []
        self.transport = Transport()
        def token(c):
            self.token_reads.append(c)
            return "FAKE_SECRET"
        self.client = AllegroReadClient(self.reg, token, self.transport)

    def service(self, sellers=None, actor="owner"):
        return SafeAllegroReadService(
            self.client, self.reg,
            authenticated_actor=actor,
            verified_sellers=sellers,
        )

    def test_no_verified_binding_denies_before_token_access(self):
        with self.assertRaises(SellerIdentityNotVerified):
            self.service().offers("account_a")
        self.assertEqual(self.token_reads, [])
        self.assertEqual(self.transport.calls, [])

    def test_mismatched_seller_binding_denies_before_token(self):
        with self.assertRaises(SellerIdentityNotVerified):
            self.service({"account_a": "seller-222"}).orders("account_a")
        self.assertEqual(self.token_reads, [])

    def test_denied_cross_account_is_not_disclosed(self):
        with self.assertRaises(ConnectionAccessDenied):
            self.service({"account_b": "seller-222"}).offers("account_b")
        self.assertEqual(self.token_reads, [])

    def test_allowed_orders_strip_buyer_data(self):
        data = self.service({"account_a": "seller-111"}).orders("account_a")
        self.assertEqual(data["count"], 1)
        self.assertNotIn(PII, json.dumps(data))
        self.assertEqual(data["orders"][0]["order_id"], OID)
        self.assertEqual(self.token_reads, ["account_a"])
        self.assertEqual(len(self.transport.calls), 1)

    def test_allowed_offers_return_only_whitelisted_fields(self):
        data = self.service({"account_a": "seller-111"}).offers("account_a")
        self.assertEqual(data["offers"][0]["offer_id"], "555")
        self.assertNotIn(PII, json.dumps(data))

    def test_allowed_single_order(self):
        data = self.service({"account_a": "seller-111"}).order("account_a", OID)
        self.assertEqual(data["order_id"], OID)
        self.assertNotIn(PII, json.dumps(data))

    def test_allowed_single_offer(self):
        data = self.service({"account_a": "seller-111"}).offer("account_a", "555")
        self.assertEqual(data["offer_id"], "555")
        self.assertNotIn(PII, json.dumps(data))

    def test_registry_scope_blocks_before_token(self):
        with self.assertRaises(MissingScope):
            self.service({"account_b": "seller-222"}, actor="other").orders("account_b")
        self.assertEqual(self.token_reads, [])

    def test_mismatched_registry_rejected_at_constructor(self):
        another = ConnectionRegistry([
            Connection("account_a", "seller-111", "production",
                       frozenset({"owner"}), frozenset({OFFER_SCOPE, ORDER_SCOPE})),
        ])
        with self.assertRaises(ValueError):
            SafeAllegroReadService(self.client, another, authenticated_actor="owner",
                                   verified_sellers={"account_a": "seller-111"})
        self.assertEqual(self.token_reads, [])

    def test_no_direct_write_or_raw_transport_tools(self):
        service = self.service({"account_a": "seller-111"})
        for method in ("post", "put", "patch", "delete", "raw_order", "execute"):
            self.assertFalse(hasattr(service, method))


if __name__ == "__main__":
    unittest.main()

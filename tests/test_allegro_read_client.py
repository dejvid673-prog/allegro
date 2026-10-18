"""No-network contract tests for a strictly read-only Allegro API client.

These tests must fail before the client exists; no credentials are used.
"""
import json
import unittest

from allegro_api.read_client import (
    AllegroReadClient, Connection, ConnectionRegistry, ConnectionAccessDenied,
    MissingScope, ReadApiError, RateLimited, Response, UrllibGetTransport,
)

OFFERS_SCOPE = "allegro:api:sale:offers:read"
ORDERS_SCOPE = "allegro:api:orders:read"
SHIPMENTS_SCOPE = "allegro:api:shipments:read"


class FakeTransport:
    def __init__(self, status=200, data=None, headers=None):
        self.calls = []
        self.status = status
        self.data = {} if data is None else data
        self.headers = {} if headers is None else headers

    def __call__(self, url, headers, timeout):
        self.calls.append((url, dict(headers), timeout))
        return Response(self.status, self.headers, json.dumps(self.data).encode("utf-8"))


def account(connection_id="main", seller_id="12345", actors=("operator",), scopes=None,
            environment="production"):
    return Connection(
        connection_id=connection_id, seller_id=seller_id, environment=environment,
        allowed_actors=frozenset(actors),
        scopes=frozenset([OFFERS_SCOPE, ORDERS_SCOPE, SHIPMENTS_SCOPE]
                         if scopes is None else scopes),
    )


class ReadClientTests(unittest.TestCase):
    def setUp(self):
        self.transport = FakeTransport(data={"offers": [{"id": "123"}]})
        self.tokens = []
        self.registry = ConnectionRegistry([account()])
        def get_token(connection_id):
            self.tokens.append(connection_id)
            return "TEST_SECRET_TOKEN_NEVER_LOG"
        self.client = AllegroReadClient(self.registry, get_token, self.transport)

    def test_offers_requests_only_fixed_get_endpoint_and_correct_headers(self):
        result = self.client.offers("main", "operator", limit=20, offset=0)
        self.assertEqual(result["offers"][0]["id"], "123")
        self.assertEqual(len(self.transport.calls), 1)
        url, headers, timeout = self.transport.calls[0]
        self.assertEqual(url, "https://api.allegro.pl/sale/offers?limit=20&offset=0")
        self.assertEqual(headers["Authorization"], "Bearer TEST_SECRET_TOKEN_NEVER_LOG")
        self.assertEqual(headers["Accept"], "application/vnd.allegro.public.v1+json")
        self.assertIn("7DEJV", headers["User-Agent"])
        self.assertTrue(0 < timeout <= 15)
        self.assertEqual(self.tokens, ["main"])

    def test_sandbox_uses_only_pinned_sandbox_host(self):
        reg = ConnectionRegistry([account(environment="sandbox")])
        cli = AllegroReadClient(reg, lambda x: "secret", self.transport)
        cli.offers("main", "operator", limit=1, offset=4)
        self.assertEqual(self.transport.calls[0][0],
                         "https://api.allegro.pl.allegrosandbox.pl/sale/offers?limit=1&offset=4")

    def test_orders_list_exact_path_and_query(self):
        self.client.orders("main", "operator", limit=10, offset=5)
        self.assertEqual(self.transport.calls[-1][0],
                         "https://api.allegro.pl/order/checkout-forms?limit=10&offset=5")

    def test_offer_detail_uses_validated_id(self):
        self.client.offer("main", "operator", offer_id="203040506")
        self.assertEqual(self.transport.calls[-1][0],
                         "https://api.allegro.pl/sale/product-offers/203040506")

    def test_order_detail_requires_uuid(self):
        oid = "29738e61-7f6a-11e8-ac45-09db60ede9d6"
        self.client.order("main", "operator", order_id=oid)
        self.assertEqual(self.transport.calls[-1][0],
                         "https://api.allegro.pl/order/checkout-forms/" + oid)

    def test_order_events_fixed_get(self):
        self.client.order_events("main", "operator", limit=20)
        self.assertEqual(self.transport.calls[-1][0],
                         "https://api.allegro.pl/order/events?limit=20")

    def test_delivery_proposals_fixed_get(self):
        oid = "29738e61-7f6a-11e8-ac45-09db60ede9d6"
        self.client.delivery_proposals("main", "operator", order_id=oid)
        self.assertEqual(self.transport.calls[-1][0],
                         "https://api.allegro.pl/shipment-management/delivery-proposals/" + oid)

    def test_cross_account_actor_is_blocked_before_secrets_read(self):
        with self.assertRaises(ConnectionAccessDenied):
            self.client.offers("main", "other-user")
        self.assertEqual(self.tokens, [])
        self.assertEqual(self.transport.calls, [])

    def test_unknown_connection_is_blocked_before_secrets_read(self):
        with self.assertRaises(ConnectionAccessDenied):
            self.client.offers("not-linked", "operator")
        self.assertFalse(self.tokens)

    def test_no_confusing_same_alias_between_accounts(self):
        with self.assertRaises(ValueError):
            ConnectionRegistry([account(), account(seller_id="56789")])

    def test_scope_must_be_explicit_and_no_token_requested_when_missing(self):
        reg = ConnectionRegistry([account(scopes={ORDERS_SCOPE})])
        cli = AllegroReadClient(reg, lambda connection: self.tokens.append(connection), self.transport)
        with self.assertRaises(MissingScope):
            cli.offers("main", "operator")
        self.assertFalse(self.tokens)

    def test_offers_only_scope_does_not_allow_order_data(self):
        reg = ConnectionRegistry([account(scopes={OFFERS_SCOPE})])
        cli = AllegroReadClient(reg, lambda connection: "secret", self.transport)
        with self.assertRaises(MissingScope):
            cli.orders("main", "operator")

    def test_wrong_scope_for_proposal_is_rejected(self):
        reg = ConnectionRegistry([account(scopes={ORDERS_SCOPE})])
        cli = AllegroReadClient(reg, lambda connection: "secret", self.transport)
        with self.assertRaises(MissingScope):
            cli.delivery_proposals("main", "operator",
                                   "29738e61-7f6a-11e8-ac45-09db60ede9d6")

    def test_explicit_input_validation_before_network(self):
        invalid = [0, -1, 101, True, "20", 1.2]
        for n in invalid:
            with self.subTest(limit=n), self.assertRaises(ValueError):
                self.client.offers("main", "operator", limit=n)
        for n in (-1, True, "0", 1.2):
            with self.subTest(offset=n), self.assertRaises(ValueError):
                self.client.orders("main", "operator", offset=n)
        self.assertFalse(self.transport.calls)
        self.assertFalse(self.tokens)

    def test_malicious_path_segments_cannot_escape_allowed_paths(self):
        for bad in ("abc/../../me", "1?foo=bar", "../200", "", "https://evil.example", 123):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                self.client.offer("main", "operator", offer_id=bad)
        for bad in ("../me", "deadbeef", "https://evil.example", "", 123):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                self.client.order("main", "operator", order_id=bad)
        self.assertFalse(self.transport.calls)

    def test_environment_is_allowlisted(self):
        with self.assertRaises(ValueError):
            ConnectionRegistry([account(environment="https://evil.example")])

    def test_no_full_error_body_and_no_secret_in_error_on_401(self):
        self.transport.status = 401
        self.transport.data = {"error": "TOKEN=TEST_SECRET_TOKEN_NEVER_LOG"}
        with self.assertRaises(ReadApiError) as ctx:
            self.client.offers("main", "operator")
        self.assertEqual(ctx.exception.status, 401)
        self.assertNotIn("TEST_SECRET", repr(ctx.exception))
        self.assertEqual(len(self.transport.calls), 1)

    def test_429_exposes_retry_after_without_automatic_retry(self):
        self.transport.status = 429
        self.transport.headers = {"Retry-After": "30"}
        with self.assertRaises(RateLimited) as ctx:
            self.client.offers("main", "operator")
        self.assertEqual(ctx.exception.retry_after_seconds, 30)
        self.assertEqual(len(self.transport.calls), 1)

    def test_429_does_not_trust_large_retry_after(self):
        self.transport.status = 429
        self.transport.headers = {"Retry-After": "999999999"}
        with self.assertRaises(RateLimited) as ctx:
            self.client.offers("main", "operator")
        self.assertIsNone(ctx.exception.retry_after_seconds)

    def test_5xx_not_automatically_retried(self):
        self.transport.status = 503
        with self.assertRaises(ReadApiError) as ctx:
            self.client.orders("main", "operator")
        self.assertEqual(ctx.exception.status, 503)
        self.assertEqual(len(self.transport.calls), 1)

    def test_invalid_json_is_clean_error(self):
        class Broken:
            def __call__(self, url, headers, timeout):
                return Response(200, {}, b"<html>api error</html>")
        cli = AllegroReadClient(self.registry, lambda c: "secret", Broken())
        with self.assertRaises(ReadApiError):
            cli.offers("main", "operator")

    def test_excessive_response_body_is_rejected(self):
        class Oversized:
            def __call__(self, url, headers, timeout):
                return Response(200, {}, b"x" * (1024 * 1024 + 1))
        cli = AllegroReadClient(self.registry, lambda c: "secret", Oversized())
        with self.assertRaises(ReadApiError):
            cli.orders("main", "operator")

    def test_transport_error_never_includes_token(self):
        class Leaky:
            def __call__(self, url, headers, timeout):
                raise RuntimeError(headers["Authorization"] + " was rejected")
        cli = AllegroReadClient(self.registry, lambda c: "TOP_SECRET", Leaky())
        with self.assertRaises(ReadApiError) as ctx:
            cli.offers("main", "operator")
        self.assertNotIn("TOP_SECRET", str(ctx.exception))

    def test_no_non_get_interface_exposed(self):
        for attribute in ("post", "patch", "put", "delete", "request", "raw_get", "execute"):
            self.assertFalse(hasattr(self.client, attribute))

    def test_different_connections_use_own_tokens_and_hosts(self):
        reg = ConnectionRegistry([
            account("production_1", "111", ("one",)),
            account("sandbox_2", "222", ("two",), environment="sandbox"),
        ])
        seen = []
        def token(cid):
            seen.append(cid)
            return cid + "_TOKEN"
        cli = AllegroReadClient(reg, token, self.transport)
        cli.offers("production_1", "one")
        cli.offers("sandbox_2", "two")
        self.assertEqual(seen, ["production_1", "sandbox_2"])
        self.assertNotEqual(self.transport.calls[0][0].split("/sale")[0],
                            self.transport.calls[1][0].split("/sale")[0])
        with self.assertRaises(ConnectionAccessDenied):
            cli.offers("production_1", "two")


if __name__ == "__main__":
    unittest.main()

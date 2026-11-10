"""Synthetic GET /me seller-ID verification. No credentials or real requests."""
import json
import unittest

from allegro_api.read_client import (
    AllegroReadClient, Connection, ConnectionRegistry,
    ConnectionAccessDenied, MissingScope, Response, SCOPE_OFFERS, SCOPE_PROFILE,
)
from allegro_api.safe_read_service import SafeAllegroReadService
from allegro_api.seller_identity import (
    SellerVerificationFailed, verify_connection_seller,
)

SENSITIVE = "DO_NOT_EXPOSE_ACCOUNT_EMAIL_OR_NIP"


class FakeGet:
    def __init__(self, identity="12345678", status=200):
        self.identity = identity
        self.status = status
        self.calls = []

    def __call__(self, url, headers, timeout):
        self.calls.append((url, headers["Authorization"]))
        if url.endswith("/me"):
            body = {
                "id": self.identity, "email": SENSITIVE, "firstName": SENSITIVE,
                "lastName": SENSITIVE, "company": {"taxId": SENSITIVE},
            }
        else:
            body = {
                "offers": [{
                    "id": "777", "stock": {"available": 1}, "buyer": {"email": SENSITIVE},
                    "sellingMode": {"price": {"amount": "25.00", "currency": "PLN"}},
                }]
            }
        return Response(self.status, {}, json.dumps(body).encode())


def registry_with(scopes=None, actors=None, environment="production", seller_id="12345678"):
    return ConnectionRegistry([Connection(
        "account-one", seller_id, environment,
        frozenset({"trusted-owner"} if actors is None else actors),
        frozenset({SCOPE_PROFILE, SCOPE_OFFERS} if scopes is None else scopes),
    )])


class IdentityTests(unittest.TestCase):
    def setUp(self):
        self.registry = registry_with()
        self.transport = FakeGet()
        self.secrets_read = []

        def token_provider(cid):
            self.secrets_read.append(cid)
            return "FAKE_TOKEN_SECRET"

        self.client = AllegroReadClient(self.registry, token_provider, self.transport)

    def test_verified_token_owner_returns_only_public_account_id(self):
        verified = verify_connection_seller(
            self.client, self.registry, "account-one", "trusted-owner"
        )
        self.assertEqual(verified.seller_id, "12345678")
        self.assertEqual(verified.connection_id, "account-one")
        self.assertNotIn(SENSITIVE, repr(verified))
        self.assertEqual(self.transport.calls[0][0], "https://api.allegro.pl/me")
        self.assertEqual(len(self.transport.calls), 1)

    def test_mismatched_account_fails_without_leaking_identity(self):
        self.transport.identity = "87654321"
        with self.assertRaises(SellerVerificationFailed) as caught:
            verify_connection_seller(self.client, self.registry, "account-one", "trusted-owner")
        self.assertNotIn("87654321", str(caught.exception))
        self.assertNotIn(SENSITIVE, str(caught.exception))

    def test_malformed_account_identity_fails_closed(self):
        for identity in (None, "", "../me", 12345678, SENSITIVE):
            self.transport.identity = identity
            with self.subTest(identity=identity), self.assertRaises(SellerVerificationFailed):
                verify_connection_seller(self.client, self.registry, "account-one", "trusted-owner")

    def test_wrong_actor_denied_before_token(self):
        with self.assertRaises(ConnectionAccessDenied):
            verify_connection_seller(self.client, self.registry, "account-one", "outsider")
        self.assertEqual(self.secrets_read, [])
        self.assertEqual(self.transport.calls, [])

    def test_missing_profile_scope_denied_before_token(self):
        r = registry_with(scopes={SCOPE_OFFERS})
        c = AllegroReadClient(r, self.client._get_token, self.transport)
        with self.assertRaises(MissingScope):
            verify_connection_seller(c, r, "account-one", "trusted-owner")
        self.assertEqual(self.secrets_read, [])
        self.assertEqual(self.transport.calls, [])

    def test_mismatched_client_registry_blocked_before_token(self):
        r = registry_with()
        with self.assertRaises(ValueError):
            verify_connection_seller(self.client, r, "account-one", "trusted-owner")
        self.assertEqual(self.secrets_read, [])
        self.assertEqual(self.transport.calls, [])

    def test_sandbox_uses_only_pinned_host(self):
        r = registry_with(environment="sandbox")
        c = AllegroReadClient(r, self.client._get_token, self.transport)
        identity = verify_connection_seller(c, r, "account-one", "trusted-owner")
        self.assertEqual(identity.environment, "sandbox")
        self.assertEqual(
            self.transport.calls[0][0],
            "https://api.allegro.pl.allegrosandbox.pl/me",
        )

    def test_verified_account_can_be_passed_to_safe_projection_service(self):
        identity = verify_connection_seller(
            self.client, self.registry, "account-one", "trusted-owner"
        )
        service = SafeAllegroReadService(
            self.client, self.registry, authenticated_actor="trusted-owner",
            verified_sellers={identity.connection_id: identity.seller_id},
        )
        offers = service.offers("account-one")
        self.assertEqual(offers["offers"][0]["offer_id"], "777")
        self.assertNotIn(SENSITIVE, json.dumps(offers))
        self.assertEqual(len(self.transport.calls), 2)

    def test_no_write_verbs_in_identity_client(self):
        self.assertFalse(hasattr(self.client, "post"))
        self.assertFalse(hasattr(self.client, "patch"))
        self.assertFalse(hasattr(self.client, "delete"))


if __name__ == "__main__":
    unittest.main()

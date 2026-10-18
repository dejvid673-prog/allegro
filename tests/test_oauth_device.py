"""Offline contract checks for Allegro OAuth Device Flow; no real credentials."""
import base64
import json
import unittest
from urllib.parse import parse_qs

from allegro_api.device_oauth import (
    DeviceOAuthClient, OAuthFlowError, TokenPair, DeviceChallenge, PollOutcome
)
from allegro_api.read_client import Response

OFFER_SCOPE = "allegro:api:sale:offers:read"
ORDER_SCOPE = "allegro:api:orders:read"


class FakePoster:
    def __init__(self, status=200, payload=None):
        self.status = status
        self.payload = payload if payload is not None else {
            "device_code": "SENSITIVE_DEVICE_CODE", "user_code": "ABC XYZ",
            "interval": 5, "expires_in": 3600,
            "verification_uri": "https://allegro.pl/skojarz-aplikacje",
            "verification_uri_complete": "https://allegro.pl/skojarz-aplikacje?code=ABCXYZ",
        }
        self.calls = []

    def __call__(self, url, headers, body, timeout):
        self.calls.append((url, dict(headers), body, timeout))
        return Response(self.status, {}, json.dumps(self.payload).encode())


class DeviceOAuthTests(unittest.TestCase):
    def setUp(self):
        self.poster = FakePoster()
        self.client = DeviceOAuthClient(
            environment="production", client_id="TEST_APP_PUBLIC_ID",
            client_secret="SECRET_CLIENT_NEVER_LOG", post=self.poster,
            scopes=(OFFER_SCOPE, ORDER_SCOPE),
        )

    def test_start_uses_post_basic_and_only_read_scopes(self):
        challenge = self.client.begin()
        self.assertIsInstance(challenge, DeviceChallenge)
        self.assertEqual(challenge.user_code, "ABC XYZ")
        self.assertNotIn("SENSITIVE_DEVICE_CODE", repr(challenge))
        url, headers, body, timeout = self.poster.calls[0]
        self.assertEqual(url, "https://allegro.pl/auth/oauth/device?client_id=TEST_APP_PUBLIC_ID")
        self.assertEqual(headers["Content-Type"], "application/x-www-form-urlencoded")
        basic = headers["Authorization"].removeprefix("Basic ")
        self.assertEqual(base64.b64decode(basic).decode(), "TEST_APP_PUBLIC_ID:SECRET_CLIENT_NEVER_LOG")
        parsed = parse_qs(body.decode())
        self.assertEqual(parsed["scope"], [OFFER_SCOPE + " " + ORDER_SCOPE])
        self.assertEqual(parsed["client_id"], ["TEST_APP_PUBLIC_ID"])
        self.assertTrue(0 < timeout <= 15)

    def test_sandbox_oauth_host_cannot_be_overridden(self):
        client = DeviceOAuthClient("sandbox", "APPID", "SHHH", self.poster, (OFFER_SCOPE,))
        self.poster.payload["verification_uri"] = "https://allegro.pl.allegrosandbox.pl/skojarz-aplikacje"
        self.poster.payload["verification_uri_complete"] = "https://allegro.pl.allegrosandbox.pl/skojarz-aplikacje?code=x"
        client.begin()
        self.assertEqual(self.poster.calls[-1][0],
                         "https://allegro.pl.allegrosandbox.pl/auth/oauth/device?client_id=APPID")

    def test_disallow_unrecognized_or_write_scopes_before_network(self):
        for scopes in ((), ("allegro:api:orders:write",), (OFFER_SCOPE, "arbitrary")):
            with self.subTest(scopes=scopes), self.assertRaises(ValueError):
                DeviceOAuthClient("production", "A", "B", self.poster, scopes)
        self.assertFalse(self.poster.calls)

    def test_invalid_environment_or_credentials_do_not_make_request(self):
        for env, cid, secret in (
            ("https://evil.example", "A", "B"),
            ("production", "", "B"),
            ("production", "A", ""),
            ("production", "A\r\nInjected", "B"),
        ):
            with self.subTest(env=env, cid=cid), self.assertRaises(ValueError):
                DeviceOAuthClient(env, cid, secret, self.poster, (OFFER_SCOPE,))
        self.assertFalse(self.poster.calls)

    def test_reject_untrusted_verification_link(self):
        self.poster.payload["verification_uri_complete"] = "https://evil.example/token?code=x"
        with self.assertRaises(OAuthFlowError):
            self.client.begin()

    def test_poll_pending_is_not_a_token_and_reports_interval(self):
        self.poster.status = 400
        self.poster.payload = {"error": "authorization_pending"}
        result = self.client.poll_once("SENSITIVE_DEVICE_CODE", interval_seconds=5)
        self.assertEqual(result.state, "PENDING")
        self.assertIsNone(result.tokens)
        self.assertEqual(result.retry_after_seconds, 5)
        url, headers, body, timeout = self.poster.calls[-1]
        self.assertEqual(url, "https://allegro.pl/auth/oauth/token")
        self.assertEqual(parse_qs(body.decode())["grant_type"],
                         ["urn:ietf:params:oauth:grant-type:device_code"])
        self.assertEqual(parse_qs(body.decode())["device_code"], ["SENSITIVE_DEVICE_CODE"])
        self.assertNotIn("SENSITIVE_DEVICE_CODE", url)

    def test_poll_slow_down_increases_interval_without_busy_loop(self):
        self.poster.status = 400
        self.poster.payload = {"error": "slow_down"}
        result = self.client.poll_once("SENSITIVE_DEVICE_CODE", interval_seconds=5)
        self.assertEqual(result.state, "SLOW_DOWN")
        self.assertGreaterEqual(result.retry_after_seconds, 10)
        self.assertEqual(len(self.poster.calls), 1)

    def test_poll_access_denied_is_terminal_and_sanitized(self):
        self.poster.status = 400
        self.poster.payload = {"error": "access_denied", "error_description": "SECRET_CLIENT_NEVER_LOG"}
        with self.assertRaises(OAuthFlowError) as c:
            self.client.poll_once("SENSITIVE_DEVICE_CODE", interval_seconds=5)
        self.assertEqual(c.exception.reason, "ACCESS_DENIED")
        self.assertNotIn("SECRET_CLIENT_NEVER_LOG", str(c.exception))

    def test_poll_invalid_device_code_is_terminal(self):
        self.poster.status = 400
        self.poster.payload = {"error": "Invalid device code"}
        with self.assertRaises(OAuthFlowError) as c:
            self.client.poll_once("SENSITIVE_DEVICE_CODE", interval_seconds=5)
        self.assertEqual(c.exception.reason, "DEVICE_INVALID")

    def test_poll_authorized_returns_opaque_token_pair(self):
        self.poster.payload = {
            "access_token": "ACCESS_SECRET", "refresh_token": "REFRESH_SECRET",
            "token_type": "bearer", "expires_in": 43199,
            "scope": OFFER_SCOPE + " " + ORDER_SCOPE,
        }
        result = self.client.poll_once("SENSITIVE_DEVICE_CODE", interval_seconds=5)
        self.assertEqual(result.state, "AUTHORIZED")
        self.assertIsInstance(result.tokens, TokenPair)
        self.assertEqual(result.tokens.access_token, "ACCESS_SECRET")
        self.assertNotIn("ACCESS_SECRET", repr(result))
        self.assertNotIn("REFRESH_SECRET", repr(result))

    def test_refresh_only_post_body_no_secret_in_url(self):
        self.poster.payload = {
            "access_token": "ACCESS_ROTATED", "refresh_token": "REFRESH_ROTATED",
            "token_type": "bearer", "expires_in": 43199, "scope": OFFER_SCOPE,
        }
        result = self.client.refresh("CURRENT_REFRESH_SECRET")
        self.assertEqual(result.refresh_token, "REFRESH_ROTATED")
        url, headers, body, _ = self.poster.calls[-1]
        self.assertEqual(url, "https://allegro.pl/auth/oauth/token")
        self.assertEqual(parse_qs(body.decode())["grant_type"], ["refresh_token"])
        self.assertEqual(parse_qs(body.decode())["refresh_token"], ["CURRENT_REFRESH_SECRET"])
        self.assertNotIn("CURRENT_REFRESH_SECRET", url)

    def test_token_errors_are_never_exposed_to_logs(self):
        self.poster.status = 401
        self.poster.payload = {"error": "SECRET_CLIENT_NEVER_LOG"}
        with self.assertRaises(OAuthFlowError) as c:
            self.client.refresh("CURRENT_REFRESH_SECRET")
        self.assertNotIn("SECRET_CLIENT_NEVER_LOG", str(c.exception))
        self.assertNotIn("CURRENT_REFRESH_SECRET", str(c.exception))

    def test_reject_invalid_expiry_and_malformed_token_response(self):
        self.poster.payload = {
            "access_token": "X", "refresh_token": "Y", "token_type": "bearer", "expires_in": 0,
        }
        with self.assertRaises(OAuthFlowError):
            self.client.refresh("refresh")
        self.poster.payload = {
            "access_token": "X", "refresh_token": "Y", "token_type": "not-bearer", "expires_in": 10,
        }
        with self.assertRaises(OAuthFlowError):
            self.client.refresh("refresh")

    def test_bad_poll_code_and_interval_rejected_before_network(self):
        for code, interval in (("", 5), ("TOKEN", 0), ("TOKEN", True),
                               ("TOKEN", -1), ("TOKEN", 999999)):
            with self.subTest(code=code, interval=interval), self.assertRaises(ValueError):
                self.client.poll_once(code, interval_seconds=interval)
        self.assertFalse(self.poster.calls)

    def test_network_exception_redacted(self):
        class Leaky:
            def __call__(self, url, headers, body, timeout):
                raise RuntimeError("SECRET_CLIENT_NEVER_LOG " + body.decode())
        client = DeviceOAuthClient("production", "id", "SECRET_CLIENT_NEVER_LOG", Leaky(), (OFFER_SCOPE,))
        with self.assertRaises(OAuthFlowError) as c:
            client.begin()
        self.assertNotIn("SECRET_CLIENT_NEVER_LOG", str(c.exception))

    def test_post_429_returns_bounded_retry_hint(self):
        self.poster.status = 429
        self.poster.payload = {"error": "too_many_requests"}
        with self.assertRaises(OAuthFlowError) as c:
            self.client.begin()
        self.assertEqual(c.exception.reason, "RATE_LIMITED")
        self.assertEqual(len(self.poster.calls), 1)


if __name__ == "__main__":
    unittest.main()

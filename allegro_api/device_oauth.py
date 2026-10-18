"""Confidential-client Device OAuth adapter for Allegro, without token storage.

The module is NOT exported via MCP. Never pass client credentials, refresh
tokens, device codes or token pairs as tool arguments or log values. The caller
owns user consent, poll timing, identity verification and atomic secure storage.
"""
from __future__ import annotations

import base64
from dataclasses import dataclass, field
import json
import re
from typing import Callable, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

from allegro_api.read_client import Response

AUTH_ROOTS = {
    "production": "https://allegro.pl/auth/oauth",
    "sandbox": "https://allegro.pl.allegrosandbox.pl/auth/oauth",
}
READ_SCOPES = frozenset((
    "allegro:api:sale:offers:read",
    "allegro:api:orders:read",
    "allegro:api:shipments:read",
))
MAX_OAUTH_REPLY = 64 * 1024
MAX_INTERVAL = 300
DEFAULT_TIMEOUT = 10.0


class OAuthFlowError(Exception):
    """Sanitized OAuth failure without raw response, tokens or credentials."""

    def __init__(self, reason: str):
        self.reason = reason
        super().__init__("Allegro OAuth: " + reason)


@dataclass(frozen=True)
class DeviceChallenge:
    device_code: str = field(repr=False)
    user_code: str
    verification_uri: str
    verification_uri_complete: str
    expires_in: int
    interval: int


@dataclass(frozen=True)
class TokenPair:
    access_token: str = field(repr=False)
    refresh_token: str = field(repr=False)
    token_type: str
    expires_in: int
    scope: str


@dataclass(frozen=True)
class PollOutcome:
    state: str
    retry_after_seconds: int | None
    tokens: TokenPair | None = field(repr=False, default=None)


class _StopRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, file_pointer, code, message, headers, url):
        return None


class UrllibPostTransport:
    """HTTPS POST form transport, TLS verification on and redirects disabled."""

    def __init__(self):
        self._opener = build_opener(_StopRedirect())

    def __call__(self, url: str, headers: Mapping[str, str],
                 body: bytes, timeout: float) -> Response:
        request = Request(url, data=body, headers=dict(headers), method="POST")
        try:
            with self._opener.open(request, timeout=timeout) as result:
                return Response(result.status, dict(result.headers.items()),
                                result.read(MAX_OAUTH_REPLY + 1))
        except HTTPError as exc:
            return Response(int(exc.code), dict(exc.headers.items()) if exc.headers else {},
                            exc.read(MAX_OAUTH_REPLY + 1))
        except (URLError, OSError, TimeoutError):
            raise OAuthFlowError("TRANSPORT_ERROR") from None


def _positive_int(value: object, min_value: int, max_value: int) -> int:
    if type(value) is int:
        number = value
    elif isinstance(value, str) and re.fullmatch(r"[0-9]{1,8}", value):
        number = int(value)
    else:
        raise OAuthFlowError("INVALID_RESPONSE")
    if not min_value <= number <= max_value:
        raise OAuthFlowError("INVALID_RESPONSE")
    return number


def _official_user_link(environment: str, url: object) -> str:
    if not isinstance(url, str):
        raise OAuthFlowError("INVALID_VERIFICATION_URI")
    try:
        parsed = urlsplit(url)
        allowed_host = urlsplit(AUTH_ROOTS[environment]).hostname
        valid = (parsed.scheme == "https" and parsed.hostname == allowed_host
                 and parsed.port is None and not parsed.username
                 and not parsed.password and parsed.path == "/skojarz-aplikacje")
    except ValueError:
        raise OAuthFlowError("INVALID_VERIFICATION_URI") from None
    if not valid:
        raise OAuthFlowError("INVALID_VERIFICATION_URI")
    return url


def _parse_json(response: Response) -> dict:
    if not isinstance(response, Response) or type(response.status) is not int:
        raise OAuthFlowError("INVALID_RESPONSE")
    if not isinstance(response.body, bytes) or len(response.body) > MAX_OAUTH_REPLY:
        raise OAuthFlowError("INVALID_RESPONSE")
    try:
        parsed = json.loads(response.body)
    except (UnicodeDecodeError, ValueError):
        raise OAuthFlowError("INVALID_RESPONSE") from None
    if not isinstance(parsed, dict):
        raise OAuthFlowError("INVALID_RESPONSE")
    return parsed


def _token_pair(parsed: dict) -> TokenPair:
    token = parsed.get("access_token")
    refresh = parsed.get("refresh_token")
    token_type = parsed.get("token_type")
    if (not isinstance(token, str) or not token.strip() or
            not isinstance(refresh, str) or not refresh.strip() or
            not isinstance(token_type, str) or token_type.casefold() != "bearer"):
        raise OAuthFlowError("INVALID_TOKEN_RESPONSE")
    expires = _positive_int(parsed.get("expires_in"), 1, 2_000_000)
    scope = parsed.get("scope", "")
    if not isinstance(scope, str):
        raise OAuthFlowError("INVALID_TOKEN_RESPONSE")
    return TokenPair(token, refresh, "bearer", expires, scope)


def _clean_client_credential(text: object) -> bool:
    return (isinstance(text, str) and 1 <= len(text) <= 256 and
            all("!" <= char <= "~" for char in text) and
            not any(char in text for char in "\r\n"))


class DeviceOAuthClient:
    """Single-request OAuth operations. No automatic polling or persistence."""

    def __init__(
        self, environment: str, client_id: str, client_secret: str,
        post: Callable[[str, Mapping[str, str], bytes, float], Response] | None = None,
        scopes: tuple[str, ...] = tuple(sorted(READ_SCOPES)),
        timeout: float = DEFAULT_TIMEOUT,
    ):
        if environment not in AUTH_ROOTS:
            raise ValueError("unsupported OAuth environment")
        if (not _clean_client_credential(client_id)
                or not _clean_client_credential(client_secret)
                or ":" in client_id):
            raise ValueError("invalid server-side client credentials")
        if (not isinstance(scopes, tuple) or not scopes
                or len(scopes) != len(set(scopes))
                or not all(isinstance(s, str) and s in READ_SCOPES for s in scopes)):
            raise ValueError("only explicit read scopes are allowed")
        if type(timeout) not in (int, float) or not 0 < timeout <= 15:
            raise ValueError("invalid timeout")
        if post is not None and not callable(post):
            raise ValueError("invalid OAuth transport")
        self._root = AUTH_ROOTS[environment]
        self._environment = environment
        self._client_id = client_id
        self._basic = "Basic " + base64.b64encode(
            (client_id + ":" + client_secret).encode("ascii")
        ).decode("ascii")
        self._scopes = tuple(scopes)
        self._post = post if post is not None else UrllibPostTransport()
        self._timeout = float(timeout)

    def _form_post(self, endpoint: str, body: dict[str, str]) -> Response:
        url = self._root + endpoint
        headers = {
            "Authorization": self._basic,
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "User-Agent": "7DEJV-Allegro-OAuth/0.2",
        }
        try:
            answer = self._post(url, headers, urlencode(body).encode("ascii"), self._timeout)
        except Exception:
            raise OAuthFlowError("TRANSPORT_ERROR") from None
        if not isinstance(answer, Response):
            raise OAuthFlowError("INVALID_RESPONSE")
        return answer

    def begin(self) -> DeviceChallenge:
        # Scope carried as explicit form parameter; must be validated in Sandbox.
        body = {"client_id": self._client_id, "scope": " ".join(self._scopes)}
        url = "/device?" + urlencode({"client_id": self._client_id})
        response = self._form_post(url, body)
        if response.status == 429:
            raise OAuthFlowError("RATE_LIMITED")
        if response.status != 200:
            raise OAuthFlowError("BEGIN_FAILED")
        data = _parse_json(response)
        code = data.get("device_code")
        user_code = data.get("user_code")
        if not isinstance(code, str) or not code or not isinstance(user_code, str) or not user_code:
            raise OAuthFlowError("INVALID_RESPONSE")
        return DeviceChallenge(
            code, user_code,
            _official_user_link(self._environment, data.get("verification_uri")),
            _official_user_link(self._environment, data.get("verification_uri_complete")),
            _positive_int(data.get("expires_in"), 1, 86400),
            _positive_int(data.get("interval"), 1, MAX_INTERVAL),
        )

    def poll_once(self, device_code: str, interval_seconds: int) -> PollOutcome:
        if not isinstance(device_code, str) or not device_code.strip() or len(device_code) > 4096:
            raise ValueError("invalid device code")
        if type(interval_seconds) is not int or not 1 <= interval_seconds <= MAX_INTERVAL:
            raise ValueError("invalid interval")
        response = self._form_post("/token", {
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            "device_code": device_code,
        })
        if response.status == 429:
            return PollOutcome("SLOW_DOWN", min(MAX_INTERVAL, interval_seconds + 5))
        data = _parse_json(response)
        if response.status == 200:
            return PollOutcome("AUTHORIZED", None, _token_pair(data))
        if response.status == 400:
            error = data.get("error")
            if error == "authorization_pending":
                return PollOutcome("PENDING", interval_seconds)
            if error == "slow_down":
                return PollOutcome("SLOW_DOWN", min(MAX_INTERVAL, interval_seconds + 5))
            if error == "access_denied":
                raise OAuthFlowError("ACCESS_DENIED")
            if error == "Invalid device code":
                raise OAuthFlowError("DEVICE_INVALID")
        raise OAuthFlowError("POLL_FAILED")

    def refresh(self, refresh_token: str) -> TokenPair:
        if not isinstance(refresh_token, str) or not refresh_token.strip() or len(refresh_token) > 10000:
            raise ValueError("invalid refresh token")
        response = self._form_post("/token", {
            "grant_type": "refresh_token", "refresh_token": refresh_token,
        })
        if response.status != 200:
            raise OAuthFlowError("REFRESH_FAILED" if response.status != 429 else "RATE_LIMITED")
        return _token_pair(_parse_json(response))

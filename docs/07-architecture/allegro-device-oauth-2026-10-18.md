# Allegro OAuth Device Flow and stateless refresh — 2026-10-18

**Level: IMPLEMENTED + TESTED AGAINST FAKE TRANSPORT. NOT LOGIN TESTED, NOT CONNECTED.**

The module allegro_api/device_oauth.py is a server-side helper, NOT an MCP tool and NOT a ready-to-run login application. It requires a separately registered Allegro OAuth Device application, protected client credentials, an authorized operator's consent and a secure token store before an account can be connected. **No login was attempted and no credentials were placed in GitHub.**

## Official source of truth

- [OAuth device authorization, token renewal, scopes, error codes](https://developer.allegro.pl/tutorials/uwierzytelnianie-i-autoryzacja-zlq9e75GdIR)
- [Sandbox OAuth host and differences](https://developer.allegro.pl/tutorials/informacje-podstawowe-b21569boAI1)
- [2025 change: token endpoint requires POST with form body](https://developer.allegro.pl/news/wprowadzimy-zmiany-w-procesie-autoryzacji-O361yP4ZGhG)

## Implemented API, limited scope

- DeviceOAuthClient.begin(): POST to official /auth/oauth/device endpoint with Basic confidential-client authentication; validates that returned verification URLs belong to the matching Allegro environment. Device code is hidden from representation.
- DeviceOAuthClient.poll_once(device_code, interval_seconds): performs **one** POST to /auth/oauth/token; explicitly distinguishes PENDING, SLOW_DOWN (+5s) and AUTHORIZED, and terminal ACCESS_DENIED/DEVICE_INVALID; no background loops, sleep, or automatic retries.
- DeviceOAuthClient.refresh(refresh_token): POST grant_type=refresh_token with secret in **request body only**, never URL; returns opaque access+refresh TokenPair, both hidden from dataclass repr. No automatic refresh, storage or 401 recovery yet.
- Device scopes allow ONLY offers:read, orders:read and shipments:read. Environments have pinned production and sandbox authorization hosts. The device request includes an explicitly restricted scope form field; **the live Allegro behavior of scope at device authorization must be tested in Sandbox** before relying on it for least privilege.
- UrllibPostTransport: HTTPS, TLS validation default, no redirects, max 64 KiB OAuth response, network timeout bounded and redacted HTTP/transport errors.

## Strict remaining responsibilities

1. A trusted application must provide the client ID and secret; never pass them via ChatGPT, a public endpoint or GitHub issue. This repository does not provide them.
2. A secure per-account token broker must persist rotated refresh/access token pairs atomically (prefer encrypted OS keyring or vault); never put tokens in logs or repo. Different production/sandbox secrets must never be mixed.
3. The orchestrator **must enforce** device poll interval and expiry using a monotonic clock. poll_once does exactly one request and reports the next interval; calling it in a fast loop is NOT compliant.
4. Returned OAuth scopes may differ from requested ones. Do not claim granted least privilege from local settings alone. Verify scopes from trusted token/authoritative API before enabling any action.
5. Identity: associate OAuth token with verified seller account and connectionId. Server actor authentication is separate from seller OAuth. No unverified account may access PII or write.
6. The read-only client is not yet wired to this helper. Joining these requires an approved secure storage/refresh controller and privacy-safe MCP response projections.
7. Device flow is a sensitive process that needs explicit user consent. No automatic device login or remote authorization is enabled.

Tests are in tests/test_oauth_device.py and are invoked by python -m unittest discover -s tests -v. A successful offline test is not proof of a real token or successful API read.

**No Allegro accounts, prices, offers, orders or parcels were changed.**

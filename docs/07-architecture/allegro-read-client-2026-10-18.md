# Allegro typed read-only client — 2026-10-18

**Status: IMPLEMENTED + MOCK TESTS; NOT CONNECTED TO ALLEGRO; OAuth NOT IMPLEMENTED.**

Module: allegro_api/read_client.py. This library is framework-neutral; it is not exported as an MCP tool. It accepts a server-side connection registry, a trusted token provider and an injectable GET transport. Repository contains **no credentials, token file, real seller account or automatic login**.

## Fixed GET operations

| Python method | Actual Allegro REST resource | Required declared scope |
|---|---|---|
| offers | GET /sale/offers | allegro:api:sale:offers:read |
| offer | GET /sale/product-offers/{offerId} | allegro:api:sale:offers:read |
| orders | GET /order/checkout-forms | allegro:api:orders:read |
| order | GET /order/checkout-forms/{id} | allegro:api:orders:read |
| order_events | GET /order/events | allegro:api:orders:read |
| delivery_proposals | GET /shipment-management/delivery-proposals/{orderId} | allegro:api:shipments:read (conservative; sandbox verification required) |

Sources: [OAuth/scopes](https://developer.allegro.pl/tutorials/uwierzytelnianie-i-autoryzacja-zlq9e75GdIR), [Allegro API methods](https://developer.allegro.pl/tutorials/lista-metod-rest-api-allegro-yPyaj0wG3C4), [REST versioning](https://developer.allegro.pl/tutorials/informacje-podstawowe-b21569boAI1), [Official OpenAPI](https://developer.allegro.pl/documentation), [OAuth POST-only change (2025)](https://developer.allegro.pl/news/wprowadzimy-zmiany-w-procesie-autoryzacji-O361yP4ZGhG). Actual scope compatibility must be checked in Sandbox using today's Swagger and consented token. Archived snapshot remains from August.

## Security contract

1. Opaque connectionId maps to one declared seller_id, environment (production/sandbox), allowed actor IDs and READ scopes. Authorize the actor **before** invoking the token provider. The declared seller_id is an unverified local assertion until a real OAuth flow identifies the seller.
2. token_provider is injected by the trusted server, never provided through an MCP tool argument. It is not implemented in this repository. No client ID, client secret, access token or refresh token is saved.
3. Hosts are pinned to https://api.allegro.pl and https://api.allegro.pl.allegrosandbox.pl. No caller-provided URL or arbitrary HTTP method; only named GET resource methods. Numeric offer IDs and canonical UUID order IDs are validated before network.
4. Built-in urllib transport blocks redirects and bounds response to 1 MiB; network timeout <= 15 seconds, no internal retries. Headers include Accept: application/vnd.allegro.public.v1+json. Error class suppresses token, raw response body and transport diagnostics. 429 exposes bounded Retry-After hint but does not automatically retry.
5. The adapter RETURNS raw order dictionaries to trusted in-process code. Raw orders can contain buyer PII. Do **not** expose them to ChatGPT/MCP without a separate redacted, purpose-limited projection. actor_id must come from verified inbound authentication, never from an LLM-supplied string.
6. Absolutely no operations that can create labels, set fulfillment states, alter listings, set prices, publish offers or send buyer messages are available.

## Tests and remaining gates

Test command: python -m unittest discover -s tests -v. CI workflow includes the five previous offline MCP tools. Unit and mocked transport tests do NOT prove a successful real login, account ownership, token refresh, sandbox compatibility or shipping.

Next: build OAuth Device/Authorization Code broker with protected token store; verify seller identity and scopes through approved Sandbox login; test 401/429 and timestamped real GET; add small privacy-safe order/offer projections and authenticated MCP interface; later controlled WzA writing with idempotency and one-operation approval. All business WRITE remains disabled.

Never report CONNECTED/VERIFIED until sandbox account-holder consent and live evidence exist.

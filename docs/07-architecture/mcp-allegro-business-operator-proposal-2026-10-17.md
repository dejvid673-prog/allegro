# Propozycja architektury MCP Allegro Commerce Operator — 2026-10-17

**Status: PROPOSED / NOT APPROVED / NOT IMPLEMENTED.** Ten dokument stanowi kontrakt do przeglądu. Opisuje docelowy system, nie dostarczone narzędzia. Właściciel produktu wskazał siedem funkcji: nadawanie paczek, audyt przesyłek, dodawanie nowych produktów/ofert, kontrola kosztów, kontrola asortymentu, sterowanie cenami, analiza rynku konkurencji.

## 1. Cel / UX

Operator używa ChatGPT/Codex do wydawania **ręcznych** poleceń: „Sprawdź dzisiejsze przesyłki”, „Które zamówienia wymagają drugiej paczki?”, „Pokaż marżę dla kredy 24 i 25 kg”, „Przygotuj 25-kg ofertę jako szkic”, „Zaproponuj zmianę ceny o 2 zł”, „Pokaż zmiany cen konkurentów na podstawie zatwierdzonego źródła”. Wszystkie wyniki operują na nazwanych kontach, wersjach danych i dowodach. AI nie wykonuje dowolnego żądania HTTP ani samodzielnie nie nadaje paczek.

Można uruchamiać moduły także bez LLM: przez CLI/API/worker z identycznymi walidacjami. ChatGPT nie przechowuje stanu zamówień, danych klientów, sekretów ani historii idempotency.

## 2. Architektura logiczna

```text
Human/manual command
       │
       ▼
MCP facade: typed high-level tools (allegro_mcp)
       │ inbound actor / allowed connectionId
       ▼
Application/domain services (framework-neutral)
       ├── order + shipment audit
       ├── deterministic packing plan / policy
       ├── shipment proposal and execution ledger
       ├── sales/cost/margin guard
       ├── assortment/product & stock reconciliation
       ├── offer draft validation + proposal
       ├── price proposal/approval + reconcile
       └── market snapshot comparison
       │
       ├── Typed Allegro REST client ← connection registry ← OAuth/secret broker
       ├── Product & Inventory Master (to be selected)
       ├── carrier adapter when WzA doesn't cover service
       └── approved market datasets + imported expenses/ads
       │
       ▼
Durable state: SQLite prototype / Postgres production
    operation ledger · outbox · audit trail · per-connection checkpoints
```

**Runtime decision deferred:** obecny Python MCP stdio może przyjąć pierwsze czyste funkcje offline. Runtime Node SDK v2 z `mcp` może stanowić późniejszy gateway HTTP, ale **nie** należy od razu mnożyć dwóch niezależnych ścieżek do Allegro. Operacje biznesowe muszą być niezależne od transportu i testowalne bez MCP.

## 3. Kontrakt narzędzi biznesowych — cele, nie zaimplementowane API

| Narzędzie robocze | Tryb | Dane / wynik | Bramka |
|---|---|---|---|
| `allegro_connections_status` | READ | konta: alias, sellerId mask, marketplace, sandbox, scopes (bez tokenów) | authorized actor |
| `allegro_orders_find` | READ/PII | lista zamówień, status, dostawa, termin, tylko niezbędne pola | per-account scope, PII minimization |
| `allegro_order_shipment_audit` | READ | brak skanu, błędny COD, etykieta bez przekazania, wiele paczek, statusy | actual order/events+timestamps |
| `allegro_shipping_preview` | DRAFT | propozycje WzA + packing plan + opłaty + wyjątki | `READY_FOR_PROCESSING`, SKU/weight evidence, carrier limits |
| `allegro_shipping_create_approved` | APPROVE/WRITE | commandId→status→shipmentId, audit ledger | explicit one-off approval, idempotency, service allowlist |
| `allegro_shipping_label_get` | READ/PII | etykieta przez uprawniony magazyn, nie przez nieograniczony LLM | secure document delivery, TTL |
| `allegro_shipments_reconcile` | READ | WzA vs carrier tracking vs order, pierwsze skany/wyjątki | freshness/consistency, no double-shipment |
| `allegro_costs_audit` | READ | koszt zakupu/net, prowizje, Smart, Ads, paczka, marża | sourceRefs and completeness |
| `allegro_price_change_propose` | DRAFT | stara/nowa cena, symulowana marża, wpływ na wiele kont | valid VAT and complete cost-model |
| `allegro_price_change_execute_approved` | APPROVE/WRITE | weryfikacja `expectedPrice`, minimalna operacja PATCH, readback | person+connection+offer+amount scoped approval |
| `allegro_assortment_audit` | READ | SKU/EAN, nieaktywne oferty, brak stocku, niezgodności, duplikaty | ownership mapping, catalog snapshot |
| `allegro_product_draft` | DRAFT | neutralny `OfferTemplate`, poprawki wymagane | category parameters, GPSR/CLP/AI provenance |
| `allegro_offer_create_draft_approved` | APPROVE/WRITE | jawny draft do konkretnego konta; bez publikacji | catalog/duplicate and full cost preflight |
| `allegro_offers_publish_approved` | RESTRICTED/WRITE | jeden zatwierdzony offerId; status command + readback | distinct approval, risk gate, sandbox first |
| `allegro_market_snapshots_compare` | READ | ceny/masa/GTIN/koszt dostawy i timestamp, z dostarczonych legalnie zbiorów | consent/license/provenance, exact product matching |
| `allegro_market_watch_setup` | BLOCKED | nie tworzyć schedulerów/crawlerów autonomicznych | użytkownik wymaga ręcznego uruchamiania |

Nazwy są propozycjami kontraktu; oficjalny SDK może ustalić finalne narzędzia po zatwierdzeniu projektu. `READ` na danych kupujących **nie** oznacza publicznego dostępu.

## 4. Kontrakty danych

Wspólne rekordy:
- `Connection`: opaque `connectionId`, provider=Allegro, environment, allowed actor roles, authorized seller accountId, allowed marketplaces, secretRef server-side, scopes, health.
- `ProductMaster`: internalSKU, EAN, variant/weight, cost, stock owner, supplier, packaging profile, safety refs; nie utożsamiać SKU z Allegro OfferId.
- `ChannelOffer`: connectionId, marketplaceId, offerId, productId/GTIN, internalSKU, price, quantity, status, observedAt, Trace-Id.
- `OrderProjection`: connectionId, orderId, status, revision, line items, payment/COD flags, fulfillment, observedAt; PII przechowywać osobno z krótką retencją.
- `ShipmentPlan`: orderId, parcel item allocation, packed grams/mm, service and carrier ID, COD amount, insurance, validation findings, version/hash, `HUMAN_REQUIRED` if unknown.
- `ShipmentOperation`: idempotencyKey, commandId, requestedAt, status NEW/IN_PROGRESS/SUCCESS/ERROR/UNKNOWN, approvedBy, approvalHash, external IDs, retry policy, lastReconciledAt.
- `CostSnapshot`: SKU × account × marketplace × delivery method × timestamp + currency, gross/net basis, rate source, `KNOWN/ZERO_CONFIRMED/NOT_APPLICABLE/UNKNOWN` for every charge; marketing and returns allocation source.
- `MarketObservation`: sourceProvider/license, fetchedAt, offerUrl/ID, GTIN, variant, weight, unit price, shipping, availability, confidence, sourceChecksum; no untrusted rankings without provenance.
- `Proposal/Approval`: initiating actor, tool, connectionId, resourceId, expectedRevision/current values, desired values, policyResults, proposalHash, expiry, approver, usedAt. Single-use approval.

Existing `templates/{cost-model,shipping-profile,offer-template}.schema.json` are starting contracts, not fully validated runtime schemas.

## 5. Packing and shipping rules — determinism before AI

Inputs: verified SKU family + quantity + packed measured weights/dimensions + channel serviceId + actual order with delivery method/payment + carrier limits from provider. Do not fill gaps by estimation.

- Allegro chalk bags: one bag per parcel. Liquid 5 L: separated from chalk; maximum three per parcel; exactly four units → two parcels of two. Quantities `>4`: **HUMAN_REQUIRED** until packing decision/versioned tests approved.
- Pallets: **MANUAL/APPROVED**; COD mismatch or missing COD = CRITICAL. Live fish: distinct regulated process; not regular parcel autopilot.
- `READY_FOR_PROCESSING` and revision fresh required before shipment create.
- Shipment create workflow: obtain `delivery-proposals` → validate service + seller rules + actual packed dimensions → persist operation and approval → `create-commands` → poll status with `Retry-After` → link shipment ID → retrieve label restricted → carrier handover event → tracking → customer fulfillment.
- No blind duplicate POST. Timeout = `UNKNOWN`, reconcile with command ID/order before deciding whether to retry.
- Carrier-specific fields (including 29.10.2026 move to `packages.transportingInfo`) covered by fixture tests. Never assume a generated label means handed to carrier.

## 6. Costs and repricing

`contributionMarginNet = salesRevenueNet - ∑knownVariableCostsNet`. Only if **all required costs complete** and taxes/revenue correctly normalized. Mandatory components listed in `templates/cost-model.schema.json`: purchase, inbound, packaging and labor, base/extra commission, Smart, carrier and surcharges, COD, promo, Ads, refunds/returns reserve, damages and other. Discounts/Allegro Ceny need separate reimbursement evidence, not automatic positive revenue.

For each price proposal expose: purchase VAT rate source, sales VAT basis, merchant fee base, gross↔net conversion, parcel count, shipping method, minimum margin, price floor and counterexample for one missed surcharge. Use decimal fixed precision and `BLOCKED` for unknowns. Never auto-follow the cheapest competitor if resulting net margin falls below threshold or product GTIN/pack size is not identical. Multi-account duplicate/product policy validated first.

## 7. Product and assortment

1. Inventory/Product Master → normalized product.
2. Allegro categories/products and parameters **fresh** from API.
3. `OfferTemplate` draft with verified shipping profile, responsible person, safety/GPSR/CLP/AI declarations, GTIN.
4. Check active offers across all linked accounts for duplicate constraints.
5. Calculate full costs and return `BLOCKED` on unknown.
6. Preview diff and obtain approval for single account; create unpublished draft only.
7. Separate publish operation after fresh preflight and new approval. Async status, readback, audit.

## 8. Market/competitor intelligence — source restriction

The official Allegro REST methods page explicitly says `GET /offers/listing` is no longer available and validation suspended for business reasons:
https://developer.allegro.pl/tutorials/lista-metod-rest-api-allegro-yPyaj0wG3C4 .
**Do not build generic public search assuming seller OAuth makes it work.**

MVP uses operator-supplied exports or a distinct, legally authorized provider/API after contractual access is established. No anonymous background scraping by default. Matching rules require exact GTIN or approved category attributes, pack weight, number of items, condition, delivery inclusion, timestamp and confidence. Outputs are **recommendations only**, not write instructions. Fees/payments and Ads are assessed on own account data, not competitors' inferred profit.

## 9. Security, observability, reliability

- Two auth boundaries; least privilege scopes; per-account connection mapping; sellerId and environment verification for each request.
- No `Authorization`, secrets, document PDFs, full customer payloads or personal details in tool responses/logs/repositories. Logs with masked IDs and Trace-Id only.
- Typed allowlist endpoints; no arbitrary `url`, `host`, `method` or raw JSON business write tools.
- Approval hash bound to exact diff/current version, account, actor, one external resource and expiry.
- Outbox + ledger persist commandId and retry state. Handle 401 once after controlled refresh, 429 `Retry-After`, 5xx retry only when idempotent and state confirmed.
- Kill switch per account/service/operation. Replay/inbox dedup. Recovery runbooks.
- Business actions from AI only on manual initiation; no unsanctioned recurring order processing, repricing or competitor crawler.
- Tests: fake Allegro transport & fixtures, test denied scopes, crossed connections, duplicate commands, timeout ambiguity, no token leakage, source data drift, bogus VAT, multiple parcels, pallet COD, disabled LISTING endpoint, final state verification.

## 10. Acceptance gates

| Gate | Evidence required | Present status |
|---|---|---|
| G0 Documented architecture and audit | reviewed proposed design, source links, ownership | **PROPOSED / review pending** |
| G1 Offline domain functions | unit/regression + MCP protocol & stdio smoke on GitHub CI | Not yet implemented (current 3 docs tools separate) |
| G2 Read-only real Allegro connection | OAuth Sandbox with scope, account identity, token refresh, tests of 401/429, masking PII | Not implemented |
| G3 Order/shipment audit | fixtures + sandbox orders, WzA endpoints, carrier tracking and first scan | Not implemented |
| G4 Costs/stock/product proposals | real source price/stock ownership, accurate VAT and full cost, duplicates + GPSR | Not implemented |
| G5 Single controlled shipment test | one approved sandbox order, command ledger, label, readback, no duplicate | Not implemented |
| G6 Single offer/price change | exact approval binding, minimal PATCH/draft, reconcile | Not implemented |
| G7 Production rollout | limited account/SKU, incident rollback, metrics and owner signoff | BLOCKED |

**Proposed starting point after approval:** offline `shipment_preflight` and `cost_audit` as framework-neutral pure Python functions with structured fixtures; no OAuth, no PII and no marketplace write. See [implementation plan](mcp-allegro-implementation-plan-2026-10-17.md).

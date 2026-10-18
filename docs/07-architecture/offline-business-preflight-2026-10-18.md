# Offline shipment and cost preflight — 2026-10-18

**Status: IMPLEMENTED offline; NOT CONNECTED to Allegro or a carrier; no production validation.**

This development adds two pure Python domain services under allegro_domain and two MCP stdio tools:

- allegro_shipment_preflight_offline(order, parcels)
- allegro_cost_preflight_offline(cost_snapshot)

These accept **caller-supplied sample or manually entered data only**. Tools do not use OAuth, create labels, send requests, touch seller listings, or store customer data. All responses include mode=OFFLINE_PREVIEW, allegro_connected=false, writes_performed=false. PASS means local rules accepted the supplied data, NOT verified shipment authorization or profitability from actual settlements.

## Shipment input contract

Order contains:
- status: READY_FOR_PROCESSING (required for PASS)
- items: list of unique SKU, kind and positive integer quantity; kind is CHALK_BAG, CANISTER_5L, PALLET or OTHER.
- service: verified (boolean), max_weight_grams (positive integer), supports_cod (boolean).
- cod_required (boolean), cod_amount_gross (decimal string when required).
- shipment_status (NOT_CREATED, LABEL_CREATED or HANDED_OVER), first_scan_at (optional timestamp as string).

Parcels are list of objects with items (SKU + positive quantity), packed_weight_grams (positive integer, measured **after packing**) and verified (boolean). Missing or unverified source is HUMAN_REQUIRED, not an excuse to invent weights. The API does not verify the caller's claim of source verification.

Deterministic safety rules imported from 7dejv-mcp/SHIPPING_RULES.md:
- Exactly 1 chalk bag per parcel, never with a 5 L canister.
- Maximum 3 × 5 L in one parcel; exactly 4 must be split 2+2; more than 4 is unapproved / HUMAN_REQUIRED.
- Total quantities across parcels must exactly match the order. Unexpected SKUs, missing pieces, oversize weight, or unsupported COD are BLOCK.
- Pallets must go to human/manual approval, and a COD pallet without COD support is BLOCK.
- LABEL_CREATED does not mean handed over to carrier. A supplied first_scan_at only represents user-supplied information, NOT externally verified tracking evidence. Real handover requires authenticated carrier/Allegro reconciliation in the future adapter.
- OTHER requires human review; no automatic support for live animals or chemistry with special shipping restrictions.

Examples of blocking codes: MISSING_ITEM_ALLOCATION, CHALK_ONE_BAG_PER_PARCEL, MIXED_CHALK_LIQUID, CARRIER_WEIGHT_LIMIT, PALLET_COD_MISMATCH, HANDOVER_UNCONFIRMED.

## Cost input contract

The seventeen cost fields and statuses come from templates/cost-model.schema.json. Each cost object requires value, status, sourceRef, effectiveAt. Statuses are KNOWN (positive amount), ZERO_CONFIRMED (exact zero with evidence), NOT_APPLICABLE (null value with evidence), or UNKNOWN (BLOCK). Fields lacking evidence or missing entirely are BLOCK.

For the entire snapshot require:
- taxBasis=NET and currency e.g. PLN.
- complete=true, gross sales price, separately verified salesRevenueNet (net sale price), minimumContributionMarginNet; all decimal amounts as strings, never float.
- No implicit VAT conversion and no replacement of UNKNOWN with 0. Exact Decimal cents.
- net contribution = supplied salesRevenueNet minus seventeen supplied net variable cost fields; percentage is of net revenue. Below-margin results are BLOCK and not a price-change recommendation.
- All sources/values are **claims provided by the caller**, not proof that Allegro fees, Ads allocation or VAT are correct.

## Verification and restrictions

CI steps: python -m unittest discover -s tests -v; python -m scripts.smoke_mcp, with requirements-mcp.txt pinned. No mock credentials needed. Present SDK smoke runs in memory; a separate stdio process/Windows/Inspector test is not yet claimed.

Follow-up: authoritative shipping profiles, real service limits, WzA order read, verified first-scan evidence, OAuth read-only and settlement-based costs. Absolutely no automatic shipping, pricing, offer creation or competitor crawling is part of this stage.

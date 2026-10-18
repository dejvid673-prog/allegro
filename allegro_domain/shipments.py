"""Deterministic offline shipment preflight. No API calls, labels or write operations."""
from __future__ import annotations

from collections import Counter
from decimal import Decimal, InvalidOperation

MAX_ENTRIES = 500
KINDS = {"CHALK_BAG", "CANISTER_5L", "PALLET", "OTHER"}


def positive_int(value: object, path: str) -> int:
    if type(value) is not int or value <= 0:
        raise ValueError(f"{path} must be a positive integer")
    return value


def nonnegative_amount(value: object, path: str) -> Decimal:
    if type(value) not in (str, int):
        raise ValueError(f"{path} must be a decimal string or integer")
    try:
        amount = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError(f"{path} must be a decimal amount") from exc
    if not amount.is_finite() or amount < 0 or amount != amount.quantize(Decimal("0.01")):
        raise ValueError(f"{path} must be a finite nonnegative amount in cents")
    return amount


def audit_shipment_plan(order: dict, parcels: list[dict]) -> dict:
    """Inspect supplied order and parcel allocation, without contacting Allegro.

    PASS means the supplied *plan* passed local rules, NOT that shipping is
    authorized, payment confirmed, a label issued or a carrier has accepted it.
    """
    if not isinstance(order, dict) or not isinstance(parcels, list):
        raise ValueError("order must be an object and parcels a list")
    items = order.get("items")
    if not isinstance(items, list) or not 1 <= len(items) <= MAX_ENTRIES or len(parcels) > MAX_ENTRIES:
        raise ValueError("order.items requires 1..500 entries; max 500 parcels")

    findings: set[str] = set()
    blocks: set[str] = set()
    reviews: set[str] = set()

    def block(code: str) -> None:
        blocks.add(code)
        findings.add(code)

    def review(code: str) -> None:
        reviews.add(code)
        findings.add(code)

    if order.get("status") != "READY_FOR_PROCESSING":
        block("ORDER_NOT_READY")

    ordered: Counter[str] = Counter()
    kinds: dict[str, str] = {}
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise ValueError(f"items[{index}] must be an object")
        sku, kind = item.get("sku"), item.get("kind")
        if not isinstance(sku, str) or not sku.strip() or len(sku) > 120:
            raise ValueError(f"items[{index}].sku is invalid")
        if not isinstance(kind, str) or kind not in KINDS:
            raise ValueError(f"items[{index}].kind is unknown")
        quantity = positive_int(item.get("quantity"), f"items[{index}].quantity")
        if sku in kinds:
            block("DUPLICATE_ORDER_SKU")
        kinds[sku] = kind
        ordered[sku] += quantity
        if kind == "PALLET":
            review("PALLET_MANUAL_APPROVAL")
        if kind == "OTHER":
            review("PRODUCT_PROFILE_REQUIRED")
        if kind == "CANISTER_5L" and quantity > 4:
            review("CANISTER_QUANTITY_NOT_APPROVED")

    service = order.get("service")
    if not isinstance(service, dict):
        service = {}
        review("UNVERIFIED_SERVICE")
    max_weight = service.get("max_weight_grams")
    if service.get("verified") is not True or type(max_weight) is not int or max_weight <= 0:
        review("UNVERIFIED_SERVICE")
        max_weight = None

    cod_required = order.get("cod_required")
    if type(cod_required) is not bool:
        review("PAYMENT_DATA_REQUIRED")
    elif cod_required:
        cod_amount = order.get("cod_amount_gross")
        if cod_amount is None or nonnegative_amount(cod_amount, "cod_amount_gross") == 0:
            block("MISSING_COD_AMOUNT")
        if service.get("supports_cod") is not True:
            block("PALLET_COD_MISMATCH" if "PALLET" in kinds.values() else "COD_NOT_SUPPORTED")

    actual: Counter[str] = Counter()
    canister_sizes: dict[str, list[int]] = {}
    if not parcels:
        block("MISSING_PARCELS")
    for index, parcel in enumerate(parcels):
        if not isinstance(parcel, dict):
            raise ValueError(f"parcels[{index}] must be an object")
        entries = parcel.get("items")
        if not isinstance(entries, list) or not 1 <= len(entries) <= MAX_ENTRIES:
            raise ValueError(f"parcels[{index}].items must contain 1..500 entries")
        if parcel.get("verified") is not True:
            review("UNVERIFIED_PACKED_WEIGHT")
        weight = parcel.get("packed_weight_grams")
        if type(weight) is not int or weight <= 0:
            review("MISSING_PACKED_WEIGHT")
        elif max_weight is not None and weight > max_weight:
            block("CARRIER_WEIGHT_LIMIT")
        chalk = cans = 0
        for j, entry in enumerate(entries):
            if not isinstance(entry, dict) or not isinstance(entry.get("sku"), str):
                raise ValueError(f"parcels[{index}].items[{j}] must have sku")
            sku = entry["sku"]
            quantity = positive_int(entry.get("quantity"), f"parcels[{index}].items[{j}].quantity")
            if sku not in kinds:
                block("UNKNOWN_SKU")
                continue
            actual[sku] += quantity
            if kinds[sku] == "CHALK_BAG":
                chalk += quantity
            if kinds[sku] == "CANISTER_5L":
                cans += quantity
                canister_sizes.setdefault(sku, []).append(quantity)
        if chalk > 1:
            block("CHALK_ONE_BAG_PER_PARCEL")
        if chalk and cans:
            block("MIXED_CHALK_LIQUID")
        if cans > 3:
            block("TOO_MANY_CANISTERS")

    for sku, expected in ordered.items():
        if actual[sku] < expected:
            block("MISSING_ITEM_ALLOCATION")
        if actual[sku] > expected:
            block("EXCESS_ITEM_ALLOCATION")
        if kinds[sku] == "CANISTER_5L" and expected == 4:
            if sorted(canister_sizes.get(sku, [])) != [2, 2]:
                review("CANISTER_FOUR_REQUIRES_TWO_PLUS_TWO")

    first_scan = order.get("first_scan_at")
    handed_over = (isinstance(first_scan, str) and bool(first_scan.strip())
                   and order.get("first_scan_verified") is True)
    if order.get("shipment_status") == "HANDED_OVER" and not handed_over:
        block("HANDOVER_UNCONFIRMED")
    if order.get("shipment_status") == "LABEL_CREATED" and not handed_over:
        findings.add("LABEL_NOT_HANDED_OVER")

    return {
        "mode": "OFFLINE_PREVIEW",
        "allegro_connected": False,
        "writes_performed": False,
        "status": "BLOCK" if blocks else "HUMAN_REQUIRED" if reviews else "PASS",
        "findings": sorted(findings),
        "parcel_count": len(parcels),
        "handover_confirmed": handed_over,
    }

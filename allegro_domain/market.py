"""Comparable-price report from explicitly supplied market observations only.

Does not scrape Allegro, access /offers/listing, schedule scans or change prices.
Source metadata is DECLARED by the caller, never independently verified here.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP

from allegro_domain.costs import money, format_money

MAX_ENTRIES = 500
MAX_AGE_DAYS = 14
ALLOWED_SOURCES = {"USER_PROVIDED_EXPORT", "LICENSED_FEED"}


def _text(value: object, path: str, required: bool = True) -> str:
    if not isinstance(value, str) or len(value) > 250 or (required and not value.strip()):
        raise ValueError(f"{path} is invalid")
    return value


def _positive(value: object, path: str) -> int:
    if type(value) is not int or not 1 <= value <= 1_000_000:
        raise ValueError(f"{path} must be a positive bounded integer")
    return value


def _timestamp(value: object, path: str) -> datetime:
    if not isinstance(value, str) or len(value) > 40:
        raise ValueError(f"{path} requires timezone-aware ISO timestamp")
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        raise ValueError(f"{path} requires timezone-aware ISO timestamp") from None
    if result.tzinfo is None or result.utcoffset() is None:
        raise ValueError(f"{path} requires timezone-aware ISO timestamp")
    return result.astimezone(timezone.utc)


def _offer_core(entry: dict, index: int, *, own: bool) -> dict:
    if not isinstance(entry, dict):
        raise ValueError(f"entry[{index}] must be an object")
    tag = "own" if own else "competitor"
    identity = (_text(entry.get("offer_id"), f"{tag}[{index}].offer_id")
                if own else _text(entry.get("offer_ref"), f"{tag}[{index}].offer_ref"))
    if own:
        _text(entry.get("connection_id"), f"own[{index}].connection_id")
        _text(entry.get("sku"), f"own[{index}].sku")
    gtin = entry.get("gtin")
    if gtin is not None:
        _text(gtin, f"{tag}[{index}].gtin", required=False)
    weight = _positive(entry.get("net_weight_grams"), f"{tag}[{index}].net_weight_grams")
    units = _positive(entry.get("units_per_offer"), f"{tag}[{index}].units_per_offer")
    condition = _text(entry.get("condition"), f"{tag}[{index}].condition")
    price = money(entry.get("price_gross"), f"{tag}[{index}].price_gross")
    shipping = money(entry.get("shipping_gross"), f"{tag}[{index}].shipping_gross")
    return {
        "id": identity, "gtin": gtin, "weight": weight,
        "units": units, "condition": condition, "delivered": price + shipping,
        "entry": entry,
    }


def _per_kg(amount: Decimal, weight: int, units: int) -> str:
    kg = Decimal(weight) * Decimal(units) / Decimal(1000)
    return str((amount / kg).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def compare_market_snapshots(
    own_offers: list[dict],
    competitor_observations: list[dict],
) -> dict:
    """Return draft comparisons only when GTIN/pack size/condition match exactly.

    Prices include declared delivery charge; service equivalence and actual
    legal provenance remain external review gates. Observations older than
    14 days cannot be used for comparisons.
    """
    if not isinstance(own_offers, list) or not isinstance(competitor_observations, list):
        raise ValueError("both datasets must be lists")
    if len(own_offers) > MAX_ENTRIES or len(competitor_observations) > MAX_ENTRIES:
        raise ValueError("maximum 500 entries in each dataset")
    mine = [_offer_core(x, i, own=True) for i, x in enumerate(own_offers)]
    competitors = []
    issues: set[str] = set()
    now = datetime.now(timezone.utc)
    source_invalid = False
    for i, row in enumerate(competitor_observations):
        entry = _offer_core(row, i, own=False)
        ref = row.get("source_ref")
        if row.get("source_type") not in ALLOWED_SOURCES or not isinstance(ref, str) or not ref.strip() or len(ref) > 250:
            issues.add("MISSING_OR_UNAPPROVED_SOURCE_DECLARATION")
            source_invalid = True
            continue
        observed = _timestamp(row.get("observed_at"), f"competitor[{i}].observed_at")
        if observed > now + timedelta(minutes=5):
            issues.add("FUTURE_MARKET_OBSERVATION")
            continue
        if observed < now - timedelta(days=MAX_AGE_DAYS):
            issues.add("STALE_MARKET_OBSERVATION")
            continue
        competitors.append(entry)
    # Fail whole batch closed when source provenance is incomplete, rather than
    # silently omitting unverifiable entries and claiming the market is complete.
    if source_invalid:
        return {
            "mode": "OFFLINE_MARKET_DRAFT", "allegro_connected": False,
            "market_data_verified": False, "writes_performed": False,
            "status": "BLOCK", "findings": sorted(issues), "comparisons": [],
            "own_count": len(mine), "competitor_count": len(competitor_observations),
        }
    comparisons = []
    for own in mine:
        candidates = [
            item for item in competitors
            if own["gtin"] and item["gtin"] and own["gtin"] == item["gtin"]
            and own["weight"] == item["weight"] and own["units"] == item["units"]
            and own["condition"] == item["condition"]
        ]
        if not candidates:
            issues.add("NO_EXACT_COMPARISON")
            continue
        best = min(candidates, key=lambda p: (p["delivered"], p["id"]))
        comparisons.append({
            "connection_id": own["entry"]["connection_id"],
            "offer_id": own["id"], "sku": own["entry"]["sku"],
            "source_ref": best["entry"]["source_ref"],
            "competitor_offer_ref": best["id"],
            "own_delivered_gross": format_money(own["delivered"]),
            "competitor_delivered_gross": format_money(best["delivered"]),
            "own_minus_competitor_gross": format_money(own["delivered"] - best["delivered"]),
            "own_delivered_per_kg_gross": _per_kg(own["delivered"], own["weight"], own["units"]),
            "competitor_delivered_per_kg_gross": _per_kg(best["delivered"], best["weight"], best["units"]),
        })
    return {
        "mode": "OFFLINE_MARKET_DRAFT", "allegro_connected": False,
        "market_data_verified": False, "writes_performed": False,
        "status": "DRAFT" if comparisons else "REVIEW",
        "findings": sorted(issues), "comparisons": comparisons,
        "own_count": len(mine), "competitor_count": len(competitor_observations),
    }

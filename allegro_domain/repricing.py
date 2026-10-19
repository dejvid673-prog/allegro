"""Price change simulation. No requests to Allegro, no repricing execution."""
from __future__ import annotations

from decimal import Decimal

from allegro_domain.costs import audit_cost_snapshot, format_money, money


def _identity(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > 128:
        raise ValueError(f"{name} is invalid")
    return value


def propose_price_change(
    current_offer: dict,
    proposed_price_gross: str,
    projected_cost_snapshot: dict,
) -> dict:
    """Produce a non-executable price proposal using recalculated projected costs.

    A complete new snapshot MUST reflect new fees/commission and NET revenue
    at the proposed GROSS price. This tool never infers VAT, commission,
    profitability from a competitor price, or approval to change an offer.
    """
    if not isinstance(current_offer, dict) or not isinstance(projected_cost_snapshot, dict):
        raise ValueError("current_offer and projected_cost_snapshot must be objects")
    conn = _identity(current_offer.get("connection_id"), "connection_id")
    offer_id = _identity(current_offer.get("offer_id"), "offer_id")
    sku = _identity(current_offer.get("sku"), "sku")
    old_price = money(current_offer.get("price_gross"), "current_offer.price_gross")
    new_price = money(proposed_price_gross, "proposed_price_gross")
    if old_price <= 0 or new_price <= 0:
        raise ValueError("both prices must be greater than zero")
    checked = audit_cost_snapshot(projected_cost_snapshot)
    findings = list(checked["findings"])
    snapshot_price = projected_cost_snapshot.get("salesPriceGross")
    if snapshot_price is None or money(snapshot_price, "salesPriceGross") != new_price:
        findings.append("PROPOSED_PRICE_COST_SNAPSHOT_MISMATCH")
    if projected_cost_snapshot.get("currency") != "PLN":
        findings.append("CURRENCY_REQUIRES_REVIEW")
    if old_price == new_price:
        findings.append("PROPOSED_PRICE_UNCHANGED")
    return {
        "mode": "OFFLINE_PRICE_DRAFT", "allegro_connected": False,
        "writes_performed": False, "approval_granted": False,
        "status": "DRAFT" if not findings else "BLOCK",
        "connection_id": conn, "offer_id": offer_id, "sku": sku,
        "expected_price_gross": format_money(old_price),
        "proposed_price_gross": format_money(new_price),
        "delta_gross": format_money(new_price - old_price),
        "contribution_margin_net": checked["contributionMarginNet"],
        "contribution_margin_pct": checked["contributionMarginPct"],
        "minimum_margin_met": checked["meetsMinimum"],
        "costs_verified_by_live_ledger": False,
        "findings": sorted(set(findings)),
        "next_step": (
            "Obtain fresh seller offer and actual cost evidence; obtain a separate "
            "single-use approval before any future WRITE operation."
        ),
    }

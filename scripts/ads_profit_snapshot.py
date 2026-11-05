#!/usr/bin/env python3
"""Read-only Allegro Ads normalized snapshot audit (stdlib, no network, no PII output).

Input contract: templates/ads-audit-import.schema.json. This is NOT an XLSX
parser and does NOT claim real incremental ad profit. Missing costs block the
contribution conclusion. Use --help for invocation.
"""
from __future__ import annotations

import argparse
import json
from decimal import Decimal, InvalidOperation
from pathlib import Path


REQUIRED_COSTS = frozenset({
    "purchase", "production", "inbound_freight", "commission", "fixed_fees",
    "shipping", "smart", "surcharges", "packaging", "labor",
    "returns_reserve", "payment", "promotion",
})


def number(value: object, field: str) -> Decimal:
    if value is None or isinstance(value, bool):
        raise ValueError(f"{field}: missing/non-numeric value")
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise ValueError(f"{field}: invalid numeric value") from exc
    if not result.is_finite() or result < 0:
        raise ValueError(f"{field}: must be finite and nonnegative")
    return result


def ratio(numerator: Decimal, denominator: Decimal) -> str | None:
    return str(numerator / denominator) if denominator != 0 else None


def audit(payload: dict) -> dict:
    if not isinstance(payload, dict):
        raise ValueError("audit input must be a JSON object")
    errors: list[str] = []
    notes: list[str] = []
    manifest = payload.get("manifest")
    if not isinstance(manifest, dict):
        raise ValueError("manifest must be an object")
    for field in ("account_id", "marketplace_id", "period_start", "period_end",
                  "currency", "monetary_basis", "grain", "attribution_maturity"):
        if not manifest.get(field):
            errors.append(f"manifest missing: {field}")
    if manifest.get("monetary_basis") not in ("GROSS", "NET"):
        errors.append("manifest monetary_basis must be GROSS or NET")

    ads_rows = payload.get("ads_rows")
    if not isinstance(ads_rows, list) or not ads_rows:
        raise ValueError("ads_rows must contain at least one row")
    unique: set[tuple] = set()
    totals = {name: Decimal("0") for name in
              ("impressions", "clicks", "spend", "attributed_revenue", "attributed_orders")}
    for index, row in enumerate(ads_rows):
        if not isinstance(row, dict):
            raise ValueError(f"ads_rows[{index}] must be object")
        key = tuple(row.get(n) for n in
                    ("date", "campaign_id", "group_id", "offer_id", "placement"))
        if key in unique:
            errors.append(f"duplicate source grain for ads_rows[{index}]")
        unique.add(key)
        for field in totals:
            try:
                totals[field] += number(row.get(field), f"ads_rows[{index}].{field}")
            except ValueError as exc:
                errors.append(str(exc))
    # Financial conclusions require all required metrics, and cannot
    # estimate missing values as 0.
    metrics = None
    if not any("ads_rows[" in s or "duplicate source grain" in s for s in errors):
        metrics = {
            "ctr": ratio(totals["clicks"], totals["impressions"]),
            "avg_cpc": ratio(totals["spend"], totals["clicks"]),
            "roas": ratio(totals["attributed_revenue"], totals["spend"]),
            "acos": ratio(totals["spend"], totals["attributed_revenue"]),
            "cvr": ratio(totals["attributed_orders"], totals["clicks"]),
            "cpa": ratio(totals["spend"], totals["attributed_orders"]),
        }

    contribution_before: Decimal | None = None
    contribution_after: Decimal | None = None
    order_lines = payload.get("order_lines")
    cost_rows = payload.get("costs")
    if not isinstance(order_lines, list) or not order_lines:
        errors.append("order_lines missing; profit analysis unavailable")
    if not isinstance(cost_rows, list) or not cost_rows:
        errors.append("costs missing; profit analysis unavailable")
    if isinstance(order_lines, list) and isinstance(cost_rows, list) and order_lines and cost_rows:
        cost_map: dict[tuple[str, str], dict] = {}
        for row in cost_rows:
            if not isinstance(row, dict):
                errors.append("invalid cost row")
                continue
            key = (str(row.get("sku")), str(row.get("offer_id")))
            if key in cost_map:
                errors.append(f"duplicate cost mapping: {key}")
            cost_map[key] = row
        seen_line_ids: set[tuple[str, str]] = set()
        revenue = Decimal("0")
        cost_sum = Decimal("0")
        attributed_order_ids: set[str] = set()
        for i, line in enumerate(order_lines):
            if not isinstance(line, dict):
                errors.append(f"invalid order line: {i}")
                continue
            id_key = (str(line.get("order_id")), str(line.get("line_item_id")))
            if id_key in seen_line_ids:
                errors.append("duplicate order line")
            seen_line_ids.add(id_key)
            if line.get("ads_attributed") is None:
                errors.append("unknown line-item attribution")
                continue
            if line.get("ads_attributed") is not True:
                continue
            attributed_order_ids.add(str(line.get("order_id")))
            try:
                quantity = number(line.get("quantity"), "order quantity")
                sale_amount = number(line.get("sale_amount"), "line sale amount")
                refund = number(line.get("refund_amount", 0), "refund")
            except ValueError as exc:
                errors.append(str(exc))
                continue
            if quantity == 0:
                errors.append("attributed order line has zero quantity")
            if refund > 0:
                errors.append("refund present: source attribution/revenue adjustment must be reconciled first")
            revenue += sale_amount
            key = (str(line.get("sku")), str(line.get("offer_id")))
            record = cost_map.get(key)
            if not record:
                errors.append("missing cost mapping for attributed SKU/offer")
                continue
            items = record.get("cost_items")
            if not isinstance(items, list):
                errors.append("missing cost_items list")
                continue
            by_type: dict[str, dict] = {}
            for item in items:
                if not isinstance(item, dict):
                    errors.append("cost item is not an object")
                    continue
                category = item.get("type")
                if category in by_type:
                    errors.append(f"duplicate cost type: {category}")
                by_type[category] = item
            missing_types = REQUIRED_COSTS.difference(by_type)
            if missing_types:
                errors.append("missing cost statuses: " + ", ".join(sorted(missing_types)))
            for cat, item in by_type.items():
                status = item.get("status")
                if status == "UNKNOWN":
                    errors.append(f"unknown cost: {cat}")
                    continue
                if status not in ("KNOWN", "ZERO_CONFIRMED", "NOT_APPLICABLE"):
                    errors.append(f"invalid cost status: {cat}")
                    continue
                if not item.get("evidence"):
                    errors.append(f"cost without evidence: {cat}")
                if status in ("NOT_APPLICABLE", "ZERO_CONFIRMED"):
                    if item.get("value") not in (None, 0):
                        errors.append(f"nonzero cost marked {status}: {cat}")
                    continue
                if item.get("basis") != manifest.get("monetary_basis"):
                    errors.append(f"mixed cost gross/net basis: {cat}")
                if item.get("per") != "unit":
                    errors.append(f"cost basis unsupported for automated allocation: {cat}")
                    continue
                try:
                    cost_sum += number(item.get("value"), f"cost {cat}") * quantity
                except ValueError as exc:
                    errors.append(str(exc))
        if len(attributed_order_ids) != totals["attributed_orders"]:
            errors.append("unique attributed order count does not reconcile with Ads report")
        if revenue != totals["attributed_revenue"]:
            errors.append("attributed order-line revenue does not reconcile with Ads report")
        if not errors:
            contribution_before = revenue - cost_sum
            contribution_after = contribution_before - totals["spend"]

    maturity = manifest.get("attribution_maturity")
    if maturity != "MATURE":
        notes.append("Attribution period incomplete or unknown; proposals provisional")
    status = "HOLD_DATA" if errors else ("PROVISIONAL" if maturity != "MATURE" else "PASS")
    return {
        "status": status,
        "scope": {key: manifest.get(key) for key in
                  ("account_id", "marketplace_id", "period_start", "period_end",
                   "currency", "monetary_basis", "grain", "attribution_maturity")},
        "totals": {key: str(value) for key, value in totals.items()},
        "metrics": metrics,
        "attributed_contribution_before_ads": str(contribution_before) if contribution_before is not None else None,
        "attributed_contribution_after_ads": str(contribution_after) if contribution_after is not None else None,
        "errors": sorted(set(errors)),
        "notes": notes + ["Attributed contribution is NOT incremental profit. No Ads writes or network calls."],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_json", type=Path, help="normalized Ads snapshot JSON (not XLSX)")
    args = parser.parse_args()
    try:
        payload = json.loads(args.input_json.read_text(encoding="utf-8"))
        result = audit(payload)
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "BLOCKED", "error": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] in ("PASS", "PROVISIONAL") else 1


if __name__ == "__main__":
    raise SystemExit(main())

"""Strict offline accounting preview from supplied evidence; never guesses VAT."""
from __future__ import annotations

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

COST_FIELDS = (
    "purchaseNet", "inboundFreightNet", "packagingMaterialsNet",
    "packagingLaborNet", "paymentFeesNet", "allegroBaseCommissionNet",
    "allegroFixedFeesNet", "smartContributionNet", "carrierBaseNet",
    "carrierSurchargesNet", "codFeeNet", "promotionFixedNet",
    "promotionCommissionNet", "adsAttributedNet", "returnsReserveNet",
    "damageReserveNet", "otherNet",
)
STATUSES = {"KNOWN", "ZERO_CONFIRMED", "UNKNOWN", "NOT_APPLICABLE"}
CENT = Decimal("0.01")


def money(value: object, path: str) -> Decimal:
    if type(value) not in (str, int, Decimal):
        raise ValueError(f"{path} must be an exact decimal string or integer")
    try:
        amount = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError(f"{path} must be an amount") from exc
    if not amount.is_finite() or amount < 0:
        raise ValueError(f"{path} must be finite and nonnegative")
    try:
        if amount != amount.quantize(CENT):
            raise ValueError(f"{path} must have no more than two significant decimals")
    except InvalidOperation as exc:
        raise ValueError(f"{path} is too large") from exc
    return amount


def format_money(amount: Decimal) -> str:
    return str(amount.quantize(CENT, rounding=ROUND_HALF_UP))


def audit_cost_snapshot(data: dict) -> dict:
    """Check costs and net contribution margin, without external settlements.

    All costs AND salesRevenueNet must be supplied as already verified NET
    amounts. Gross→net VAT conversion is deliberately not inferred.
    An UNKNOWN, missing field or missing proof prevents an apparent profit.
    """
    if not isinstance(data, dict):
        raise ValueError("cost snapshot must be an object")
    findings: set[str] = set()
    if data.get("taxBasis") != "NET":
        findings.add("TAX_BASIS_NOT_NET")
    if data.get("complete") is not True:
        findings.add("SNAPSHOT_NOT_VERIFIED_COMPLETE")
    if not isinstance(data.get("currency"), str) or len(data["currency"]) != 3 or not data["currency"].isalpha():
        findings.add("INVALID_CURRENCY")
    costs: list[Decimal] = []
    for field in COST_FIELDS:
        item = data.get(field)
        if not isinstance(item, dict):
            findings.add(f"UNKNOWN_COST:{field}")
            continue
        status = item.get("status")
        if not isinstance(status, str) or status not in STATUSES:
            raise ValueError(f"{field}.status is invalid")
        if status == "UNKNOWN":
            findings.add(f"UNKNOWN_COST:{field}")
            if item.get("value") is not None:
                findings.add(f"INCONSISTENT_COST_STATE:{field}")
            continue
        has_ref = isinstance(item.get("sourceRef"), str) and bool(item["sourceRef"].strip())
        has_date = isinstance(item.get("effectiveAt"), str) and bool(item["effectiveAt"].strip())
        if not has_ref or not has_date:
            findings.add(f"MISSING_COST_EVIDENCE:{field}")
        value = item.get("value")
        if status == "NOT_APPLICABLE":
            if value is not None:
                findings.add(f"INCONSISTENT_COST_STATE:{field}")
            costs.append(Decimal(0))
            continue
        if value is None:
            findings.add(f"UNKNOWN_COST:{field}")
            continue
        amount = money(value, f"{field}.value")
        if (status == "ZERO_CONFIRMED" and amount != 0) or (status == "KNOWN" and amount == 0):
            findings.add(f"INCONSISTENT_COST_STATE:{field}")
        costs.append(amount)

    for field, code in (
        ("salesRevenueNet", "UNKNOWN_NET_REVENUE"),
        ("salesPriceGross", "UNKNOWN_GROSS_PRICE"),
        ("minimumContributionMarginNet", "UNKNOWN_MINIMUM_MARGIN"),
    ):
        if data.get(field) is None:
            findings.add(code)
        else:
            money(data[field], field)

    result = {
        "mode": "OFFLINE_PREVIEW", "allegro_connected": False,
        "writes_performed": False, "status": "BLOCK", "findings": sorted(findings),
        "totalVariableCostNet": None, "contributionMarginNet": None,
        "contributionMarginPct": None, "meetsMinimum": None,
    }
    if findings:
        return result

    revenue = money(data["salesRevenueNet"], "salesRevenueNet")
    total = sum(costs, Decimal(0))
    margin = revenue - total
    minimum = money(data["minimumContributionMarginNet"], "minimumContributionMarginNet")
    result["totalVariableCostNet"] = format_money(total)
    result["contributionMarginNet"] = format_money(margin)
    result["contributionMarginPct"] = format_money(margin / revenue * 100) if revenue else None
    result["meetsMinimum"] = margin >= minimum
    if margin < minimum:
        result["findings"] = ["BELOW_MINIMUM_MARGIN"]
    else:
        result["status"] = "PASS"
    return result

"""Post-label shipping event auditor. Inspects supplied data, never creates labels."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from allegro_domain.shipments import nonnegative_amount

MAX_SHIPMENTS = 500
VALID_STATUSES = {
    "NOT_CREATED", "LABEL_CREATED", "HANDED_OVER",
    "IN_TRANSIT", "DELIVERED", "CANCELLED",
}
REQUIRES_HANDOVER = {"HANDED_OVER", "IN_TRANSIT", "DELIVERED"}


def _id(value: object, path: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > 128:
        raise ValueError(f"{path} must be a nonempty identifier")
    return value


def _date(value: object, path: str, *, optional: bool = False) -> datetime | None:
    if optional and value is None:
        return None
    if not isinstance(value, str) or len(value) > 40:
        raise ValueError(f"{path} must be an ISO timestamp with timezone")
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        raise ValueError(f"{path} must be an ISO timestamp with timezone") from None
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise ValueError(f"{path} must be an ISO timestamp with timezone")
    return dt.astimezone(timezone.utc)


def audit_shipment_events(shipments: list[dict], as_of: str | None = None) -> dict:
    """Detect shipment exceptions including stale labels and mismatched COD.

    'first_scan_verified' must reflect trusted carrier evidence, NOT user
    assumption or presence of a tracking number. Results are offline only.
    """
    if not isinstance(shipments, list) or len(shipments) > MAX_SHIPMENTS:
        raise ValueError("shipments must be a list of up to 500 entries")
    now = _date(as_of, "as_of") if as_of is not None else datetime.now(timezone.utc)
    findings: list[dict] = []
    critical = False
    confirmed = 0
    track_to_order: dict[tuple[str, str], str] = {}
    shipment_keys: set[tuple[str, str]] = set()

    def report(code: str, conn: str, order: str, shipping_id: str, block: bool = False):
        nonlocal critical
        critical |= block
        findings.append({
            "code": code, "connection_id": conn, "order_id": order,
            "shipment_id": shipping_id, "severity": "BLOCK" if block else "REVIEW",
        })

    for i, row in enumerate(shipments):
        if not isinstance(row, dict):
            raise ValueError(f"shipments[{i}] must be an object")
        conn = _id(row.get("connection_id"), f"shipments[{i}].connection_id")
        order = _id(row.get("order_id"), f"shipments[{i}].order_id")
        shipping_id = _id(row.get("shipment_id"), f"shipments[{i}].shipment_id")
        key = (conn, shipping_id)
        if key in shipment_keys:
            raise ValueError("duplicate shipment identity within snapshot")
        shipment_keys.add(key)
        state = row.get("status")
        if state not in VALID_STATUSES:
            raise ValueError(f"shipments[{i}].status is invalid")
        label = _date(row.get("label_created_at"), "label_created_at", optional=True)
        scan = _date(row.get("first_scan_at"), "first_scan_at", optional=True)
        verified = row.get("first_scan_verified")
        if type(verified) is not bool:
            raise ValueError("first_scan_verified must be boolean")
        cod = row.get("cod_required")
        if type(cod) is not bool:
            report("PAYMENT_VERIFICATION_REQUIRED", conn, order, shipping_id)
        elif cod:
            expected = row.get("cod_amount_gross")
            carrier = row.get("carrier_cod_amount_gross")
            if expected is None or carrier is None:
                report("COD_AMOUNT_MISSING", conn, order, shipping_id, block=True)
            else:
                expected_amount = nonnegative_amount(expected, "cod_amount_gross")
                carrier_amount = nonnegative_amount(carrier, "carrier_cod_amount_gross")
                if expected_amount == 0 or carrier_amount == 0:
                    report("COD_AMOUNT_ZERO", conn, order, shipping_id, block=True)
                if expected_amount != carrier_amount:
                    report("COD_AMOUNT_MISMATCH", conn, order, shipping_id, block=True)
        tracking = row.get("tracking_number")
        if tracking is not None:
            _id(tracking, f"shipments[{i}].tracking_number")
            tracking_key = (conn, tracking)
            old_order = track_to_order.get(tracking_key)
            if old_order is not None and old_order != order:
                report("TRACKING_ASSIGNED_TO_MULTIPLE_ORDERS",
                       conn, order, shipping_id, block=True)
            track_to_order[tracking_key] = order
        if label is None and state not in {"NOT_CREATED", "CANCELLED"}:
            report("MISSING_LABEL_TIMESTAMP", conn, order, shipping_id)
        if label is not None and label > now + timedelta(minutes=5):
            report("LABEL_FROM_FUTURE", conn, order, shipping_id, block=True)
        if verified and scan is None:
            report("SCAN_VERIFIED_WITHOUT_TIMESTAMP", conn, order, shipping_id, block=True)
        if scan is not None and scan > now + timedelta(minutes=5):
            report("FIRST_SCAN_FROM_FUTURE", conn, order, shipping_id, block=True)
        if label is not None and scan is not None and scan < label - timedelta(minutes=5):
            report("SCAN_BEFORE_LABEL_CREATION", conn, order, shipping_id, block=True)
        handed_over = (verified and scan is not None and scan <= now + timedelta(minutes=5)
                       and (label is None or scan >= label - timedelta(minutes=5)))
        if handed_over:
            confirmed += 1
        elif state in REQUIRES_HANDOVER:
            report("FALSE_HANDOVER_STATUS", conn, order, shipping_id, block=True)
        elif scan is not None:
            report("FIRST_SCAN_UNVERIFIED", conn, order, shipping_id)
        elif label is not None and state != "CANCELLED" and now - label > timedelta(hours=24):
            report("LABEL_OLDER_THAN_24H_NO_FIRST_SCAN", conn, order, shipping_id)
        if state == "LABEL_CREATED" and handed_over:
            report("STATUS_NOT_RECONCILED_WITH_FIRST_SCAN", conn, order, shipping_id)
        if state == "DELIVERED" and not handed_over:
            # Already blocked through FALSE_HANDOVER_STATUS; no duplicate finding needed.
            pass

    findings.sort(key=lambda x: (x["connection_id"], x["order_id"], x["shipment_id"], x["code"]))
    return {
        "mode": "OFFLINE_SHIPMENT_AUDIT", "allegro_connected": False,
        "writes_performed": False,
        "status": "BLOCK" if critical else "REVIEW" if findings else "PASS",
        "shipment_count": len(shipments), "confirmed_handover_count": confirmed,
        "findings": findings,
        "source_verified_by_carrier_api": False,
    }

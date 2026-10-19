"""Offline, cross-account assortment consistency audit. No stock or price writes."""
from __future__ import annotations

from collections import Counter
from decimal import Decimal

from allegro_domain.costs import money

MAX_ENTRIES = 500
STATUSES = {"ACTIVE", "INACTIVE", "ENDED", "UNKNOWN"}


def _id(value: object, path: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > 128:
        raise ValueError(f"{path} must be a non-empty identifier <= 128 chars")
    return value


def _quantity(value: object, path: str) -> int:
    if type(value) is not int or value < 0:
        raise ValueError(f"{path} must be a nonnegative integer")
    return value


def _expectations(value: object, path: str, stock: bool) -> dict:
    if value is None:
        return {}
    if not isinstance(value, dict) or len(value) > MAX_ENTRIES:
        raise ValueError(f"{path} must be a mapping")
    parsed = {}
    for account, expected in value.items():
        _id(account, f"{path}.connection_id")
        parsed[account] = (
            _quantity(expected, f"{path}[{account}]")
            if stock else money(expected, f"{path}[{account}]")
        )
    return parsed


def audit_assortment_snapshot(offers: list[dict], product_master: list[dict]) -> dict:
    """Compare caller-supplied snapshots; a finding is not authorization to sync.

    Expected stock/price must be explicit PER connection. Stock on hand or
    overall master price is not implicitly equal to available offer quantity.
    A possible third offer must be reviewed with Allegro category/condition.
    """
    if not isinstance(offers, list) or not isinstance(product_master, list):
        raise ValueError("offers and product_master must be lists")
    if len(offers) > MAX_ENTRIES or len(product_master) > MAX_ENTRIES:
        raise ValueError("maximum 500 offers and 500 master entries")
    masters: dict[str, dict] = {}
    for i, entry in enumerate(product_master):
        if not isinstance(entry, dict):
            raise ValueError(f"product_master[{i}] must be an object")
        sku = _id(entry.get("sku"), f"product_master[{i}].sku")
        if sku in masters:
            raise ValueError("duplicate master sku")
        gtin = entry.get("gtin")
        if gtin is not None and (not isinstance(gtin, str) or len(gtin) > 32):
            raise ValueError("invalid master gtin")
        masters[sku] = {
            "gtin": gtin,
            "stock": _expectations(entry.get("expected_stock_by_connection"),
                                   f"product_master[{i}].expected_stock_by_connection", True),
            "price": _expectations(entry.get("expected_price_by_connection"),
                                   f"product_master[{i}].expected_price_by_connection", False),
        }

    findings: list[dict] = []
    offer_keys = set()
    active_counts = Counter()

    def issue(code: str, connection_id: str, offer_id: str, sku: str):
        findings.append({
            "code": code, "connection_id": connection_id,
            "offer_id": offer_id, "sku": sku,
        })

    for i, entry in enumerate(offers):
        if not isinstance(entry, dict):
            raise ValueError(f"offers[{i}] must be an object")
        conn = _id(entry.get("connection_id"), f"offers[{i}].connection_id")
        offer_id = _id(entry.get("offer_id"), f"offers[{i}].offer_id")
        sku = _id(entry.get("sku"), f"offers[{i}].sku")
        key = (conn, offer_id)
        if key in offer_keys:
            raise ValueError("duplicate connection_id/offer_id in snapshot")
        offer_keys.add(key)
        stock = _quantity(entry.get("stock"), f"offers[{i}].stock")
        price = money(entry.get("price_gross"), f"offers[{i}].price_gross")
        state = entry.get("status")
        if state not in STATUSES:
            raise ValueError(f"offers[{i}].status is invalid")
        gtin = entry.get("gtin")
        if gtin is not None and (not isinstance(gtin, str) or len(gtin) > 32):
            raise ValueError("invalid offer gtin")
        if state == "ACTIVE":
            active_counts[sku] += 1
        master = masters.get(sku)
        if master is None:
            issue("SKU_MISSING_IN_MASTER", conn, offer_id, sku)
            continue
        if not gtin:
            issue("GTIN_MISSING", conn, offer_id, sku)
        elif not master["gtin"]:
            issue("MASTER_GTIN_UNKNOWN", conn, offer_id, sku)
        elif gtin != master["gtin"]:
            issue("GTIN_MISMATCH", conn, offer_id, sku)
        if conn not in master["stock"]:
            issue("STOCK_EXPECTATION_UNKNOWN", conn, offer_id, sku)
        elif stock != master["stock"][conn]:
            issue("STOCK_DRIFT", conn, offer_id, sku)
        if conn not in master["price"]:
            issue("PRICE_EXPECTATION_UNKNOWN", conn, offer_id, sku)
        elif price != master["price"][conn]:
            issue("PRICE_DRIFT", conn, offer_id, sku)
        if state == "ACTIVE" and price == Decimal(0):
            issue("ACTIVE_OFFER_ZERO_PRICE", conn, offer_id, sku)

    for sku, count in sorted(active_counts.items()):
        if count >= 3:
            issue("POSSIBLE_MULTI_ACCOUNT_DUPLICATE", "*", "*", sku)

    return {
        "mode": "OFFLINE_AUDIT", "allegro_connected": False, "writes_performed": False,
        "status": "REVIEW" if findings else "PASS",
        "offer_count": len(offers), "master_count": len(masters),
        "findings": sorted(findings, key=lambda f: (
            f["connection_id"], f["offer_id"], f["sku"], f["code"]
        )),
    }

"""Strict, buyer-PII-free projections for Allegro READ responses.

Pure functions only: no HTTP, tokens, account lookup, writes or persistence.
Safe for LLM summaries after a trusted host has authorized the actor/account.
Original raw responses must stay inside the authorized backend. Projections
are NOT accounting-grade: billing, refunds and shipping invoices are separate.
"""
from __future__ import annotations

import re
from typing import Any

MAX_PAGE = 100
MAX_LINES = 100
PRICE_PATTERN = re.compile(r"[0-9]{1,12}(?:\.[0-9]{1,2})?")
ID_PATTERN = re.compile(r"[0-9]{1,32}")
UUID_PATTERN = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
DATE_PATTERN = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})")


class ProjectionError(ValueError):
    """Sanitized structural error: never includes external data or PII."""


def _object(data: object, field: str, required: bool = False) -> dict:
    if data is None and not required:
        return {}
    if not isinstance(data, dict):
        raise ProjectionError("INVALID_" + field)
    return data


def _text(data: object, field: str, max_length: int = 120) -> str | None:
    if data is None:
        return None
    if not isinstance(data, str) or not data or len(data) > max_length:
        raise ProjectionError("INVALID_" + field)
    if any(ord(char) < 32 or ord(char) == 127 for char in data):
        raise ProjectionError("INVALID_" + field)
    return data


def _digits(data: object, field: str, required: bool = True) -> str | None:
    if data is None and not required:
        return None
    if not isinstance(data, str) or not ID_PATTERN.fullmatch(data):
        raise ProjectionError("INVALID_" + field)
    return data


def _uuid(data: object, field: str) -> str:
    if not isinstance(data, str) or not UUID_PATTERN.fullmatch(data):
        raise ProjectionError("INVALID_" + field)
    return data


def _int(data: object, field: str, minimum: int = 0) -> int | None:
    if data is None:
        return None
    if type(data) is not int or not minimum <= data <= 1_000_000_000:
        raise ProjectionError("INVALID_" + field)
    return data


def _money(data: object, field: str) -> dict[str, str] | None:
    if data is None:
        return None
    item = _object(data, field, required=True)
    amount = item.get("amount")
    currency = item.get("currency")
    if (not isinstance(amount, str) or not PRICE_PATTERN.fullmatch(amount)
            or not isinstance(currency, str)
            or not re.fullmatch(r"[A-Z]{3}", currency)):
        raise ProjectionError("INVALID_" + field)
    return {"amount": amount, "currency": currency}


def _timestamp(data: object, field: str) -> str | None:
    if data is None:
        return None
    if not isinstance(data, str) or not DATE_PATTERN.fullmatch(data):
        raise ProjectionError("INVALID_" + field)
    return data


def _list(data: object, key: str, max_items: int) -> list:
    obj = _object(data, "RESPONSE", required=True)
    items = obj.get(key)
    if not isinstance(items, list) or len(items) > max_items:
        raise ProjectionError("INVALID_" + key.upper())
    return items


def project_offer(raw: dict) -> dict[str, Any]:
    """Offer metadata only. Price/stock may be missing, never default to zero."""
    src = _object(raw, "OFFER", required=True)
    selling = _object(src.get("sellingMode"), "SELLING_MODE")
    stock = _object(src.get("stock"), "STOCK")
    publication = _object(src.get("publication"), "PUBLICATION")
    external = _object(src.get("external"), "EXTERNAL")
    category = _object(src.get("category"), "CATEGORY")
    price = _money(_object(selling.get("price"), "PRICE") if selling.get("price") is not None else None, "PRICE")
    stock_available = _int(stock.get("available"), "AVAILABLE")
    return {
        "offer_id": _digits(src.get("id"), "OFFER_ID"),
        "title": _text(src.get("name"), "TITLE", 160),
        "external_sku": _text(external.get("id"), "EXTERNAL_ID", 120),
        "category_id": _digits(category.get("id"), "CATEGORY_ID", required=False),
        "publication_status": _text(publication.get("status"), "PUBLICATION_STATUS", 40),
        "price_gross": price,
        "stock_available": stock_available,
        "stock_sold": _int(stock.get("sold"), "SOLD"),
        "data_complete": price is not None and stock_available is not None,
    }


def project_offers_page(raw: dict) -> dict[str, Any]:
    """Fixed allowlist only; no transport headers, contacts or other raw fields."""
    src = _object(raw, "OFFERS_RESPONSE", required=True)
    offers = [project_offer(item) for item in _list(src, "offers", MAX_PAGE)]
    if len({offer["offer_id"] for offer in offers}) != len(offers):
        raise ProjectionError("DUPLICATE_OFFER_ID")
    count = _int(src.get("totalCount"), "TOTAL_COUNT")
    return {
        "projection": "allegro_offers_read_v1",
        "privacy": "ALLOWLISTED_NO_BUYER_FIELDS",
        "count": len(offers),
        "total_count": count,
        "offers": offers,
    }


def _line_item(raw: dict) -> dict[str, Any]:
    line = _object(raw, "LINE_ITEM", required=True)
    offer = _object(line.get("offer"), "LINE_OFFER")
    external = _object(offer.get("external"), "LINE_EXTERNAL")
    qty = _int(line.get("quantity"), "QUANTITY", minimum=1)
    price = _money(line.get("price"), "LINE_PRICE")
    return {
        "line_id": _uuid(line.get("id"), "LINE_ID"),
        "offer_id": _digits(offer.get("id"), "LINE_OFFER_ID"),
        "external_sku": _text(external.get("id"), "LINE_EXTERNAL_ID"),
        "quantity": qty,
        "line_price_snapshot": price,
        "data_complete": qty is not None and price is not None,
    }


def project_order(raw: dict) -> dict[str, Any]:
    """Intentionally excludes buyer, addresses, messages, invoice and contacts."""
    src = _object(raw, "ORDER", required=True)
    status = _text(src.get("status"), "ORDER_STATUS", 48)
    if status is None:
        raise ProjectionError("MISSING_ORDER_STATUS")
    lines = [_line_item(line) for line in _list(src, "lineItems", MAX_LINES)]
    if len({line["line_id"] for line in lines}) != len(lines):
        raise ProjectionError("DUPLICATE_LINE_ID")
    fulfillment = _object(src.get("fulfillment"), "FULFILLMENT")
    delivery = _object(src.get("delivery"), "DELIVERY")
    payment = _object(src.get("payment"), "PAYMENT")
    summary = _object(src.get("summary"), "SUMMARY")
    delivery_cost = _money(delivery.get("cost"), "DELIVERY_COST")
    total_to_pay = _money(summary.get("totalToPay"), "TOTAL_TO_PAY")
    return {
        "order_id": _uuid(src.get("id"), "ORDER_ID"),
        "status": status,
        "fulfillment_status": _text(fulfillment.get("status"), "FULFILLMENT_STATUS", 48),
        "updated_at": _timestamp(src.get("updatedAt"), "UPDATED_AT"),
        "payment_type": _text(payment.get("type"), "PAYMENT_TYPE", 48),
        "delivery_cost": delivery_cost,
        "total_to_pay": total_to_pay,
        "line_items": lines,
        "data_complete": (bool(lines) and all(line["data_complete"] for line in lines)
                          and delivery_cost is not None and total_to_pay is not None),
    }


def project_orders_page(raw: dict) -> dict[str, Any]:
    """Page summary fit for LLM/analytics, never a customer-service data source."""
    src = _object(raw, "ORDERS_RESPONSE", required=True)
    items = [project_order(item) for item in _list(src, "checkoutForms", MAX_PAGE)]
    if len({item["order_id"] for item in items}) != len(items):
        raise ProjectionError("DUPLICATE_ORDER_ID")
    count = _int(src.get("totalCount"), "TOTAL_COUNT")
    return {
        "projection": "allegro_orders_read_v1",
        "privacy": "ALLOWLISTED_NO_BUYER_FIELDS",
        "count": len(items),
        "total_count": count,
        "orders": items,
    }

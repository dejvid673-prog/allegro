"""Deterministic, account-free readers of the pinned Allegro API catalog.

This module never makes network requests or handles seller/customer data.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "sources" / "generated" / "endpoints.json"
METADATA_PATH = ROOT / "sources" / "generated" / "openapi-metadata.json"


def _json_file(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def catalog_status() -> dict[str, Any]:
    """Describe the committed snapshot; never imply it matches today's upstream."""
    meta = _json_file(METADATA_PATH)
    return {
        "mode": "OFFLINE_READ_ONLY",
        "allegro_connected": False,
        "live_api_verified": False,
        "snapshot_status": "HOLD: upstream OpenAPI drift; review and refresh required",
        "snapshot_fetched_at": meta["fetchedAt"],
        "source": meta["canonicalSource"],
        "sha256": meta["sha256"],
        "path_count": meta["pathCount"],
        "operation_count": meta["operationCount"],
        "schema_count": meta["schemaCount"],
        "deprecated_operation_count": meta["deprecatedOperationCount"],
    }


def _read_operations() -> list[dict[str, Any]]:
    all_operations = _json_file(CATALOG_PATH)
    if not isinstance(all_operations, list):
        raise ValueError("Invalid local endpoint catalog")
    # GET-only is an additional restriction, not an authorization substitute.
    return [record for record in all_operations
            if isinstance(record, dict) and record.get("method") == "GET"]


def find_read_endpoints(query: str, limit: int = 10) -> dict[str, Any]:
    """Search documented GET operations. Does not call the Allegro REST API."""
    if not isinstance(query, str) or not 1 <= len(query.strip()) <= 120:
        raise ValueError("query must be a non-empty string of at most 120 characters")
    if type(limit) is not int or not 1 <= limit <= 30:
        raise ValueError("limit must be an integer between 1 and 30")
    phrase = query.strip().casefold()
    matching: list[dict[str, Any]] = []
    for op in _read_operations():
        haystack = " ".join(str(op.get(field, "")) for field in
                            ("path", "summary", "operationId"))
        haystack += " " + " ".join(str(t) for t in op.get("tags", []))
        if phrase in haystack.casefold():
            matching.append({
                "path": op["path"],
                "method": "GET",
                "operation_id": op.get("operationId"),
                "summary": op.get("summary"),
                "deprecated": bool(op.get("deprecated", False)),
                "scopes": op.get("scopes", []),
            })
    return {
        "snapshot_status": "STALE_UNVERIFIED",
        "total_matches": len(matching),
        "returned": matching[:limit],
    }


def get_read_endpoint(path: str) -> dict[str, Any]:
    """Exact documented GET path; does not accept URLs or issue HTTP requests."""
    if not isinstance(path, str) or len(path) > 200 or not path.startswith("/"):
        raise ValueError("path must be an exact catalog path beginning with /")
    for op in _read_operations():
        if op.get("path") == path:
            return {
                "snapshot_status": "STALE_UNVERIFIED",
                "method": "GET",
                "path": op["path"],
                "operation_id": op.get("operationId"),
                "summary": op.get("summary"),
                "scopes": op.get("scopes", []),
                "response_codes": op.get("responseCodes", []),
                "tags": op.get("tags", []),
                "deprecated": bool(op.get("deprecated", False)),
                "parameter_count": op.get("parameterCount"),
            }
    raise ValueError("GET endpoint not present in the pinned catalog")

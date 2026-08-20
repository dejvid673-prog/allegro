#!/usr/bin/env python3
"""Validate source registry, JSON schemas/examples and generated API catalog."""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def load_json(path: Path, errors: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # validation script should collect all file failures
        errors.append(f"{path.relative_to(ROOT)}: invalid JSON: {exc}")
        return None


def validate_registry(errors: list[str]) -> None:
    path = ROOT / "sources" / "registry.json"
    data = load_json(path, errors)
    if not isinstance(data, dict) or not isinstance(data.get("sources"), list):
        errors.append("sources/registry.json: missing sources array")
        return
    ids: set[str] = set()
    urls: set[str] = set()
    required = {"id", "title", "url", "owner", "kind", "authority", "areas", "review_cadence", "last_verified", "status", "notes"}
    for index, source in enumerate(data["sources"]):
        label = f"sources/registry.json sources[{index}]"
        if not isinstance(source, dict):
            errors.append(f"{label}: not an object")
            continue
        missing = required - source.keys()
        if missing:
            errors.append(f"{label}: missing {sorted(missing)}")
        source_id = source.get("id")
        if source_id in ids:
            errors.append(f"{label}: duplicate id {source_id}")
        ids.add(source_id)
        url = source.get("url", "")
        if url in urls and source_id != "news-messaging-purchase-problems":
            errors.append(f"{label}: duplicate url {url}")
        urls.add(url)
        if not str(url).startswith("https://"):
            errors.append(f"{label}: URL must use https")
        try:
            date.fromisoformat(source.get("last_verified", ""))
        except ValueError:
            errors.append(f"{label}: invalid last_verified")
        authority = source.get("authority")
        if not isinstance(authority, int) or not 1 <= authority <= 8:
            errors.append(f"{label}: authority must be 1..8")


def validate_json_files(errors: list[str]) -> None:
    for path in sorted((ROOT / "templates").rglob("*.json")):
        load_json(path, errors)
    for path in sorted((ROOT / "sources" / "generated").glob("*.json")):
        load_json(path, errors)


def validate_catalog(errors: list[str]) -> None:
    endpoints_path = ROOT / "sources" / "generated" / "endpoints.json"
    metadata_path = ROOT / "sources" / "generated" / "openapi-metadata.json"
    markdown_path = ROOT / "docs" / "02-api" / "endpoint-catalog.md"
    if not endpoints_path.exists() or not metadata_path.exists() or not markdown_path.exists():
        errors.append("generated API catalog is missing; run scripts/build_api_catalog.py")
        return
    endpoints = load_json(endpoints_path, errors)
    metadata = load_json(metadata_path, errors)
    if isinstance(endpoints, list) and isinstance(metadata, dict):
        if len(endpoints) != metadata.get("operationCount"):
            errors.append("generated operationCount does not match endpoints.json")
        keys = {(item.get("method"), item.get("path")) for item in endpoints if isinstance(item, dict)}
        if len(keys) != len(endpoints):
            errors.append("generated endpoints contain duplicate method/path")


def main() -> int:
    errors: list[str] = []
    validate_registry(errors)
    validate_json_files(errors)
    validate_catalog(errors)
    if errors:
        print("Repository validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Repository validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())

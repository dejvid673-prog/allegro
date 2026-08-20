#!/usr/bin/env python3
"""Generate a deterministic Allegro endpoint catalog from official OpenAPI."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

SOURCE_URL = "https://developer.allegro.pl/swagger.yaml"
HTTP_METHODS = {"get", "put", "post", "delete", "patch", "options", "head", "trace"}


def read_source(path: str | None) -> tuple[bytes, str]:
    if path:
        source_path = Path(path).resolve()
        return source_path.read_bytes(), str(source_path)
    request = urllib.request.Request(
        SOURCE_URL,
        headers={"User-Agent": "RaFishAllegroDocs/1.0 (+https://github.com/dejvid673-prog/allegro)"},
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read(), SOURCE_URL


def scopes_from_security(security: Any) -> list[str]:
    scopes: set[str] = set()
    if not isinstance(security, list):
        return []
    for requirement in security:
        if not isinstance(requirement, dict):
            continue
        for values in requirement.values():
            if isinstance(values, list):
                scopes.update(str(value) for value in values)
    return sorted(scopes)


def build_catalog(spec: dict[str, Any]) -> list[dict[str, Any]]:
    global_security = spec.get("security", [])
    records: list[dict[str, Any]] = []
    for path, path_item in sorted(spec.get("paths", {}).items()):
        if not isinstance(path_item, dict):
            continue
        path_parameters = path_item.get("parameters", [])
        for method, operation in path_item.items():
            if method.lower() not in HTTP_METHODS or not isinstance(operation, dict):
                continue
            operation_security = operation.get("security", global_security)
            responses = operation.get("responses", {})
            parameters = list(path_parameters) + list(operation.get("parameters", []))
            records.append(
                {
                    "method": method.upper(),
                    "path": path,
                    "operationId": operation.get("operationId"),
                    "summary": operation.get("summary", ""),
                    "tags": sorted(operation.get("tags", ["untagged"])),
                    "deprecated": bool(operation.get("deprecated", False)),
                    "scopes": scopes_from_security(operation_security),
                    "responseCodes": sorted(str(code) for code in responses.keys()),
                    "parameterCount": len(parameters),
                }
            )
    return sorted(records, key=lambda item: (item["tags"][0], item["path"], item["method"]))


def markdown_escape(value: Any) -> str:
    return str(value if value is not None else "—").replace("|", "\\|").replace("\n", " ")


def render_markdown(spec: dict[str, Any], catalog: list[dict[str, Any]], sha256: str, fetched_at: str) -> str:
    tag_counts: Counter[str] = Counter()
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in catalog:
        for tag in record["tags"]:
            tag_counts[tag] += 1
        grouped[record["tags"][0]].append(record)

    schemas = spec.get("components", {}).get("schemas", {})
    scopes = sorted({scope for record in catalog for scope in record["scopes"]})
    deprecated = [record for record in catalog if record["deprecated"]]
    lines = [
        "# Katalog endpointów Allegro REST API",
        "",
        "> Plik generowany przez `scripts/build_api_catalog.py`. Nie edytuj ręcznie.",
        "",
        f"- źródło kontraktu: `{SOURCE_URL}`",
        f"- odczytano: `{fetched_at}`",
        f"- SHA-256 źródła: `{sha256}`",
        f"- OpenAPI: `{spec.get('openapi', 'unknown')}`",
        f"- wersja API: `{spec.get('info', {}).get('version', 'unknown')}`",
        f"- paths: **{len(spec.get('paths', {}))}**",
        f"- operations: **{len(catalog)}**",
        f"- schemas: **{len(schemas)}**",
        f"- deprecated operations: **{len(deprecated)}**",
        "",
        "## Zakresy OAuth używane przez operacje",
        "",
    ]
    lines.extend(f"- `{scope}`" for scope in scopes)
    lines.extend(["", "## Liczba operacji według tagu", "", "| Tag | Operacje |", "|---|---:|"])
    lines.extend(f"| {markdown_escape(tag)} | {count} |" for tag, count in sorted(tag_counts.items()))

    for tag, records in sorted(grouped.items()):
        lines.extend(
            [
                "",
                f"## {tag}",
                "",
                "| Metoda | Ścieżka | operationId | Zakresy | Odpowiedzi | Deprecated |",
                "|---|---|---|---|---|---|",
            ]
        )
        for record in records:
            lines.append(
                "| {method} | `{path}` | `{operation}` | {scopes} | {responses} | {deprecated} |".format(
                    method=record["method"],
                    path=markdown_escape(record["path"]),
                    operation=markdown_escape(record["operationId"]),
                    scopes=", ".join(f"`{scope}`" for scope in record["scopes"]) or "—",
                    responses=", ".join(record["responseCodes"]) or "—",
                    deprecated="tak" if record["deprecated"] else "nie",
                )
            )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help="Local Swagger YAML; otherwise download the official file")
    parser.add_argument("--fetched-at", help="ISO timestamp for reproducible generation")
    args = parser.parse_args()

    raw, actual_source = read_source(args.input)
    spec = yaml.safe_load(raw)
    if not isinstance(spec, dict) or "paths" not in spec:
        raise ValueError("Input is not an OpenAPI document with paths")

    fetched_at = args.fetched_at or datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    digest = hashlib.sha256(raw).hexdigest()
    catalog = build_catalog(spec)
    root = Path(__file__).resolve().parents[1]
    generated_dir = root / "sources" / "generated"
    docs_dir = root / "docs" / "02-api"
    generated_dir.mkdir(parents=True, exist_ok=True)
    docs_dir.mkdir(parents=True, exist_ok=True)

    metadata = {
        "schemaVersion": 1,
        "canonicalSource": SOURCE_URL,
        "actualSource": SOURCE_URL if args.input else actual_source,
        "fetchedAt": fetched_at,
        "sha256": digest,
        "openapi": spec.get("openapi"),
        "apiTitle": spec.get("info", {}).get("title"),
        "apiVersion": spec.get("info", {}).get("version"),
        "pathCount": len(spec.get("paths", {})),
        "operationCount": len(catalog),
        "schemaCount": len(spec.get("components", {}).get("schemas", {})),
        "deprecatedOperationCount": sum(1 for item in catalog if item["deprecated"]),
        "servers": spec.get("servers", []),
    }
    (generated_dir / "endpoints.json").write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (generated_dir / "openapi-metadata.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (docs_dir / "endpoint-catalog.md").write_text(render_markdown(spec, catalog, digest, fetched_at), encoding="utf-8")
    print(f"Generated {len(catalog)} operations from {len(spec.get('paths', {}))} paths; sha256={digest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

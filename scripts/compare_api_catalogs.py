"""Compare pinned and candidate Allegro endpoint catalogs without external access.

This detects changes to the generated operation index, NOT to all OpenAPI schemas,
media types, parameters or security definitions. Those require full spec review.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

TRACKED_FIELDS = ("scopes", "deprecated", "responseCodes", "parameterCount", "operationId")


def _index(catalog: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    if not isinstance(catalog, list):
        raise ValueError("Expected JSON list of operations")
    indexed: dict[str, dict[str, Any]] = {}
    for entry in catalog:
        if not isinstance(entry, dict) or "method" not in entry or "path" not in entry:
            raise ValueError("Invalid operation in endpoint catalog")
        key = f"{entry['method'].upper()} {entry['path']}"
        if key in indexed:
            raise ValueError(f"Duplicate operation: {key}")
        indexed[key] = entry
    return indexed


def compare_catalogs(before: list[dict], after: list[dict]) -> dict[str, Any]:
    old, new = _index(before), _index(after)
    added = sorted(new.keys() - old.keys())
    removed = sorted(old.keys() - new.keys())
    changed = []
    for key in sorted(old.keys() & new.keys()):
        differences = {
            field: {"before": old[key].get(field), "after": new[key].get(field)}
            for field in TRACKED_FIELDS
            if old[key].get(field) != new[key].get(field)
        }
        if differences:
            changed.append({"operation": key, "fields": differences})
    return {
        "old_operation_count": len(old),
        "new_operation_count": len(new),
        "added": added,
        "removed": removed,
        "changed": changed,
        "limitations": [
            "Does not inspect full OpenAPI schemas, request/response bodies, media types or parameter definitions.",
            "OpenAPI SHA difference may result from changes outside tracked operation fields.",
        ],
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Allegro OpenAPI candidate — operation-level diff",
        "",
        f"- old operations: **{report['old_operation_count']}**",
        f"- new operations: **{report['new_operation_count']}**",
        f"- added: **{len(report['added'])}**",
        f"- removed: **{len(report['removed'])}**",
        f"- modified tracked fields: **{len(report['changed'])}**",
        "",
        "**HOLD:** This is not full schema compatibility validation. Human review is mandatory.",
        "",
    ]
    for heading, items in (("Added", report["added"]), ("Removed", report["removed"])):
        lines += [f"## {heading}", ""]
        lines += [f"- `{value}`" for value in items[:50]]
        if len(items) > 50:
            lines.append(f"- ... and {len(items) - 50} more (see JSON artifact)")
        if not items:
            lines.append("- none")
        lines.append("")
    lines += ["## Changed tracked fields", ""]
    for item in report["changed"][:50]:
        lines.append(f"- `{item['operation']}`: {', '.join(item['fields'])}")
    if len(report["changed"]) > 50:
        lines.append(f"- ... and {len(report['changed']) - 50} more (see JSON artifact)")
    if not report["changed"]:
        lines.append("- none")
    lines += ["", "## Limitations", ""]
    lines += [f"- {line}" for line in report["limitations"]]
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--before", type=Path, required=True)
    parser.add_argument("--after", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-markdown", type=Path, required=True)
    args = parser.parse_args()
    before = json.loads(args.before.read_text(encoding="utf-8"))
    after = json.loads(args.after.read_text(encoding="utf-8"))
    report = compare_catalogs(before, after)
    args.output_json.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    args.output_markdown.write_text(render_markdown(report), encoding="utf-8")
    print(f"Added={len(report['added'])}; removed={len(report['removed'])}; changed={len(report['changed'])}")


if __name__ == "__main__":
    main()

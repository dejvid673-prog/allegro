#!/usr/bin/env python3
"""Exit non-zero when the official Allegro OpenAPI differs from the recorded snapshot."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.request
from pathlib import Path

SOURCE_URL = "https://developer.allegro.pl/swagger.yaml"
ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help="Use a local Swagger file instead of downloading")
    args = parser.parse_args()

    metadata_path = ROOT / "sources" / "generated" / "openapi-metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    expected = metadata["sha256"]
    if args.input:
        raw = Path(args.input).read_bytes()
    else:
        request = urllib.request.Request(
            SOURCE_URL,
            headers={"User-Agent": "RaFishAllegroDocs/1.0 (+https://github.com/dejvid673-prog/allegro)"},
        )
        with urllib.request.urlopen(request, timeout=60) as response:
            raw = response.read()
    actual = hashlib.sha256(raw).hexdigest()
    if actual != expected:
        print("Allegro OpenAPI changed")
        print(f"recorded: {expected}")
        print(f"current:  {actual}")
        print("Run scripts/build_api_catalog.py and review the generated diff.")
        return 2
    print(f"Allegro OpenAPI is current: {actual}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

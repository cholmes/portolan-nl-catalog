#!/usr/bin/env python3
"""Apply sourced column descriptions from column_descriptions.json.

Each registry entry names the publisher documentation that defines the
columns (researched and content-verified 2026-11-20). The generator writes
the descriptions into the collection's table:columns and links the codebook
with a rel:via text/html link, so the provenance is machine-readable.
Idempotent: re-running reproduces the same bytes (tests/test_generators.py).

Collections generated from data (the vro set) are NOT in the registry; their
descriptions live in make_collections.py's per-collection config instead.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from tools.lib import paths, stac

CATALOG = Path(str(paths.CATALOG))
REGISTRY = Path(__file__).with_name("column_descriptions.json")


def main() -> int:
    registry = json.loads(REGISTRY.read_text())
    for rel, entry in registry.items():
        p = CATALOG / rel / "collection.json"
        doc = json.loads(p.read_text())
        cols = doc.get("table:columns") or []
        names = {c["name"] for c in cols}
        applied = 0
        for c in cols:
            desc = entry["columns"].get(c["name"])
            if desc and c.get("description") != desc:
                c["description"] = desc
                applied += 1
        # the registry may define more fields than one collection carries
        # (shared INSPIRE definitions); report only columns still undescribed
        missing = [c["name"] for c in cols if not c.get("description")]
        src = entry["source"]
        title = f"Column definitions: {src['title']}"
        links = doc.setdefault("links", [])
        if not any(l.get("href") == src["url"] for l in links if isinstance(l, dict)):
            after = max((i for i, l in enumerate(links)
                         if isinstance(l, dict) and l.get("rel") == "via"),
                        default=len(links) - 1)
            links.insert(after + 1, stac.link("via", src["url"], "text/html", title))
        stac.write_json(p, doc)
        state = f"{applied} set" if applied else "up to date"
        print(f"  {rel}: {state}; {len(missing)} still undescribed"
              + (f" ({', '.join(missing[:6])})" if missing else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())

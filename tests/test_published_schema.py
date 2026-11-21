"""Check that every declared column exists in the published parquet.

`table:columns` is the schema a reader plans a query against. A name that
drifts from the published file sends that reader to a column that is not
there, and the collection's own documented queries drift with it. A November
2026 run found 14 of 33 collections out of step, most of them a `geometry`
entry over a file whose geometry column is `geom`.

The gate reads parquet footers only, so it is cheap next to the documented
queries. It runs against https://data.source.coop, so it needs the live flag.

SKIPs (exit 0) unless PORTOLAN_LIVE=1. Requires the duckdb package.

Run: PORTOLAN_LIVE=1 python3 tests/test_published_schema.py
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CATALOG = REPO / "catalog"
PUB = "https://data.source.coop/cholmes/portolan-nl"
HTTP_TIMEOUT = 120  # seconds; a footer read is small

# Columns a reader never selects by name. GeoParquet writes the covering
# column itself, and the CLI adds the partition key, so neither belongs in
# table:columns and neither is a drift signal.
IGNORED = {"bbox", "geom_bbox", "geometry_bbox", "kdtree_cell"}


def data_parquet_urls(rel: str, doc: dict) -> list[str]:
    urls = []
    for asset in (doc.get("assets") or {}).values():
        if not isinstance(asset, dict):
            continue
        if "data" not in (asset.get("roles") or []):
            continue
        if asset.get("type") != "application/vnd.apache.parquet":
            continue
        href = asset.get("href") or ""
        url = f"{PUB}/{rel}/{href[2:]}" if href.startswith("./") else href
        if url and url not in urls:
            urls.append(url)
    return urls


def main() -> int:
    if os.environ.get("PORTOLAN_LIVE") != "1":
        print("SKIP: set PORTOLAN_LIVE=1 to run the published-schema check")
        return 0
    try:
        import duckdb
    except ImportError:
        print("FAIL: the duckdb package is required for the live checks")
        return 1

    con = duckdb.connect()
    con.execute(f"SET http_timeout={HTTP_TIMEOUT * 1000}")

    failures: list[str] = []
    warnings: list[str] = []
    checked = unreadable = 0
    for path in sorted(CATALOG.rglob("collection.json")):
        rel = path.parent.relative_to(CATALOG).as_posix()
        doc = json.loads(path.read_text())
        declared = [c["name"] for c in doc.get("table:columns", [])]
        if not declared:
            continue
        urls = data_parquet_urls(rel, doc)
        if not urls:
            # The items carry the data; their own metadata declares the schema.
            continue
        # A collection can publish several data assets with different
        # schemas, so the declared set is checked against their union.
        actual: set[str] = set()
        failed = False
        for url in urls:
            try:
                rows = con.execute(
                    f"DESCRIBE SELECT * FROM read_parquet('{url}')"
                ).fetchall()
            except Exception as e:  # noqa: BLE001 - report, not crash
                unreadable += 1
                failures.append(f"{rel}: cannot read {url}: {type(e).__name__}: {e}")
                failed = True
                break
            actual |= {r[0] for r in rows}
        if failed:
            continue
        checked += 1
        # A declared column the file does not have is wrong: it sends a
        # reader to a column that is not there. A column the file has and
        # the metadata omits is incomplete, not wrong, so it warns. Closing
        # that gap needs a sourced description per column, which the
        # never-invent rule puts outside a schema pass.
        missing = [c for c in declared if c not in actual and c not in IGNORED]
        extra = [c for c in actual if c not in declared and c not in IGNORED]
        if missing:
            failures.append(f"{rel}: declared but not in the file: {missing}")
        if extra:
            warnings.append(f"{rel}: in the file but not declared: {extra}")

    for w in warnings:
        print(f"WARN {w}")
    for f in failures:
        print(f"FAIL {f}")
    if failures:
        print(f"\n{len(failures)} failure(s), {len(warnings)} warning(s); "
              f"{checked} collection(s) checked, {unreadable} unreadable")
        return 1
    print(f"OK: every declared column exists in the published parquet across "
          f"{checked} collection(s); {len(warnings)} collection(s) declare "
          f"fewer columns than the file holds")
    return 0


if __name__ == "__main__":
    sys.exit(main())

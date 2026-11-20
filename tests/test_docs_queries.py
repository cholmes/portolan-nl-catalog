"""Run the documented queries and claim checks against the published catalog.

Two gates, both against https://data.source.coop (the live bucket), so this
is the scheduled companion to the metadata-only PR gates:

1. Claim checks: every collection's table:row_count equals the row count in
   the published parquet footers of its data assets. This is the check that
   found six doubled counts in November 2026.
2. Documented queries: every self-contained ```sql block in a committed
   README.md or AGENTS.md that reads a published URL runs in DuckDB and
   returns without error. Python blocks that import only duckdb/pandas run
   the same way. Everything else is listed as skipped, not silently ignored.

SKIPs (exit 0) unless PORTOLAN_LIVE=1, so the local zero-setup suite is
unaffected; the scheduled workflow sets it. Requires the duckdb package.

Run: PORTOLAN_LIVE=1 python3 tests/test_docs_queries.py
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CATALOG = REPO / "catalog"
PUB = "https://data.source.coop/cholmes/portolan-nl"
QUERY_TIMEOUT = 240  # seconds; the cross-year brp scans take minutes

# Collections whose table:row_count deliberately does not equal the sum of
# all parquet data assets. Each entry names the assets the count covers and
# why. Grow this only with a reason.
ROW_COUNT_EXCEPTIONS = {
    "cbs/bevolkingsspreiding": {
        "covers": ["grid", "nuts2", "lau"],
        "why": "row_count counts features; bevolkingsspreiding.parquet is the"
               " long-format observation table (many rows per feature)",
    },
    "tudelft/3dbag": {
        "covers": ["lod13-data"],
        "why": "row_count counts the primary LoD 1.3 layer; pand-data is an"
               " alternative per-building aggregation of the same buildings",
    },
}


def collections():
    for p in sorted(CATALOG.rglob("collection.json")):
        yield p.parent.relative_to(CATALOG).as_posix(), json.loads(p.read_text())


def check_row_counts(duckdb) -> list[str]:
    con = duckdb.connect()
    bad = []
    for rel, doc in collections():
        want = doc.get("table:row_count")
        if want is None:
            continue
        exc = ROW_COUNT_EXCEPTIONS.get(rel)
        hrefs = []
        for key, a in (doc.get("assets") or {}).items():
            if not isinstance(a, dict) or "data" not in (a.get("roles") or []):
                continue
            if a.get("type") != "application/vnd.apache.parquet":
                continue
            if exc and key not in exc["covers"]:
                continue
            if a["href"] not in hrefs:
                hrefs.append(a["href"])
        if not hrefs:
            # items hold the data (brp); the per-item assets carry their own
            # table:row_count, checked through the documented queries instead.
            continue
        total = 0
        for href in hrefs:
            url = f"{PUB}/{rel}/{href[2:]}" if href.startswith("./") else href
            n = con.execute(
                f"SELECT SUM(num_rows) FROM parquet_file_metadata('{url}')"
            ).fetchone()[0]
            total += int(n or 0)
        if total != want:
            bad.append(f"{rel}: table:row_count {want} != {total} in the published parquet")
    return bad


FENCE = re.compile(r"```(sql|python)\n(.*?)```", re.S)


def doc_blocks():
    for p in sorted(CATALOG.rglob("*.md")):
        text = p.read_text(encoding="utf-8", errors="replace")
        for lang, body in FENCE.findall(text):
            if "data.source.coop/cholmes/portolan-nl" not in body \
                    and "us-west-2.opendata.source.coop/cholmes/portolan-nl" not in body:
                continue
            yield p.relative_to(CATALOG).as_posix(), lang, body


def run_sql(duckdb, body: str) -> str | None:
    con = duckdb.connect()
    con.execute(f"SET http_timeout={QUERY_TIMEOUT * 1000}")
    try:
        for stmt in [s.strip() for s in body.split(";") if s.strip()]:
            con.execute(stmt)
    except Exception as e:  # noqa: BLE001 - report, do not crash the gate
        return f"{type(e).__name__}: {e}"
    return None


ALLOWED_IMPORTS = {"duckdb", "pandas", "json", "io", "textwrap"}


def run_python(body: str) -> str | None:
    imports = set(re.findall(r"^\s*(?:import|from)\s+(\w+)", body, re.M))
    if not imports <= ALLOWED_IMPORTS:
        return "SKIP"  # geopandas/matplotlib examples need heavier deps
    r = subprocess.run([sys.executable, "-c", body], capture_output=True,
                       text=True, timeout=QUERY_TIMEOUT)
    if r.returncode != 0:
        return r.stderr.strip()[-400:]
    return None


def main() -> int:
    if os.environ.get("PORTOLAN_LIVE") != "1":
        print("SKIP: set PORTOLAN_LIVE=1 to run the live documented-query checks")
        return 0
    try:
        import duckdb
    except ImportError:
        print("FAIL: the duckdb package is required for the live checks")
        return 1

    failures = check_row_counts(duckdb)
    ran = skipped = 0
    for where, lang, body in doc_blocks():
        try:
            err = run_sql(duckdb, body) if lang == "sql" else run_python(body)
        except subprocess.TimeoutExpired:
            err = f"timed out after {QUERY_TIMEOUT}s"
        if err == "SKIP":
            skipped += 1
            print(f"skip  {where} ({lang}: needs extra dependencies)")
            continue
        ran += 1
        if err:
            failures.append(f"{where} ({lang}): {err}")

    for f in failures:
        print(f"FAIL {f}")
    if failures:
        print(f"\n{len(failures)} failure(s); {ran} blocks ran, {skipped} skipped")
        return 1
    print(f"OK: row counts match the published parquet; "
          f"{ran} documented blocks ran clean, {skipped} skipped (heavy deps)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

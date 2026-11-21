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

import concurrent.futures as cf
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CATALOG = REPO / "catalog"
PUB = "https://data.source.coop/cholmes/portolan-nl"
QUERY_TIMEOUT = 300  # seconds per block; the cross-year brp scans take minutes
# The blocks run one at a time. A concurrent run truncates range reads from the
# bucket: a November 2026 run with 4 workers reported 25 ZSTD decompression
# failures and 12 thrift errors, and every one of those files read clean
# sequentially. Raise this only with evidence that the bucket holds up.
WORKERS = 1

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


# A document's sql blocks run in order in one session, which is how a reader
# works down the page. Each document opens with a setup block that installs the
# spatial extension, so the session loads it first: a later block calls ST_Area
# without repeating the install.
#
# The session runs in a child process. An in-process duckdb call cannot be
# interrupted: a worker that blocks on a stalled read from the bucket never
# returns, and ThreadPoolExecutor.map then waits for it forever. A run in
# November 2026 sat for 11 hours this way. A child process accepts a timeout
# and the parent kills it.
SQL_RUNNER = """
import sys
import duckdb
blocks = sys.stdin.read().split("\\x00")
con = duckdb.connect()
con.execute("SET http_timeout=" + sys.argv[1])
try:
    con.execute("INSTALL spatial; LOAD spatial;")
except Exception:
    pass  # a document that needs no geometry still runs
for i, body in enumerate(blocks):
    for stmt in [s.strip() for s in body.split(";") if s.strip()]:
        try:
            con.execute(stmt)
        except Exception as e:
            sys.stderr.write("block %d: %s: %s" % (i + 1, type(e).__name__, e))
            raise SystemExit(1)
"""


def run_sql(bodies: list[str]) -> str | None:
    """Run one document's sql blocks in order. Report the first failure."""
    r = subprocess.run([sys.executable, "-c", SQL_RUNNER, str(QUERY_TIMEOUT * 1000)],
                       input="\x00".join(bodies), capture_output=True, text=True,
                       timeout=QUERY_TIMEOUT)
    if r.returncode != 0:
        return r.stderr.strip()[-400:]
    return None


ALLOWED_IMPORTS = {"duckdb", "pandas", "json", "io", "textwrap"}


def runnable_python(bodies: list[str]) -> tuple[list[str], int]:
    """The blocks this gate can run, and the count it cannot.

    A geopandas or matplotlib example needs heavier dependencies than the
    gate installs, so it is reported as skipped rather than run.
    """
    keep, skipped = [], 0
    for body in bodies:
        imports = set(re.findall(r"^\s*(?:import|from)\s+(\w+)", body, re.M))
        if imports <= ALLOWED_IMPORTS:
            keep.append(body)
        else:
            skipped += 1
    return keep, skipped


def run_python(bodies: list[str]) -> str | None:
    """Run one document's python blocks in order, as one script.

    A later block uses the connection an earlier one opened, the same way a
    reader works down the page, so the blocks share a process.
    """
    if not bodies:
        return "SKIP"
    r = subprocess.run([sys.executable, "-c", "\n".join(bodies)],
                       capture_output=True, text=True, timeout=QUERY_TIMEOUT)
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

    started = time.monotonic()
    failures = check_row_counts(duckdb)
    print(f"row-count claim checks: {len(failures)} failure(s) "
          f"in {time.monotonic() - started:.0f}s")

    # One job per document for sql, one job per block for python. A python
    # block is a standalone script, so it carries its own setup.
    sql_by_doc: dict[str, list[str]] = {}
    py_by_doc: dict[str, list[str]] = {}
    for where, lang, body in doc_blocks():
        bucket = sql_by_doc if lang == "sql" else py_by_doc
        bucket.setdefault(where, []).append(body)

    skipped_heavy = 0
    jobs = [(w, "sql", b) for w, b in sql_by_doc.items()]
    for where, bodies in py_by_doc.items():
        keep, n = runnable_python(bodies)
        skipped_heavy += n
        if keep:
            jobs.append((where, "python", keep))

    def run_one(job):
        where, lang, body = job
        try:
            return where, lang, (run_sql(body) if lang == "sql"
                                 else run_python(body))
        except subprocess.TimeoutExpired:
            return where, lang, f"timed out after {QUERY_TIMEOUT}s"
        except Exception as e:  # noqa: BLE001 - a crashed worker is a failure
            return where, lang, f"{type(e).__name__}: {e}"

    ran = 0
    skipped = skipped_heavy
    t0 = time.monotonic()
    with cf.ThreadPoolExecutor(WORKERS) as pool:
        for where, lang, err in pool.map(run_one, jobs):
            if err == "SKIP":
                skipped += 1
                continue
            ran += 1
            if err:
                failures.append(f"{where} ({lang}): {err}")
    elapsed = time.monotonic() - t0

    for f in failures:
        print(f"FAIL {f}")
    if failures:
        print(f"\n{len(failures)} failure(s); {ran} job(s) ran in {elapsed:.0f}s, "
              f"{skipped} skipped")
        return 1
    print(f"OK: row counts match the published parquet; {ran} documented job(s) "
          f"ran clean in {elapsed:.0f}s, {skipped} skipped (heavy deps)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

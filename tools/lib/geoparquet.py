"""Facts read out of a GeoParquet file.

Two levels, deliberately. geo_meta and arrow_columns read only the Parquet
footer, which is cheap even on a multi-gigabyte file. top_values and
distinct_count scan a column and are not; callers that only need the schema
should not pay for a scan.

Note on scope: the design spec expected this module to be shared by
make_collections and generate_items. It is not -- generate_items works from
hardcoded per-year stats and never opens a parquet. What is genuinely
duplicated is the "top N values by frequency" query, which appears in
make_extra_styles, make_point_legends and make_styles_thumbnails.
"""
from __future__ import annotations
import json

_TYPE_MAP = {"int64": "int64", "int32": "int32", "double": "float64",
             "string": "string", "large_string": "string", "binary": "binary"}


def geo_meta(parquet) -> tuple[str, str, int | None]:
    """(primary_geometry_column, geometry_type, epsg) from the 'geo' footer key."""
    import pyarrow.parquet as pq
    geo = json.loads(pq.read_metadata(parquet).metadata[b"geo"].decode())
    pc = geo["primary_column"]
    col = geo["columns"][pc]
    gtype = col.get("geometry_types", ["Unknown"])
    crs = col.get("crs") or {}
    cid = crs.get("id") if isinstance(crs, dict) else None
    epsg = int(cid["code"]) if cid and str(cid.get("authority", "")).upper() == "EPSG" else None
    return pc, (gtype[0] if gtype else "Unknown"), epsg


def arrow_columns(parquet) -> list[tuple[str, str]]:
    """(name, stac_table_type) for every column, in file order."""
    import pyarrow.parquet as pq
    return [(f.name, _TYPE_MAP.get(str(f.type), str(f.type))) for f in pq.read_schema(parquet)]


def top_values(parquet, field: str, n: int = 8) -> list:
    """The n most frequent non-null values of `field`, most frequent first.

    The value itself is the tie-break. Without it this is nondeterministic and
    the generators are not reproducible: bodemverontreiniging_besluit, for one,
    has five distinct delivery_accountable_party values tied at 3 rows with the
    top-8 cutoff falling inside that group, so consecutive runs disagree about
    which two make the list.
    """
    import duckdb
    return [r[0] for r in duckdb.connect().execute(
        f"SELECT {field} FROM read_parquet('{parquet}') WHERE {field} IS NOT NULL "
        f"GROUP BY 1 ORDER BY COUNT(*) DESC, {field} LIMIT {n}").fetchall()]


def top_map(parquet, field: str, palette: list[str], n: int = 8) -> dict:
    """{value: color} for the n most frequent values, cycling through palette."""
    return {v: palette[i % len(palette)] for i, v in enumerate(top_values(parquet, field, n))}


def distinct_count(parquet, field: str) -> int:
    import duckdb
    return duckdb.connect().execute(
        f"SELECT COUNT(DISTINCT {field}) FROM read_parquet('{parquet}')").fetchone()[0]

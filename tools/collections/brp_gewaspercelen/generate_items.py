#!/usr/bin/env python3
"""Generate per-year STAC Item JSON files for brp_gewaspercelen.

Each year (one per BRP edition) becomes a STAC item with assets pointing at:
- the year's GeoParquet
- the year's PMTiles (if present)
- the year's source file (GPKG for 2020+, FGDB .zip for ≤2019)
- per-year MapLibre styles under styles/years/YYYY/

Item bbox/geometry uses the WGS84 footprint computed from the parquet.
Run after parquet files and bbox stats are available.
"""

import json
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.lib import paths, stac

ROOT = paths.CATALOG / "rvo" / "brp_gewaspercelen"

# Per-year stats (computed with DuckDB ST_Transform from the per-year parquet).
# Historical-year stats (2009–2019) are filled in after the normalization pass completes;
# until then, only the listed years generate items.
YEAR_STATS: dict[int, dict] = {
    2009: {"features": 819146,  "bbox": [3.3597, 50.7504, 7.2245, 53.4954]},
    2010: {"features": 782837,  "bbox": [3.3597, 50.7504, 7.2244, 53.4954]},
    2011: {"features": 779674,  "bbox": [3.3597, 50.7504, 7.2244, 53.4954]},
    2012: {"features": 772865,  "bbox": [3.3597, 50.7504, 7.2244, 53.4954]},
    2013: {"features": 762725,  "bbox": [3.3597, 50.7504, 7.2244, 53.4954]},
    2014: {"features": 765006,  "bbox": [3.3597, 50.7504, 7.2244, 53.4954]},
    2015: {"features": 790930,  "bbox": [3.3597, 50.7504, 7.2244, 53.4954]},
    2016: {"features": 786572,  "bbox": [3.3597, 50.7504, 7.2244, 53.4959]},
    2017: {"features": 785710,  "bbox": [3.3597, 50.7504, 7.2244, 53.4959]},
    2018: {"features": 774822,  "bbox": [3.3597, 50.7504, 7.2244, 53.4970]},
    2019: {"features": 772565,  "bbox": [3.3597, 50.7504, 7.2244, 53.4970]},
    2020: {"features": 773139,  "bbox": [3.3597, 50.7504, 7.2244, 53.4970]},
    2021: {"features": 772539,  "bbox": [3.3597, 50.7504, 7.2244, 53.4970]},
    2022: {"features": 758504,  "bbox": [3.3597, 50.7504, 7.2244, 53.4970]},
    2023: {"features": 2588592, "bbox": [3.3597, 50.7504, 7.2244, 53.4970]},
    2024: {"features": 2493631, "bbox": [3.3597, 50.7504, 7.2244, 53.4988]},
    2025: {"features": 2331084, "bbox": [3.3597, 50.7504, 7.2244, 53.4989]},
}

# Source-file metadata. Distinguishes new (PDOK definitive GPKG, no transformation)
# from historical (Esri File Geodatabase in a zip, schema normalized).
NEW_YEARS = (2020, 2021, 2022, 2023, 2024, 2025)
HISTORICAL_YEARS = tuple(range(2009, 2020))  # 2009..2019

# Which years publish PMTiles. Declared, not probed: this used to test whether
# the .pmtiles file was on disk, which made the generator depend on the data
# working directory. Anywhere that directory is absent -- CI, a fresh clone --
# every item silently lost its tiles asset and its rel:pmtiles link. What an
# item advertises is a property of the published catalog, not of which files
# happen to sit on the machine running the generator.
YEARS_WITH_PMTILES = frozenset(range(2009, 2026))

SOURCES: dict[int, dict] = {}
for yr in NEW_YEARS:
    SOURCES[yr] = {
        "filename": f"brpgewaspercelen_definitief_{yr}.gpkg",
        "type": "application/geopackage+sqlite3",
        "title": f"Source GeoPackage (PDOK definitive {yr})",
        "description": (
            f"Original GeoPackage download from PDOK, used to derive the GeoParquet "
            f"and PMTiles for {yr}. EPSG:28992. **No schema transformation** — the "
            "GeoParquet columns are byte-equivalent to the GPKG."
        ),
        "via_url": f"https://service.pdok.nl/rvo/gewaspercelen/atom/downloads/brpgewaspercelen_definitief_{yr}.gpkg",
    }
for yr in HISTORICAL_YEARS:
    SOURCES[yr] = {
        "filename": f"brpgewaspercelen_definitief_{yr}.zip",
        "type": "application/zip",
        "title": f"Source Esri File Geodatabase, zipped (PDOK definitive {yr})",
        "description": (
            f"Original PDOK distribution for {yr}: an Esri File Geodatabase (.gdb) "
            "inside a zip archive. Unzipped contents are readable with GDAL/ogr2ogr "
            "(`OpenFileGDB` driver) or ArcGIS. The corresponding GeoParquet in this "
            "collection is **schema-normalized** from this source:\n\n"
            "- `OGC_FID` → `id`\n"
            "- `CAT_GEWASCATEGORIE` → `category`\n"
            "- `GWS_GEWAS` → `gewas`\n"
            "- `GWS_GEWASCODE` (varchar) → `gewascode` (int32)\n"
            f"- added `jaar = {yr}` (from the filename)\n"
            "- added `status = 'Definitief'` (constant for this collection)\n"
            "- dropped `Shape_Length`, `Shape_Area`, `GEOMETRIE_Length`, "
            "`GEOMETRIE_Area` (recomputable with `ST_Length` / `ST_Area`)\n\n"
            "Geometry is kept in EPSG:28992. See README.md for the full normalization pipeline."
        ),
        "via_url": f"https://service.pdok.nl/rvo/gewaspercelen/atom/downloads/brpgewaspercelen_definitief_{yr}.zip",
    }

STYLES = [
    ("default", "Default", "Agricultural landscape — green for grassland, yellow for arable."),
    ("by-category", "By Crop Category", "Distinct colors for each broad crop category."),
    ("by-crop", "By Crop Type", "Individual colors for the most common specific crops."),
    ("landscape-elements", "Landscape Elements", "Highlights ditches, hedgerows, tree rows, and ponds."),
]

# table:columns. The schema is identical across every year; only the column
# *descriptions* differ, because the historical years are normalized from an Esri
# File Geodatabase while 2020+ come straight from PDOK's GeoPackage. Keyed on
# which of those two sources the year came from.
_COLUMN_TYPES = [("id", "int64"), ("category", "string"), ("gewas", "string"),
                 ("gewascode", "int32"), ("jaar", "int32"), ("status", "string"),
                 ("geom", "binary")]

_GEOM_DESC = ("Parcel boundary polygon in EPSG:28992 (Amersfoort / RD New), WKB-encoded.")

# Landschapselement entered the BRP in 2023, so only earlier years carry the note
# saying the category is absent. 2023 onward legitimately have it.
LANDSCAPE_ELEMENT_FROM = 2023
_CATEGORY_NOTE = " Note: Landschapselement was added in 2023; absent in this year."

COLUMN_DESCRIPTIONS = {
    "gpkg": {   # 2020+, no schema transformation
        "id": "Feature ID. Matches the source GeoPackage.",
        "category": ("Broad crop category (e.g. Grasland, Bouwland, Landschapselement, "
                     "Natuurterrein, Braakland, Overige)."),
        "gewas": "Specific crop name (e.g. Grasland blijvend, Aardappelen consumptie, Mais snij-).",
        "gewascode": "Numeric crop code identifying the specific crop type.",
        "jaar": "Registration year.",
        "status": "Registration status — always 'Definitief' in this collection.",
        "geom": _GEOM_DESC,
    },
    "fgdb": {   # 2009-2019, schema-normalized from the Esri File Geodatabase
        "id": "Feature ID, mapped from the source FGDB's `OGC_FID`.",
        "category": "Broad crop category, mapped from FGDB field `CAT_GEWASCATEGORIE`.",
        "gewas": "Specific crop name, mapped from FGDB field `GWS_GEWAS`.",
        "gewascode": ("Numeric crop code, mapped from FGDB field `GWS_GEWASCODE` "
                      "(cast from varchar to int32)."),
        "jaar": ("Registration year — synthesized from the source filename (not present "
                 "in the original FGDB)."),
        "status": ("Registration status — set to 'Definitief' (constant; not present in "
                   "the original FGDB)."),
        "geom": _GEOM_DESC,
    },
}


def table_columns(year: int) -> list[dict]:
    descs = dict(COLUMN_DESCRIPTIONS["gpkg" if year in NEW_YEARS else "fgdb"])
    if year < LANDSCAPE_ELEMENT_FROM:
        descs["category"] += _CATEGORY_NOTE
    return [{"name": n, "type": t, "description": descs[n]} for n, t in _COLUMN_TYPES]

STAC_EXTENSIONS = [
    "https://stac-extensions.github.io/table/v1.2.0/schema.json",
    "https://stac-extensions.github.io/vector/v0.1.0/schema.json",
    "https://stac-extensions.github.io/web-map-links/v1.3.0/schema.json",
    "https://stac-extensions.github.io/projection/v2.0.0/schema.json",
]


def bbox_to_polygon(bbox: list[float]) -> dict:
    x0, y0, x1, y1 = bbox
    return {
        "type": "Polygon",
        "coordinates": [
            [[x0, y0], [x1, y0], [x1, y1], [x0, y1], [x0, y0]],
        ],
    }


def build_item(year: int) -> dict:
    """Build the STAC Item that lives at <root>/YYYY/brp_gewaspercelen_YYYY.json.

    All asset hrefs are bare filenames relative to the year directory, so the year
    folder is self-contained and can be moved or browsed in isolation.
    """
    stats = YEAR_STATS[year]
    src = SOURCES[year]
    bbox = stats["bbox"]
    parquet = f"brp_gewaspercelen_{year}.parquet"
    pmtiles = f"brp_gewaspercelen_{year}.pmtiles"
    has_pmtiles = year in YEARS_WITH_PMTILES

    assets: dict[str, dict] = {
        "data": {
            "href": f"./{parquet}",
            "type": "application/vnd.apache.parquet",
            "title": f"BRP Gewaspercelen {year} (GeoParquet)",
            "description": (
                f"{stats['features']:,} agricultural parcel polygons for the {year} "
                "BRP definitive edition. EPSG:28992 (Amersfoort / RD New), zstd-"
                "compressed, sorted by bbox per OGC Best Practices for Distributing "
                "GeoParquet."
            ),
            "table:row_count": stats["features"],
            "roles": ["data"],
        },
        "source": {
            "href": f"./{src['filename']}",
            "type": src["type"],
            "title": src["title"],
            "description": src["description"],
            "roles": ["source"],
        },
    }
    if has_pmtiles:
        assets["pmtiles"] = {
            "href": f"./{pmtiles}",
            "type": "application/vnd.pmtiles",
            "title": f"BRP Gewaspercelen {year} (vector tiles)",
            "roles": ["visual"],
        }
    for style_id, title, desc in STYLES:
        assets[f"styles/{style_id}"] = {
            "href": f"./styles/{style_id}.json",
            "type": "application/json",
            "title": f"{title} ({year})",
            "description": (
                f"{desc} Points at ./brp_gewaspercelen_{year}.pmtiles. Generated from "
                "the canonical base style in ../styles/ via ../scripts/regen_year_styles.py."
            ),
            "roles": ["style"],
        }
    # README.md and llms.txt are reached through rel:describedby and rel:llms links
    # below, not as assets. Assets on an item are the data it describes.

    rel_dir = f"rvo/brp_gewaspercelen/{year}"
    coll_title = "BRP Gewaspercelen (Agricultural Crop Parcels)"
    links = [
        stac.root_link(3),
        stac.self_link(f"{rel_dir}/brp_gewaspercelen_{year}.json"),
        stac.link("collection", "../collection.json", stac.JSON, coll_title),
        stac.parent_link("../collection.json", coll_title),
        stac.link("via", src["via_url"], src["type"], f"PDOK source download ({year})"),
    ]
    if has_pmtiles:
        links.append(stac.link("pmtiles", f"{paths.DATA_BASE}/{rel_dir}/{pmtiles}",
                               "application/vnd.pmtiles"))
    links.append(stac.link("llms", "./llms.txt", "text/markdown", "Agent/LLM usage guide"))
    links.append(stac.link("describedby", f"{paths.SRC_BASE}/{rel_dir}/README.md",
                           "text/html", f"BRP Gewaspercelen {year} documentation"))

    return {
        "type": "Feature",
        "stac_version": "1.1.0",
        "stac_extensions": STAC_EXTENSIONS,
        "id": f"brp_gewaspercelen_{year}",
        "collection": "brp_gewaspercelen",
        "geometry": bbox_to_polygon(bbox),
        "bbox": bbox,
        "properties": {
            "datetime": f"{year}-05-15T00:00:00Z",
            "start_datetime": f"{year}-05-15T00:00:00Z",
            "end_datetime": f"{year}-05-15T00:00:00Z",
            "title": f"BRP Gewaspercelen {year}",
            "description": (
                f"Definitive crop parcel registration for {year}. The BRP is an annual "
                "snapshot reflecting what farmers register each May 15 (the CAP deadline); "
                "this 'definitief' edition is finalized after verification. Published by "
                "RVO via PDOK."
            ),
            "proj:code": "EPSG:28992",
            "table:row_count": stats["features"],
            "table:primary_geometry": "geom",
            "geoparquet:geometry_type": "Polygon",
            "geoparquet:feature_count": stats["features"],
            "vector:geometry_types": ["Polygon"],
            "portolan:styles": [f"styles/{sid}" for sid, _, _ in STYLES],
            "table:columns": table_columns(year),
        },
        "assets": assets,
        "links": links,
    }


def main() -> None:
    for year in YEAR_STATS:
        year_dir = ROOT / str(year)
        year_dir.mkdir(parents=True, exist_ok=True)
        item = build_item(year)
        out = year_dir / f"brp_gewaspercelen_{year}.json"
        stac.write_json(out, item)
        print(f"wrote {year}/{out.name} ({item['properties']['table:row_count']:,} rows)")


if __name__ == "__main__":
    main()

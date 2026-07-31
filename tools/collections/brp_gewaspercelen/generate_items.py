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

ROOT = Path(__file__).resolve().parent.parent

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
    pmtiles_path = ROOT / str(year) / pmtiles

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
    if pmtiles_path.exists():
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
    assets["readme"] = {
        "href": "./README.md",
        "type": "text/markdown",
        "title": f"BRP Gewaspercelen {year} — README",
        "roles": ["metadata"],
    }
    assets["llms"] = {
        "href": "./llms.txt",
        "type": "text/markdown",
        "title": f"BRP Gewaspercelen {year} — agent/LLM usage guide",
        "roles": ["metadata"],
    }

    links = [
        {
            "rel": "root",
            "href": "../../../catalog.json",
            "type": "application/json",
            "title": "Portolan NL — Cloud-Native Dutch Geodata",
        },
        {
            "rel": "self",
            "href": (
                "https://data.source.coop/cholmes/portolan-nl/rvo/brp_gewaspercelen/"
                f"{year}/brp_gewaspercelen_{year}.json"
            ),
            "type": "application/json",
        },
        {
            "rel": "collection",
            "href": "../collection.json",
            "type": "application/json",
            "title": "BRP Gewaspercelen (Agricultural Crop Parcels)",
        },
        {
            "rel": "parent",
            "href": "../collection.json",
            "type": "application/json",
            "title": "BRP Gewaspercelen (Agricultural Crop Parcels)",
        },
        {
            "rel": "via",
            "href": src["via_url"],
            "type": src["type"],
            "title": f"PDOK source download ({year})",
        },
    ]
    if pmtiles_path.exists():
        links.append({
            "rel": "pmtiles",
            "href": (
                "https://data.source.coop/cholmes/portolan-nl/rvo/brp_gewaspercelen/"
                f"{year}/{pmtiles}"
            ),
            "type": "application/vnd.pmtiles",
        })

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
        out.write_text(json.dumps(item, indent=2, ensure_ascii=False) + "\n")
        print(f"wrote {year}/{out.name} ({item['properties']['table:row_count']:,} rows)")


if __name__ == "__main__":
    main()

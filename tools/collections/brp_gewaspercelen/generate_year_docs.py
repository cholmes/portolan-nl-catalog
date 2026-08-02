#!/usr/bin/env python3
"""Generate per-year README.md and AGENTS.md for each BRP year folder.

Each year subdirectory is intended to stand alone — someone can download just
YYYY/ and have everything they need to use that year's data. README and AGENTS.md
both link back to the parent collection for cross-year context.
"""

import json
from pathlib import Path

# Reuse the same year stats as generate_items.py — keep the two scripts aligned.
from generate_items import YEAR_STATS, SOURCES, NEW_YEARS, HISTORICAL_YEARS

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.lib import paths, docs

ROOT = paths.CATALOG / "rvo" / "brp_gewaspercelen"

PARENT_BASE_URL = docs.collection_url("rvo/brp_gewaspercelen")


def normalization_notes(year: int) -> str:
    if year in NEW_YEARS:
        return (
            "**Source format:** PDOK GeoPackage (`brpgewaspercelen_definitief_"
            f"{year}.gpkg`). The GeoParquet preserves the source schema "
            "byte-for-byte — no field renames or value transformations."
        )
    return (
        "**Source format:** PDOK Esri File Geodatabase, distributed as a zip "
        f"archive (`brpgewaspercelen_definitief_{year}.zip`). The GeoParquet is "
        "**schema-normalized** from the upstream FGDB:\n\n"
        "- `OGC_FID` → `id`\n"
        "- `CAT_GEWASCATEGORIE` → `category`\n"
        "- `GWS_GEWAS` → `gewas`\n"
        "- `GWS_GEWASCODE` (varchar) → `gewascode` (int32)\n"
        f"- added `jaar = {year}` from the filename\n"
        "- added `status = 'Definitief'` (constant)\n"
        "- dropped `Shape_Length`/`Shape_Area`/`GEOMETRIE_Length`/`GEOMETRIE_Area`\n\n"
        "Geometry stays in EPSG:28992."
    )


def landscape_note(year: int) -> str:
    if year < 2023:
        return (
            "**Landscape elements:** the `Landschapselement` category was added "
            f"to the BRP scope in 2023, so it is absent from this {year} edition. "
            "The `landscape-elements` style renders nothing here."
        )
    return (
        "**Landscape elements:** the `Landschapselement` category covers ditches, "
        "hedgerows, tree rows, and ponds. It was added to the BRP scope in 2023."
    )


def readme(year: int) -> str:
    stats = YEAR_STATS[year]
    src = SOURCES[year]
    return f"""# BRP Gewaspercelen {year}

The {year} edition of the Basisregistratie Gewaspercelen (BRP) — every agricultural parcel in the Netherlands with its registered crop type, as recorded by farmers for CAP subsidy on **{year}-05-15** (the 'definitief' finalized edition).

> This folder is **one partition** of a multi-year collection. For the cross-year story and queries spanning 2009–2025, see the [parent collection](../README.md) (README + AGENTS.md at the parent level).

## Key numbers

| | |
|---|---|
| Parcels | {stats['features']:,} |
| Snapshot date | {year}-05-15 |
| Spatial extent (WGS84) | {stats['bbox']} |
| CRS | EPSG:28992 (Amersfoort / RD New) |
| License | CC0-1.0 |

## Files in this folder

| File | Description |
|---|---|
| [`brp_gewaspercelen_{year}.parquet`]({PARENT_BASE_URL}/{year}/brp_gewaspercelen_{year}.parquet) | GeoParquet, zstd, bbox-covering, spatially sorted |
| [`brp_gewaspercelen_{year}.pmtiles`]({PARENT_BASE_URL}/{year}/brp_gewaspercelen_{year}.pmtiles) | Vector tiles for web maps |
| [`brp_gewaspercelen_{year}.json`]({PARENT_BASE_URL}/{year}/brp_gewaspercelen_{year}.json) | STAC Item |
| [`{src['filename']}`]({PARENT_BASE_URL}/{year}/{src['filename']}) | Original PDOK source download |
| `styles/` | MapLibre styles (default, by-category, by-crop, landscape-elements) |

## Quick start

```python
import duckdb
con = duckdb.connect()
con.execute("INSTALL spatial; LOAD spatial;")

URL = '{PARENT_BASE_URL}/{year}/brp_gewaspercelen_{year}.parquet'

# Crop distribution by category, with total hectares
df = con.execute(f\"\"\"
    SELECT category, COUNT(*) AS parcels,
           ROUND(SUM(ST_Area(geom)) / 10000, 0) AS area_ha
    FROM read_parquet('{{URL}}')
    GROUP BY category
    ORDER BY area_ha DESC
\"\"\").df()
print(df)
```

DuckDB streams via HTTP range requests — no full download needed.

## Schema

| Column | Type | Description |
|---|---|---|
| id | int64 | Feature ID *within this year*. Not stable across years. |
| category | string | Broad crop category (Grasland, Bouwland, …) |
| gewas | string | Specific crop name |
| gewascode | int32 | Numeric crop code (stable across years) |
| jaar | int32 | `{year}` for every row |
| status | string | `Definitief` (finalized) |
| geom | binary | Polygon, WKB, EPSG:28992 |

{normalization_notes(year)}

{landscape_note(year)}

## Cross-year analysis

For "fields without potatoes in the last three years"-style queries that need many editions at once, point your tool at the parent collection's glob asset:

```
{PARENT_BASE_URL}/*/brp_gewaspercelen_*.parquet
```

See [`../AGENTS.md`](../AGENTS.md) and the parent [collection.json]({PARENT_BASE_URL}/collection.json) for full multi-year examples.

## Source

- [PDOK dataset page](https://www.pdok.nl/introductie/-/article/basisregistratie-gewaspercelen-brp-)
- [Source download ({src['title']})]({src['via_url']})

---

*Part of [Portolan NL](https://source.coop/cholmes/portolan-nl) — Cloud-Native Dutch Geodata.*
"""


def llms(year: int) -> str:
    stats = YEAR_STATS[year]
    src = SOURCES[year]
    parquet_url = f"{PARENT_BASE_URL}/{year}/brp_gewaspercelen_{year}.parquet"
    glob_url = f"{PARENT_BASE_URL}/*/brp_gewaspercelen_*.parquet"
    return f"""# BRP Gewaspercelen {year} — Agent/LLM Usage Guide

The {year} edition of the Dutch Basisregistratie Gewaspercelen (BRP). One year of
agricultural parcel polygons with registered crop type. {stats['features']:,} polygons,
all snapshotted on {year}-05-15 (the CAP registration deadline). Definitief — finalized
after verification.

## When to use this year's file vs the parent glob

- **This year only:** point your tool at
  `{parquet_url}`
- **All years (2009–2025) at once:** point your tool at the collection's `portolan:glob`
  asset, `{glob_url}` — every year becomes a single virtual dataset, distinguished by the
  `jaar` column. Use this for crop-rotation, trajectory, and "what was here last year?"
  queries. The parent [`AGENTS.md`]({PARENT_BASE_URL}/AGENTS.md) has the cross-year examples.

## Quick start

```python
import duckdb
con = duckdb.connect()
con.execute("INSTALL spatial; LOAD spatial;")
URL = '{parquet_url}'
df = con.execute(f"SELECT * FROM read_parquet('{{URL}}') LIMIT 5").df()
```

## Schema

| Column | Type | Notes |
|---|---|---|
| id | int64 | NOT stable across years |
| category | string | Grasland, Bouwland, {'Landschapselement, ' if year >= 2023 else ''}Natuurterrein, Braakland, Overige |
| gewas | string | Specific crop name (300+ distinct values across years) |
| gewascode | int32 | Numeric crop code, **stable across years** |
| jaar | int32 | `{year}` everywhere in this file |
| status | string | `Definitief` |
| geom | binary | Polygon WKB, EPSG:28992 (metres) |

{normalization_notes(year)}

{landscape_note(year)}

## Useful queries (single year — this file)

### Crop distribution per category

```sql
SELECT category, COUNT(*) parcels,
       ROUND(SUM(ST_Area(geom))/10000, 0) area_ha
FROM read_parquet('{parquet_url}')
GROUP BY category ORDER BY area_ha DESC
```

### Top 20 crops

```sql
SELECT gewas, gewascode, COUNT(*) parcels
FROM read_parquet('{parquet_url}')
GROUP BY gewas, gewascode
ORDER BY parcels DESC
LIMIT 20
```

### Find parcels near a location (Wageningen ≈ x=173600, y=443600 in RD New)

```sql
SELECT id, category, gewas
FROM read_parquet('{parquet_url}')
WHERE ST_DWithin(geom, ST_Point(173600, 443600), 1000)
```

EPSG:28992 is in metres, so the buffer is in metres.

## Visualization

- **PMTiles** (for web maps): `{PARENT_BASE_URL}/{year}/brp_gewaspercelen_{year}.pmtiles`
- **MapLibre styles** in `./styles/`:
  - `default.json` — natural agricultural palette
  - `by-category.json` — distinct color per broad category
  - `by-crop.json` — individual colors for the most common crops
  - `landscape-elements.json` — highlights ditches, hedgerows, etc{' (empty for this year)' if year < 2023 else ''}
- Each style file references `../brp_gewaspercelen_{year}.pmtiles` so the year folder is self-contained.

## Source

- {src['title']}: {src['via_url']}
- License: CC0-1.0
- Provider: RVO (Rijksdienst voor Ondernemend Nederland) via PDOK

## Related

- Parent collection (all 17 years): {PARENT_BASE_URL}/collection.json
- Parent `AGENTS.md` with cross-year SQL examples: {PARENT_BASE_URL}/AGENTS.md
"""


def main() -> None:
    for year in YEAR_STATS:
        year_dir = ROOT / str(year)
        year_dir.mkdir(parents=True, exist_ok=True)
        (year_dir / "README.md").write_text(readme(year))
        (year_dir / "AGENTS.md").write_text(llms(year))
        print(f"wrote {year}/README.md + {year}/AGENTS.md")


if __name__ == "__main__":
    main()

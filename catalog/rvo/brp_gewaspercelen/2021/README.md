# BRP Gewaspercelen 2021

The 2021 edition of the Basisregistratie Gewaspercelen (BRP) — every agricultural parcel in the Netherlands with its registered crop type, as recorded by farmers for CAP subsidy on **2021-05-15** (the 'definitief' finalized edition).

> This folder is **one partition** of a multi-year collection. For the cross-year story and queries spanning 2009–2025, see the [parent collection](https://data.source.coop/cholmes/portolan-nl/rvo/brp_gewaspercelen/) (README + AGENTS.md at the parent level).

## Key numbers

| | |
|---|---|
| Parcels | 772,539 |
| Snapshot date | 2021-05-15 |
| Spatial extent (WGS84) | [3.3597, 50.7504, 7.2244, 53.497] |
| CRS | EPSG:28992 (Amersfoort / RD New) |
| License | CC0-1.0 |

## Files in this folder

| File | Description |
|---|---|
| `brp_gewaspercelen_2021.parquet` | GeoParquet, zstd, bbox-covering, spatially sorted |
| `brp_gewaspercelen_2021.pmtiles` | Vector tiles for web maps |
| `brp_gewaspercelen_2021.json` | STAC Item |
| `brpgewaspercelen_definitief_2021.gpkg` | Original PDOK source download |
| `styles/` | MapLibre styles (default, by-category, by-crop, landscape-elements) |

## Quick start

```python
import duckdb
con = duckdb.connect()
con.execute("INSTALL spatial; LOAD spatial;")

URL = 'https://data.source.coop/cholmes/portolan-nl/rvo/brp_gewaspercelen/2021/brp_gewaspercelen_2021.parquet'

# Crop distribution by category, with total hectares
df = con.execute(f"""
    SELECT category, COUNT(*) AS parcels,
           ROUND(SUM(ST_Area(geom)) / 10000, 0) AS area_ha
    FROM read_parquet('{URL}')
    GROUP BY category
    ORDER BY area_ha DESC
""").df()
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
| jaar | int32 | `2021` for every row |
| status | string | `Definitief` (finalized) |
| geom | binary | Polygon, WKB, EPSG:28992 |

**Source format:** PDOK GeoPackage (`brpgewaspercelen_definitief_2021.gpkg`). The GeoParquet preserves the source schema byte-for-byte — no field renames or value transformations.

**Landscape elements:** the `Landschapselement` category was added to the BRP scope in 2023, so it is absent from this 2021 edition. The `landscape-elements` style renders nothing here.

## Cross-year analysis

For "fields without potatoes in the last three years"-style queries that need many editions at once, point your tool at the parent collection's glob asset:

```
https://data.source.coop/cholmes/portolan-nl/rvo/brp_gewaspercelen/*/brp_gewaspercelen_*.parquet
```

See [`../AGENTS.md`](../AGENTS.md) and the parent [collection.json](https://data.source.coop/cholmes/portolan-nl/rvo/brp_gewaspercelen/collection.json) for full multi-year examples.

## Source

- [PDOK dataset page](https://www.pdok.nl/introductie/-/article/basisregistratie-gewaspercelen-brp-)
- [Source download (Source GeoPackage (PDOK definitive 2021))](https://service.pdok.nl/rvo/gewaspercelen/atom/downloads/brpgewaspercelen_definitief_2021.gpkg)

---

*Part of [Portolan NL](https://data.source.coop/cholmes) — Cloud-Native Dutch Geodata.*

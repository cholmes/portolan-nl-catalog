# BRP Gewaspercelen 2025 — Agent/LLM Usage Guide

The 2025 edition of the Dutch Basisregistratie Gewaspercelen (BRP). One year of
agricultural parcel polygons with registered crop type. 2,331,084 polygons,
all snapshotted on 2025-05-15 (the CAP registration deadline). Definitief — finalized
after verification.

## When to use this year's file vs the parent glob

- **This year only:** point your tool at
  `https://data.source.coop/cholmes/portolan-nl/rvo/brp_gewaspercelen/2025/brp_gewaspercelen_2025.parquet`
- **All years (2009–2025) at once:** point your tool at the collection's `portolan:glob`
  asset, `https://data.source.coop/cholmes/portolan-nl/rvo/brp_gewaspercelen/*/brp_gewaspercelen_*.parquet` — every year becomes a single virtual dataset, distinguished by the
  `jaar` column. Use this for crop-rotation, trajectory, and "what was here last year?"
  queries. The parent [`AGENTS.md`](https://data.source.coop/cholmes/portolan-nl/rvo/brp_gewaspercelen/AGENTS.md) has the cross-year examples.

## Quick start

```python
import duckdb
con = duckdb.connect()
con.execute("INSTALL spatial; LOAD spatial;")
URL = 'https://data.source.coop/cholmes/portolan-nl/rvo/brp_gewaspercelen/2025/brp_gewaspercelen_2025.parquet'
df = con.execute(f"SELECT * FROM read_parquet('{URL}') LIMIT 5").df()
```

## Schema

| Column | Type | Notes |
|---|---|---|
| id | int64 | NOT stable across years |
| category | string | Grasland, Bouwland, Landschapselement, Natuurterrein, Braakland, Overige |
| gewas | string | Specific crop name (300+ distinct values across years) |
| gewascode | int32 | Numeric crop code, **stable across years** |
| jaar | int32 | `2025` everywhere in this file |
| status | string | `Definitief` |
| geom | binary | Polygon WKB, EPSG:28992 (metres) |

**Source format:** PDOK GeoPackage (`brpgewaspercelen_definitief_2025.gpkg`). The GeoParquet preserves the source schema byte-for-byte — no field renames or value transformations.

**Landscape elements:** the `Landschapselement` category covers ditches, hedgerows, tree rows, and ponds. It was added to the BRP scope in 2023.

## Useful queries (single year — this file)

### Crop distribution per category

```sql
SELECT category, COUNT(*) parcels,
       ROUND(SUM(ST_Area(geom))/10000, 0) area_ha
FROM read_parquet('https://data.source.coop/cholmes/portolan-nl/rvo/brp_gewaspercelen/2025/brp_gewaspercelen_2025.parquet')
GROUP BY category ORDER BY area_ha DESC
```

### Top 20 crops

```sql
SELECT gewas, gewascode, COUNT(*) parcels
FROM read_parquet('https://data.source.coop/cholmes/portolan-nl/rvo/brp_gewaspercelen/2025/brp_gewaspercelen_2025.parquet')
GROUP BY gewas, gewascode
ORDER BY parcels DESC
LIMIT 20
```

### Find parcels near a location (Wageningen ≈ x=173600, y=443600 in RD New)

```sql
SELECT id, category, gewas
FROM read_parquet('https://data.source.coop/cholmes/portolan-nl/rvo/brp_gewaspercelen/2025/brp_gewaspercelen_2025.parquet')
WHERE ST_DWithin(geom, ST_Point(173600, 443600), 1000)
```

EPSG:28992 is in metres, so the buffer is in metres.

## Visualization

- **PMTiles** (for web maps): `https://data.source.coop/cholmes/portolan-nl/rvo/brp_gewaspercelen/2025/brp_gewaspercelen_2025.pmtiles`
- **MapLibre styles** in `./styles/`:
  - `default.json` — natural agricultural palette
  - `by-category.json` — distinct color per broad category
  - `by-crop.json` — individual colors for the most common crops
  - `landscape-elements.json` — highlights ditches, hedgerows, etc
- Each style file references `../brp_gewaspercelen_2025.pmtiles` so the year folder is self-contained.

## Source

- Source GeoPackage (PDOK definitive 2025): https://service.pdok.nl/rvo/gewaspercelen/atom/downloads/brpgewaspercelen_definitief_2025.gpkg
- License: CC0-1.0
- Provider: RVO (Rijksdienst voor Ondernemend Nederland) via PDOK

## Related

- Parent collection (all 17 years): https://data.source.coop/cholmes/portolan-nl/rvo/brp_gewaspercelen/collection.json
- Parent `AGENTS.md` with cross-year SQL examples: https://data.source.coop/cholmes/portolan-nl/rvo/brp_gewaspercelen/AGENTS.md

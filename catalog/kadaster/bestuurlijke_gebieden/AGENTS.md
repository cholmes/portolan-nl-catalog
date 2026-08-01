# Administrative Areas (Bestuurlijke Gebieden) — Kadaster / Netherlands

## What This Dataset Is

The official administrative boundaries of the Netherlands: **342 municipalities** (gemeenten),
**12 provinces** (provincies), and **1 national territory** (landgebied). This is the
authoritative reference dataset for Dutch administrative divisions, maintained by Kadaster
and published via PDOK.

The dataset is updated annually on January 1st to reflect municipal mergers (herindelingen).
This is the **2026 edition**. The number of municipalities has been declining through mergers:
355 (2020) → 352 (2021) → 345 (2022) → 342 (2023–2026).

CBS (Statistics Netherlands) assigns municipality codes that are used across all Dutch
government datasets. This dataset is the fundamental reference for spatial joins with any
Dutch dataset that uses municipality or province codes.

**Source:** https://www.pdok.nl/introductie/-/article/0c3b462c-0a5d-463f-b082-51ed7bdf7684
**Provider:** Kadaster (Netherlands Cadastre, Land Registry and Mapping Agency)
**License:** CC BY 4.0 (attribution required)

## How to Access

The collection contains **three separate GeoParquet files** (one per administrative level),
all in EPSG:28992. The municipality file is the most commonly used.

```python
import duckdb

con = duckdb.connect()
con.execute("INSTALL spatial; LOAD spatial;")

BASE = 'https://data.source.coop/cholmes/portolan-nl/kadaster/bestuurlijke_gebieden'

# Municipalities (most common use case):
df = con.execute(f"""
    SELECT * FROM read_parquet('{BASE}/gemeentegebied.parquet')
    LIMIT 5
""").df()
```

Files are small: gemeentegebied ~8 MB, provinciegebied ~1.6 MB, landgebied ~0.4 MB.

## Files

| File | Contents | Features |
|------|----------|----------|
| `gemeentegebied.parquet` | Municipality boundaries | 342 |
| `provinciegebied.parquet` | Province boundaries | 12 |
| `landgebied.parquet` | National territory boundary | 1 |

## Schema — Gemeentegebied (Municipalities)

| Field | Type | Meaning |
|-------|------|---------|
| `geometry` | WKB MultiPolygon | Municipality boundary in **EPSG:28992**. |
| `identificatie` | string | **CBS municipality code** (4-digit, e.g. `0363` for Amsterdam). The key join field for all Dutch government data. |
| `naam` | string | **Municipality name** (Dutch). |
| `code` | string | Prefixed code: `GM0363`. GM = gemeente (municipality). |
| `ligt_in_provincie_code` | string | Province code this municipality belongs to (e.g. `PV27`). |
| `ligt_in_provincie_naam` | string | Province name (e.g. `Noord-Holland`). |
| `fid` | int64 | Internal feature ID. |

## Schema — Provinciegebied (Provinces)

| Field | Type | Meaning |
|-------|------|---------|
| `geometry` | WKB MultiPolygon | Province boundary in **EPSG:28992**. |
| `identificatie` | string | Province identifier. |
| `naam` | string | **Province name** (Dutch). |
| `code` | string | Prefixed code: `PV27`. PV = provincie. |
| `ligt_in_land_code` | string | Country code. |
| `ligt_in_land_naam` | string | Country name (`Nederland`). |
| `fid` | int64 | Internal feature ID. |

## Schema — Landgebied (National Territory)

| Field | Type | Meaning |
|-------|------|---------|
| `geometry` | WKB MultiPolygon | National territory boundary in **EPSG:28992**. |
| `identificatie` | string | Country identifier. |
| `naam` | string | Country name (`Nederland`). |
| `code` | string | Country code (`LND6030`). |
| `fid` | int64 | Internal feature ID. |

## The 12 Provinces

| Code | Name |
|------|------|
| PV20 | Groningen |
| PV21 | Fryslân |
| PV22 | Drenthe |
| PV23 | Overijssel |
| PV24 | Flevoland |
| PV25 | Gelderland |
| PV26 | Utrecht |
| PV27 | Noord-Holland |
| PV28 | Zuid-Holland |
| PV29 | Zeeland |
| PV30 | Noord-Brabant |
| PV31 | Limburg |

## Code System

CBS municipality codes are **stable numeric codes** that do not change. When municipalities
merge, the new municipality gets a new code. The `code` field adds a prefix:
- **GM** for gemeenten (e.g., `GM0363` = Amsterdam)
- **PV** for provincies (e.g., `PV27` = Noord-Holland)
- **LND** for land (e.g., `LND6030` = Nederland)

These coded identifiers are used across all Dutch government datasets (CBS statistics, BAG,
BRP, Kadaster), making this dataset the fundamental reference for spatial joins.

## Geometry Notes

- CRS is **EPSG:28992** (Amersfoort / RD New). Reproject to EPSG:4326 for web maps.
- Covers European Netherlands only (not Caribbean municipalities Bonaire, Sint Eustatius, Saba).
- Bounding box (RD): X 10,425–278,026, Y 306,846–621,876.
- All geometries are MultiPolygon.

## Useful Query Patterns

### List all municipalities in a province

```sql
SELECT identificatie, naam, code
FROM read_parquet('https://data.source.coop/cholmes/portolan-nl/kadaster/bestuurlijke_gebieden/gemeentegebied.parquet')
WHERE ligt_in_provincie_naam = 'Noord-Holland'
ORDER BY naam
```

### Count municipalities per province

```sql
SELECT ligt_in_provincie_naam AS province, COUNT(*) AS municipalities
FROM read_parquet('https://data.source.coop/cholmes/portolan-nl/kadaster/bestuurlijke_gebieden/gemeentegebied.parquet')
GROUP BY 1
ORDER BY municipalities DESC
```

### Find which municipality a point falls in

```sql
INSTALL spatial; LOAD spatial;

SELECT naam, code
FROM read_parquet('https://data.source.coop/cholmes/portolan-nl/kadaster/bestuurlijke_gebieden/gemeentegebied.parquet')
WHERE ST_Intersects(
    ST_GeomFromWKB(geometry),
    ST_Transform(ST_Point(4.9003, 52.3792), 'EPSG:4326', 'EPSG:28992')
)
```

### Compute municipality areas

```sql
INSTALL spatial; LOAD spatial;

SELECT naam, code,
       ST_Area(ST_GeomFromWKB(geometry)) / 1e6 AS area_km2
FROM read_parquet('https://data.source.coop/cholmes/portolan-nl/kadaster/bestuurlijke_gebieden/gemeentegebied.parquet')
ORDER BY area_km2 DESC
LIMIT 10
```

Note: Area computation in EPSG:28992 gives accurate results in square metres since it's a
projected CRS.

### Join with other datasets using gemeente code

```sql
SELECT g.naam AS gemeente, other.*
FROM read_parquet('.../gemeentegebied.parquet') g
JOIN read_parquet('.../other_dataset.parquet') other
  ON g.identificatie = other.gemeentecode
```

### Load into GeoPandas

```python
import geopandas as gpd

gemeenten = gpd.read_parquet(
    'https://data.source.coop/cholmes/portolan-nl/kadaster/bestuurlijke_gebieden/gemeentegebied.parquet'
)
provincies = gpd.read_parquet(
    'https://data.source.coop/cholmes/portolan-nl/kadaster/bestuurlijke_gebieden/provinciegebied.parquet'
)
```

## Related Datasets

- **CBS Gebiedsindelingen** (also in this catalog, planned): Much broader — includes COROP regions,
  labor market regions, safety regions, water boards, and 20+ other regional classifications.
- **CBS Wijken en Buurten** (also in this catalog, planned): Demographic data at the
  neighborhood level, joinable via municipality code.
- **BAG** (Kadaster): Building and address registry, references municipality codes.

## Caveats

- European Netherlands only — excludes Caribbean Netherlands (BES islands).
- The 2026 edition has 342 municipalities. If joining with older datasets, check for
  municipality mergers that may have changed codes.
- The `ligt_in_provincie_code` and `ligt_in_provincie_naam` fields are only present in
  gemeentegebied; `ligt_in_land_code` and `ligt_in_land_naam` only in provinciegebied.


## Visualization Styles

One Mapbox GL v8 style is available for interactive map visualization.

Style files are Mapbox GL v8 JSON with relative PMTiles source paths. They can be
used with MapLibre GL JS, OpenLayers (via ol-mapbox-style), or any Mapbox GL v8-compatible renderer.

- **`styles/default.json`** — Light peach municipality fills with red boundary lines and labeled names. Clean administrative reference map.

Style files are at: `https://data.source.coop/cholmes/portolan-nl/kadaster/bestuurlijke_gebieden/styles/`
## Also Available As

- **PMTiles (vector tiles):** `bestuurlijke_gebieden.pmtiles` — municipality boundaries
  for web visualization.
- **GeoPackage:** All three layers in one file from PDOK Atom feed.
- **OGC API Features:** `https://api.pdok.nl/kadaster/brk-bestuurlijke-gebieden/ogc/v1/`.

---
*Hand-maintained agent guide (ported from this collection's llms.txt in August 2026). Update it alongside collection.json.*

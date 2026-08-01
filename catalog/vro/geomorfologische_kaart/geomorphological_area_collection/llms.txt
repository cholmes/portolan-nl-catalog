# BRO Geomorphological Map — Map area collections

## What this is
Map-area collections of the national Geomorphological Map 1:50,000 (BRO object **GMM**) — 70
polygons that group the map by survey / publication unit.

**Features:** 70  |  **CRS:** EPSG:28992  |  **License:** CC0 1.0 (public domain)
**Source:** PDOK / BRO (provider VRO).  **Formats:** GeoParquet · PMTiles · GeoPackage (PDOK Atom).

## Why it matters
Use to understand provenance/version groupings of the geomorphological map.

## About the BRO

This collection comes from the **Basisregistratie Ondergrond (BRO)** — the Dutch Key Registry of the Subsurface, a statutory base registry in force since 1 January 2018. Government bodies must register subsurface data in the BRO and may only use registered data for public tasks. Data is published openly via PDOK, usually within ~1 day of registration. The Ministry of Housing and Spatial Planning (**VRO**) is the system-responsible provider; the data here is produced by **TNO – Geologische Dienst Nederland** (subsurface objects) or **Wageningen Environmental Research** (the soil and geomorphological maps).

Two BRO concepts appear in almost every dataset:
- **`bro_id`** — the unique registration identifier of each object (e.g. `GMW000000012345`).
- **`quality_regime`** — `IMBRO` (full quality assurance) or `IMBRO/A` (transitional data delivered under a lighter regime; treat with slightly more caution).

## How to access

DuckDB (analytics):

```python
import duckdb
con = duckdb.connect(); con.execute("INSTALL spatial; LOAD spatial;")
df = con.execute("""
    SELECT * FROM read_parquet('https://data.source.coop/cholmes/portolan-nl/vro/geomorfologische_kaart/geomorphological_area_collection/geomorphological_area_collection.parquet') LIMIT 5
""").df()
```

GeoPandas:

```python
import geopandas as gpd
gdf = gpd.read_parquet('https://data.source.coop/cholmes/portolan-nl/vro/geomorfologische_kaart/geomorphological_area_collection/geomorphological_area_collection.parquet')   # CRS EPSG:28992
```

## Schema — field meanings

| Column | Type | Meaning |
|--------|------|---------|
| `fid` | int64 | Feature ID. |
| `version` | string |  |
| `collection_id` | string |  |
| `name` | string |  |
| `inventorymethod` | string |  |
| `source` | string |  |
| `beginlifespan` | int64 |  |
| `endlifespan` | int64 |  |
| `citation_id` | string |  |
| `geom` | binary | Feature geometry (WKB) in EPSG:28992 (Amersfoort / RD New). |
| `geom_bbox` | struct<xmin: float, ymin: float, xmax: float, ymax: float> | Per-feature bounding box struct for spatial filtering. |

Geometry is stored in `geom` (WKB, EPSG:28992); `geom_bbox` is a per-feature bounding-box
struct enabling fast spatial pre-filtering.

### Spatial query (point-in-area / nearby)

```sql
INSTALL spatial; LOAD spatial;
SELECT bro_id
FROM read_parquet('https://data.source.coop/cholmes/portolan-nl/vro/geomorfologische_kaart/geomorphological_area_collection/geomorphological_area_collection.parquet')
WHERE ST_DWithin(
    ST_GeomFromWKB(geom),
    ST_Point(5.12, 52.09),            -- lon, lat (transform if data is EPSG:28992)
    0.05);
```

## Caveats
- A provenance/grouping layer, not the landform map — see *geomorphological_area*.

## Related collections
geomorphological_area (the map).

## Dutch ↔ English glossary

Column names in this collection are the English BRO field names. Common Dutch equivalents:
`bronhouder` = delivery_accountable_party (data owner), `kwaliteitsregime` = quality_regime, `bodemklasse` = soil class, `hoofdklasse` = main soil class, `genese` = genesis (landform origin), `reliëf` = relief, `boring/booronderzoek` = borehole, `sondering` = cone penetration test, `grondwater` = groundwater, `mijnbouw` = mining, `bodemverontreiniging` = soil contamination.

## Visualization styles

Mapbox GL v8 style files (use with MapLibre GL JS, OpenLayers via ol-mapbox-style, or any Mapbox GL v8 renderer) live alongside the PMTiles:

- **`styles/default.json`** — BRO Geomorphological Map — Map area collections — Default (https://data.source.coop/cholmes/portolan-nl/vro/geomorfologische_kaart/geomorphological_area_collection/styles/default.json)
- **`styles/by-method.json`** — BRO Geomorphological Map — Map area collections — By inventory method (https://data.source.coop/cholmes/portolan-nl/vro/geomorfologische_kaart/geomorphological_area_collection/styles/by-method.json)

## Also available as
- **PMTiles** (vector tiles): `geomorphological_area_collection.pmtiles`
- **GeoPackage** (full relational model): PDOK Atom download for BRO object — see the `via` links in
  `collection.json`.

---
*Part of the Portolan NL catalog · CC0 1.0 · provider VRO (Ministerie van Volkshuisvesting en
Ruimtelijke Ordening).*

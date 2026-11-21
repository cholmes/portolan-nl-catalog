# BRO Soil Map — Area of pedological interest

## What this is
The area of pedological interest of the national Soil Map 1:50,000 (BRO object **SGM**) — 6,192
polygons delimiting where soil mapping applies. Built-up areas and large open water are excluded.

**Features:** 6,192  |  **CRS:** EPSG:28992  |  **License:** CC0 1.0 (public domain)
**Source:** PDOK / BRO (provider VRO).  **Formats:** GeoParquet · PMTiles · GeoPackage (PDOK Atom).

## Why it matters
Use as a mask/extent for the soil map; shows where soil data exists.

## About the BRO

Part of the **Basisregistratie Ondergrond (BRO)**, the Dutch Key Registry of the Subsurface; see the [VRO catalog](../../catalog.json) description and [../../AGENTS.md](../../AGENTS.md) for the registry context. The schema table below defines the shared BRO fields (`bro_id`, `quality_regime`).

## How to access

DuckDB (analytics):

```python
import duckdb
con = duckdb.connect(); con.execute("INSTALL spatial; LOAD spatial;")
df = con.execute("""
    SELECT * FROM read_parquet('https://data.source.coop/cholmes/portolan-nl/vro/bodemkaart/areaofpedologicalinterest/areaofpedologicalinterest.parquet') LIMIT 5
""").df()
```

GeoPandas:

```python
import geopandas as gpd
gdf = gpd.read_parquet('https://data.source.coop/cholmes/portolan-nl/vro/bodemkaart/areaofpedologicalinterest/areaofpedologicalinterest.parquet')   # CRS EPSG:28992
```

## Schema — field meanings

| Column | Type | Meaning |
|--------|------|---------|
| `fid` | int64 | Feature ID. |
| `maparea_id` | string | Unique ID of this map polygon in the delivered SGM model version (e.g. V2025-1.areaofpedologicalinterrest.NNN). |
| `maparea_collection` | string | Soil area collection (bodemvlakcollectie) this polygon belongs to, given by collection kind (SGM cat. 4.3.6.2). |
| `beginlifespan` | string | Date/time this version of the spatial object was inserted or changed in the dataset (INSPIRE lifespan; not in SGM catalogus v1.2; null in data). |
| `endlifespan` | string | Date/time this version of the spatial object was superseded or retired (INSPIRE lifespan; not in SGM catalogus v1.2; null in data). |
| `pedologicalinterest` | string | Pedological interest (bodemkundig belang): area type where soil cannot be typed, relevant for interpreting surrounding soils (SGM cat. 4.3.8). |
| `geom` | binary | Feature geometry (WKB) in EPSG:28992 (Amersfoort / RD New). |
| `geom_bbox` | struct<xmin: float, ymin: float, xmax: float, ymax: float> | Per-feature bounding box struct for spatial filtering. |

Geometry is stored in `geom` (WKB, EPSG:28992); `geom_bbox` is a per-feature bounding-box
struct enabling fast spatial pre-filtering.

### Spatial query (point-in-area / nearby)

```sql
INSTALL spatial; LOAD spatial;
SELECT bro_id
FROM read_parquet('https://data.source.coop/cholmes/portolan-nl/vro/bodemkaart/areaofpedologicalinterest/areaofpedologicalinterest.parquet')
WHERE ST_DWithin(
    geom,
    ST_Point(5.12, 52.09),            -- lon, lat (transform if data is EPSG:28992)
    0.05);
```

## Caveats
- This is a coverage/extent layer, not the soil map itself — see the *soilarea* collection.

## Related collections
soilarea (the soil map).

## Dutch ↔ English glossary

Column names in this collection are the English BRO field names. Common Dutch equivalents:
`bronhouder` = delivery_accountable_party (data owner), `kwaliteitsregime` = quality_regime, `bodemklasse` = soil class, `hoofdklasse` = main soil class, `genese` = genesis (landform origin), `reliëf` = relief, `boring/booronderzoek` = borehole, `sondering` = cone penetration test, `grondwater` = groundwater, `mijnbouw` = mining, `bodemverontreiniging` = soil contamination.

## Visualization styles

Mapbox GL v8 style files (use with MapLibre GL JS, OpenLayers via ol-mapbox-style, or any Mapbox GL v8 renderer) live alongside the PMTiles:

- **`styles/default.json`** — BRO Soil Map — Area of pedological interest — Default (https://data.source.coop/cholmes/portolan-nl/vro/bodemkaart/areaofpedologicalinterest/styles/default.json)
- **`styles/by-collection.json`** — BRO Soil Map — Area of pedological interest — By survey campaign (https://data.source.coop/cholmes/portolan-nl/vro/bodemkaart/areaofpedologicalinterest/styles/by-collection.json)
- **`styles/by-interest.json`** — BRO Soil Map — Area of pedological interest — By area type (https://data.source.coop/cholmes/portolan-nl/vro/bodemkaart/areaofpedologicalinterest/styles/by-interest.json)

## Also available as
- **PMTiles** (vector tiles): [`areaofpedologicalinterest.pmtiles`](https://data.source.coop/cholmes/portolan-nl/vro/bodemkaart/areaofpedologicalinterest/areaofpedologicalinterest.pmtiles)
- **GeoPackage** (full relational model): PDOK Atom download for BRO object — see the `via` links in
  `collection.json`.

---
*Part of the Portolan NL catalog · CC0 1.0 · provider VRO (Ministerie van Volkshuisvesting en
Ruimtelijke Ordening).*

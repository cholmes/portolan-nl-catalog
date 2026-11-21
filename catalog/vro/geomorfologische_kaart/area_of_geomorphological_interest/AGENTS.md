# BRO Geomorphological Map — Area of geomorphological interest

## What this is
The area of geomorphological interest of the national Geomorphological Map 1:50,000 (BRO object
**GMM**) — 40,840 polygons delimiting where the geomorphological mapping applies.

**Features:** 40,840  |  **CRS:** EPSG:28992  |  **License:** CC0 1.0 (public domain)
**Source:** PDOK / BRO (provider VRO).  **Formats:** GeoParquet · PMTiles · GeoPackage (PDOK Atom).

## Why it matters
Use as a mask/extent for the geomorphological map.

## About the BRO

Part of the **Basisregistratie Ondergrond (BRO)**, the Dutch Key Registry of the Subsurface; see the [VRO catalog](../../catalog.json) description and [../../AGENTS.md](../../AGENTS.md) for the registry context. The schema table below defines the shared BRO fields (`bro_id`, `quality_regime`).

## How to access

DuckDB (analytics):

```python
import duckdb
con = duckdb.connect(); con.execute("INSTALL spatial; LOAD spatial;")
df = con.execute("""
    SELECT * FROM read_parquet('https://data.source.coop/cholmes/portolan-nl/vro/geomorfologische_kaart/area_of_geomorphological_interest/area_of_geomorphological_interest.parquet') LIMIT 5
""").df()
```

GeoPandas:

```python
import geopandas as gpd
gdf = gpd.read_parquet('https://data.source.coop/cholmes/portolan-nl/vro/geomorfologische_kaart/area_of_geomorphological_interest/area_of_geomorphological_interest.parquet')   # CRS EPSG:28992
```

## Schema — field meanings

| Column | Type | Meaning |
|--------|------|---------|
| `fid` | int64 | Feature ID. |
| `identification` | string | Unique ID of the map polygon (Kaartvlak identificatie) of this area of geomorphological interest (GMM cat. 4.3.3.1). |
| `collection_id` | string | ID of the geomorphological area collection (vlakcollectie) this polygon belongs to (GMM cat. 4.3.2.1). |
| `type` | string | Type of geomorphological interest (geomorfologisch belang): Dijk or Water; features relevant to landform formation, without a landform description (GMM cat. 4.3.4). |
| `geom` | binary | Feature geometry (WKB) in EPSG:28992 (Amersfoort / RD New). |
| `geom_bbox` | struct<xmin: float, ymin: float, xmax: float, ymax: float> | Per-feature bounding box struct for spatial filtering. |

Geometry is stored in `geom` (WKB, EPSG:28992); `geom_bbox` is a per-feature bounding-box
struct enabling fast spatial pre-filtering.

### Spatial query (point-in-area / nearby)

```sql
INSTALL spatial; LOAD spatial;
SELECT bro_id
FROM read_parquet('https://data.source.coop/cholmes/portolan-nl/vro/geomorfologische_kaart/area_of_geomorphological_interest/area_of_geomorphological_interest.parquet')
WHERE ST_DWithin(
    geom,
    ST_Point(5.12, 52.09),            -- lon, lat (transform if data is EPSG:28992)
    0.05);
```

## Caveats
- Coverage/extent layer, not the map itself — see *geomorphological_area*.

## Related collections
geomorphological_area (the map).

## Dutch ↔ English glossary

Column names in this collection are the English BRO field names. Common Dutch equivalents:
`bronhouder` = delivery_accountable_party (data owner), `kwaliteitsregime` = quality_regime, `bodemklasse` = soil class, `hoofdklasse` = main soil class, `genese` = genesis (landform origin), `reliëf` = relief, `boring/booronderzoek` = borehole, `sondering` = cone penetration test, `grondwater` = groundwater, `mijnbouw` = mining, `bodemverontreiniging` = soil contamination.

## Visualization styles

Mapbox GL v8 style files (use with MapLibre GL JS, OpenLayers via ol-mapbox-style, or any Mapbox GL v8 renderer) live alongside the PMTiles:

- **`styles/default.json`** — BRO Geomorphological Map — Area of geomorphological interest — Default (https://data.source.coop/cholmes/portolan-nl/vro/geomorfologische_kaart/area_of_geomorphological_interest/styles/default.json)
- **`styles/by-type.json`** — BRO Geomorphological Map — Area of geomorphological interest — By type (https://data.source.coop/cholmes/portolan-nl/vro/geomorfologische_kaart/area_of_geomorphological_interest/styles/by-type.json)

## Also available as
- **PMTiles** (vector tiles): [`area_of_geomorphological_interest.pmtiles`](https://data.source.coop/cholmes/portolan-nl/vro/geomorfologische_kaart/area_of_geomorphological_interest/area_of_geomorphological_interest.pmtiles)
- **GeoPackage** (full relational model): PDOK Atom download for BRO object — see the `via` links in
  `collection.json`.

---
*Part of the Portolan NL catalog · CC0 1.0 · provider VRO (Ministerie van Volkshuisvesting en
Ruimtelijke Ordening).*

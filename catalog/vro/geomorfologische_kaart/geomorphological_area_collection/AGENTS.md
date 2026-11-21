# BRO Geomorphological Map — Map area collections

## What this is
Map-area collections of the national Geomorphological Map 1:50,000 (BRO object **GMM**) — 70
polygons that group the map by survey / publication unit.

**Features:** 70  |  **CRS:** EPSG:28992  |  **License:** CC0 1.0 (public domain)
**Source:** PDOK / BRO (provider VRO).  **Formats:** GeoParquet · PMTiles · GeoPackage (PDOK Atom).

## Why it matters
Use to understand provenance/version groupings of the geomorphological map.

## About the BRO

Part of the **Basisregistratie Ondergrond (BRO)**, the Dutch Key Registry of the Subsurface; see the [VRO catalog](../../catalog.json) description and [../../AGENTS.md](../../AGENTS.md) for the registry context. The schema table below defines the shared BRO fields (`bro_id`, `quality_regime`).

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
| `version` | string | Version of the delivered GMM map model (e.g. GEOM50000-V2025-1); model version management per GMM cat. 6.3.1. |
| `collection_id` | string | Unique identifier (identificatie) of the geomorphological area collection in the GMM registration object (GMM cat. 4.3.2.1). |
| `name` | string | Name of the (sub)collection: the map sheet number or project name, e.g. Bergen_op_Zoom (GMM cat. 4.3.1.1 naam). |
| `inventorymethod` | string | Inventory method (inventarisatiemethode): analogue mapping with field survey or digital mapping with field verification (GMM cat. 4.3.2.5, 6.5). |
| `source` | string | Elevation source (bron/Bestand): name and version of the height data file used to delineate and classify the areas, e.g. AHN4 (GMM cat. 4.3.2.8, 4.3.6). |
| `beginlifespan` | int64 | Date (yyyymmdd) this version of the spatial object was inserted or changed in the dataset (begin levensduur, GMM cat. 4.3.2.6). |
| `endlifespan` | int64 | Date (yyyymmdd) this version of the spatial object was superseded or retired; empty while current (einde levensduur, GMM cat. 4.3.2.7). |
| `citation_id` | string | Reference to the CI_Citation record documenting this collection, e.g. the descriptive report of the survey or update (GMM cat. 4.3.2.4). |
| `geom` | binary | Feature geometry (WKB) in EPSG:28992 (Amersfoort / RD New). |
| `geom_bbox` | struct<xmin: float, ymin: float, xmax: float, ymax: float> | Per-feature bounding box struct for spatial filtering. |

Geometry is stored in `geom` (WKB, EPSG:28992); `geom_bbox` is a per-feature bounding-box
struct enabling fast spatial pre-filtering.

### Spatial query (point-in-area / nearby)

```sql
INSTALL spatial; LOAD spatial;
SELECT collection_id
FROM read_parquet('https://data.source.coop/cholmes/portolan-nl/vro/geomorfologische_kaart/geomorphological_area_collection/geomorphological_area_collection.parquet')
WHERE ST_DWithin(
    geom,
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
- **PMTiles** (vector tiles): [`geomorphological_area_collection.pmtiles`](https://data.source.coop/cholmes/portolan-nl/vro/geomorfologische_kaart/geomorphological_area_collection/geomorphological_area_collection.pmtiles)
- **GeoPackage** (full relational model): PDOK Atom download for BRO object — see the `via` links in
  `collection.json`.

---
*Part of the Portolan NL catalog · CC0 1.0 · provider VRO (Ministerie van Volkshuisvesting en
Ruimtelijke Ordening).*

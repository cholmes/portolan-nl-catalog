# BRO Soil Map of the Netherlands 1:50,000 — Soil areas (SGM)

## What this is
The **Soil Map of the Netherlands 1:50,000** (Dutch *Bodemkaart van Nederland*, BRO object
**SGM**) — the authoritative national soil map produced by Wageningen Environmental Research. Each
of the 48,025 polygons is a mapped soil area. This collection is **enriched**: the primary soil
unit (`soilunit_code`, the BRO *bodemcode*) and its main soil class (`hoofdklasse`, e.g.
*Podzolgronden*, *Zeekleigronden*, *Veengronden*) and full classification (`bodemklasse`) have
been joined from the soil-unit tables so you can map and analyse soil type directly.

**Features:** 48,025  |  **CRS:** EPSG:28992  |  **License:** CC0 1.0 (public domain)
**Source:** PDOK / BRO (provider VRO).  **Formats:** GeoParquet · PMTiles · GeoPackage (PDOK Atom).

## Why it matters
One of the most widely used environmental datasets in the Netherlands: agriculture and precision
farming, hydrology and water management, nature development, carbon/peat studies, and spatial
planning.

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
    SELECT * FROM read_parquet('https://data.source.coop/cholmes/portolan-nl/vro/bodemkaart/soilarea/soilarea.parquet') LIMIT 5
""").df()
```

GeoPandas:

```python
import geopandas as gpd
gdf = gpd.read_parquet('https://data.source.coop/cholmes/portolan-nl/vro/bodemkaart/soilarea/soilarea.parquet')   # CRS EPSG:28992
```

## Schema — field meanings

| Column | Type | Meaning |
|--------|------|---------|
| `fid` | int64 | Feature ID. |
| `maparea_id` | string | Soil-area polygon identifier. |
| `maparea_collection` | string | Survey campaign / map collection the polygon belongs to. |
| `soilslope` | string | Slope class of the soil area (mostly 'Niet opgenomen'). |
| `soilunit_code` | string | Primary soil-unit code (BRO bodemcode), e.g. 'cHn21'. |
| `hoofdklasse` | string | Main soil class (mainsoilclassification), e.g. Podzolgronden, Zeekleigronden. |
| `bodemklasse` | string | Full soil classification text of the primary soil unit. |
| `legenda_url` | string | URL to the official soil-class legend entry. |
| `geom` | binary | Feature geometry (WKB) in EPSG:28992 (Amersfoort / RD New). |
| `geom_bbox` | struct<xmin: float, ymin: float, xmax: float, ymax: float> | Per-feature bounding box struct for spatial filtering. |

Geometry is stored in `geom` (WKB, EPSG:28992); `geom_bbox` is a per-feature bounding-box
struct enabling fast spatial pre-filtering.

### Spatial query (point-in-area / nearby)

```sql
INSTALL spatial; LOAD spatial;
SELECT bro_id
FROM read_parquet('https://data.source.coop/cholmes/portolan-nl/vro/bodemkaart/soilarea/soilarea.parquet')
WHERE ST_DWithin(
    ST_GeomFromWKB(geom),
    ST_Point(5.12, 52.09),            -- lon, lat (transform if data is EPSG:28992)
    0.05);
```

## Caveats
- A soil area can carry **several** soil units; this collection keeps the **primary** unit (sequence number 0). Secondary units are in the source GeoPackage.
- `soilslope` is `Niet opgenomen` (not recorded) for almost all polygons.
- Built-up areas and large water bodies are not mapped — see the companion *areaofpedologicalinterest* collection for the mapped extent.
- Full legend per soil code: https://legenda-bodemkaart.bodemdata.nl/ (also in `legenda_url`).

## Related collections
Area of pedological interest, soil boreholes (BHR-P), soil trenches (SFR).

## Dutch ↔ English glossary

Column names in this collection are the English BRO field names. Common Dutch equivalents:
`bronhouder` = delivery_accountable_party (data owner), `kwaliteitsregime` = quality_regime, `bodemklasse` = soil class, `hoofdklasse` = main soil class, `genese` = genesis (landform origin), `reliëf` = relief, `boring/booronderzoek` = borehole, `sondering` = cone penetration test, `grondwater` = groundwater, `mijnbouw` = mining, `bodemverontreiniging` = soil contamination.

## Visualization styles

Mapbox GL v8 style files (use with MapLibre GL JS, OpenLayers via ol-mapbox-style, or any Mapbox GL v8 renderer) live alongside the PMTiles:

- **`styles/default.json`** — BRO Soil Map of the Netherlands 1:50,000 — Soil areas (SGM) — Default (https://data.source.coop/cholmes/portolan-nl/vro/bodemkaart/soilarea/styles/default.json)
- **`styles/by-collection.json`** — BRO Soil Map of the Netherlands 1:50,000 — Soil areas (SGM) — By survey campaign (https://data.source.coop/cholmes/portolan-nl/vro/bodemkaart/soilarea/styles/by-collection.json)
- **`styles/by-texture.json`** — BRO Soil Map of the Netherlands 1:50,000 — Soil areas (SGM) — By texture (sand / clay / peat) (https://data.source.coop/cholmes/portolan-nl/vro/bodemkaart/soilarea/styles/by-texture.json)

## Also available as
- **PMTiles** (vector tiles): `soilarea.pmtiles`
- **GeoPackage** (full relational model): PDOK Atom download for BRO object — see the `via` links in
  `collection.json`.

---
*Part of the Portolan NL catalog · CC0 1.0 · provider VRO (Ministerie van Volkshuisvesting en
Ruimtelijke Ordening).*

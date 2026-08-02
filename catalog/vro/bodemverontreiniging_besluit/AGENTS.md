# BRO Government Decision on Soil Contamination (SLD)

## What this is
Formal government decisions on soil contamination (Dutch *overheidsbesluit bodemverontreiniging*,
BRO object **SLD**). Each polygon is an area covered by an authority decision about a contaminated
site — its assessment, remediation or aftercare status — under the Soil Protection Act (Wbb) and,
since 2024, the Environment and Planning Act (Omgevingswet). 121 decision areas are included.

**Features:** 121  |  **CRS:** EPSG:4258  |  **License:** CC0 1.0 (public domain)
**Source:** PDOK / BRO (provider VRO).  **Formats:** GeoParquet · PMTiles · GeoPackage (PDOK Atom).

## Why it matters
Used in conveyancing, spatial planning, permitting and environmental due diligence: it shows where
a formal contamination decision applies.

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
    SELECT * FROM read_parquet('https://data.source.coop/cholmes/portolan-nl/vro/bodemverontreiniging_besluit/bodemverontreiniging_besluit.parquet') LIMIT 5
""").df()
```

GeoPandas:

```python
import geopandas as gpd
gdf = gpd.read_parquet('https://data.source.coop/cholmes/portolan-nl/vro/bodemverontreiniging_besluit/bodemverontreiniging_besluit.parquet')   # CRS EPSG:4258
```

## Schema — field meanings

| Column | Type | Meaning |
|--------|------|---------|
| `soil_legal_decision_pk` | int64 |  |
| `bro_id` | string | BRO registration ID — unique identifier of the object in the Basisregistratie Ondergrond. |
| `quality_regime` | string | BRO quality regime: IMBRO (full assurance) or IMBRO/A (transitional/lower assurance). |
| `delivery_accountable_party` | string | KvK number of the party accountable for delivery (bronhouder). |
| `delivery_context` | string | Legal/administrative framework under which the object was registered. |
| `applied_transformation` | string | Whether a coordinate/height transformation was applied (ja/nee). |
| `standardized_location` | binary | Object location — WKB geometry in EPSG:4258 (ETRS89). |
| `standardized_location_bbox` | struct<xmin: float, ymin: float, xmax: float, ymax: float> | Per-feature bounding box struct (xmin,ymin,xmax,ymax) for spatial filtering. |

Geometry is stored in `standardized_location` (WKB, EPSG:4258); `standardized_location_bbox` is a per-feature bounding-box
struct enabling fast spatial pre-filtering.

### Spatial query (point-in-area / nearby)

```sql
INSTALL spatial; LOAD spatial;
SELECT bro_id
FROM read_parquet('https://data.source.coop/cholmes/portolan-nl/vro/bodemverontreiniging_besluit/bodemverontreiniging_besluit.parquet')
WHERE ST_DWithin(
    ST_GeomFromWKB(standardized_location),
    ST_Point(5.12, 52.09),            -- lon, lat (transform if data is EPSG:28992)
    0.05);
```

## Caveats
- This is a young, sparse BRO object — the national coverage is still growing.
- The decision/aftercare/contamination detail (nature of contamination, measures) lives in related tables in the source GeoPackage; this collection holds the decision-area geometry + summary.

## Related collections
Environmental soil investigation (SAD), soil map (bodemkaart).

## Dutch ↔ English glossary

Column names in this collection are the English BRO field names. Common Dutch equivalents:
`bronhouder` = delivery_accountable_party (data owner), `kwaliteitsregime` = quality_regime, `bodemklasse` = soil class, `hoofdklasse` = main soil class, `genese` = genesis (landform origin), `reliëf` = relief, `boring/booronderzoek` = borehole, `sondering` = cone penetration test, `grondwater` = groundwater, `mijnbouw` = mining, `bodemverontreiniging` = soil contamination.

## Visualization styles

Mapbox GL v8 style files (use with MapLibre GL JS, OpenLayers via ol-mapbox-style, or any Mapbox GL v8 renderer) live alongside the PMTiles:

- **`styles/default.json`** — BRO Government Decision on Soil Contamination (SLD) — Default (https://data.source.coop/cholmes/portolan-nl/vro/bodemverontreiniging_besluit/styles/default.json)
- **`styles/by-bronhouder.json`** — BRO Government Decision on Soil Contamination (SLD) — By data owner (bronhouder) (https://data.source.coop/cholmes/portolan-nl/vro/bodemverontreiniging_besluit/styles/by-bronhouder.json)
- **`styles/by-quality-regime.json`** — BRO Government Decision on Soil Contamination (SLD) — By quality regime (https://data.source.coop/cholmes/portolan-nl/vro/bodemverontreiniging_besluit/styles/by-quality-regime.json)

## Also available as
- **PMTiles** (vector tiles): [`bodemverontreiniging_besluit.pmtiles`](https://data.source.coop/cholmes/portolan-nl/vro/bodemverontreiniging_besluit/bodemverontreiniging_besluit.pmtiles)
- **GeoPackage** (full relational model): PDOK Atom download for BRO object — see the `via` links in
  `collection.json`.

---
*Part of the Portolan NL catalog · CC0 1.0 · provider VRO (Ministerie van Volkshuisvesting en
Ruimtelijke Ordening).*

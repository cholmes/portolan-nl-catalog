# BRO Geomorphological Map 1:50,000 — Geomorphological areas (GMM)

## What this is
The **Geomorphological Map of the Netherlands 1:50,000** (Dutch *Geomorfologische kaart*, BRO
object **GMM**), produced by Wageningen Environmental Research. Each of the 80,148 polygons is a
landform, classified by **genesis** (how it formed — eolian, fluvial, marine, glacial,
periglacial, anthropogenic, …), **relief** form, and **landform subgroup**. The classification is
denormalised directly into the feature, so it is ready to map and analyse.

**Features:** 80,148  |  **CRS:** EPSG:28992  |  **License:** CC0 1.0 (public domain)
**Source:** PDOK / BRO (provider VRO).  **Formats:** GeoParquet · PMTiles · GeoPackage (PDOK Atom).

## Why it matters
Used in landscape ecology, archaeology (landform predicts site potential), nature development,
water management and spatial planning.

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
    SELECT * FROM read_parquet('https://data.source.coop/cholmes/portolan-nl/vro/geomorfologische_kaart/geomorphological_area/geomorphological_area.parquet') LIMIT 5
""").df()
```

GeoPandas:

```python
import geopandas as gpd
gdf = gpd.read_parquet('https://data.source.coop/cholmes/portolan-nl/vro/geomorfologische_kaart/geomorphological_area/geomorphological_area.parquet')   # CRS EPSG:28992
```

## Schema — field meanings

| Column | Type | Meaning |
|--------|------|---------|
| `fid` | int64 | Feature ID. |
| `collection_id` | string |  |
| `identification` | string |  |
| `relief_code` | int64 | Relief-form code. |
| `active_process` | string | Whether the landform process is still active (ja/nee). |
| `genese_code` | string | Genesis code (1=Glaciaal, 2=Periglaciaal, 3=Denudatief, 4=Fluviatiel, 5=Eolisch, 6=Lacustrien, 7=Marien, 8=Organogeen, 9=Antropogeen, 0=Tectonisch). |
| `landform_subgroup_code` | string | Landform subgroup code (e.g. B44 = stroomrug/stream ridge). |
| `additional_surface_relief_code` | string | Additional surface relief code (optional). |
| `additional_surface_cover_code` | string | Additional surface cover code (optional). |
| `genese_description` | string | Genesis description (Dutch). |
| `genese_validfrom` | int64 |  |
| `genese_validto` | int64 |  |
| `landform_subgroup_description` | string | Landform subgroup description (Dutch). |
| `landform_subgroup_url` | string | URL to the landform legend entry. |
| `landform_subgroup_validfrom` | int64 |  |
| `landform_subgroup_validto` | int64 |  |
| `additional_surface_relief_description` | string |  |
| `additional_surface_relief_validfrom` | int64 |  |
| `additional_surface_relief_validto` | int64 |  |
| `additional_surface_cover_description` | string |  |
| `additional_surface_cover_validfrom` | int64 |  |
| `additional_surface_cover_validto` | int64 |  |
| `relief_klasse` | string |  |
| `relief_subklasse` | string |  |
| `helling` | string |  |
| `lokaal_maximaal_hoogteverschil` | string |  |
| `diepte_tov_omgeving` | string |  |
| `steilste_verhang` | string |  |
| `maximaal_hoogteverschil` | string |  |
| `maximaal_verval` | string |  |
| `relief_validfrom` | int64 |  |
| `relief_validto` | int64 |  |
| `geom` | binary | Feature geometry (WKB) in EPSG:28992 (Amersfoort / RD New). |
| `geom_bbox` | struct<xmin: float, ymin: float, xmax: float, ymax: float> | Per-feature bounding box struct for spatial filtering. |

Geometry is stored in `geom` (WKB, EPSG:28992); `geom_bbox` is a per-feature bounding-box
struct enabling fast spatial pre-filtering.

### Spatial query (point-in-area / nearby)

```sql
INSTALL spatial; LOAD spatial;
SELECT bro_id
FROM read_parquet('https://data.source.coop/cholmes/portolan-nl/vro/geomorfologische_kaart/geomorphological_area/geomorphological_area.parquet')
WHERE ST_DWithin(
    ST_GeomFromWKB(geom),
    ST_Point(5.12, 52.09),            -- lon, lat (transform if data is EPSG:28992)
    0.05);
```

## Caveats
- `genese_code` is numeric: 1=Glaciaal, 2=Periglaciaal, 3=Denudatief, 4=Fluviatiel, 5=Eolisch, 6=Lacustrien, 7=Marien, 8=Organogeen, 9=Antropogeen, 0=Tectonisch (Eolisch and Fluviatiel dominate).
- Landform subgroup legend: https://legendageomorfologie.wur.nl/ (also in `landform_subgroup_url`).
- `validfrom`/`validto` fields are integer YYYYMMDD codes.

## Related collections
Area of geomorphological interest, soil map (bodemkaart), AHN elevation.

## Dutch ↔ English glossary

Column names in this collection are the English BRO field names. Common Dutch equivalents:
`bronhouder` = delivery_accountable_party (data owner), `kwaliteitsregime` = quality_regime, `bodemklasse` = soil class, `hoofdklasse` = main soil class, `genese` = genesis (landform origin), `reliëf` = relief, `boring/booronderzoek` = borehole, `sondering` = cone penetration test, `grondwater` = groundwater, `mijnbouw` = mining, `bodemverontreiniging` = soil contamination.

## Visualization styles

Mapbox GL v8 style files (use with MapLibre GL JS, OpenLayers via ol-mapbox-style, or any Mapbox GL v8 renderer) live alongside the PMTiles:

- **`styles/default.json`** — BRO Geomorphological Map 1:50,000 — Geomorphological areas (GMM) — Default (https://data.source.coop/cholmes/portolan-nl/vro/geomorfologische_kaart/geomorphological_area/styles/default.json)
- **`styles/by-landform.json`** — BRO Geomorphological Map 1:50,000 — Geomorphological areas (GMM) — By landform subgroup (https://data.source.coop/cholmes/portolan-nl/vro/geomorfologische_kaart/geomorphological_area/styles/by-landform.json)
- **`styles/by-relief.json`** — BRO Geomorphological Map 1:50,000 — Geomorphological areas (GMM) — By relief class (https://data.source.coop/cholmes/portolan-nl/vro/geomorfologische_kaart/geomorphological_area/styles/by-relief.json)

## Also available as
- **PMTiles** (vector tiles): [`geomorphological_area.pmtiles`](https://data.source.coop/cholmes/portolan-nl/vro/geomorfologische_kaart/geomorphological_area/geomorphological_area.pmtiles)
- **GeoPackage** (full relational model): PDOK Atom download for BRO object — see the `via` links in
  `collection.json`.

---
*Part of the Portolan NL catalog · CC0 1.0 · provider VRO (Ministerie van Volkshuisvesting en
Ruimtelijke Ordening).*

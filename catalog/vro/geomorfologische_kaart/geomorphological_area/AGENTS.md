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

Part of the **Basisregistratie Ondergrond (BRO)**, the Dutch Key Registry of the Subsurface; see the [VRO catalog](../../catalog.json) description and [../../AGENTS.md](../../AGENTS.md) for the registry context. The schema table below defines the shared BRO fields (`bro_id`, `quality_regime`).

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
| `collection_id` | string | ID of the geomorphological area collection (Geomorfologische vlakcollectie) this polygon belongs to (GMM cat. 4.3.2.1 identificatie). |
| `identification` | string | Unique ID of the map polygon (Kaartvlak identificatie), a published spatial-object identifier for external reference (GMM cat. 4.3.3.1). |
| `relief_code` | int64 | Relief-form code. |
| `active_process` | string | Whether the landform process is still active (ja/nee). |
| `genese_code` | string | Genesis code (1=Glaciaal, 2=Periglaciaal, 3=Denudatief, 4=Fluviatiel, 5=Eolisch, 6=Lacustrien, 7=Marien, 8=Organogeen, 9=Antropogeen, 0=Tectonisch). |
| `landform_subgroup_code` | string | Landform subgroup code (e.g. B44 = stroomrug/stream ridge). |
| `additional_surface_relief_code` | string | Additional surface relief code (optional). |
| `additional_surface_cover_code` | string | Additional surface cover code (optional). |
| `genese_description` | string | Genesis description (Dutch). |
| `genese_validfrom` | int64 | Start date (yyyymmdd) from which the recorded genesis (ontstaanswijze) value is valid; material history per GMM cat. 2.5, 4.3.8.3. |
| `genese_validto` | int64 | End date (yyyymmdd) of validity of the recorded genesis value; empty while current (material history, GMM cat. 2.5). |
| `landform_subgroup_description` | string | Landform subgroup description (Dutch). |
| `landform_subgroup_url` | string | URL to the landform legend entry. |
| `landform_subgroup_validfrom` | int64 | Start date (yyyymmdd) from which the recorded landform subgroup (landvormsubgroep) value is valid (material history, GMM cat. 2.5, 4.3.7.5). |
| `landform_subgroup_validto` | int64 | End date (yyyymmdd) of validity of the recorded landform subgroup value; empty while current (material history, GMM cat. 2.5). |
| `additional_surface_relief_description` | string | Relief addition (toevoeging relief): further typing of the relief and/or relative elevation of the landform unit (GMM cat. 4.3.7.1, list 5.4). |
| `additional_surface_relief_validfrom` | int64 | Start date (yyyymmdd) from which the recorded relief addition is valid (material history, GMM cat. 2.5). |
| `additional_surface_relief_validto` | int64 | End date (yyyymmdd) of validity of the recorded relief addition; empty while current (material history, GMM cat. 2.5). |
| `additional_surface_cover_description` | string | Cover addition (toevoeging bedekking): typing of the deviating sediment layer covering the landform subgroup (GMM cat. 4.3.7.3, 6.3.6). |
| `additional_surface_cover_validfrom` | int64 | Start date (yyyymmdd) from which the recorded cover addition is valid (material history, GMM cat. 2.5). |
| `additional_surface_cover_validto` | int64 | End date (yyyymmdd) of validity of the recorded cover addition; empty while current (material history, GMM cat. 2.5). |
| `relief_klasse` | string | Relief class (reliefklasse): whether the relief code is for valley-shaped (dalvormige) or non-valley landform groups (GMM cat. 4.3.9.2, 4.3.10). |
| `relief_subklasse` | string | Relief description (relief) of the non-valley relief code, e.g. 'Vrij vlak, laaggelegen relief'; empty for valleys (GMM cat. list 5.3). |
| `helling` | string | Slope: class of the angle of the steepest slope of the landform; non-valley relief codes only (GMM cat. list 5.3, 6.3.3). |
| `lokaal_maximaal_hoogteverschil` | string | Local maximum height difference within the landform, in metres; non-valley relief codes only (GMM cat. list 5.3, 6.3.3). |
| `diepte_tov_omgeving` | string | Depth of the valley incision relative to the surroundings, in metres; valley relief codes only (GMM cat. list 5.2 diepte). |
| `steilste_verhang` | string | Steepest gradient (steilste verhang) of the valley form; valley relief codes only (GMM cat. list 5.2). |
| `maximaal_hoogteverschil` | string | Maximum height difference within the form, in metres; valley relief codes only (GMM cat. list 5.2). |
| `maximaal_verval` | string | Maximum drop (maximaal verval) of the valley, in metres; valley relief codes only (GMM cat. list 5.2). |
| `relief_validfrom` | int64 | Start date (yyyymmdd) from which the recorded relief typing is valid (material history, GMM cat. 2.5, 4.3.7.4). |
| `relief_validto` | int64 | End date (yyyymmdd) of validity of the recorded relief typing; empty while current (material history, GMM cat. 2.5). |
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
    geom,
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

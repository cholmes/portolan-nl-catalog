# Bestand Bodemgebruik 2017 (Land Use File) — CBS / Netherlands

## What This Dataset Is

A complete digital map of **land use in the Netherlands** for the year 2017, produced by
**CBS** (Centraal Bureau voor de Statistiek / Statistics Netherlands). Every parcel of land
in the country is classified by its functional use at ground level: transportation,
buildings, recreation, agriculture, forest, water, and more.

CBS has tracked Dutch land use since 1900. The Bestand Bodemgebruik (BBG) series provides
a consistent time series, allowing analysis of how the Netherlands has changed over
decades — from agricultural land being converted to housing, to urban expansion, to nature
restoration.

**Important:** This is the BBG 2017 edition, produced under the *old methodology*. From
2020 onwards, CBS produces the **NBBG** (Nieuw Bestand Bodemgebruik / Renewed Land Use
File) which uses semi-automated procedures and digital base registries (BAG, BGT, BRT)
instead of manual interpretation. The two are **not directly comparable** due to
methodological differences.

**Source:** https://www.pdok.nl/introductie/-/article/cbs-bestand-bodemgebruik-2017
**CBS page:** https://www.cbs.nl/nl-nl/dossier/nederland-regionaal/geografische-data/natuur-en-milieu/bestand-bodemgebruik
**Provider:** CBS (Centraal Bureau voor de Statistiek / Statistics Netherlands)
**License:** CC0 (public domain)
**Reference year:** 2017
**WFS endpoint:** https://service.pdok.nl/cbs/bestandbodemgebruik/2017/wfs/v1_0
**WMS endpoint:** https://service.pdok.nl/cbs/bestandbodemgebruik/2017/wms/v1_0
**Feature type:** bestandbodemgebruik:BBG2017

## How to Access

GeoParquet and PMTiles files are available from Source Cooperative. Native CRS is
**EPSG:28992** (RD New / Amersfoort) — coordinates are in meters.

| File | Features | Size | Contents |
|------|----------|------|----------|
| `bbg2017.parquet` | 171,543 | 1.2 GB | All land use polygons with classification |
| `bbg2017.pmtiles` | — | 189 MB | Land use polygons as vector tiles |

**Base URL:** `https://data.source.coop/cholmes/portolan-nl/cbs/bestand_bodemgebruik_2017/`

```python
import duckdb

con = duckdb.connect()
con.execute("INSTALL spatial; LOAD spatial;")

URL = 'https://data.source.coop/cholmes/portolan-nl/cbs/bestand_bodemgebruik_2017/bbg2017.parquet'
df = con.execute(f"SELECT * FROM read_parquet('{URL}') LIMIT 5").df()
```

Also available via WFS and WMS from PDOK:
- **WFS:** `https://service.pdok.nl/cbs/bestandbodemgebruik/2017/wfs/v1_0`
- **WMS:** `https://service.pdok.nl/cbs/bestandbodemgebruik/2017/wms/v1_0`

## Schema — Field Meanings

| Field | Type | Meaning |
|-------|------|---------|
| `bg2017` | int32 | **Land use code** — numeric code identifying the specific land use type in the BBG 2017 hierarchical classification. |
| `bodemgebruik` | string | **Land use type label** (Dutch) — the specific land use classification name, e.g. "Spoorterrein", "Woonterrein", "Bos". |
| `categorie` | string | **Category label** (Dutch) — higher-level grouping, e.g. "Verkeersterrein", "Bebouwd terrein". Often the same as `bodemgebruik` for categories that have no sub-types. |
| `geom` | MultiPolygon | **Land use polygon** in EPSG:28992 (RD New). Coordinates in meters. |

## Hierarchical Classification System

The BBG uses a hierarchical classification. The `categorie` field gives the broad group;
`bodemgebruik` gives the specific type. The `bg2017` numeric code uniquely identifies each
type.

### Main Categories and Land Use Types

**Verkeersterrein (Traffic/Transportation)**
- Spoorterrein — Railway area
- Wegverkeersterrein — Road traffic area
- Vliegveld — Airport

**Bebouwd terrein (Built-up Area)**
- Woonterrein — Residential area
- Detailhandel en horeca — Retail and hospitality
- Openbare voorziening — Public facilities
- Sociaal-culturele voorziening — Social-cultural facilities
- Bedrijfsterrein — Business/industrial area
- Stortplaats — Landfill/dump site
- Wrakkenopslagplaats — Vehicle scrapyard
- Begraafplaats — Cemetery
- Delfstofwinning — Mineral extraction
- Bouwterrein — Construction site
- Semi-bebouwd overig terrein — Semi-built-up other

**Recreatieterrein (Recreation)**
- Park en plantsoen — Park and public garden
- Sportterrein — Sports facility
- Volkstuin — Allotment garden
- Dagrecreatief terrein — Day recreation area
- Verblijfsrecreatief terrein — Overnight recreation area

**Agrarisch terrein (Agricultural)**
- Glastuinbouw — Greenhouse horticulture
- Overig agrarisch gebruik — Other agricultural use

**Bos en open natuurlijk terrein (Forest and Open Nature)**
- Bos — Forest
- Open droog natuurlijk terrein — Open dry natural area
- Open nat natuurlijk terrein — Open wet natural area

**Binnenwater (Inland Water)**
- IJsselmeer/Markermeer — IJsselmeer/Markermeer lake
- Afgesloten zeearm — Closed sea inlet
- Rijn en Maas — Rhine and Meuse rivers
- Randmeer — Border lake
- Spaarbekken — Reservoir
- Recreatief binnenwater — Recreational inland water
- Binnenwater voor delfstofwinning — Inland water for mineral extraction
- Vloei- en/of slibveld — Flow/sludge field
- Overig binnenwater — Other inland water

**Buitenwater (Outer Water)**
- Waddenzee, Eems, Dollard — Wadden Sea, Ems, Dollard
- Oosterschelde — Eastern Scheldt
- Westerschelde — Western Scheldt
- Noordzee — North Sea

## Important Columns

- **`bg2017`** — the numeric code; use this for joins and programmatic filtering
- **`bodemgebruik`** — the human-readable land use label; use for display and reports
- **`categorie`** — the higher-level category; useful for aggregation and summary statistics
- **`geom`** — MultiPolygon geometries covering the entire Netherlands

## Geometry Notes

- CRS is **EPSG:28992** (RD New / Amersfoort) — coordinates are in **meters**, NOT
  degrees. This is the Dutch national coordinate system.
- All geometries are **MultiPolygon** type
- The dataset covers the **entire Netherlands** including inland and coastal waters
- Minimum mapping unit is typically **1 hectare** (10,000 m2) for most categories
- Boundaries are largely derived from the Top10NL/BRT topographic base map
- Bounding box in WGS84: [3.37, 50.73, 7.24, 53.55]
- To convert to WGS84 (lon/lat) for web mapping:
  ```sql
  ST_Transform(geom, 'EPSG:28992', 'EPSG:4326')
  ```

## Useful Query Patterns

### Count features by land use type

```sql
SELECT bodemgebruik, COUNT(*) AS cnt
FROM read_parquet('bestand_bodemgebruik_2017.parquet')
GROUP BY bodemgebruik
ORDER BY cnt DESC
```

### Total area per category (in hectares)

```sql
INSTALL spatial; LOAD spatial;

SELECT categorie,
       COUNT(*) AS polygons,
       ROUND(SUM(ST_Area(geom)) / 10000, 1) AS hectares
FROM read_parquet('bestand_bodemgebruik_2017.parquet')
GROUP BY categorie
ORDER BY hectares DESC
```

Since CRS is in meters, `ST_Area(geom)` gives m2 directly. Divide by 10,000 for hectares.

### Find all forest areas

```sql
SELECT bodemgebruik, ST_Area(geom) / 10000 AS hectares
FROM read_parquet('bestand_bodemgebruik_2017.parquet')
WHERE bodemgebruik = 'Bos'
ORDER BY hectares DESC
LIMIT 20
```

### Find land use at a specific location (WGS84 coordinates)

```sql
INSTALL spatial; LOAD spatial;

WITH target AS (
    SELECT ST_Transform(ST_Point(4.9003, 52.3792), 'EPSG:4326', 'EPSG:28992') AS pt
)
SELECT bodemgebruik, categorie, bg2017
FROM read_parquet('bestand_bodemgebruik_2017.parquet'), target
WHERE ST_Intersects(geom, pt)
```

### Area breakdown for a specific municipality (using bbox filter)

```sql
INSTALL spatial; LOAD spatial;

-- Amsterdam area (approximate RD New coordinates)
SELECT categorie,
       ROUND(SUM(ST_Area(geom)) / 10000, 1) AS hectares
FROM read_parquet('bestand_bodemgebruik_2017.parquet')
WHERE bbox.xmin >= 109000 AND bbox.xmax <= 135000
  AND bbox.ymin >= 478000 AND bbox.ymax <= 498000
GROUP BY categorie
ORDER BY hectares DESC
```

### Compare residential vs agricultural land

```sql
SELECT
    CASE
        WHEN bodemgebruik = 'Woonterrein' THEN 'Residential'
        WHEN bodemgebruik IN ('Glastuinbouw', 'Overig agrarisch gebruik') THEN 'Agricultural'
        WHEN bodemgebruik = 'Bos' THEN 'Forest'
        WHEN categorie LIKE '%water%' OR categorie LIKE '%Water%' THEN 'Water'
        ELSE 'Other'
    END AS land_use_group,
    ROUND(SUM(ST_Area(geom)) / 1e6, 1) AS area_km2
FROM read_parquet('bestand_bodemgebruik_2017.parquet')
GROUP BY 1
ORDER BY area_km2 DESC
```

### Load into GeoPandas

```python
import geopandas as gpd

gdf = gpd.read_parquet('bestand_bodemgebruik_2017.parquet')
print(f"CRS: {gdf.crs}")  # EPSG:28992
print(f"Rows: {len(gdf):,}")
print(gdf['bodemgebruik'].value_counts())

# Convert to WGS84 for web mapping
gdf_wgs84 = gdf.to_crs(epsg=4326)
```

## BBG vs NBBG — Methodology Change

Starting from reference year 2020, CBS switched to the **NBBG** (Nieuw Bestand
Bodemgebruik). Key differences:

| Aspect | BBG (this dataset, up to 2017) | NBBG (2020 onwards) |
|--------|-------------------------------|---------------------|
| Method | Manual interpretation of aerial photos | Semi-automated using base registries (BAG, BGT, BRT) |
| Base map | Top10NL topographic map | BGT (large-scale topography) + BRT |
| Buildings | Derived from Top10NL | Derived from BAG (building registry) |
| Classification | ~40 types | Similar but with adjustments |
| Consistency | Consistent across BBG series | New baseline, not directly comparable to BBG |

**Do not** combine BBG and NBBG data for time-series analysis without understanding the
methodological break. CBS publishes bridging tables and documentation for this purpose.

## Historical Context

CBS has been mapping Dutch land use since 1900. The BBG time series includes editions for:
1996, 2000, 2003, 2006, 2008, 2010, 2012, 2015, and 2017. Each edition used a similar
methodology (manual photo interpretation over topographic base maps), making them broadly
comparable for trend analysis.

Major trends visible in the BBG time series:
- Steady expansion of built-up area (residential, industrial)
- Decline in agricultural land
- Relatively stable forest coverage
- Growth of infrastructure (roads, railways)

## Caveats

- **EPSG:28992 coordinates**: Coordinates are in meters (RD New), not degrees. Transform
  to WGS84 for web maps or combining with international data.
- **Minimum mapping unit**: Most land use types have a 1-hectare minimum. Smaller patches
  may be merged into surrounding land use types.
- **Ground-level use only**: The classification reflects use at ground level. A park under
  a viaduct is classified as recreation, not as infrastructure.
- **Reference year**: The data reflects the situation in 2017, based on aerial photos from
  summer 2017 and the topographic base map of that year.
- **Not comparable with NBBG**: The 2020+ NBBG uses a different methodology. Do not create
  time series spanning both BBG and NBBG without consulting CBS methodology documentation.
- **Water areas**: The dataset includes both inland and coastal waters (Wadden Sea, North
  Sea within Dutch territory), so total area exceeds the land area of the Netherlands.
- **MultiPolygon geometries**: All features are MultiPolygon, even when consisting of a
  single polygon.


## Visualization Styles

Two Mapbox GL v8 styles are available for interactive map visualization via the PMTiles file.

Style files are Mapbox GL v8 JSON with relative PMTiles source paths. They can be
used with MapLibre GL JS, OpenLayers (via ol-mapbox-style), or any Mapbox GL v8-compatible renderer.

- **`styles/default.json`** — **Land use overview.** Colors polygons by `bodemgebruik` (14 broad categories): green for agriculture, dark green for forest, gray for built areas, yellow for recreation, blue for water. Classic land use map of the Netherlands.
- **`styles/by-detailed-use.json`** — **Detailed land use analysis.** Colors by `categorie` (38 fine-grained classes): distinguishes between arable land, greenhouses, grassland, orchards, different forest types, residential vs. industrial vs. commercial areas, and specific water bodies (IJsselmeer, Rijn & Maas, etc.). Best for detailed land use studies and comparing specific sub-categories.

Style files are at: `https://data.source.coop/cholmes/portolan-nl/cbs/bestand_bodemgebruik_2017/styles/`
## Also Available As

- **GeoParquet:** `bbg2017.parquet` (1.2 GB, 171,543 features, EPSG:28992)
- **PMTiles:** `bbg2017.pmtiles` (189 MB, for web map visualization)
- **WFS**: Live access via `https://service.pdok.nl/cbs/bestandbodemgebruik/2017/wfs/v1_0`
  (feature type: `bestandbodemgebruik:BBG2017`)
- **WMS**: Map images via `https://service.pdok.nl/cbs/bestandbodemgebruik/2017/wms/v1_0`
- **ATOM download**: Bulk download from PDOK

---
*Hand-maintained agent guide (ported from this collection's llms.txt in August 2026). Update it alongside collection.json.*

# Bevolkingsspreiding (Population Distribution) — CBS / Netherlands

## What This Dataset Is

INSPIRE-harmonized population distribution data for the Netherlands, published by
**CBS** (Centraal Bureau voor de Statistiek / Statistics Netherlands). Contains the
number of inhabitants at three geographic levels:

1. **1km squared grid** (pd-nl-grid-2012) — population per 1km squared cell on the European
   ETRS89-LAEA grid, reference year 2012
2. **NUTS2 provinces** (pd-nl-nuts2-2018) — population per province, reference year 2018
3. **LAU municipalities** (pd-nl-lau-2018) — population per municipality, reference year 2018

This is the Dutch contribution to the European INSPIRE Statistical Units / Population
Distribution theme (Directive 2007/2/EC, Annex III theme 10).

**Source:** https://www.pdok.nl/introductie/-/article/cbs-bevolkingsspreiding-population-distribution-
**Provider:** CBS (Centraal Bureau voor de Statistiek / Statistics Netherlands)
**License:** CC0 (public domain)

## How to Access

Three GeoParquet files (one per geographic level) and a combined PMTiles file for
web visualization are available from Source Cooperative. Native CRS is **EPSG:3035**
(ETRS89-LAEA) — coordinates are in meters.

| File | Features | Size | Contents |
|------|----------|------|----------|
| `grid.parquet` | 30,641 | 3.8 MB | 1km² grid cells with population (2012) |
| `lau.parquet` | 380 | 635 KB | Municipal boundaries with population (2018) |
| `nuts2.parquet` | 12 | 200 KB | Provincial boundaries with population (2018) |
| `bevolkingsspreiding.pmtiles` | — | 61 MB | All three layers as vector tiles |

**Base URL:** `https://data.source.coop/cholmes/portolan-nl/cbs/bevolkingsspreiding/`

```python
import duckdb

con = duckdb.connect()
con.execute("INSTALL spatial; LOAD spatial;")

URL = 'https://data.source.coop/cholmes/portolan-nl/cbs/bevolkingsspreiding/grid.parquet'
df = con.execute(f"SELECT * FROM read_parquet('{URL}') LIMIT 5").df()
```

Also available via WFS, WMS, and ATOM from PDOK:
- **WFS:** `https://service.pdok.nl/cbs/pd/wfs/v1_0`
- **WMS:** `https://service.pdok.nl/cbs/pd/wms/v1_0`
- **ATOM:** `https://service.pdok.nl/cbs/pd/atom/v1_0/index.xml`

## Schema — Field Meanings (Grid Feature Type)

| Field | Type | Meaning |
|-------|------|---------|
| `gid` | string | **Grid cell ID** following the European grid naming convention: `NL_CRS3035RES1000mN{northing}E{easting}`. Encodes CRS, resolution, and position. |
| `gmsurface` | string | Grid cell surface identifier. |
| `measure` | string | Statistical measure: `populationAtResidencePlace` — population counted at place of residence. |
| `stat` | string | Statistic type: `T` = total. |
| `freq` | string | Frequency: `A` = annual. |
| `obsvalue` | float64 | **The population count** — number of inhabitants in the grid cell or region. This is the key data column. |
| `obsstatus` | string | Observation status: `A` = actual value. |
| `periodofreference` | string | Reference year for the observation (e.g. `2012`). |

## Important Columns

The columns you will most often use:

- **`gid`** — cell/region identifier (the grid cell ID encodes its geographic position)
- **`obsvalue`** — the population count
- **`periodofreference`** — the reference year
- **geometry** — the cell or region boundary polygon

## Coordinate Reference System — EPSG:3035

Unlike most Dutch geodatasets which use **EPSG:28992** (RD New / Amersfoort), this
dataset uses **EPSG:3035** (ETRS89-LAEA Europe). This is the standard European grid
CRS used by Eurostat and INSPIRE for cross-border statistical comparisons.

Key implications:
- Coordinates are in **metres** but on a Lambert Azimuthal Equal Area projection
  centred on the European continent
- Grid cell IDs encode northing/easting in EPSG:3035 coordinates
- To combine with other Dutch datasets (e.g. BAG, bestuurlijke gebieden), you must
  **reproject** from EPSG:3035 to EPSG:28992 or EPSG:4326

```sql
-- Example: reproject from EPSG:3035 to WGS84
INSTALL spatial; LOAD spatial;
SELECT ST_Transform(geom, 'EPSG:3035', 'EPSG:4326') AS geom_wgs84
```

## INSPIRE Context

This dataset is part of the INSPIRE Directive implementation:
- **Theme:** Annex III, theme 10 — Population Distribution / Demography
- **Spatial scope:** Statistical Units (grid, NUTS, LAU)
- The 1km squared grid follows the **EEA reference grid** (ETRS89-LAEA), enabling
  seamless combination with population grids from other EU member states
- NUTS2 regions correspond to Dutch provinces
- LAU regions correspond to Dutch municipalities (gemeenten)

## Useful Query Patterns

### Fetch grid population data via WFS (using ogr2ogr)

```bash
ogr2ogr -f GeoJSON grid_pop.geojson \
  "WFS:https://service.pdok.nl/cbs/pd/wfs/v1_0" \
  pd-nl-grid-2012 \
  -lco RFC7946=YES
```

### Fetch municipality-level population

```bash
ogr2ogr -f GeoJSON lau_pop.geojson \
  "WFS:https://service.pdok.nl/cbs/pd/wfs/v1_0" \
  pd-nl-lau-2018
```

### Load ATOM download into DuckDB

If you download the GML files from the ATOM service:

```sql
INSTALL spatial; LOAD spatial;

SELECT gid, obsvalue, periodofreference,
       ST_GeomFromWKB(geom) AS geometry
FROM ST_Read('pd-nl-grid-2012.gml')
ORDER BY obsvalue DESC
LIMIT 20
```

### Most populated grid cells

```sql
SELECT gid, obsvalue AS population
FROM population_grid
WHERE obsvalue > 0
ORDER BY obsvalue DESC
LIMIT 20
```

### Population by province (NUTS2)

```sql
SELECT gid AS province_code, obsvalue AS population
FROM nuts2_population
ORDER BY obsvalue DESC
```


## Visualization Styles

One Mapbox GL v8 style is available for interactive map visualization via the PMTiles file.

Style files are Mapbox GL v8 JSON with relative PMTiles source paths. They can be
used with MapLibre GL JS, OpenLayers (via ol-mapbox-style), or any Mapbox GL v8-compatible renderer.

- **`styles/default.json`** — **Population density heatmap.** Red sequential ramp on `obsvalue` (population count) across the grid layer. White (low) to dark red (high density). Shows the Randstad concentration and rural/urban contrasts across the Netherlands.

Style files are at: `https://data.source.coop/cholmes/portolan-nl/cbs/bevolkingsspreiding/styles/`
## Caveats

- **EPSG:3035, not EPSG:28992**: This is one of the few Dutch datasets that uses the
  European LAEA projection instead of the Dutch national RD New system. Make sure to
  handle the CRS correctly when combining with other Dutch data.
- **Different reference years**: Grid data is from 2012, while NUTS2 and LAU data is
  from 2018. Do not directly compare grid totals with regional totals without accounting
  for population growth.
- **INSPIRE field naming**: Fields use INSPIRE-compliant names (`obsvalue`, `obsstatus`,
  `periodofreference`) rather than intuitive Dutch or English names.
- **Small dataset**: The grid parquet (3.8 MB) and regional files (<1 MB each) are small
  enough to load entirely into memory for analysis.
- **Grid cell IDs encode position**: The `gid` field contains the EPSG:3035 coordinates
  of the grid cell origin, which can be parsed to reconstruct the cell location without
  needing the geometry.
- **Population counts only**: This dataset contains only total population counts, not
  demographic breakdowns (age, gender, etc.). For detailed demographic data, use other
  CBS datasets like Wijken en Buurten.

---
*Hand-maintained agent guide (ported from this collection's llms.txt in August 2026). Update it alongside collection.json.*

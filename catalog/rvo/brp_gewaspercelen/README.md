# BRP Gewaspercelen (Agricultural Crop Parcels)

Every agricultural parcel in the Netherlands with its registered crop type, from the Basisregistratie Gewaspercelen (BRP) — the national crop parcel registration. Published as a **multi-year partitioned collection**: one GeoParquet + PMTiles partition per BRP definitive edition. Covers **2009–2025** — 17 years, **18.3 M parcels total**. Published by RVO (Netherlands Enterprise Agency) via PDOK.

The BRP is an annual snapshot reflecting what farmers register each May 15 for Common Agricultural Policy (CAP) subsidy applications; each 'definitief' edition is finalized after verification.

> **AI/Agent users:** See [llms.txt](./llms.txt) for field descriptions, query examples, and usage tips.

![netherlands](https://img.shields.io/badge/netherlands-blue) ![agriculture](https://img.shields.io/badge/agriculture-green) ![open-data](https://img.shields.io/badge/open--data-blue) ![pdok](https://img.shields.io/badge/pdok-blue) ![geoparquet](https://img.shields.io/badge/geoparquet-blue) ![pmtiles](https://img.shields.io/badge/pmtiles-blue) ![multi-year](https://img.shields.io/badge/multi--year-blue)

## Spatial Coverage

- **Bounding Box**: [3.36, 50.75, 7.22, 53.50] — all agricultural land in the Netherlands.

## Temporal Coverage

| Year | Parcels | Snapshot date | Source format |
|------|--------:|---------------|---------------|
| 2009 |   819,146 | 2009-05-15 | Esri File Geodatabase (zip), schema-normalized |
| 2010 |   782,837 | 2010-05-15 | Esri File Geodatabase (zip), schema-normalized |
| 2011 |   779,674 | 2011-05-15 | Esri File Geodatabase (zip), schema-normalized |
| 2012 |   772,865 | 2012-05-15 | Esri File Geodatabase (zip), schema-normalized |
| 2013 |   762,725 | 2013-05-15 | Esri File Geodatabase (zip), schema-normalized |
| 2014 |   765,006 | 2014-05-15 | Esri File Geodatabase (zip), schema-normalized |
| 2015 |   790,930 | 2015-05-15 | Esri File Geodatabase (zip), schema-normalized |
| 2016 |   786,572 | 2016-05-15 | Esri File Geodatabase (zip), schema-normalized |
| 2017 |   785,710 | 2017-05-15 | Esri File Geodatabase (zip), schema-normalized |
| 2018 |   774,822 | 2018-05-15 | Esri File Geodatabase (zip), schema-normalized |
| 2019 |   772,565 | 2019-05-15 | Esri File Geodatabase (zip), schema-normalized |
| 2020 |   773,139 | 2020-05-15 | PDOK GeoPackage, as-is |
| 2021 |   772,539 | 2021-05-15 | PDOK GeoPackage, as-is |
| 2022 |   758,504 | 2022-05-15 | PDOK GeoPackage, as-is |
| 2023 | 2,588,592 | 2023-05-15 | PDOK GeoPackage, as-is |
| 2024 | 2,493,631 | 2024-05-15 | PDOK GeoPackage, as-is |
| 2025 | 2,331,084 | 2025-05-15 | PDOK GeoPackage, as-is |

The big jump from 2022→2023 is the addition of **Landschapselementen** (landscape elements — ditches, hedgerows, tree rows, ponds) to the BRP scope. 2009–2019 partitions were derived from upstream Esri File Geodatabases with a different column schema; see Processing Notes for what was renamed/cast/dropped.

## Layout

Each year is **self-contained in its own subfolder** — download only what you need, or use the parent-level glob for cross-year analysis.

```
brp_gewaspercelen/
├── collection.json                                 STAC Collection (multi-year, parent)
├── README.md                                       this file (overall guide)
├── llms.txt                                        agent/LLM usage guide (cross-year)
├── thumbnail.png
├── versions.json
├── styles/                                         canonical base styles (latest-year PMTiles)
│   └── default.json, by-category.json, by-crop.json, landscape-elements.json
├── scripts/
│   ├── generate_items.py                           rebuild STAC items from per-year stats
│   ├── generate_year_docs.py                       rebuild per-year README + llms.txt
│   └── regen_year_styles.py                        propagate base style tweaks to per-year copies
│
├── 2009/                                           ────────────────────────────────────
│   ├── brp_gewaspercelen_2009.json                 STAC Item
│   ├── brp_gewaspercelen_2009.parquet              GeoParquet (zstd, bbox covering, sorted)
│   ├── brp_gewaspercelen_2009.pmtiles              vector tiles
│   ├── brpgewaspercelen_definitief_2009.zip        original Esri FGDB (zip), schema normalized
│   ├── README.md                                   year-specific overview
│   ├── llms.txt                                    year-specific agent guide
│   └── styles/                                     per-year style copies pointing at this PMTiles
│
├── 2010/  …  2019/                                 same layout, all from FGDB zip sources
│
├── 2020/                                           ────────────────────────────────────
│   ├── brp_gewaspercelen_2020.json                 STAC Item
│   ├── brp_gewaspercelen_2020.parquet
│   ├── brp_gewaspercelen_2020.pmtiles
│   ├── brpgewaspercelen_definitief_2020.gpkg       original PDOK GeoPackage (no transformation)
│   ├── README.md
│   ├── llms.txt
│   └── styles/
│
└── 2021/ … 2025/                                   same layout, all from GeoPackage sources
```

The collection-level `data` asset uses the **`portolan:glob` syntax** (per [portolan-spec / formats/vector.md](https://github.com/portolan-sdi/portolan-spec/blob/main/formats/vector.md)) — `href: "./*/brp_gewaspercelen_*.parquet"` — so DuckDB, GDAL, and PyArrow can read every year as a single dataset from one URL.

## Schema

| Column | Type | Description |
|--------|------|-------------|
| id | int64 | Feature ID within the year's partition. **Not stable across years** — the BRP re-registers parcels each May. Use a spatial join to follow a parcel through time. |
| category | string | Broad crop category (Grasland, Bouwland, Landschapselement, Natuurterrein, Braakland, Overige). Landschapselement first appears in 2023. |
| gewas | string | Specific crop name within the category (e.g. Grasland blijvend, Aardappelen consumptie, Mais snij-). |
| gewascode | int32 | Numeric crop code. **Stable across years** — safest field for cross-year crop-type filters. |
| jaar | int32 | Registration year — also encoded in the partition filename. |
| status | string | Registration status — 'Definitief' for everything in this collection. |
| geom | binary | Parcel boundary polygon in EPSG:28992 (Amersfoort / RD New), WKB encoded. |

## Map Styles

Four pre-built MapLibre GL styles, all driven from a single canonical base in `styles/`. Per-year copies are auto-generated into each year's `YYYY/styles/` directory so the year folder is self-contained; edit the base, then run `python scripts/regen_year_styles.py`.

| Style | Description |
|-------|-------------|
| [Default](./styles/default.json) | Natural agricultural palette — greens for grass and landscape, yellow for arable. |
| [By Category](./styles/by-category.json) | Distinct colors per broad category. |
| [By Crop Type](./styles/by-crop.json) | Individual colors for the 18 most common specific crops. |
| [Landscape Elements](./styles/landscape-elements.json) | Highlights ditches, hedgerows, tree rows, ponds (only meaningful from 2023 on). |

## Quick Start — Single Year

```python
import duckdb
con = duckdb.connect()
con.execute("INSTALL spatial; LOAD spatial;")

URL = 'https://data.source.coop/cholmes/portolan-nl/rvo/brp_gewaspercelen/2025/brp_gewaspercelen_2025.parquet'

df = con.execute(f"""
    SELECT category, COUNT(*) AS parcels,
           ROUND(SUM(ST_Area(geom)) / 10000, 0) AS area_ha
    FROM read_parquet('{URL}')
    GROUP BY category ORDER BY area_ha DESC
""").df()
print(df)
```

DuckDB streams via HTTP range requests — no full download needed.

## Quick Start — Cross-Year (the partitioned glob)

```python
import duckdb
con = duckdb.connect()
con.execute("INSTALL spatial; LOAD spatial;")

# The collection's `data` asset is a glob — pass it straight through.
GLOB = 'https://data.source.coop/cholmes/portolan-nl/rvo/brp_gewaspercelen/*/brp_gewaspercelen_*.parquet'

# How much grassland each year?
df = con.execute(f"""
    SELECT jaar, COUNT(*) AS parcels,
           ROUND(SUM(ST_Area(geom)) / 10000, 0) AS hectares
    FROM read_parquet('{GLOB}')
    WHERE category = 'Grasland'
    GROUP BY jaar ORDER BY jaar
""").df()
print(df)
```

### Example — "fields that haven't had potatoes in the last three years"

Parcel `id` is *not* stable across years, so identify parcels by geometry. Use the 2025 parcels as the universe and check 2023–2025 for any potato crops.

```python
POTATO_CODES = (2014, 2015, 2017, 2016)   # consumption, seed, starch, etc.

df = con.execute(f"""
WITH year_potato AS (
    SELECT ST_Centroid(geom) AS pt
    FROM read_parquet('{GLOB}')
    WHERE jaar BETWEEN 2023 AND 2025
      AND gewascode IN {POTATO_CODES}
)
SELECT p.id, p.gewas, ST_AsText(p.geom) AS geom_wkt
FROM read_parquet('{URL}') p           -- 2025 universe
LEFT JOIN year_potato yp
       ON ST_Intersects(p.geom, yp.pt)
WHERE yp.pt IS NULL
LIMIT 10
""").df()
```

For production cross-year tracking, write a one-time parcel-identity table by spatial-joining all 17 years' centroids:

```sql
INSTALL spatial; LOAD spatial;
CREATE TABLE parcel_identity AS
  SELECT row_number() OVER () AS pid, ST_Centroid(geom) AS pt
  FROM read_parquet('…/brp_gewaspercelen_2025.parquet');

CREATE TABLE parcel_history AS
  SELECT pi.pid, p.jaar, p.gewas, p.gewascode, p.category
  FROM read_parquet('…/*/brp_gewaspercelen_*.parquet') p
  JOIN parcel_identity pi ON ST_Intersects(p.geom, pi.pt);
```

Then rotation/diversity/trajectory queries are just SQL on `parcel_history`:

```sql
-- Crops most often planted the year after potatoes
WITH potato_then AS (
    SELECT pid, jaar AS y FROM parcel_history
    WHERE gewascode IN (2014, 2015, 2016, 2017)
)
SELECT next_yr.gewas, COUNT(*) AS following_potato
FROM potato_then pt
JOIN parcel_history next_yr ON next_yr.pid = pt.pid AND next_yr.jaar = pt.y + 1
GROUP BY next_yr.gewas ORDER BY following_potato DESC LIMIT 20;

-- Permanent grassland (Grasland every year 2009–2025)
SELECT pid FROM parcel_history
GROUP BY pid
HAVING COUNT(*) = 17 AND COUNT(*) FILTER (WHERE category = 'Grasland') = 17;
```

See [llms.txt](./llms.txt) for more cross-year examples (crop rotation, land-use trajectories, year-over-year volatility, Grasland → Bouwland conversions).

## Source Files

Each year keeps its original source file alongside the derived GeoParquet + PMTiles, exposed as the `source` asset on each STAC item:

- **2020–2025**: `brpgewaspercelen_definitief_YYYY.gpkg` — PDOK GeoPackages. Schemas exactly match the derived GeoParquet — no field renames or value transformations performed.
- **2009–2019**: `brpgewaspercelen_definitief_YYYY.zip` — PDOK Esri File Geodatabases inside zip archives. Upstream schema differs (`OGC_FID`, `CAT_GEWASCATEGORIE`, `GWS_GEWAS`, `GWS_GEWASCODE` as varchar, plus `Shape_Length`/`Shape_Area` or `GEOMETRIE_Length`/`GEOMETRIE_Area`). The derived GeoParquets are **normalized**: columns renamed (`OGC_FID`→`id`, `CAT_GEWASCATEGORIE`→`category`, `GWS_GEWAS`→`gewas`, `GWS_GEWASCODE`→`gewascode`), `gewascode` cast varchar→int32, `jaar` synthesized from the filename, `status` set to `'Definitief'`, and the source-side length/area columns dropped (they are recomputable with `ST_Length`/`ST_Area`). Geometry stays in EPSG:28992. This normalization is documented on each historical item's `source` asset.

## Files

| File pattern | Description |
|---|---|
| `YYYY/brp_gewaspercelen_YYYY.parquet` | GeoParquet (zstd, bbox covering, spatially sorted). 200 MB–1.6 GB per year. |
| `YYYY/brp_gewaspercelen_YYYY.pmtiles` | PMTiles for web mapping. ~220 MB–~640 MB per year. |
| `YYYY/brp_gewaspercelen_YYYY.json` | STAC Item per year. |
| `YYYY/README.md` + `YYYY/llms.txt` | Year-specific docs (each year folder stands alone). |
| `YYYY/styles/*.json` | Per-year MapLibre style copies of the canonical base. |
| `YYYY/brpgewaspercelen_definitief_YYYY.gpkg` | Original PDOK GeoPackage (2020–2025). |
| `YYYY/brpgewaspercelen_definitief_YYYY.zip` | Original PDOK Esri File Geodatabase, zipped (2009–2019). |
| `2025/brp_gewaspercelen_2025.pmtiles` | Also the **collection-level** PMTiles asset (latest year). |
| `thumbnail.png` | Map preview. |
| `llms.txt` | Agent/LLM usage guide. |

## STAC Metadata

- **Root**: `../../catalog.json` (Portolan NL)
- **Parent**: `../catalog.json` (RVO)
- **Items**: `brp_gewaspercelen_2020.json` … `brp_gewaspercelen_2025.json`
- **Collection-level data asset** is a `portolan:glob` (`./*/brp_gewaspercelen_*.parquet`) — primary entry point for cross-year analysis.

## Source

- [PDOK dataset page](https://www.pdok.nl/introductie/-/article/basisregistratie-gewaspercelen-brp-)
- Per-year ATOM download URLs:
  - 2020–2025: `https://service.pdok.nl/rvo/gewaspercelen/atom/downloads/brpgewaspercelen_definitief_YYYY.gpkg`
  - 2009–2019: `https://service.pdok.nl/rvo/gewaspercelen/atom/downloads/brpgewaspercelen_definitief_YYYY.zip` (Esri FGDB)

## Processing Notes

Per-year GeoPackages from PDOK were converted to GeoParquet with `ogr2ogr -f Parquet` using `COMPRESSION=ZSTD`, `SORT_BY_BBOX=YES`, `WRITE_COVERING_BBOX=YES` (default), `GEOMETRY_NAME=geom`, and `ROW_GROUP_SIZE=100000`, preserving the native EPSG:28992 CRS — per OGC [Best Practices for Distributing GeoParquet](https://github.com/opengeospatial/geoparquet/blob/main/format-specs/distributing-geoparquet.md). The 2025 GeoPackage had a few mixed-dimension geometries that required `-dim XY` to flatten to 2D before conversion. PMTiles built via `ogr2ogr -f GeoJSONSeq … -t_srs EPSG:4326 | tippecanoe -Z 0 -z 15 --drop-densest-as-needed --detect-shared-borders`.

## License

[CC0-1.0](https://creativecommons.org/publicdomain/zero/1.0/) (public domain)

## Contact

Chris Holmes <cholmes@9eo.org>

---

*Part of [Portolan NL](https://source.coop/cholmes/portolan-nl) — Cloud-Native Dutch Geodata*

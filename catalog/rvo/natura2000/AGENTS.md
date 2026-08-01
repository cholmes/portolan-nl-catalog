# Natura 2000 Protected Areas — RVO / Netherlands

## What This Dataset Is

Boundaries of all 162 Natura 2000 protected areas in the Netherlands, designated under the
EU Birds Directive (Vogelrichtlijn) and Habitats Directive (Habitatrichtlijn). Contains
209 features because some areas have separate features for different designation types.

Natura 2000 is the largest coordinated network of protected areas in the world, spanning all
EU member states. In the Netherlands, these 162 areas carry the **strongest nature protection
in Dutch law** — any plan or project that may significantly affect a Natura 2000 area requires
a preliminary assessment (voortoets) and potentially a full appropriate assessment (passende
beoordeling) under the Wet natuurbescherming.

Since 2019, this dataset has been politically critical due to the Dutch **nitrogen crisis**
(stikstofcrisis): the Council of State struck down the PAS program because nitrogen deposition
exceeded critical loads in Natura 2000 areas, halting thousands of construction and farming projects.

Includes both terrestrial and marine areas extending into the North Sea EEZ (e.g., Doggerbank,
Noordzeekustzone, Voordelta).

**Source:** https://www.pdok.nl/introductie/-/article/natura-2000
**Provider:** RVO (Rijksdienst voor Ondernemend Nederland / Netherlands Enterprise Agency)
**License:** CC0 (public domain)

## How to Access

The data is a GeoParquet file in **EPSG:28992** (Amersfoort / RD New). Use DuckDB with the
spatial extension.

```python
import duckdb

con = duckdb.connect()
con.execute("INSTALL spatial; LOAD spatial;")

URL = 'https://data.source.coop/cholmes/portolan-nl/rvo/natura2000/natura2000.parquet'

df = con.execute(f"""
    SELECT * FROM read_parquet('{URL}')
    LIMIT 5
""").df()
```

The file is ~7.5 MB (209 features) — loads entirely into memory.

## Schema — Field Meanings

| Field | Type | Meaning |
|-------|------|---------|
| `geometry` | WKB MultiPolygon | Area boundary in **EPSG:28992** (Amersfoort / RD New). |
| `naam_n2k` | string | **Name** of the Natura 2000 area (Dutch). |
| `nr` | int32 | Official area number (1–166). The key identifier for joining with other datasets. |
| `vhn_new` | int16 | **Designation type code**: 1=VR (Birds), 2=HR (Habitats), 3=VR+HR (Both), 9=HR quarry. |
| `beschermin` | string | Designation type as text: `VR`, `HR`, `VR+HR`, or `HR groeve`. |
| `sitecode_v` | string | EU site code for Birds Directive (blank if HR-only). |
| `sitecode_h` | string | EU site code for Habitats Directive (blank if VR-only). |
| `status` | string | Legal designation status (free-text with inconsistent date formats). |
| `shape_area` | float64 | Area per feature in m². **Per-feature, not per site** — sum by `nr` for total site area. |
| `shape_len` | float64 | Perimeter per feature in metres. |
| `kadaster` | string | Cadastral reference number. |
| `staatscour` | string | Staatscourant (Government Gazette) publication reference. |
| `puuid` | string | Persistent unique identifier. |
| `fuuid` | string | Feature unique identifier. |
| `id` | int64 | Feature ID. |
| `objectid` | int32 | Internal object ID. |

## Important Columns

The columns you'll actually use:

- **`naam_n2k`** — area name
- **`nr`** — official area number (use for grouping/joining)
- **`beschermin`** (or `vhn_new`) — designation type (VR/HR/VR+HR)
- **`shape_area`** — area in m² (per-feature)
- **`geometry`** — area boundary polygon

## 209 Features ≠ 162 Areas

**Critical:** The dataset has 209 features for 162 distinct Natura 2000 areas. Multiple features
per area occur when parts of the area fall under different EU directive designations. For example,
De Wieden (nr=35) has separate VR and VR+HR features.

**Do not count features to determine the number of protected areas.** Use `COUNT(DISTINCT nr)`.

Distribution by designation type:
- HR (Habitats Directive only): 108 features
- VR+HR (Both directives): 58 features
- VR (Birds Directive only): 39 features
- HR groeve (Habitats quarry): 4 features

## Geometry Notes

- CRS is **EPSG:28992** (Amersfoort / RD New). Reproject to EPSG:4326 for web maps.
- Extent extends into the **North Sea** for marine areas (e.g., Doggerbank, Klaverbank).
- The source had 3D Measured geometry (Z and M dimensions) — stripped to 2D in this export.
- For area, use `shape_area` rather than computing from geometry for consistency with official figures.

## Useful Query Patterns

### List all unique Natura 2000 areas

```sql
SELECT nr, naam_n2k,
       STRING_AGG(DISTINCT beschermin, ', ') AS designations,
       SUM(shape_area) / 1e6 AS total_area_km2
FROM read_parquet('https://data.source.coop/cholmes/portolan-nl/rvo/natura2000/natura2000.parquet')
GROUP BY nr, naam_n2k
ORDER BY total_area_km2 DESC
```

### Count areas by designation type

```sql
SELECT beschermin, COUNT(*) AS features, COUNT(DISTINCT nr) AS distinct_areas
FROM read_parquet('https://data.source.coop/cholmes/portolan-nl/rvo/natura2000/natura2000.parquet')
GROUP BY beschermin
ORDER BY features DESC
```

### Find the largest areas

```sql
SELECT nr, naam_n2k, SUM(shape_area) / 1e6 AS area_km2
FROM read_parquet('https://data.source.coop/cholmes/portolan-nl/rvo/natura2000/natura2000.parquet')
GROUP BY nr, naam_n2k
ORDER BY area_km2 DESC
LIMIT 10
```

### Check if a point falls within a Natura 2000 area

```sql
INSTALL spatial; LOAD spatial;

SELECT naam_n2k, beschermin
FROM read_parquet('https://data.source.coop/cholmes/portolan-nl/rvo/natura2000/natura2000.parquet')
WHERE ST_Intersects(
    ST_GeomFromWKB(geometry),
    ST_Transform(ST_Point(5.39, 52.16), 'EPSG:4326', 'EPSG:28992')
)
```

Note: The point must be transformed to EPSG:28992 to match the data CRS.

### Areas designated under both directives

```sql
SELECT naam_n2k, nr
FROM read_parquet('https://data.source.coop/cholmes/portolan-nl/rvo/natura2000/natura2000.parquet')
WHERE vhn_new = 3
ORDER BY naam_n2k
```

### Load into GeoPandas

```python
import geopandas as gpd

gdf = gpd.read_parquet(
    'https://data.source.coop/cholmes/portolan-nl/rvo/natura2000/natura2000.parquet'
)
# Reproject to WGS84:
gdf_wgs = gdf.to_crs(epsg=4326)
```

## Related Datasets

- **National Parks** (also in this catalog): Dutch national designation; many overlap with
  Natura 2000 but are separate legal systems.
- **AERIUS** (RIVM): Nitrogen deposition calculations use Natura 2000 boundaries as receptor areas.
- **Habitattypenkaart**: Detailed habitat type mapping within each Natura 2000 area.

## Caveats

- **209 features ≠ 162 areas** — always group by `nr` when counting or computing areas.
- `shape_area` is per-feature. For multi-feature areas, geometries under different designations
  may overlap, so summing all `shape_area` values overestimates total protected area.
- The `status` field has inconsistent date formats — not suitable for programmatic date extraction.
- The 4 "HR groeve" features are limestone quarries (mergelgroeven) in South Limburg — a special
  sub-category of the Habitats Directive.
- Marine areas mean the extent reaches far into the North Sea (up to Y=852,887 in RD coordinates).


## Visualization Styles

Two Mapbox GL v8 styles are available for interactive map visualization via the PMTiles file.

Style files are Mapbox GL v8 JSON with relative PMTiles source paths. They can be
used with MapLibre GL JS, OpenLayers (via ol-mapbox-style), or any Mapbox GL v8-compatible renderer.

- **`styles/default.json`** — Light yellow-green fill with green outlines and area name labels. Shows the 162+ Natura 2000 protected areas. Visually lighter than Nationale Parken to distinguish the two protection regimes.
- **`styles/by-directive.json`** — **EU protection framework analysis.** Colors by `beschermin` (protection type): sky blue for Birds Directive (VR, 39 areas), forest green for Habitats Directive (HR, 108 areas), teal for both directives (VR+HR, 58 areas), brown for quarry sites (HR groeve, 4 areas). Shows which EU legal framework protects each area — important for understanding management requirements and legal obligations.

Style files are at: `https://data.source.coop/cholmes/portolan-nl/rvo/natura2000/styles/`
## Also Available As

- **PMTiles (vector tiles):** `natura2000.pmtiles` — for web map visualization.
- **OGC API Features:** `https://api.pdok.nl/rvo/natura2000/ogc/v1`.
- **GeoPackage:** `https://service.pdok.nl/rvo/natura2000/atom/downloads/natura2000.gpkg`.

---
*Hand-maintained agent guide (ported from this collection's llms.txt in August 2026). Update it alongside collection.json.*

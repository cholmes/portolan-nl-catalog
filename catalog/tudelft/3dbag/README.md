# 3D BAG

All ~10.8 million buildings in the Netherlands as 3D models, produced by the [3D Geoinformation Research Group](https://3d.bk.tudelft.nl/) at [TU Delft](https://www.tudelft.nl/) in collaboration with [3DGI](https://3dgi.xyz/).

The [3D BAG](https://3dbag.nl/) enriches the official [BAG building registry](https://www.pdok.nl/introductie/-/article/basisregistratie-adressen-en-gebouwen-ba-1) — maintained by [Kadaster](https://www.kadaster.nl/) — with building heights, roof types, volumes, and surface areas derived from the [AHN](https://www.ahn.nl/) (Actueel Hoogtebestand Nederland) national point cloud survey. The source BAG footprints and attributes are available in this catalog as [Buildings (Panden)](../../kadaster/panden/).

> AI/Agent users: See [AGENTS.md](./AGENTS.md) for field descriptions, query examples, and usage tips.

![netherlands](https://img.shields.io/badge/netherlands-blue) ![3d-buildings](https://img.shields.io/badge/3d--buildings-blue) ![open-data](https://img.shields.io/badge/open--data-blue) ![geodata](https://img.shields.io/badge/geodata-blue) ![cloud-native](https://img.shields.io/badge/cloud--native-blue) ![geoparquet](https://img.shields.io/badge/geoparquet-blue) ![stac](https://img.shields.io/badge/stac-blue) ![pmtiles](https://img.shields.io/badge/pmtiles-blue) ![tu-delft](https://img.shields.io/badge/tu--delft-blue)

## Data Sources

| Source | Provider | What it contributes |
|--------|----------|-------------------|
| [BAG](https://www.pdok.nl/introductie/-/article/basisregistratie-adressen-en-gebouwen-ba-1) | [Kadaster](https://www.kadaster.nl/) | Building footprints, construction year, status, usage function, floor area |
| [AHN](https://www.ahn.nl/) | [Het Waterschapshuis](https://www.hetwaterschapshuis.nl/) | LiDAR point cloud (AHN3/AHN4/AHN5) for height derivation |

The [3D BAG reconstruction pipeline](https://3d.bk.tudelft.nl/projects/3dbag/) automatically combines these two open datasets, using the AHN point cloud to compute building heights, roof geometry, volumes, and surface areas for every BAG building footprint. Models are validated with [val3dity](https://github.com/tudelft3d/val3dity).

## Spatial Coverage

- **Bounding Box**: [3.36, 50.75, 7.23, 53.50] (all of the Netherlands)

## Files

This collection contains three files derived from the 3D BAG:

### 3dbag-lod13.pmtiles (1.2 GB)

**Vector tiles for web map visualization.** Contains LOD 1.3 building-part polygons (14.1M features) with pre-computed `height` and `base_height` fields ready for [MapLibre GL fill-extrusion](https://maplibre.org/maplibre-style-spec/layers/#fill-extrusion) rendering. EPSG:4326, zoom levels 0-15.

### 3dbag-lod13.parquet (747 MB)

**GeoParquet for analytical queries.** Same LOD 1.3 building-part data as the PMTiles in the original Dutch coordinate system (EPSG:7415 — Amersfoort / RD New + NAP height). 14.1M rows. Use for spatial joins, bulk analysis, and processing.

### 3dbag-pand.parquet (1.3 GB)

**Whole-building GeoParquet with full 3D attributes.** One row per building (10.8M rows), 62 columns including volumes, surface areas, floor counts, roof types, and AHN quality metrics. EPSG:7415. Join to the LOD 1.3 parts on `identificatie` for combined analysis.

## Schema — LOD 1.3 Building Parts

The LOD 1.3 files (PMTiles and GeoParquet) share this schema:

| Field | Type | Meaning |
|-------|------|---------|
| `identificatie` | string | **BAG building ID** (16 chars). Links to [Kadaster BAG](../../kadaster/panden/). First 4 digits = municipality code. |
| `b3_pand_deel_id` | int64 | **Building-part ID** within a building. Buildings are split where roof heights differ. |
| `b3_dd_id` | int64 | **Sub-part ID** within a building part. |
| `height` | double | **Building part height** in meters (roof 70th percentile minus ground elevation). Use as `fill-extrusion-height`. |
| `base_height` | double | **Base elevation** relative to ground in meters. Use as `fill-extrusion-base` for stepped parts. |
| `dak_type` | string | **Roof type**: `horizontal`, `slanted`, `multiple horizontal`, or `unknown`. |
| `bouwjaar` | int64 | **Construction year** from BAG. 9999 = unknown. |
| `status` | string | **Building status** from BAG (e.g. `Pand in gebruik`). |
| `gebruiksdoel` | string | **Usage function** from BAG (e.g. `woonfunctie`, `kantoorfunctie`). Comma-separated for mixed use. |
| `oppervlakte_min` | int64 | **Min floor area** (m²) of dwelling units. |
| `oppervlakte_max` | int64 | **Max floor area** (m²) of dwelling units. |
| `aantal_verblijfsobjecten` | int64 | **Number of dwelling units** in the building. |

## Schema — Whole Buildings (3dbag-pand.parquet)

The whole-building file has 62 columns. Key fields beyond the LOD 1.3 schema:

| Field | Type | Meaning |
|-------|------|---------|
| `b3_h_maaiveld` | double | Ground level elevation (m, NAP datum) |
| `b3_h_nok` | double | Ridge line height (m) |
| `b3_bouwlagen` | double | Estimated floor count |
| `b3_volume_lod12` | double | Building volume at LOD 1.2 (m³) |
| `b3_volume_lod13` | double | Building volume at LOD 1.3 (m³) |
| `b3_volume_lod22` | double | Building volume at LOD 2.2 (m³) |
| `b3_opp_grond` | double | Ground floor area (m²) |
| `b3_opp_dak_plat` | double | Flat roof area (m²) |
| `b3_opp_dak_schuin` | double | Sloped roof area (m²) |
| `b3_opp_buitenmuur` | double | Exterior wall area (m²) |
| `b3_opp_scheidingsmuur` | double | Party/shared wall area (m²) |
| `b3_dak_type` | string | Roof type classification |
| `b3_rmse_lod12/13/22` | double | Reconstruction accuracy (RMSE in meters) |
| `b3_pw_bron` | string | Point cloud source (`ahn3`, `ahn4`, `ahn5`) |
| `b3_kas_warenhuis` | bool | Greenhouse/warehouse flag |
| `b3_is_glas_dak` | bool | Glass roof flag |
| `oorspronkelijkbouwjaar` | double | Construction year |

See the full [3D BAG attribute documentation](https://docs.3dbag.nl/en/schema/attributes/) for all 62 fields.

## How the Files Relate

- **3dbag-lod13.pmtiles** and **3dbag-lod13.parquet** contain the same data — building parts with BAG attributes and computed heights — in different formats (vector tiles vs. GeoParquet) and CRS (EPSG:4326 vs. EPSG:7415).
- **3dbag-pand.parquet** is one level up: whole buildings (not parts) with the full set of 3D metrics. Join to the LOD 1.3 files on `identificatie`.
- The `height` fields in the LOD 1.3 files are already computed relative to ground, ready for extrusion rendering. The raw absolute heights (NAP datum) are in 3dbag-pand.parquet.

## Relationship to BAG (Kadaster)

The 3D BAG is **derived from** the [BAG building registry](../../kadaster/panden/) maintained by Kadaster:

- The BAG provides 2D building footprints, construction year, status, usage function, and floor area — but **no building heights or floor counts**.
- The 3D BAG adds heights, roof types, volumes, and surface areas by combining BAG footprints with AHN point cloud data.
- The `identificatie` field is the shared key that links 3D BAG records back to BAG buildings.

If you need only 2D footprints with BAG attributes (and no heights), use [Buildings (Panden)](../../kadaster/panden/) — it is smaller and simpler.

## Quick Start — 3D Map Visualization

Use the PMTiles with [MapLibre GL JS](https://maplibre.org/) for instant 3D building visualization:

```javascript
map.addSource('3dbag', {
  type: 'vector',
  url: 'pmtiles://https://data.source.coop/cholmes/portolan-nl/tudelft/3dbag/3dbag-lod13.pmtiles'
});

map.addLayer({
  id: 'buildings-3d',
  type: 'fill-extrusion',
  source: '3dbag',
  'source-layer': 'buildings',
  paint: {
    'fill-extrusion-color': '#D4D4D4',
    'fill-extrusion-height': ['get', 'height'],
    'fill-extrusion-base': ['get', 'base_height'],
    'fill-extrusion-opacity': 0.85
  }
});
```

## Quick Start — DuckDB Analytics

```sql
INSTALL spatial; LOAD spatial;

-- Query LOD 1.3 building parts
SELECT identificatie, height, base_height, dak_type, bouwjaar, gebruiksdoel
FROM read_parquet('https://data.source.coop/cholmes/portolan-nl/tudelft/3dbag/3dbag-lod13.parquet')
WHERE height > 50
ORDER BY height DESC
LIMIT 20;

-- Query whole-building attributes
SELECT identificatie, b3_volume_lod13, b3_opp_grond, b3_bouwlagen, b3_dak_type
FROM read_parquet('https://data.source.coop/cholmes/portolan-nl/tudelft/3dbag/3dbag-pand.parquet')
WHERE b3_volume_lod13 > 10000
ORDER BY b3_volume_lod13 DESC
LIMIT 20;
```

## Quick Start — Python

```python
import geopandas as gpd

gdf = gpd.read_parquet(
    'https://data.source.coop/cholmes/portolan-nl/tudelft/3dbag/3dbag-lod13.parquet',
    columns=['identificatie', 'height', 'base_height', 'dak_type', 'bouwjaar', 'geom']
)
print(f"CRS: {gdf.crs}")  # EPSG:7415
print(f"Rows: {len(gdf):,}")
```

## Visualization Styles

Six [MapLibre GL styles](./styles/) are provided — five use 3D fill-extrusion:

| Style | Description |
|-------|-------------|
| [Default](./styles/default.json) | Light grey 3D extruded buildings |
| [By Height](./styles/by-height.json) | Blue-to-red color ramp by building height (3D) |
| [By Age](./styles/by-age.json) | Brown-to-yellow by construction year (3D) |
| [By Function](./styles/by-use.json) | Categorical colors by building use (3D) |
| [By Roof Type](./styles/by-roof-type.json) | Categorical colors by roof type (3D) |
| [Flat](./styles/flat.json) | 2D flat fill for overview/performance |

## Attribution

Produced by the [3D Geoinformation Research Group](https://3d.bk.tudelft.nl/), TU Delft, and [3DGI](https://3dgi.xyz/). Funded by the [European Research Council](https://erc.europa.eu/).

## License

[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — attribution required to the 3D Geoinformation Research Group, TU Delft.

## Links

- [3D BAG viewer & download](https://3dbag.nl/)
- [3D BAG documentation](https://docs.3dbag.nl/en/)
- [3D BAG project page](https://3d.bk.tudelft.nl/projects/3dbag/)
- [3D BAG attribute reference](https://docs.3dbag.nl/en/schema/attributes/)
- [Source BAG data (Kadaster/PDOK)](https://www.pdok.nl/introductie/-/article/basisregistratie-adressen-en-gebouwen-ba-1)
- [AHN point cloud](https://www.ahn.nl/)
- [BAG buildings in this catalog (Kadaster)](../../kadaster/panden/)

## Contact

Chris Holmes <cholmes@9eo.org>

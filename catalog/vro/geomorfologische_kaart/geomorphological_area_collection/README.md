# BRO Geomorphological Map — Map area collections

70 map-area collection polygons grouping the national Geomorphological Map 1:50,000 (GMM) by survey/publication. Produced under VRO; bronhouder Wageningen Environmental Research.

> AI/Agent users: see [AGENTS.md](./AGENTS.md) for field meanings, query examples and caveats.

![netherlands](https://img.shields.io/badge/netherlands-blue) ![bro](https://img.shields.io/badge/BRO-subsurface-blue) ![vro](https://img.shields.io/badge/provider-VRO-blue) ![cc0](https://img.shields.io/badge/license-CC0--1.0-green)

## Spatial coverage

- **Geometry:** MultiPolygon  ·  **Features:** 70  ·  **CRS:** EPSG:28992
- **Bounding box (WGS84):** [3.242611, 50.737537, 7.23837, 53.596828]

## Schema

| Column | Type | Description |
|--------|------|-------------|
| fid | int64 | Feature ID. |
| version | string |  |
| collection_id | string |  |
| name | string |  |
| inventorymethod | string |  |
| source | string |  |
| beginlifespan | int64 |  |
| endlifespan | int64 |  |
| citation_id | string |  |
| geom | binary | Feature geometry (WKB) in EPSG:28992 (Amersfoort / RD New). |
| geom_bbox | struct<xmin: float, ymin: float, xmax: float, ymax: float> | Per-feature bounding box struct for spatial filtering. |

## Files

| File | Format | Description |
|------|--------|-------------|
| geomorphological_area_collection.parquet | GeoParquet | 70 features (EPSG:28992) |
| geomorphological_area_collection.pmtiles | PMTiles | Vector tiles for web maps |
| styles/ | Mapbox GL v8 | Visualization styles |
| thumbnail.webp | WebP | Official PDOK preview |

## Quick start

```python
import geopandas as gpd
gdf = gpd.read_parquet('https://data.source.coop/cholmes/portolan-nl/vro/geomorfologische_kaart/geomorphological_area_collection/geomorphological_area_collection.parquet')
```

## Styles

- `styles/default` — BRO Geomorphological Map — Map area collections — Default
- `styles/by-method` — BRO Geomorphological Map — Map area collections — By inventory method

## Source

PDOK — Basisregistratie Ondergrond (BRO). Provider: Ministerie van Volkshuisvesting en Ruimtelijke
Ordening (VRO). Bronhouder: TNO – Geologische Dienst Nederland / Wageningen Environmental Research.

## License

[CC0-1.0](https://creativecommons.org/publicdomain/zero/1.0/) — public domain.

---
*Part of [Portolan NL](../../README.md) · generated from STAC metadata.*

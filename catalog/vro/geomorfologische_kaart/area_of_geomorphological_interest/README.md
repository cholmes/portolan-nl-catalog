# BRO Geomorphological Map — Area of geomorphological interest

40,840 polygons delimiting the area of geomorphological interest of the national Geomorphological Map 1:50,000 (GMM). Produced under VRO; bronhouder Wageningen Environmental Research.

> AI/Agent users: see [llms.txt](./llms.txt) for field meanings, query examples and caveats.

![netherlands](https://img.shields.io/badge/netherlands-blue) ![bro](https://img.shields.io/badge/BRO-subsurface-blue) ![vro](https://img.shields.io/badge/provider-VRO-blue) ![cc0](https://img.shields.io/badge/license-CC0--1.0-green)

## Spatial coverage

- **Geometry:** MultiPolygon  ·  **Features:** 40,840  ·  **CRS:** EPSG:28992
- **Bounding box (WGS84):** [3.346056, 50.754011, 7.217599, 53.610935]

## Schema

| Column | Type | Description |
|--------|------|-------------|
| fid | int64 | Feature ID. |
| identification | string |  |
| collection_id | string |  |
| type | string |  |
| geom | binary | Feature geometry (WKB) in EPSG:28992 (Amersfoort / RD New). |
| geom_bbox | struct<xmin: float, ymin: float, xmax: float, ymax: float> | Per-feature bounding box struct for spatial filtering. |

## Files

| File | Format | Description |
|------|--------|-------------|
| area_of_geomorphological_interest.parquet | GeoParquet | 40,840 features (EPSG:28992) |
| area_of_geomorphological_interest.pmtiles | PMTiles | Vector tiles for web maps |
| styles/ | Mapbox GL v8 | Visualization styles |
| thumbnail.png | PNG | Official PDOK preview |

## Quick start

```python
import geopandas as gpd
gdf = gpd.read_parquet('https://data.source.coop/cholmes/portolan-nl/vro/geomorfologische_kaart/area_of_geomorphological_interest/area_of_geomorphological_interest.parquet')
```

## Styles

- `styles/default` — BRO Geomorphological Map — Area of geomorphological interest — Default

## Source

PDOK — Basisregistratie Ondergrond (BRO). Provider: Ministerie van Volkshuisvesting en Ruimtelijke
Ordening (VRO). Bronhouder: TNO – Geologische Dienst Nederland / Wageningen Environmental Research.

## License

[CC0-1.0](https://creativecommons.org/publicdomain/zero/1.0/) — public domain.

---
*Part of [Portolan NL](../../README.md) · generated from STAC metadata.*

# BRO Soil Map — Area of pedological interest

6,192 polygons delimiting the area of pedological interest of the national Soil Map 1:50,000 (Bodemkaart, SGM) — where soil mapping applies. Produced under VRO; bronhouder [Wageningen Environmental Research](https://www.wur.nl/).

> AI/Agent users: see [AGENTS.md](./AGENTS.md) for field meanings, query examples and caveats.

![netherlands](https://img.shields.io/badge/netherlands-blue) ![bro](https://img.shields.io/badge/BRO-subsurface-blue) ![vro](https://img.shields.io/badge/provider-VRO-blue) ![cc0](https://img.shields.io/badge/license-CC0--1.0-green)

## Spatial coverage

- **Geometry:** MultiPolygon  ·  **Features:** 6,192  ·  **CRS:** EPSG:28992
- **Bounding box (WGS84):** [3.368324, 50.756177, 7.218594, 53.551534]

## Schema

| Column | Type | Description |
|--------|------|-------------|
| fid | int64 | Feature ID. |
| maparea_id | string |  |
| maparea_collection | string |  |
| beginlifespan | string |  |
| endlifespan | string |  |
| pedologicalinterest | string |  |
| geom | binary | Feature geometry (WKB) in EPSG:28992 (Amersfoort / RD New). |
| geom_bbox | struct<xmin: float, ymin: float, xmax: float, ymax: float> | Per-feature bounding box struct for spatial filtering. |

## Files

| File | Format | Description |
|------|--------|-------------|
| [areaofpedologicalinterest.parquet](https://data.source.coop/cholmes/portolan-nl/vro/bodemkaart/areaofpedologicalinterest/areaofpedologicalinterest.parquet) | GeoParquet | 6,192 features (EPSG:28992) |
| [areaofpedologicalinterest.pmtiles](https://data.source.coop/cholmes/portolan-nl/vro/bodemkaart/areaofpedologicalinterest/areaofpedologicalinterest.pmtiles) | PMTiles | Vector tiles for web maps |
| styles/ | Mapbox GL v8 | Visualization styles |
| [thumbnail.webp](https://data.source.coop/cholmes/portolan-nl/vro/bodemkaart/areaofpedologicalinterest/thumbnail.webp) | WebP | Official PDOK preview |

## Quick start

```python
import geopandas as gpd
gdf = gpd.read_parquet('https://data.source.coop/cholmes/portolan-nl/vro/bodemkaart/areaofpedologicalinterest/areaofpedologicalinterest.parquet')
```

## Styles

- `styles/default` — BRO Soil Map — Area of pedological interest — Default
- `styles/by-collection` — BRO Soil Map — Area of pedological interest — By survey campaign
- `styles/by-interest` — BRO Soil Map — Area of pedological interest — By area type

## Source

PDOK — Basisregistratie Ondergrond (BRO). Provider: Ministerie van Volkshuisvesting en Ruimtelijke
Ordening (VRO). Bronhouder: TNO – Geologische Dienst Nederland / Wageningen Environmental Research.

## License

[CC0-1.0](https://creativecommons.org/publicdomain/zero/1.0/) — public domain.

---
*Part of [Portolan NL](../../README.md) · generated from STAC metadata.*

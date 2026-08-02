# BRO Soil Map of the Netherlands 1:50,000 — Soil areas (SGM)

48,025 soil-area polygons of the national Soil Map of the Netherlands 1:50,000 (Bodemkaart, SGM), enriched here with the primary soil unit and main soil class. Produced under VRO; bronhouder [Wageningen Environmental Research](https://www.wur.nl/).

> AI/Agent users: see [AGENTS.md](./AGENTS.md) for field meanings, query examples and caveats.

![netherlands](https://img.shields.io/badge/netherlands-blue) ![bro](https://img.shields.io/badge/BRO-subsurface-blue) ![vro](https://img.shields.io/badge/provider-VRO-blue) ![cc0](https://img.shields.io/badge/license-CC0--1.0-green)

## Spatial coverage

- **Geometry:** MultiPolygon  ·  **Features:** 48,025  ·  **CRS:** EPSG:28992
- **Bounding box (WGS84):** [3.358571, 50.750579, 7.227762, 53.55359]

## Schema

| Column | Type | Description |
|--------|------|-------------|
| fid | int64 | Feature ID. |
| maparea_id | string | Soil-area polygon identifier. |
| maparea_collection | string | Survey campaign / map collection the polygon belongs to. |
| soilslope | string | Slope class of the soil area (mostly 'Niet opgenomen'). |
| soilunit_code | string | Primary soil-unit code (BRO bodemcode), e.g. 'cHn21'. |
| hoofdklasse | string | Main soil class (mainsoilclassification), e.g. Podzolgronden, Zeekleigronden. |
| bodemklasse | string | Full soil classification text of the primary soil unit. |
| legenda_url | string | URL to the official soil-class legend entry. |
| geom | binary | Feature geometry (WKB) in EPSG:28992 (Amersfoort / RD New). |
| geom_bbox | struct<xmin: float, ymin: float, xmax: float, ymax: float> | Per-feature bounding box struct for spatial filtering. |

## Files

| File | Format | Description |
|------|--------|-------------|
| [soilarea.parquet](https://data.source.coop/cholmes/portolan-nl/vro/bodemkaart/soilarea/soilarea.parquet) | GeoParquet | 48,025 features (EPSG:28992) |
| [soilarea.pmtiles](https://data.source.coop/cholmes/portolan-nl/vro/bodemkaart/soilarea/soilarea.pmtiles) | PMTiles | Vector tiles for web maps |
| styles/ | Mapbox GL v8 | Visualization styles |
| [thumbnail.webp](https://data.source.coop/cholmes/portolan-nl/vro/bodemkaart/soilarea/thumbnail.webp) | WebP | Official PDOK preview |

## Quick start

```python
import geopandas as gpd
gdf = gpd.read_parquet('https://data.source.coop/cholmes/portolan-nl/vro/bodemkaart/soilarea/soilarea.parquet')
```

## Styles

- `styles/default` — BRO Soil Map of the Netherlands 1:50,000 — Soil areas (SGM) — Default
- `styles/by-collection` — BRO Soil Map of the Netherlands 1:50,000 — Soil areas (SGM) — By survey campaign
- `styles/by-texture` — BRO Soil Map of the Netherlands 1:50,000 — Soil areas (SGM) — By texture (sand / clay / peat)

## Source

PDOK — Basisregistratie Ondergrond (BRO). Provider: Ministerie van Volkshuisvesting en Ruimtelijke
Ordening (VRO). Bronhouder: TNO – Geologische Dienst Nederland / Wageningen Environmental Research.

## License

[CC0-1.0](https://creativecommons.org/publicdomain/zero/1.0/) — public domain.

---
*Part of [Portolan NL](../../README.md) · generated from STAC metadata.*

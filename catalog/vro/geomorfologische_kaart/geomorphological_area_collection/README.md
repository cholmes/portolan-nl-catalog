# BRO Geomorphological Map — Map area collections

70 map-area collection polygons grouping the national Geomorphological Map 1:50,000 (GMM) by survey/publication. Produced under VRO; bronhouder [Wageningen Environmental Research](https://www.wur.nl/).

> AI/Agent users: see [AGENTS.md](./AGENTS.md) for field meanings, query examples and caveats.

![netherlands](https://img.shields.io/badge/netherlands-blue) ![bro](https://img.shields.io/badge/BRO-subsurface-blue) ![vro](https://img.shields.io/badge/provider-VRO-blue) ![cc0](https://img.shields.io/badge/license-CC0--1.0-green)

## Spatial coverage

- **Geometry:** MultiPolygon  ·  **Features:** 70  ·  **CRS:** EPSG:28992
- **Bounding box (WGS84):** [3.242611, 50.737537, 7.23837, 53.596828]

## Schema

| Column | Type | Description |
|--------|------|-------------|
| fid | int64 | Feature ID. |
| version | string | Version of the delivered GMM map model (e.g. GEOM50000-V2025-1); model version management per GMM cat. 6.3.1. |
| collection_id | string | Unique identifier (identificatie) of the geomorphological area collection in the GMM registration object (GMM cat. 4.3.2.1). |
| name | string | Name of the (sub)collection: the map sheet number or project name, e.g. Bergen_op_Zoom (GMM cat. 4.3.1.1 naam). |
| inventorymethod | string | Inventory method (inventarisatiemethode): analogue mapping with field survey or digital mapping with field verification (GMM cat. 4.3.2.5, 6.5). |
| source | string | Elevation source (bron/Bestand): name and version of the height data file used to delineate and classify the areas, e.g. AHN4 (GMM cat. 4.3.2.8, 4.3.6). |
| beginlifespan | int64 | Date (yyyymmdd) this version of the spatial object was inserted or changed in the dataset (begin levensduur, GMM cat. 4.3.2.6). |
| endlifespan | int64 | Date (yyyymmdd) this version of the spatial object was superseded or retired; empty while current (einde levensduur, GMM cat. 4.3.2.7). |
| citation_id | string | Reference to the CI_Citation record documenting this collection, e.g. the descriptive report of the survey or update (GMM cat. 4.3.2.4). |
| geom | binary | Feature geometry (WKB) in EPSG:28992 (Amersfoort / RD New). |
| geom_bbox | struct<xmin: float, ymin: float, xmax: float, ymax: float> | Per-feature bounding box struct for spatial filtering. |

## Files

| File | Format | Description |
|------|--------|-------------|
| [geomorphological_area_collection.parquet](https://data.source.coop/cholmes/portolan-nl/vro/geomorfologische_kaart/geomorphological_area_collection/geomorphological_area_collection.parquet) | GeoParquet | 70 features (EPSG:28992) |
| [geomorphological_area_collection.pmtiles](https://data.source.coop/cholmes/portolan-nl/vro/geomorfologische_kaart/geomorphological_area_collection/geomorphological_area_collection.pmtiles) | PMTiles | Vector tiles for web maps |
| styles/ | Mapbox GL v8 | Visualization styles |
| [thumbnail.webp](https://data.source.coop/cholmes/portolan-nl/vro/geomorfologische_kaart/geomorphological_area_collection/thumbnail.webp) | WebP | Official PDOK preview |

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

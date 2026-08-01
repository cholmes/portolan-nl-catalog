# BRO Mining Construction (EPC / Mijnbouwconstructie)

4,975 mining-law subsurface constructions (mijnbouwconstructie, EPC) from the BRO — deep boreholes, mine systems and salt caverns for oil, gas, geothermal energy and storage. Produced under VRO; bronhouder TNO.

> AI/Agent users: see [AGENTS.md](./AGENTS.md) for field meanings, query examples and caveats.

![netherlands](https://img.shields.io/badge/netherlands-blue) ![bro](https://img.shields.io/badge/BRO-subsurface-blue) ![vro](https://img.shields.io/badge/provider-VRO-blue) ![cc0](https://img.shields.io/badge/license-CC0--1.0-green)

## Spatial coverage

- **Geometry:** MultiPoint  ·  **Features:** 4,975  ·  **CRS:** EPSG:4258
- **Bounding box (WGS84):** [2.816739, 50.758652, 7.201984, 55.681014]

## Schema

| Column | Type | Description |
|--------|------|-------------|
| mining_construction_pk | int64 |  |
| bro_id | string | BRO registration ID — unique identifier of the object in the Basisregistratie Ondergrond. |
| quality_regime | string | BRO quality regime: IMBRO (full assurance) or IMBRO/A (transitional/lower assurance). |
| delivery_accountable_party | string | KvK number of the party accountable for delivery (bronhouder). |
| delivery_context | string | Legal/administrative framework under which the object was registered. |
| legal_status | string | Legal status of the construction (e.g. onbekend, buitenGebruikMijnbouw). |
| owner | string | Owner / operator of the mining construction. |
| source_reference | string | Reference to the source document. |
| applied_transformation | string | Whether a coordinate/height transformation was applied (ja/nee). |
| standardized_location | binary | Object location — WKB geometry in EPSG:4258 (ETRS89). |
| standardized_location_bbox | struct<xmin: float, ymin: float, xmax: float, ymax: float> | Per-feature bounding box struct (xmin,ymin,xmax,ymax) for spatial filtering. |

## Files

| File | Format | Description |
|------|--------|-------------|
| mijnbouwconstructie.parquet | GeoParquet | 4,975 features (EPSG:4258) |
| mijnbouwconstructie.pmtiles | PMTiles | Vector tiles for web maps |
| styles/ | Mapbox GL v8 | Visualization styles |
| thumbnail.webp | WebP | Official PDOK preview |

## Quick start

```python
import geopandas as gpd
gdf = gpd.read_parquet('https://data.source.coop/cholmes/portolan-nl/vro/mijnbouwconstructie/mijnbouwconstructie.parquet')
```

## Styles

- `styles/default` — BRO Mining Construction (EPC / Mijnbouwconstructie) — Default
- `styles/by-legal-status` — BRO Mining Construction (EPC / Mijnbouwconstructie) — By legal status

## Source

PDOK — Basisregistratie Ondergrond (BRO). Provider: Ministerie van Volkshuisvesting en Ruimtelijke
Ordening (VRO). Bronhouder: TNO – Geologische Dienst Nederland / Wageningen Environmental Research.

## License

[CC0-1.0](https://creativecommons.org/publicdomain/zero/1.0/) — public domain.

---
*Part of [Portolan NL](../README.md) · generated from STAC metadata.*

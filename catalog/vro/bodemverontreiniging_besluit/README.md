# BRO Government Decision on Soil Contamination (SLD)

121 formal government decisions on soil contamination (overheidsbesluit bodemverontreiniging, SLD) from the BRO — areas with an authority decision on assessment, remediation or aftercare. Produced under VRO; bronhouder TNO.

> AI/Agent users: see [llms.txt](./llms.txt) for field meanings, query examples and caveats.

![netherlands](https://img.shields.io/badge/netherlands-blue) ![bro](https://img.shields.io/badge/BRO-subsurface-blue) ![vro](https://img.shields.io/badge/provider-VRO-blue) ![cc0](https://img.shields.io/badge/license-CC0--1.0-green)

## Spatial coverage

- **Geometry:** MultiPolygon  ·  **Features:** 121  ·  **CRS:** EPSG:4258
- **Bounding box (WGS84):** [4.274015, 51.265245, 6.997793, 53.281982]

## Schema

| Column | Type | Description |
|--------|------|-------------|
| soil_legal_decision_pk | int64 |  |
| bro_id | string | BRO registration ID — unique identifier of the object in the Basisregistratie Ondergrond. |
| quality_regime | string | BRO quality regime: IMBRO (full assurance) or IMBRO/A (transitional/lower assurance). |
| delivery_accountable_party | string | KvK number of the party accountable for delivery (bronhouder). |
| delivery_context | string | Legal/administrative framework under which the object was registered. |
| applied_transformation | string | Whether a coordinate/height transformation was applied (ja/nee). |
| standardized_location | binary | Object location — WKB geometry in EPSG:4258 (ETRS89). |
| standardized_location_bbox | struct<xmin: float, ymin: float, xmax: float, ymax: float> | Per-feature bounding box struct (xmin,ymin,xmax,ymax) for spatial filtering. |

## Files

| File | Format | Description |
|------|--------|-------------|
| bodemverontreiniging_besluit.parquet | GeoParquet | 121 features (EPSG:4258) |
| bodemverontreiniging_besluit.pmtiles | PMTiles | Vector tiles for web maps |
| styles/ | Mapbox GL v8 | Visualization styles |
| thumbnail.webp | WebP | Official PDOK preview |

## Quick start

```python
import geopandas as gpd
gdf = gpd.read_parquet('https://data.source.coop/cholmes/portolan-nl/vro/bodemverontreiniging_besluit/bodemverontreiniging_besluit.parquet')
```

## Styles

- `styles/default` — BRO Government Decision on Soil Contamination (SLD) — Default
- `styles/by-bronhouder` — BRO Government Decision on Soil Contamination (SLD) — By data owner (bronhouder)
- `styles/by-quality-regime` — BRO Government Decision on Soil Contamination (SLD) — By quality regime

## Source

PDOK — Basisregistratie Ondergrond (BRO). Provider: Ministerie van Volkshuisvesting en Ruimtelijke
Ordening (VRO). Bronhouder: TNO – Geologische Dienst Nederland / Wageningen Environmental Research.

## License

[CC0-1.0](https://creativecommons.org/publicdomain/zero/1.0/) — public domain.

---
*Part of [Portolan NL](../README.md) · generated from STAC metadata.*

# BRO Groundwater Use System (GUF / Grondwatergebruiksysteem)

50,637 groundwater use systems (grondwatergebruiksysteem, GUF) from the BRO — constructions that extract or infiltrate groundwater, including ground-source energy (ATES/bodemenergie). Produced under VRO; bronhouder TNO.

> AI/Agent users: see [llms.txt](./llms.txt) for field meanings, query examples and caveats.

![netherlands](https://img.shields.io/badge/netherlands-blue) ![bro](https://img.shields.io/badge/BRO-subsurface-blue) ![vro](https://img.shields.io/badge/provider-VRO-blue) ![cc0](https://img.shields.io/badge/license-CC0--1.0-green)

## Spatial coverage

- **Geometry:** MultiPoint  ·  **Features:** 50,637  ·  **CRS:** EPSG:4258
- **Bounding box (WGS84):** [3.372981, 50.766874, 7.202634, 53.487785]

## Schema

| Column | Type | Description |
|--------|------|-------------|
| groundwater_usage_facility_pk | int64 |  |
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
| grondwatergebruiksysteem.parquet | GeoParquet | 50,637 features (EPSG:4258) |
| grondwatergebruiksysteem.pmtiles | PMTiles | Vector tiles for web maps |
| styles/ | Mapbox GL v8 | Visualization styles |
| thumbnail.png | PNG | Official PDOK preview |

## Quick start

```python
import geopandas as gpd
gdf = gpd.read_parquet('https://data.source.coop/cholmes/portolan-nl/vro/grondwatergebruiksysteem/grondwatergebruiksysteem.parquet')
```

## Styles

- `styles/default` — BRO Groundwater Use System (GUF / Grondwatergebruiksysteem) — Default
- `styles/by-delivery-context` — BRO Groundwater Use System (GUF / Grondwatergebruiksysteem) — By delivery context
- `styles/by-quality-regime` — BRO Groundwater Use System (GUF / Grondwatergebruiksysteem) — By quality regime

## Source

PDOK — Basisregistratie Ondergrond (BRO). Provider: Ministerie van Volkshuisvesting en Ruimtelijke
Ordening (VRO). Bronhouder: TNO – Geologische Dienst Nederland / Wageningen Environmental Research.

## License

[CC0-1.0](https://creativecommons.org/publicdomain/zero/1.0/) — public domain.

---
*Part of [Portolan NL](../README.md) · generated from STAC metadata.*

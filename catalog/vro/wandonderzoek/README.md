# BRO Soil Trench Investigation (SFR / Wandonderzoek)

2,806 soil-profile pit/trench investigations (wandonderzoek, SFR) from the Dutch Key Registry of the Subsurface (BRO). Each point is a described soil face used for soil mapping, agriculture and nature management. Produced under VRO; bronhouder TNO.

> AI/Agent users: see [llms.txt](./llms.txt) for field meanings, query examples and caveats.

![netherlands](https://img.shields.io/badge/netherlands-blue) ![bro](https://img.shields.io/badge/BRO-subsurface-blue) ![vro](https://img.shields.io/badge/provider-VRO-blue) ![cc0](https://img.shields.io/badge/license-CC0--1.0-green)

## Spatial coverage

- **Geometry:** Point  ·  **Features:** 2,806  ·  **CRS:** EPSG:4258
- **Bounding box (WGS84):** [3.374896, 50.756136, 7.191841, 53.386308]

## Schema

| Column | Type | Description |
|--------|------|-------------|
| soil_face_research_pk | int64 | Internal primary key. |
| bro_id | string | BRO registration ID — unique identifier of the object in the Basisregistratie Ondergrond. |
| quality_regime | string | BRO quality regime: IMBRO (full assurance) or IMBRO/A (transitional/lower assurance). |
| delivery_accountable_party | string | KvK number of the party accountable for delivery (bronhouder). |
| delivery_context | string | Legal/administrative framework under which the object was registered. |
| survey_purpose | string | Purpose of the survey (e.g. national soil map unit, nature soil build-up). |
| discipline | string | Investigation discipline (bodemkunde / soil science). |
| research_report_date | string | Date the research report was registered (YYYY-MM-DD, free text). |
| fieldwork_date | string | Date of fieldwork (YYYY-MM-DD, free text). |
| litter_layer_investigated | string | Whether the litter layer was investigated (ja/nee). |
| applied_transformation | string | Whether a coordinate/height transformation was applied (ja/nee). |
| standardized_location | binary | Object location — WKB geometry in EPSG:4258 (ETRS89). |
| standardized_location_bbox | struct<xmin: float, ymin: float, xmax: float, ymax: float> | Per-feature bounding box struct (xmin,ymin,xmax,ymax) for spatial filtering. |

## Files

| File | Format | Description |
|------|--------|-------------|
| wandonderzoek.parquet | GeoParquet | 2,806 features (EPSG:4258) |
| wandonderzoek.pmtiles | PMTiles | Vector tiles for web maps |
| styles/ | Mapbox GL v8 | Visualization styles |
| thumbnail.png | PNG | Official PDOK preview |

## Quick start

```python
import geopandas as gpd
gdf = gpd.read_parquet('https://data.source.coop/cholmes/portolan-nl/vro/wandonderzoek/wandonderzoek.parquet')
```

## Styles

- `styles/default` — BRO Soil Trench Investigation (SFR / Wandonderzoek) — Default
- `styles/by-survey-purpose` — BRO Soil Trench Investigation (SFR / Wandonderzoek) — By survey purpose

## Source

PDOK — Basisregistratie Ondergrond (BRO). Provider: Ministerie van Volkshuisvesting en Ruimtelijke
Ordening (VRO). Bronhouder: TNO – Geologische Dienst Nederland / Wageningen Environmental Research.

## License

[CC0-1.0](https://creativecommons.org/publicdomain/zero/1.0/) — public domain.

---
*Part of [Portolan NL](../README.md) · generated from STAC metadata.*

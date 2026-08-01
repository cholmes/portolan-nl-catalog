# BRO Geomorphological Map 1:50,000 — Geomorphological areas (GMM)

80,148 landform polygons of the national Geomorphological Map of the Netherlands 1:50,000 (Geomorfologische kaart, GMM), classified by genesis, relief and landform subgroup. Produced under VRO; bronhouder Wageningen Environmental Research.

> AI/Agent users: see [AGENTS.md](./AGENTS.md) for field meanings, query examples and caveats.

![netherlands](https://img.shields.io/badge/netherlands-blue) ![bro](https://img.shields.io/badge/BRO-subsurface-blue) ![vro](https://img.shields.io/badge/provider-VRO-blue) ![cc0](https://img.shields.io/badge/license-CC0--1.0-green)

## Spatial coverage

- **Geometry:** MultiPolygon  ·  **Features:** 80,148  ·  **CRS:** EPSG:28992
- **Bounding box (WGS84):** [3.357819, 50.750537, 7.228386, 53.558432]

## Schema

| Column | Type | Description |
|--------|------|-------------|
| fid | int64 | Feature ID. |
| collection_id | string |  |
| identification | string |  |
| relief_code | int64 | Relief-form code. |
| active_process | string | Whether the landform process is still active (ja/nee). |
| genese_code | string | Genesis code (1=Glaciaal, 2=Periglaciaal, 3=Denudatief, 4=Fluviatiel, 5=Eolisch, 6=Lacustrien, 7=Marien, 8=Organogeen, 9=Antropogeen, 0=Tectonisch). |
| landform_subgroup_code | string | Landform subgroup code (e.g. B44 = stroomrug/stream ridge). |
| additional_surface_relief_code | string | Additional surface relief code (optional). |
| additional_surface_cover_code | string | Additional surface cover code (optional). |
| genese_description | string | Genesis description (Dutch). |
| genese_validfrom | int64 |  |
| genese_validto | int64 |  |
| landform_subgroup_description | string | Landform subgroup description (Dutch). |
| landform_subgroup_url | string | URL to the landform legend entry. |
| landform_subgroup_validfrom | int64 |  |
| landform_subgroup_validto | int64 |  |
| additional_surface_relief_description | string |  |
| additional_surface_relief_validfrom | int64 |  |
| additional_surface_relief_validto | int64 |  |
| additional_surface_cover_description | string |  |
| additional_surface_cover_validfrom | int64 |  |
| additional_surface_cover_validto | int64 |  |
| relief_klasse | string |  |
| relief_subklasse | string |  |
| helling | string |  |
| lokaal_maximaal_hoogteverschil | string |  |
| diepte_tov_omgeving | string |  |
| steilste_verhang | string |  |
| maximaal_hoogteverschil | string |  |
| maximaal_verval | string |  |
| relief_validfrom | int64 |  |
| relief_validto | int64 |  |
| geom | binary | Feature geometry (WKB) in EPSG:28992 (Amersfoort / RD New). |
| geom_bbox | struct<xmin: float, ymin: float, xmax: float, ymax: float> | Per-feature bounding box struct for spatial filtering. |

## Files

| File | Format | Description |
|------|--------|-------------|
| geomorphological_area.parquet | GeoParquet | 80,148 features (EPSG:28992) |
| geomorphological_area.pmtiles | PMTiles | Vector tiles for web maps |
| styles/ | Mapbox GL v8 | Visualization styles |
| thumbnail.webp | WebP | Official PDOK preview |

## Quick start

```python
import geopandas as gpd
gdf = gpd.read_parquet('https://data.source.coop/cholmes/portolan-nl/vro/geomorfologische_kaart/geomorphological_area/geomorphological_area.parquet')
```

## Styles

- `styles/default` — BRO Geomorphological Map 1:50,000 — Geomorphological areas (GMM) — Default
- `styles/by-landform` — BRO Geomorphological Map 1:50,000 — Geomorphological areas (GMM) — By landform subgroup
- `styles/by-relief` — BRO Geomorphological Map 1:50,000 — Geomorphological areas (GMM) — By relief class

## Source

PDOK — Basisregistratie Ondergrond (BRO). Provider: Ministerie van Volkshuisvesting en Ruimtelijke
Ordening (VRO). Bronhouder: TNO – Geologische Dienst Nederland / Wageningen Environmental Research.

## License

[CC0-1.0](https://creativecommons.org/publicdomain/zero/1.0/) — public domain.

---
*Part of [Portolan NL](../../README.md) · generated from STAC metadata.*

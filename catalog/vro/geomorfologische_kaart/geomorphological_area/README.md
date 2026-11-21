# BRO Geomorphological Map 1:50,000 — Geomorphological areas (GMM)

80,148 landform polygons of the national Geomorphological Map of the Netherlands 1:50,000 (Geomorfologische kaart, GMM), classified by genesis, relief and landform subgroup. Produced under VRO; bronhouder [Wageningen Environmental Research](https://www.wur.nl/).

> AI/Agent users: see [AGENTS.md](./AGENTS.md) for field meanings, query examples and caveats.

![netherlands](https://img.shields.io/badge/netherlands-blue) ![bro](https://img.shields.io/badge/BRO-subsurface-blue) ![vro](https://img.shields.io/badge/provider-VRO-blue) ![cc0](https://img.shields.io/badge/license-CC0--1.0-green)

## Spatial coverage

- **Geometry:** MultiPolygon  ·  **Features:** 80,148  ·  **CRS:** EPSG:28992
- **Bounding box (WGS84):** [3.357819, 50.750537, 7.228386, 53.558432]

## Schema

| Column | Type | Description |
|--------|------|-------------|
| fid | int64 | Feature ID. |
| collection_id | string | ID of the geomorphological area collection (Geomorfologische vlakcollectie) this polygon belongs to (GMM cat. 4.3.2.1 identificatie). |
| identification | string | Unique ID of the map polygon (Kaartvlak identificatie), a published spatial-object identifier for external reference (GMM cat. 4.3.3.1). |
| relief_code | int64 | Relief-form code. |
| active_process | string | Whether the landform process is still active (ja/nee). |
| genese_code | string | Genesis code (1=Glaciaal, 2=Periglaciaal, 3=Denudatief, 4=Fluviatiel, 5=Eolisch, 6=Lacustrien, 7=Marien, 8=Organogeen, 9=Antropogeen, 0=Tectonisch). |
| landform_subgroup_code | string | Landform subgroup code (e.g. B44 = stroomrug/stream ridge). |
| additional_surface_relief_code | string | Additional surface relief code (optional). |
| additional_surface_cover_code | string | Additional surface cover code (optional). |
| genese_description | string | Genesis description (Dutch). |
| genese_validfrom | int64 | Start date (yyyymmdd) from which the recorded genesis (ontstaanswijze) value is valid; material history per GMM cat. 2.5, 4.3.8.3. |
| genese_validto | int64 | End date (yyyymmdd) of validity of the recorded genesis value; empty while current (material history, GMM cat. 2.5). |
| landform_subgroup_description | string | Landform subgroup description (Dutch). |
| landform_subgroup_url | string | URL to the landform legend entry. |
| landform_subgroup_validfrom | int64 | Start date (yyyymmdd) from which the recorded landform subgroup (landvormsubgroep) value is valid (material history, GMM cat. 2.5, 4.3.7.5). |
| landform_subgroup_validto | int64 | End date (yyyymmdd) of validity of the recorded landform subgroup value; empty while current (material history, GMM cat. 2.5). |
| additional_surface_relief_description | string | Relief addition (toevoeging relief): further typing of the relief and/or relative elevation of the landform unit (GMM cat. 4.3.7.1, list 5.4). |
| additional_surface_relief_validfrom | int64 | Start date (yyyymmdd) from which the recorded relief addition is valid (material history, GMM cat. 2.5). |
| additional_surface_relief_validto | int64 | End date (yyyymmdd) of validity of the recorded relief addition; empty while current (material history, GMM cat. 2.5). |
| additional_surface_cover_description | string | Cover addition (toevoeging bedekking): typing of the deviating sediment layer covering the landform subgroup (GMM cat. 4.3.7.3, 6.3.6). |
| additional_surface_cover_validfrom | int64 | Start date (yyyymmdd) from which the recorded cover addition is valid (material history, GMM cat. 2.5). |
| additional_surface_cover_validto | int64 | End date (yyyymmdd) of validity of the recorded cover addition; empty while current (material history, GMM cat. 2.5). |
| relief_klasse | string | Relief class (reliefklasse): whether the relief code is for valley-shaped (dalvormige) or non-valley landform groups (GMM cat. 4.3.9.2, 4.3.10). |
| relief_subklasse | string | Relief description (relief) of the non-valley relief code, e.g. 'Vrij vlak, laaggelegen relief'; empty for valleys (GMM cat. list 5.3). |
| helling | string | Slope: class of the angle of the steepest slope of the landform; non-valley relief codes only (GMM cat. list 5.3, 6.3.3). |
| lokaal_maximaal_hoogteverschil | string | Local maximum height difference within the landform, in metres; non-valley relief codes only (GMM cat. list 5.3, 6.3.3). |
| diepte_tov_omgeving | string | Depth of the valley incision relative to the surroundings, in metres; valley relief codes only (GMM cat. list 5.2 diepte). |
| steilste_verhang | string | Steepest gradient (steilste verhang) of the valley form; valley relief codes only (GMM cat. list 5.2). |
| maximaal_hoogteverschil | string | Maximum height difference within the form, in metres; valley relief codes only (GMM cat. list 5.2). |
| maximaal_verval | string | Maximum drop (maximaal verval) of the valley, in metres; valley relief codes only (GMM cat. list 5.2). |
| relief_validfrom | int64 | Start date (yyyymmdd) from which the recorded relief typing is valid (material history, GMM cat. 2.5, 4.3.7.4). |
| relief_validto | int64 | End date (yyyymmdd) of validity of the recorded relief typing; empty while current (material history, GMM cat. 2.5). |
| geom | binary | Feature geometry (WKB) in EPSG:28992 (Amersfoort / RD New). |
| geom_bbox | struct<xmin: float, ymin: float, xmax: float, ymax: float> | Per-feature bounding box struct for spatial filtering. |

## Files

| File | Format | Description |
|------|--------|-------------|
| [geomorphological_area.parquet](https://data.source.coop/cholmes/portolan-nl/vro/geomorfologische_kaart/geomorphological_area/geomorphological_area.parquet) | GeoParquet | 80,148 features (EPSG:28992) |
| [geomorphological_area.pmtiles](https://data.source.coop/cholmes/portolan-nl/vro/geomorfologische_kaart/geomorphological_area/geomorphological_area.pmtiles) | PMTiles | Vector tiles for web maps |
| styles/ | Mapbox GL v8 | Visualization styles |
| [thumbnail.webp](https://data.source.coop/cholmes/portolan-nl/vro/geomorfologische_kaart/geomorphological_area/thumbnail.webp) | WebP | Official PDOK preview |

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

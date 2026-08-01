#!/usr/bin/env python3
"""Generate concise README.md per collection + vro/README.md, from collection.json."""
import glob
import json
import os

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from tools.lib import paths, docs

# Generators write into the published tree; paths.py owns where that is.
ROOT = str(paths.CATALOG)
DATA = paths.DATA_BASE

COLL_PATHS = [
    "wandonderzoek", "mijnbouwconstructie", "bodemverontreiniging_besluit",
    "grondwatergebruiksysteem", "bodemkaart/soilarea", "bodemkaart/areaofpedologicalinterest",
    "geomorfologische_kaart/geomorphological_area",
    "geomorfologische_kaart/area_of_geomorphological_interest",
    "geomorfologische_kaart/geomorphological_area_collection",
]


def coll_readme(path):
    cdir = os.path.join(ROOT, "vro", path)
    c = json.load(open(os.path.join(cdir, "collection.json")))
    layer = c["pmtiles:layers"][0]
    n = c["table:row_count"]
    epsg = c["proj:epsg"]
    gtype = c["geoparquet:geometry_type"]
    bbox = c["extent"]["spatial"]["bbox"][0]
    rows = docs.column_table(c["table:columns"])
    styles = "\n".join(f"- `{k}` — {title}" for k, title, _ in docs.style_entries(c))
    depth = path.count("/")
    rooturl = "../" * (depth + 1)
    md = f"""# {c['title']}

{c['description'].split(chr(10))[0]}

> AI/Agent users: see [llms.txt](./llms.txt) for field meanings, query examples and caveats.

![netherlands](https://img.shields.io/badge/netherlands-blue) ![bro](https://img.shields.io/badge/BRO-subsurface-blue) ![vro](https://img.shields.io/badge/provider-VRO-blue) ![cc0](https://img.shields.io/badge/license-CC0--1.0-green)

## Spatial coverage

- **Geometry:** {gtype}  ·  **Features:** {n:,}  ·  **CRS:** EPSG:{epsg}
- **Bounding box (WGS84):** {bbox}

## Schema

{chr(10).join(rows)}

## Files

| File | Format | Description |
|------|--------|-------------|
| {layer}.parquet | GeoParquet | {n:,} features (EPSG:{epsg}) |
| {layer}.pmtiles | PMTiles | Vector tiles for web maps |
| styles/ | Mapbox GL v8 | Visualization styles |
| thumbnail.webp | WebP | Official PDOK preview |

## Quick start

```python
import geopandas as gpd
gdf = gpd.read_parquet('{DATA}/vro/{path}/{layer}.parquet')
```

## Styles

{styles}

## Source

PDOK — Basisregistratie Ondergrond (BRO). Provider: Ministerie van Volkshuisvesting en Ruimtelijke
Ordening (VRO). Bronhouder: TNO – Geologische Dienst Nederland / Wageningen Environmental Research.

## License

[CC0-1.0](https://creativecommons.org/publicdomain/zero/1.0/) — public domain.

---
*Part of [Portolan NL]({rooturl}README.md) · generated from STAC metadata.*
"""
    with open(os.path.join(cdir, "README.md"), "w") as f:
        f.write(md)
    print("  wrote vro/%s/README.md" % path)


VRO_README = f"""# Ministerie van Volkshuisvesting en Ruimtelijke Ordening (VRO)

Open geodata for which the **Ministry of Housing and Spatial Planning (VRO)** is the responsible
provider on [PDOK](https://www.pdok.nl/), drawn from the **Basisregistratie Ondergrond (BRO)** — the
Dutch Key Registry of the Subsurface. This subcatalog covers the BRO datasets flagged as EU
**High Value Data**, republished as cloud-native GeoParquet + PMTiles with STAC metadata.

Underlying data is produced by **TNO – Geologische Dienst Nederland** (subsurface objects) and
**Wageningen Environmental Research** (the soil and geomorphological maps). All data is **CC0 1.0**.

## Collections

| Collection | BRO | Geometry | Features |
|------------|-----|----------|----------|
| [wandonderzoek](./wandonderzoek/) | SFR | points | 2,806 |
| [mijnbouwconstructie](./mijnbouwconstructie/) | EPC | points | 4,975 |
| [bodemverontreiniging_besluit](./bodemverontreiniging_besluit/) | SLD | polygons | 121 |
| [grondwatergebruiksysteem](./grondwatergebruiksysteem/) | GUF | points | 50,637 |
| [bodemkaart](./bodemkaart/) → soilarea, areaofpedologicalinterest | SGM | polygons | 48,025 / 6,192 |
| [geomorfologische_kaart](./geomorfologische_kaart/) → geomorphological_area (+2) | GMM | polygons | 80,148 / 40,840 / 70 |

The **Soil Map** and **Geomorphological Map** are organised as sub-catalogs, with one collection per
distinct map layer in the source GeoPackage (see each sub-catalog's description for how the layers
differ).

## Coming next

- **Tabular (non-geo) collections** for objects with no own geometry: groundwater monitoring
  networks (GMN), production dossiers (GPD), and groundwater composition analyses (GAR).
- **Phase 2** point datasets: soil/geological/geotechnical boreholes (BHR-P, BHR-G, BHR-GT),
  groundwater monitoring wells (GMW), and integrated groundwater monitoring (GM).
- **Metadata-only entries** for the 3D/raster subsurface models (GeoTOP, DGM, REGIS II, WDM) and the
  large point datasets CPT and SAD.

## License

[CC0-1.0](https://creativecommons.org/publicdomain/zero/1.0/) — public domain.

---
*Part of [Portolan NL](../README.md).*
"""

if __name__ == "__main__":
    for p in COLL_PATHS:
        coll_readme(p)
    with open(os.path.join(ROOT, "vro", "README.md"), "w") as f:
        f.write(VRO_README)
    print("  wrote vro/README.md")
    print("DONE")

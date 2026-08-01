#!/usr/bin/env python3
"""Build the vro/ subcatalog + the two map sub-subcatalogs, and wire the root catalog."""
import json
import os

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from tools.lib import paths, stac

PORTOLAN_SCHEMA = "https://schemas.portolan-sdi.org/portolan/v0.1.0/schema.json"

# Generators write into the published tree; paths.py owns where that is.
ROOT = str(paths.CATALOG)
DATA = paths.DATA_BASE
SRC = paths.SRC_BASE


def child(href, title):
    return stac.link("child", href, stac.JSON, title)


def write(path, obj):
    stac.write_json(os.path.join(ROOT, path), obj)
    print("  wrote", path)


# ---- vro/catalog.json -------------------------------------------------------
vro = {
    "type": "Catalog", "id": "vro", "stac_version": "1.1.0",
    "title": "Ministerie van Volkshuisvesting en Ruimtelijke Ordening (VRO)",
    "description": (
        "Open geodata for which the Ministry of Housing and Spatial Planning (VRO) is the "
        "responsible provider on PDOK, drawn from the **Basisregistratie Ondergrond (BRO)** — the "
        "Dutch Key Registry of the Subsurface. These are the BRO datasets flagged as EU **High Value "
        "Data**: soil and geological boreholes, groundwater systems, soil-contamination decisions, "
        "mining constructions, and the national Soil Map and Geomorphological Map. The underlying "
        "data is produced by **TNO – Geologische Dienst Nederland** (subsurface objects) and "
        "**Wageningen Environmental Research** (the soil and geomorphological maps). All data is "
        "CC0 1.0 (public domain).\n\nEach collection is republished here as cloud-native GeoParquet "
        "+ PMTiles with STAC metadata. Datasets whose source GeoPackage contains several distinct "
        "map layers (the Soil Map and the Geomorphological Map) are organised as sub-catalogs with "
        "one collection per layer."
    ),
    "links": [
        stac.root_link(1),
        stac.parent_link(),
        stac.describedby_link("VRO subcatalog"),
        stac.agents_link(),
        child("./wandonderzoek/collection.json", "BRO Soil Trench Investigation (SFR)"),
        child("./mijnbouwconstructie/collection.json", "BRO Mining Construction (EPC)"),
        child("./bodemverontreiniging_besluit/collection.json",
              "BRO Government Decision on Soil Contamination (SLD)"),
        child("./grondwatergebruiksysteem/collection.json", "BRO Groundwater Use System (GUF)"),
        child("./bodemkaart/catalog.json", "BRO Soil Map of the Netherlands 1:50,000 (SGM)"),
        child("./geomorfologische_kaart/catalog.json",
              "BRO Geomorphological Map of the Netherlands 1:50,000 (GMM)"),
    ],
}
vro["stac_extensions"] = [PORTOLAN_SCHEMA]
write("vro/catalog.json", vro)

# ---- vro/bodemkaart/catalog.json -------------------------------------------
bodem = {
    "type": "Catalog", "id": "bodemkaart", "stac_version": "1.1.0",
    "title": "BRO Soil Map of the Netherlands 1:50,000 (Bodemkaart, SGM)",
    "description": (
        "The national Soil Map of the Netherlands at scale 1:50,000 (Bodemkaart van Nederland, BRO "
        "object SGM), produced by Wageningen Environmental Research. The source GeoPackage holds two "
        "distinct polygon layers, published here as separate collections:\n\n"
        "- **soilarea** — the soil map itself: 48,025 soil-area polygons, each enriched with its "
        "primary soil unit (bodemcode) and main soil class (e.g. Podzolgronden, Zeekleigronden, "
        "Veengronden). This is the layer you map and analyse.\n"
        "- **areaofpedologicalinterest** — 6,192 polygons delimiting where soil mapping applies "
        "(the area of pedological interest); built-up areas and large water bodies are excluded.\n\n"
        "CC0 1.0. Provider VRO; bronhouder Wageningen Environmental Research."
    ),
    "links": [
        stac.root_link(2),
        stac.parent_link(title="Ministerie van Volkshuisvesting en Ruimtelijke Ordening (VRO)"),
        stac.preview_link(),
        child("./soilarea/collection.json", "Soil areas (the soil map)"),
        child("./areaofpedologicalinterest/collection.json", "Area of pedological interest"),
    ],
    "assets": {"thumbnail": stac.thumbnail_asset()},
}
bodem["links"] += [stac.describedby_link(bodem["title"]), stac.agents_link()]
bodem["stac_extensions"] = [PORTOLAN_SCHEMA]
write("vro/bodemkaart/catalog.json", bodem)

# ---- vro/geomorfologische_kaart/catalog.json -------------------------------
geom = {
    "type": "Catalog", "id": "geomorfologische_kaart", "stac_version": "1.1.0",
    "title": "BRO Geomorphological Map of the Netherlands 1:50,000 (Geomorfologische kaart, GMM)",
    "description": (
        "The national Geomorphological Map of the Netherlands at scale 1:50,000 (BRO object GMM), "
        "produced by Wageningen Environmental Research. The source GeoPackage holds three distinct "
        "polygon layers, published here as separate collections:\n\n"
        "- **geomorphological_area** — the map itself: 80,148 landform polygons, each classified by "
        "genesis (eolian, fluvial, marine, glacial, anthropogenic, …), relief form and landform "
        "subgroup. This is the layer you map and analyse.\n"
        "- **area_of_geomorphological_interest** — 40,840 polygons delimiting where the "
        "geomorphological mapping applies.\n"
        "- **geomorphological_area_collection** — 70 polygons grouping the map by survey / "
        "publication unit.\n\n"
        "CC0 1.0. Provider VRO; bronhouder Wageningen Environmental Research."
    ),
    "links": [
        stac.root_link(2),
        stac.parent_link(title="Ministerie van Volkshuisvesting en Ruimtelijke Ordening (VRO)"),
        stac.preview_link(),
        child("./geomorphological_area/collection.json", "Geomorphological areas (the map)"),
        child("./area_of_geomorphological_interest/collection.json",
              "Area of geomorphological interest"),
        child("./geomorphological_area_collection/collection.json", "Map area collections"),
    ],
    "assets": {"thumbnail": stac.thumbnail_asset()},
}
geom["links"] += [stac.describedby_link(geom["title"]), stac.agents_link()]
geom["stac_extensions"] = [PORTOLAN_SCHEMA]
write("vro/geomorfologische_kaart/catalog.json", geom)

# ---- wire root catalog ------------------------------------------------------
root_path = os.path.join(ROOT, "catalog.json")
root = json.load(open(root_path))
if not any(l.get("href") == "./vro/catalog.json" for l in root["links"]):
    # insert after the last existing child link
    idx = max(i for i, l in enumerate(root["links"]) if l.get("rel") == "child")
    root["links"].insert(idx + 1, child("./vro/catalog.json",
                                        "Ministerie van Volkshuisvesting en Ruimtelijke Ordening (VRO)"))
    stac.write_json(root_path, root)
    print("  wired root catalog -> vro")
else:
    print("  root already wired")
print("DONE")

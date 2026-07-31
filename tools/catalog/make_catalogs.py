#!/usr/bin/env python3
"""Build the vro/ subcatalog + the two map sub-subcatalogs, and wire the root catalog."""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA = "https://data.source.coop/cholmes/portolan-nl"
SRC = "https://source.coop/cholmes/portolan-nl"


def child(href, title):
    return {"rel": "child", "href": href, "type": "application/json", "title": title}


def write(path, obj):
    with open(os.path.join(ROOT, path), "w") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
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
        {"rel": "root", "href": "../catalog.json", "type": "application/json",
         "title": "Portolan NL — Cloud-Native Dutch Geodata"},
        {"rel": "self", "href": f"{DATA}/vro/catalog.json", "type": "application/json"},
        {"rel": "parent", "href": "../catalog.json", "type": "application/json"},
        {"rel": "describedby", "href": f"{SRC}/vro/README.md", "type": "text/html",
         "title": "VRO subcatalog documentation"},
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
        {"rel": "root", "href": "../../catalog.json", "type": "application/json",
         "title": "Portolan NL — Cloud-Native Dutch Geodata"},
        {"rel": "self", "href": f"{DATA}/vro/bodemkaart/catalog.json", "type": "application/json"},
        {"rel": "parent", "href": "../catalog.json", "type": "application/json",
         "title": "Ministerie van Volkshuisvesting en Ruimtelijke Ordening (VRO)"},
        {"rel": "preview", "href": "./thumbnail.png", "type": "image/png", "title": "Thumbnail (PDOK preview)"},
        child("./soilarea/collection.json", "Soil areas (the soil map)"),
        child("./areaofpedologicalinterest/collection.json", "Area of pedological interest"),
    ],
    "assets": {"thumbnail": {"href": "./thumbnail.png", "type": "image/png",
                             "title": "Thumbnail (PDOK preview)", "roles": ["thumbnail"]}},
}
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
        {"rel": "root", "href": "../../catalog.json", "type": "application/json",
         "title": "Portolan NL — Cloud-Native Dutch Geodata"},
        {"rel": "self", "href": f"{DATA}/vro/geomorfologische_kaart/catalog.json",
         "type": "application/json"},
        {"rel": "parent", "href": "../catalog.json", "type": "application/json",
         "title": "Ministerie van Volkshuisvesting en Ruimtelijke Ordening (VRO)"},
        {"rel": "preview", "href": "./thumbnail.png", "type": "image/png", "title": "Thumbnail (PDOK preview)"},
        child("./geomorphological_area/collection.json", "Geomorphological areas (the map)"),
        child("./area_of_geomorphological_interest/collection.json",
              "Area of geomorphological interest"),
        child("./geomorphological_area_collection/collection.json", "Map area collections"),
    ],
    "assets": {"thumbnail": {"href": "./thumbnail.png", "type": "image/png",
                             "title": "Thumbnail (PDOK preview)", "roles": ["thumbnail"]}},
}
write("vro/geomorfologische_kaart/catalog.json", geom)

# ---- wire root catalog ------------------------------------------------------
root_path = os.path.join(ROOT, "catalog.json")
root = json.load(open(root_path))
if not any(l.get("href") == "./vro/catalog.json" for l in root["links"]):
    # insert after the last existing child link
    idx = max(i for i, l in enumerate(root["links"]) if l.get("rel") == "child")
    root["links"].insert(idx + 1, child("./vro/catalog.json",
                                        "Ministerie van Volkshuisvesting en Ruimtelijke Ordening (VRO)"))
    with open(root_path, "w") as f:
        json.dump(root, f, indent=2, ensure_ascii=False)
    print("  wired root catalog -> vro")
else:
    print("  root already wired")
print("DONE")

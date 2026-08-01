#!/usr/bin/env python3
"""Generate STAC collection.json for the VRO/BRO vector collections.

Reads real GeoParquet metadata (geometry type, CRS, columns, bbox) and writes
collection.json following the rvo/natura2000 template: table/vector/web-map-links/
projection extensions, full assets (data, pmtiles, thumbnail, styles), a
portolan:styles manifest, license CC0-1.0, and via links to the PDOK source.

Run from catalog root:  python3 vro/scripts/make_collections.py
"""
import glob
import json
import os

import geopandas as gpd
import pyarrow.parquet as pq

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from tools.lib import paths, stac

# Generators write into the published tree; paths.py owns where that is.
ROOT = str(paths.CATALOG)

def data_dir(cdir):
    """Catalog directory -> the directory holding its data files.

    The repo holds no parquet; it lives in the working directory. Generators
    still write metadata into cdir, they just read the data from here.
    """
    return str(paths.DATA_ROOT / os.path.relpath(cdir, ROOT))

DATA_BASE = paths.DATA_BASE

# shared BRO column descriptions (English real-table columns)
SHARED_COLS = {
    "bro_id": "BRO registration ID — unique identifier of the object in the Basisregistratie Ondergrond.",
    "quality_regime": "BRO quality regime: IMBRO (full assurance) or IMBRO/A (transitional/lower assurance).",
    "delivery_accountable_party": "KvK number of the party accountable for delivery (bronhouder).",
    "delivery_context": "Legal/administrative framework under which the object was registered.",
    "applied_transformation": "Whether a coordinate/height transformation was applied (ja/nee).",
    "standardized_location": "Object location — WKB geometry in EPSG:4258 (ETRS89).",
    "standardized_location_bbox": "Per-feature bounding box struct (xmin,ymin,xmax,ymax) for spatial filtering.",
    "geom": "Feature geometry (WKB) in EPSG:28992 (Amersfoort / RD New).",
    "geom_bbox": "Per-feature bounding box struct for spatial filtering.",
    "fid": "Feature ID.",
    "soil_face_research_pk": "Internal primary key.",
}

# per-collection config
# key = path under vro/ ; fields drive titles, descriptions, source links, columns
C = {
    "wandonderzoek": dict(
        title="BRO Soil Trench Investigation (SFR / Wandonderzoek)",
        layer="wandonderzoek", slug="bro-wandonderzoek", maxzoom=6,
        short="2,806 soil-profile pit/trench investigations (wandonderzoek, SFR) from the Dutch "
              "Key Registry of the Subsurface (BRO). Each point is a described soil face used for "
              "soil mapping, agriculture and nature management. Produced under VRO; bronhouder TNO.",
        cols={"survey_purpose": "Purpose of the survey (e.g. national soil map unit, nature soil build-up).",
              "discipline": "Investigation discipline (bodemkunde / soil science).",
              "research_report_date": "Date the research report was registered (YYYY-MM-DD, free text).",
              "fieldwork_date": "Date of fieldwork (YYYY-MM-DD, free text).",
              "litter_layer_investigated": "Whether the litter layer was investigated (ja/nee)."}),
    "mijnbouwconstructie": dict(
        title="BRO Mining Construction (EPC / Mijnbouwconstructie)",
        layer="mijnbouwconstructie", slug="bro-mijnbouwconstructie", maxzoom=11,
        short="4,975 mining-law subsurface constructions (mijnbouwconstructie, EPC) from the BRO — "
              "deep boreholes, mine systems and salt caverns for oil, gas, geothermal energy and "
              "storage. Produced under VRO; bronhouder TNO.",
        cols={"legal_status": "Legal status of the construction (e.g. onbekend, buitenGebruikMijnbouw).",
              "owner": "Owner / operator of the mining construction.",
              "source_reference": "Reference to the source document."}),
    "bodemverontreiniging_besluit": dict(
        title="BRO Government Decision on Soil Contamination (SLD)",
        layer="bodemverontreiniging_besluit", slug="bro-overheidsbesluit-bodemverontreiniging", maxzoom=13,
        short="121 formal government decisions on soil contamination (overheidsbesluit "
              "bodemverontreiniging, SLD) from the BRO — areas with an authority decision on "
              "assessment, remediation or aftercare. Produced under VRO; bronhouder TNO.",
        cols={}),
    "grondwatergebruiksysteem": dict(
        title="BRO Groundwater Use System (GUF / Grondwatergebruiksysteem)",
        layer="grondwatergebruiksysteem", slug="bro-grondwatergebruiksysteem", maxzoom=12,
        short="50,637 groundwater use systems (grondwatergebruiksysteem, GUF) from the BRO — "
              "constructions that extract or infiltrate groundwater, including ground-source "
              "energy (ATES/bodemenergie). Produced under VRO; bronhouder TNO.",
        cols={}),
    "bodemkaart/soilarea": dict(
        title="BRO Soil Map of the Netherlands 1:50,000 — Soil areas (SGM)",
        layer="soilarea", slug="bro-bodemkaart", maxzoom=12, crs=28992,
        short="48,025 soil-area polygons of the national Soil Map of the Netherlands 1:50,000 "
              "(Bodemkaart, SGM), enriched here with the primary soil unit and main soil class. "
              "Produced under VRO; bronhouder Wageningen Environmental Research.",
        cols={"maparea_id": "Soil-area polygon identifier.",
              "maparea_collection": "Survey campaign / map collection the polygon belongs to.",
              "soilslope": "Slope class of the soil area (mostly 'Niet opgenomen').",
              "soilunit_code": "Primary soil-unit code (BRO bodemcode), e.g. 'cHn21'.",
              "hoofdklasse": "Main soil class (mainsoilclassification), e.g. Podzolgronden, Zeekleigronden.",
              "bodemklasse": "Full soil classification text of the primary soil unit.",
              "legenda_url": "URL to the official soil-class legend entry."}),
    "bodemkaart/areaofpedologicalinterest": dict(
        title="BRO Soil Map — Area of pedological interest",
        layer="areaofpedologicalinterest", slug="bro-bodemkaart", maxzoom=12, crs=28992,
        short="6,192 polygons delimiting the area of pedological interest of the national Soil Map "
              "1:50,000 (Bodemkaart, SGM) — where soil mapping applies. Produced under VRO; "
              "bronhouder Wageningen Environmental Research.",
        cols={}),
    "geomorfologische_kaart/geomorphological_area": dict(
        title="BRO Geomorphological Map 1:50,000 — Geomorphological areas (GMM)",
        layer="geomorphological_area", slug="bro-geomorfologische-kaart", maxzoom=12, crs=28992,
        short="80,148 landform polygons of the national Geomorphological Map of the Netherlands "
              "1:50,000 (Geomorfologische kaart, GMM), classified by genesis, relief and landform "
              "subgroup. Produced under VRO; bronhouder Wageningen Environmental Research.",
        cols={"genese_code": "Genesis code (1=Glaciaal, 2=Periglaciaal, 3=Denudatief, 4=Fluviatiel, "
                             "5=Eolisch, 6=Lacustrien, 7=Marien, 8=Organogeen, 9=Antropogeen, 0=Tectonisch).",
              "genese_description": "Genesis description (Dutch).",
              "relief_code": "Relief-form code.",
              "landform_subgroup_code": "Landform subgroup code (e.g. B44 = stroomrug/stream ridge).",
              "landform_subgroup_description": "Landform subgroup description (Dutch).",
              "landform_subgroup_url": "URL to the landform legend entry.",
              "active_process": "Whether the landform process is still active (ja/nee).",
              "additional_surface_relief_code": "Additional surface relief code (optional).",
              "additional_surface_cover_code": "Additional surface cover code (optional)."}),
    "geomorfologische_kaart/area_of_geomorphological_interest": dict(
        title="BRO Geomorphological Map — Area of geomorphological interest",
        layer="area_of_geomorphological_interest", slug="bro-geomorfologische-kaart", maxzoom=12, crs=28992,
        short="40,840 polygons delimiting the area of geomorphological interest of the national "
              "Geomorphological Map 1:50,000 (GMM). Produced under VRO; bronhouder Wageningen "
              "Environmental Research.",
        cols={}),
    "geomorfologische_kaart/geomorphological_area_collection": dict(
        title="BRO Geomorphological Map — Map area collections",
        layer="geomorphological_area_collection", slug="bro-geomorfologische-kaart", maxzoom=12, crs=28992,
        short="70 map-area collection polygons grouping the national Geomorphological Map 1:50,000 "
              "(GMM) by survey/publication. Produced under VRO; bronhouder Wageningen Environmental "
              "Research.",
        cols={}),
}

STYLE_TITLES = {
    "default": "Default", "by-survey-purpose": "By survey purpose",
    "by-legal-status": "By legal status", "by-quality-regime": "By quality regime",
    "by-texture": "By texture (sand / clay / peat)", "by-relief": "By relief class",
    "by-interest": "By area type", "by-collection": "By survey campaign",
    "by-type": "By type", "by-method": "By inventory method",
    "by-landform": "By landform subgroup", "by-litter": "By litter layer investigated",
    "by-delivery-context": "By delivery context", "by-bronhouder": "By data owner (bronhouder)",
}


def geo_meta(parquet):
    md = pq.read_metadata(parquet).metadata
    geo = json.loads(md[b"geo"].decode())
    pc = geo["primary_column"]
    col = geo["columns"][pc]
    gtype = col.get("geometry_types", ["Unknown"])
    crs = col.get("crs") or {}
    epsg = None
    cid = crs.get("id") if isinstance(crs, dict) else None
    if cid and str(cid.get("authority", "")).upper() == "EPSG":
        epsg = int(cid["code"])
    return pc, (gtype[0] if gtype else "Unknown"), epsg


def arrow_cols(parquet):
    sch = pq.read_schema(parquet)
    out = []
    for f in sch:
        t = str(f.type)
        tmap = {"int64": "int64", "int32": "int32", "double": "float64",
                "string": "string", "large_string": "string", "binary": "binary"}
        out.append((f.name, tmap.get(t, t)))
    return out


def build(path, cfg):
    cdir = os.path.join(ROOT, "vro", path)
    layer = cfg["layer"]
    parquet = os.path.join(data_dir(cdir), f"{layer}.parquet")
    pmtiles = f"./{layer}.pmtiles"
    depth = 2 + path.count("/")  # links back to root catalog.json
    parent = "../catalog.json"
    pc, gtype, epsg = geo_meta(parquet)
    if cfg.get("crs"):
        epsg = cfg["crs"]
    # WGS84 extent
    g = gpd.read_parquet(parquet)
    if g.crs is None:
        g.set_crs(epsg or 4258, inplace=True)
    minx, miny, maxx, maxy = g.to_crs(4326).total_bounds
    n = len(g)
    cx, cy = (minx + maxx) / 2, (miny + maxy) / 2
    # columns
    cols = []
    descs = dict(SHARED_COLS); descs.update(cfg.get("cols", {}))
    for name, typ in arrow_cols(parquet):
        c = {"name": name, "type": typ}
        if name in descs:
            c["description"] = descs[name]
        cols.append(c)
    # styles
    style_files = sorted(glob.glob(os.path.join(cdir, "styles", "*.json")))
    order = []
    assets = {
        layer: stac.asset(f"./{layer}.parquet", "application/vnd.apache.parquet",
                          f"{cfg['title']} (GeoParquet)", ["data"]),
        "pmtiles": stac.asset(pmtiles, "application/vnd.pmtiles",
                              f"{cfg['title']} (vector tiles)", ["visual"]),
        "thumbnail": stac.thumbnail_asset(),
    }
    for sf in style_files:
        nm = os.path.splitext(os.path.basename(sf))[0]
        key = f"styles/{nm}"
        assets[key] = stac.asset(f"./styles/{nm}.json", stac.JSON,
                                 f"{cfg['title']} — {STYLE_TITLES.get(nm, nm)}", ["style"])
    # default first in manifest
    names = [os.path.splitext(os.path.basename(s))[0] for s in style_files]
    names = (["default"] if "default" in names else []) + [x for x in names if x != "default"]
    order = [f"styles/{x}" for x in names]

    atom = f"https://service.pdok.nl/tno/{cfg['slug']}/atom/index.xml"
    wms = f"https://service.pdok.nl/tno/{cfg['slug']}/wms/v1_0?request=GetCapabilities&service=WMS"

    coll = {
        "type": "Collection", "id": layer, "stac_version": "1.1.0",
        "title": cfg["title"],
        "description": cfg["short"] + "\n\n🤖 AI/Agent users: see llms.txt for field descriptions, "
                       "query examples and usage tips.",
        "links": [
            stac.root_link(depth),
            stac.self_link(f"vro/{path}/collection.json"),
            stac.parent_link(parent),
            stac.link("via", atom, "application/atom+xml",
                      "PDOK Atom download (source GeoPackage)"),
            stac.link("via", wms, "application/xml", "PDOK WMS (GetCapabilities)"),
            # web-map-links: the extension is declared below, and declaring it
            # without a web-map link is a validation error. Every sibling
            # collection in the catalog carries this link.
            stac.link("pmtiles", f"{paths.DATA_BASE}/vro/{path}/{layer}.pmtiles",
                      "application/vnd.pmtiles"),
            stac.link("llms", "./llms.txt", "text/markdown", "Agent/LLM usage guide"),
            stac.link("describedby", f"{paths.SRC_BASE}/vro/{path}/README.md",
                      "text/html", f"{cfg['title']} documentation"),
        ],
        "stac_extensions": [
            "https://stac-extensions.github.io/table/v1.2.0/schema.json",
            "https://stac-extensions.github.io/vector/v0.1.0/schema.json",
            "https://stac-extensions.github.io/web-map-links/v1.3.0/schema.json",
            "https://stac-extensions.github.io/projection/v2.0.0/schema.json",
        ],
        "table:row_count": n, "table:primary_geometry": pc, "table:columns": cols,
        "geoparquet:geometry_type": gtype, "geoparquet:feature_count": n,
        "proj:epsg": epsg,
        "pmtiles:min_zoom": 0, "pmtiles:max_zoom": cfg["maxzoom"], "pmtiles:tile_type": "mvt",
        "pmtiles:center": [round(cx, 6), round(cy, 6), cfg["maxzoom"]],
        "pmtiles:layers": [layer],
        "extent": {"spatial": {"bbox": [[round(minx, 6), round(miny, 6), round(maxx, 6), round(maxy, 6)]]},
                   "temporal": {"interval": [[None, None]]}},
        "assets": assets, "license": "CC0-1.0",
        "summaries": {"geoparquet:geometry_type": [gtype], "vector:geometry_types": [gtype]},
        "portolan:styles": order,
    }
    out = os.path.join(cdir, "collection.json")
    stac.write_json(out, coll)
    print(f"  {out}  ({gtype}, {n} feats, EPSG:{epsg}, {len(order)} styles)")


if __name__ == "__main__":
    for path, cfg in C.items():
        build(path, cfg)
    print("DONE")

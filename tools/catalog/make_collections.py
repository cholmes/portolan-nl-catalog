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
from tools.lib import paths, stac, geoparquet

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
        landing=("https://www.nationaalgeoregister.nl/geonetwork/srv/dut/catalog.search#/metadata/6cbbecc1-753b-416d-ad72-1621695ec356",
                 "NGR metadata page: BRO Wandonderzoek bodemkunde (SFR)"),
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
        landing=("https://www.pdok.nl/introductie/-/article/bro-mijnbouwconstructie-epc-",
                 "PDOK dataset page: BRO Mijnbouwconstructie (EPC)"),
        title="BRO Mining Construction (EPC / Mijnbouwconstructie)",
        layer="mijnbouwconstructie", slug="bro-mijnbouwconstructie", maxzoom=11,
        short="4,975 mining-law subsurface constructions (mijnbouwconstructie, EPC) from the BRO — "
              "deep boreholes, mine systems and salt caverns for oil, gas, geothermal energy and "
              "storage. Produced under VRO; bronhouder TNO.",
        cols={"legal_status": "Legal status of the construction (e.g. onbekend, buitenGebruikMijnbouw).",
              "owner": "Owner / operator of the mining construction.",
              "source_reference": "Reference to the source document."}),
    "bodemverontreiniging_besluit": dict(
        landing=("https://www.pdok.nl/introductie/-/article/bro-overheidsbesluit-bodemverontreiniging-sld-",
                 "PDOK dataset page: BRO Overheidsbesluit bodemverontreiniging (SLD)"),
        title="BRO Government Decision on Soil Contamination (SLD)",
        layer="bodemverontreiniging_besluit", slug="bro-overheidsbesluit-bodemverontreiniging", maxzoom=13,
        short="121 formal government decisions on soil contamination (overheidsbesluit "
              "bodemverontreiniging, SLD) from the BRO — areas with an authority decision on "
              "assessment, remediation or aftercare. Produced under VRO; bronhouder TNO.",
        cols={}),
    "grondwatergebruiksysteem": dict(
        wms="https://service.pdok.nl/tno/bro-grondwatergebruiksysteem-geharmoniseerd/wms/v2_0?request=GetCapabilities&service=WMS",
        landing=("https://www.pdok.nl/introductie/-/article/bro-grondwatergebruiksysteem-guf-",
                 "PDOK dataset page: BRO Grondwatergebruiksysteem (GUF)"),
        title="BRO Groundwater Use System (GUF / Grondwatergebruiksysteem)",
        layer="grondwatergebruiksysteem", slug="bro-grondwatergebruiksysteem", maxzoom=12,
        short="50,637 groundwater use systems (grondwatergebruiksysteem, GUF) from the BRO — "
              "constructions that extract or infiltrate groundwater, including ground-source "
              "energy (ATES/bodemenergie). Produced under VRO; bronhouder TNO.",
        cols={}),
    "bodemkaart/soilarea": dict(
        landing=("https://www.pdok.nl/introductie/-/article/bro-bodemkaart-sgm-",
                 "PDOK dataset page: BRO Bodemkaart (SGM)"),
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
        landing=("https://www.pdok.nl/introductie/-/article/bro-bodemkaart-sgm-",
                 "PDOK dataset page: BRO Bodemkaart (SGM)"),
        title="BRO Soil Map — Area of pedological interest",
        layer="areaofpedologicalinterest", slug="bro-bodemkaart", maxzoom=12, crs=28992,
        short="6,192 polygons delimiting the area of pedological interest of the national Soil Map "
              "1:50,000 (Bodemkaart, SGM) — where soil mapping applies. Produced under VRO; "
              "bronhouder Wageningen Environmental Research.",
        cols={}),
    "geomorfologische_kaart/geomorphological_area": dict(
        wms="https://service.pdok.nl/tno/bro-geomorfologische-kaart/wms/v2_0?request=GetCapabilities&service=WMS",
        landing=("https://www.pdok.nl/introductie/-/article/bro-geomorfologische-kaart-gmm-",
                 "PDOK dataset page: BRO Geomorfologische kaart (GMM)"),
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
        wms="https://service.pdok.nl/tno/bro-geomorfologische-kaart/wms/v2_0?request=GetCapabilities&service=WMS",
        landing=("https://www.pdok.nl/introductie/-/article/bro-geomorfologische-kaart-gmm-",
                 "PDOK dataset page: BRO Geomorfologische kaart (GMM)"),
        title="BRO Geomorphological Map — Area of geomorphological interest",
        layer="area_of_geomorphological_interest", slug="bro-geomorfologische-kaart", maxzoom=12, crs=28992,
        short="40,840 polygons delimiting the area of geomorphological interest of the national "
              "Geomorphological Map 1:50,000 (GMM). Produced under VRO; bronhouder Wageningen "
              "Environmental Research.",
        cols={}),
    "geomorfologische_kaart/geomorphological_area_collection": dict(
        wms="https://service.pdok.nl/tno/bro-geomorfologische-kaart/wms/v2_0?request=GetCapabilities&service=WMS",
        landing=("https://www.pdok.nl/introductie/-/article/bro-geomorfologische-kaart-gmm-",
                 "PDOK dataset page: BRO Geomorfologische kaart (GMM)"),
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



# Researched column definitions, grounded in the BRO catalogi on
# docs.geostandaarden.nl (content-verified 2026-11-20; see the catalogus
# via links the collections carry). Merged over SHARED_COLS per collection.
RESEARCHED_COLS = {
 "geomorfologische_kaart/geomorphological_area": {
  "collection_id": "ID of the geomorphological area collection (Geomorfologische vlakcollectie) this polygon belongs to (GMM cat. 4.3.2.1 identificatie).",
  "identification": "Unique ID of the map polygon (Kaartvlak identificatie), a published spatial-object identifier for external reference (GMM cat. 4.3.3.1).",
  "genese_validfrom": "Start date (yyyymmdd) from which the recorded genesis (ontstaanswijze) value is valid; material history per GMM cat. 2.5, 4.3.8.3.",
  "genese_validto": "End date (yyyymmdd) of validity of the recorded genesis value; empty while current (material history, GMM cat. 2.5).",
  "landform_subgroup_validfrom": "Start date (yyyymmdd) from which the recorded landform subgroup (landvormsubgroep) value is valid (material history, GMM cat. 2.5, 4.3.7.5).",
  "landform_subgroup_validto": "End date (yyyymmdd) of validity of the recorded landform subgroup value; empty while current (material history, GMM cat. 2.5).",
  "additional_surface_relief_description": "Relief addition (toevoeging relief): further typing of the relief and/or relative elevation of the landform unit (GMM cat. 4.3.7.1, list 5.4).",
  "additional_surface_relief_validfrom": "Start date (yyyymmdd) from which the recorded relief addition is valid (material history, GMM cat. 2.5).",
  "additional_surface_relief_validto": "End date (yyyymmdd) of validity of the recorded relief addition; empty while current (material history, GMM cat. 2.5).",
  "additional_surface_cover_description": "Cover addition (toevoeging bedekking): typing of the deviating sediment layer covering the landform subgroup (GMM cat. 4.3.7.3, 6.3.6).",
  "additional_surface_cover_validfrom": "Start date (yyyymmdd) from which the recorded cover addition is valid (material history, GMM cat. 2.5).",
  "additional_surface_cover_validto": "End date (yyyymmdd) of validity of the recorded cover addition; empty while current (material history, GMM cat. 2.5).",
  "relief_klasse": "Relief class (reliefklasse): whether the relief code is for valley-shaped (dalvormige) or non-valley landform groups (GMM cat. 4.3.9.2, 4.3.10).",
  "relief_subklasse": "Relief description (relief) of the non-valley relief code, e.g. 'Vrij vlak, laaggelegen relief'; empty for valleys (GMM cat. list 5.3).",
  "helling": "Slope: class of the angle of the steepest slope of the landform; non-valley relief codes only (GMM cat. list 5.3, 6.3.3).",
  "lokaal_maximaal_hoogteverschil": "Local maximum height difference within the landform, in metres; non-valley relief codes only (GMM cat. list 5.3, 6.3.3).",
  "diepte_tov_omgeving": "Depth of the valley incision relative to the surroundings, in metres; valley relief codes only (GMM cat. list 5.2 diepte).",
  "steilste_verhang": "Steepest gradient (steilste verhang) of the valley form; valley relief codes only (GMM cat. list 5.2).",
  "maximaal_hoogteverschil": "Maximum height difference within the form, in metres; valley relief codes only (GMM cat. list 5.2).",
  "maximaal_verval": "Maximum drop (maximaal verval) of the valley, in metres; valley relief codes only (GMM cat. list 5.2).",
  "relief_validfrom": "Start date (yyyymmdd) from which the recorded relief typing is valid (material history, GMM cat. 2.5, 4.3.7.4).",
  "relief_validto": "End date (yyyymmdd) of validity of the recorded relief typing; empty while current (material history, GMM cat. 2.5)."
 },
 "geomorfologische_kaart/geomorphological_area_collection": {
  "version": "Version of the delivered GMM map model (e.g. GEOM50000-V2025-1); model version management per GMM cat. 6.3.1.",
  "collection_id": "Unique identifier (identificatie) of the geomorphological area collection in the GMM registration object (GMM cat. 4.3.2.1).",
  "name": "Name of the (sub)collection: the map sheet number or project name, e.g. Bergen_op_Zoom (GMM cat. 4.3.1.1 naam).",
  "inventorymethod": "Inventory method (inventarisatiemethode): analogue mapping with field survey or digital mapping with field verification (GMM cat. 4.3.2.5, 6.5).",
  "source": "Elevation source (bron/Bestand): name and version of the height data file used to delineate and classify the areas, e.g. AHN4 (GMM cat. 4.3.2.8, 4.3.6).",
  "beginlifespan": "Date (yyyymmdd) this version of the spatial object was inserted or changed in the dataset (begin levensduur, GMM cat. 4.3.2.6).",
  "endlifespan": "Date (yyyymmdd) this version of the spatial object was superseded or retired; empty while current (einde levensduur, GMM cat. 4.3.2.7).",
  "citation_id": "Reference to the CI_Citation record documenting this collection, e.g. the descriptive report of the survey or update (GMM cat. 4.3.2.4)."
 },
 "geomorfologische_kaart/area_of_geomorphological_interest": {
  "identification": "Unique ID of the map polygon (Kaartvlak identificatie) of this area of geomorphological interest (GMM cat. 4.3.3.1).",
  "collection_id": "ID of the geomorphological area collection (vlakcollectie) this polygon belongs to (GMM cat. 4.3.2.1).",
  "type": "Type of geomorphological interest (geomorfologisch belang): Dijk or Water; features relevant to landform formation, without a landform description (GMM cat. 4.3.4)."
 },
 "bodemkaart/areaofpedologicalinterest": {
  "maparea_id": "Unique ID of this map polygon in the delivered SGM model version (e.g. V2025-1.areaofpedologicalinterrest.NNN).",
  "maparea_collection": "Soil area collection (bodemvlakcollectie) this polygon belongs to, given by collection kind (SGM cat. 4.3.6.2).",
  "beginlifespan": "Date/time this version of the spatial object was inserted or changed in the dataset (INSPIRE lifespan; not in SGM catalogus v1.2; null in data).",
  "endlifespan": "Date/time this version of the spatial object was superseded or retired (INSPIRE lifespan; not in SGM catalogus v1.2; null in data).",
  "pedologicalinterest": "Pedological interest (bodemkundig belang): area type where soil cannot be typed, relevant for interpreting surrounding soils (SGM cat. 4.3.8)."
 },
 "bodemverontreiniging_besluit": {
  "soil_legal_decision_pk": "Technical surrogate key from the PDOK GeoPackage delivery (sequential integer, unique per row); not defined in the SLD catalogus."
 },
 "mijnbouwconstructie": {
  "mining_construction_pk": "Technical surrogate key from the PDOK GeoPackage delivery (sequential integer, unique per row); not defined in the EPC catalogus."
 },
 "grondwatergebruiksysteem": {
  "groundwater_usage_facility_pk": "Technical surrogate key from the PDOK GeoPackage delivery (sequential integer, unique per row); not defined in the GUF catalogus."
 }
}

# The catalogus each collection's column definitions come from (via link).
CATALOGUS = {
 "geomorfologische_kaart/geomorphological_area": [
  "https://docs.geostandaarden.nl/bro/def-im-GMM-20230607/",
  "Column definitions: BRO Catalogus geomorfologische kaart (GMM) v1.1"
 ],
 "geomorfologische_kaart/geomorphological_area_collection": [
  "https://docs.geostandaarden.nl/bro/def-im-GMM-20230607/",
  "Column definitions: BRO Catalogus geomorfologische kaart (GMM) v1.1"
 ],
 "geomorfologische_kaart/area_of_geomorphological_interest": [
  "https://docs.geostandaarden.nl/bro/def-im-GMM-20230607/",
  "Column definitions: BRO Catalogus geomorfologische kaart (GMM) v1.1"
 ],
 "bodemkaart/soilarea": [
  "https://docs.geostandaarden.nl/bro/def-im-SGM-20230607/",
  "Column definitions: BRO Catalogus bodemkaart (SGM) v1.2"
 ],
 "bodemkaart/areaofpedologicalinterest": [
  "https://docs.geostandaarden.nl/bro/def-im-SGM-20230607/",
  "Column definitions: BRO Catalogus bodemkaart (SGM) v1.2"
 ]
}


geo_meta = geoparquet.geo_meta
arrow_cols = geoparquet.arrow_columns


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
    descs = dict(SHARED_COLS)
    descs.update(RESEARCHED_COLS.get(path, {}))
    descs.update(cfg.get("cols", {}))
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
                          f"{cfg['title']} (GeoParquet)", ["data"],
                          description=f"{cfg['title']} as cloud-native GeoParquet."),
        "pmtiles": stac.asset(pmtiles, "application/vnd.pmtiles",
                              f"{cfg['title']} (vector tiles)", ["visual"],
                              description=f"PMTiles vector tiles of {cfg['title']}"
                                          " for web-map display."),
        "thumbnail": stac.thumbnail_asset(
            description=f"WebP preview rendering of {cfg['title']}"
                        " for catalog browsing."),
    }
    # file:size / file:checksum for the files the repo itself publishes
    # (PTL-AST-003). Data files live on S3 and are not hashed here.
    assets["thumbnail"].update(stac.file_meta(os.path.join(cdir, "thumbnail.webp")))
    multi_style = len(style_files) > 1
    for sf in style_files:
        nm = os.path.splitext(os.path.basename(sf))[0]
        key = f"styles/{nm}"
        # PTL-VIZ-006 / spec PR #97: where a collection has more than one style,
        # exactly one names itself the default with a second asset role.
        roles = ["style", "default"] if (multi_style and nm == "default") else ["style"]
        assets[key] = stac.style_asset(f"./styles/{nm}.json",
                                       f"{cfg['title']} — {STYLE_TITLES.get(nm, nm)}",
                                       roles,
                                       description=f"MapLibre style '{nm}' for the"
                                                   " PMTiles visual asset.")
        assets[key].update(stac.file_meta(sf))
    # default first in manifest
    names = [os.path.splitext(os.path.basename(s))[0] for s in style_files]
    names = (["default"] if "default" in names else []) + [x for x in names if x != "default"]
    order = [f"styles/{x}" for x in names]

    atom = f"https://service.pdok.nl/tno/{cfg['slug']}/atom/index.xml"
    # PDOK moved some WMS endpoints (verified 2026-11-20); a config override
    # carries the working URL where the v1_0 pattern now 404s.
    wms = cfg.get("wms") or f"https://service.pdok.nl/tno/{cfg['slug']}/wms/v1_0?request=GetCapabilities&service=WMS"
    landing_url, landing_title = cfg["landing"]

    coll = {
        "type": "Collection", "id": layer, "stac_version": "1.1.0",
        "title": cfg["title"],
        "description": cfg["short"] + "\n\n🤖 AI/Agent users: see AGENTS.md for field descriptions, "
                       "query examples and usage tips.",
        "links": [
            stac.root_link(depth),
            stac.parent_link(parent),
            stac.link("via", atom, "application/atom+xml",
                      "PDOK Atom download (source GeoPackage)"),
            stac.link("via", wms, "application/xml", "PDOK WMS (GetCapabilities)"),
            # PORTO-CORE-053/-084: at least one via link is the source's own
            # HTML page; the service links above keep their real media types.
            stac.link("via", landing_url, "text/html", landing_title),
            *( [stac.link("via", *CATALOGUS[path][:1], "text/html", CATALOGUS[path][1])]
               if path in CATALOGUS else [] ),
            # web-map-links: the extension is declared below, and declaring it
            # without a web-map link is a validation error. Every sibling
            # collection in the catalog carries this link.
            stac.link("pmtiles", f"{paths.DATA_BASE}/vro/{path}/{layer}.pmtiles",
                      "application/vnd.pmtiles", **{"pmtiles:layers": [layer]}),
            stac.describedby_link(cfg["title"]),
            stac.agents_link(),
        ],
        "stac_extensions": [
            stac.PORTOLAN_SCHEMA,
            stac.FILE_SCHEMA,
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
        "providers": [dict(stac.VRO_PRODUCER), dict(stac.HOST_PROVIDER)],
    }
    out = os.path.join(cdir, "collection.json")
    # `updated` records when this collection last synced to the published prefix.
    # That is a fact about publishing, not about the source data, so the
    # generator carries forward whatever is already there rather than dropping
    # it. tools/catalog/conform.py sets it from the S3 listing.
    if os.path.exists(out):
        prev = json.load(open(out))
        if "updated" in prev:
            coll["updated"] = prev["updated"]
        # file:size/file:checksum of the published data files are measured
        # against S3 (see the v0.3 upgrade PR), not derivable from the
        # working directory, so they carry forward like 'updated' -- but only
        # while the asset still points at the same file.
        for key, a in coll["assets"].items():
            pa = (prev.get("assets") or {}).get(key)
            if isinstance(pa, dict) and pa.get("href") == a.get("href") \
                    and "file:size" not in a:
                for fk in ("file:size", "file:checksum"):
                    if fk in pa:
                        a[fk] = pa[fk]
    stac.write_json(out, coll)
    print(f"  {out}  ({gtype}, {n} feats, EPSG:{epsg}, {len(order)} styles)")


if __name__ == "__main__":
    for path, cfg in C.items():
        build(path, cfg)
    print("DONE")

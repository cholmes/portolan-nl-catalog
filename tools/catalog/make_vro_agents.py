#!/usr/bin/env python3
"""Generate the AGENTS.md agent guide for each VRO/BRO collection.

Formerly make_llms.py writing AGENTS.md; the spec settled on AGENTS.md
(rel:agents) as the one agent-guide surface, so the same content now lands
there.

Pairs hand-authored domain text with an auto-generated schema table, access snippets and
query examples derived from the collection.json. Run from catalog root.
"""
import json
import os

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from tools.lib import paths, docs

# Generators write into the published tree; paths.py owns where that is.
ROOT = str(paths.CATALOG)
DATA = paths.DATA_BASE

BRO_NOTE = (
    "## About the BRO\n\n"
    "This collection comes from the **Basisregistratie Ondergrond (BRO)** — the Dutch Key Registry "
    "of the Subsurface, a statutory base registry in force since 1 January 2018. Government bodies "
    "must register subsurface data in the BRO and may only use registered data for public tasks. "
    "Data is published openly via PDOK, usually within ~1 day of registration. The Ministry of "
    "Housing and Spatial Planning (**VRO**) is the system-responsible provider; the data here is "
    "produced by **TNO – Geologische Dienst Nederland** (subsurface objects) or **Wageningen "
    "Environmental Research** (the soil and geomorphological maps).\n\n"
    "Two BRO concepts appear in almost every dataset:\n"
    "- **`bro_id`** — the unique registration identifier of each object (e.g. `GMW000000012345`).\n"
    "- **`quality_regime`** — `IMBRO` (full quality assurance) or `IMBRO/A` (transitional data "
    "delivered under a lighter regime; treat with slightly more caution).\n"
)

GLOSSARY = (
    "## Dutch ↔ English glossary\n\n"
    "Column names in this collection are the English BRO field names. Common Dutch equivalents:\n"
    "`bronhouder` = delivery_accountable_party (data owner), `kwaliteitsregime` = quality_regime, "
    "`bodemklasse` = soil class, `hoofdklasse` = main soil class, `genese` = genesis (landform "
    "origin), `reliëf` = relief, `boring/booronderzoek` = borehole, `sondering` = cone penetration "
    "test, `grondwater` = groundwater, `mijnbouw` = mining, `bodemverontreiniging` = soil "
    "contamination.\n"
)

# per-collection authored content
A = {
 "wandonderzoek": dict(layer="wandonderzoek", what="""
The soil-trench / soil-profile-pit investigation (Dutch *wandonderzoek*, BRO object **SFR** —
*Soil Face Research*). A soil scientist exposes a vertical soil face (a pit or trench, typically
down to ~6 m) and describes the profile: horizons, texture, colour, organic matter and more. Each
record here is one such investigation **location** (2,806 points), with summary attributes; it is a
key field input behind the national Soil Map (Bodemkaart).
""", uses="""
Used in soil science, agriculture, nature-area soil build-up studies, hydrology and land
evaluation. Together with soil boreholes (BHR-P) these are the ground-truth observations the
Bodemkaart is built from.
""", caveats=[
  "This layer is the **investigation location + summary**. The full layered profile description, "
  "samples and lab analyses live in dozens of related tables inside the source GeoPackage and are "
  "not included in this point collection.",
  "`discipline` is always `bodemkunde` (soil science) for this object.",
  "`research_report_date` and `fieldwork_date` are free-text date strings, not typed dates.",
 ], related="Soil boreholes (BHR-P), the national Soil Map (bodemkaart/soilarea)."),

 "mijnbouwconstructie": dict(layer="mijnbouwconstructie", what="""
Mining-law subsurface constructions (Dutch *mijnbouwconstructie*, BRO object **EPC**). These are
works regulated under the Mining Act in the deep subsurface: deep boreholes (boorgaten), mine
systems and salt caverns used for oil and gas, geothermal energy, and underground storage. 4,975
constructions are included. This object was added to the BRO/PDOK in October 2025.
""", uses="""
Used in energy, geothermal and storage planning, subsurface spatial planning, and risk/permitting
work. The point marks the surface location of the construction.
""", caveats=[
  "`legal_status` is frequently `onbekend` (unknown) or `buitenGebruikMijnbouw` (decommissioned).",
  "Some mining data younger than five years can be legally shielded and may therefore be absent.",
  "Detailed sub-objects (boreholes, salt caverns, mine maps) exist in the source GeoPackage's "
  "related tables; this collection is the construction location + summary.",
 ], related="Geological boreholes (BHR-G), GeoTOP / DGM subsurface models."),

 "bodemverontreiniging_besluit": dict(layer="bodemverontreiniging_besluit", what="""
Formal government decisions on soil contamination (Dutch *overheidsbesluit bodemverontreiniging*,
BRO object **SLD**). Each polygon is an area covered by an authority decision about a contaminated
site — its assessment, remediation or aftercare status — under the Soil Protection Act (Wbb) and,
since 2024, the Environment and Planning Act (Omgevingswet). 121 decision areas are included.
""", uses="""
Used in conveyancing, spatial planning, permitting and environmental due diligence: it shows where
a formal contamination decision applies.
""", caveats=[
  "This is a young, sparse BRO object — the national coverage is still growing.",
  "The decision/aftercare/contamination detail (nature of contamination, measures) lives in related "
  "tables in the source GeoPackage; this collection holds the decision-area geometry + summary.",
 ], related="Environmental soil investigation (SAD), soil map (bodemkaart)."),

 "grondwatergebruiksysteem": dict(layer="grondwatergebruiksysteem", what="""
Groundwater use systems (Dutch *grondwatergebruiksysteem*, BRO object **GUF**). A use system is a
construction that uses groundwater — either directly (extraction or infiltration wells for drinking
water, industry or agriculture) or indirectly through **ground-source energy** (open and closed
geothermal / ATES "bodemenergie" systems). 50,637 systems are included.
""", uses="""
Central to the energy transition (heat/cold storage), drinking-water and industrial water supply,
and groundwater management. One of the larger, denser BRO point datasets.
""", caveats=[
  "Production/abstraction volumes are **not** in this collection — they are in the Groundwater "
  "Production Dossier (GPD), which has no own geometry and is published separately as a table.",
  "Detailed installations and facilities live in related tables in the source GeoPackage.",
 ], related="Groundwater production dossier (GPD, tabular), groundwater monitoring wells (GMW)."),

 "bodemkaart/soilarea": dict(layer="soilarea", what="""
The **Soil Map of the Netherlands 1:50,000** (Dutch *Bodemkaart van Nederland*, BRO object
**SGM**) — the authoritative national soil map produced by Wageningen Environmental Research. Each
of the 48,025 polygons is a mapped soil area. This collection is **enriched**: the primary soil
unit (`soilunit_code`, the BRO *bodemcode*) and its main soil class (`hoofdklasse`, e.g.
*Podzolgronden*, *Zeekleigronden*, *Veengronden*) and full classification (`bodemklasse`) have
been joined from the soil-unit tables so you can map and analyse soil type directly.
""", uses="""
One of the most widely used environmental datasets in the Netherlands: agriculture and precision
farming, hydrology and water management, nature development, carbon/peat studies, and spatial
planning.
""", caveats=[
  "A soil area can carry **several** soil units; this collection keeps the **primary** unit "
  "(sequence number 0). Secondary units are in the source GeoPackage.",
  "`soilslope` is `Niet opgenomen` (not recorded) for almost all polygons.",
  "Built-up areas and large water bodies are not mapped — see the companion "
  "*areaofpedologicalinterest* collection for the mapped extent.",
  "Full legend per soil code: https://legenda-bodemkaart.bodemdata.nl/ (also in `legenda_url`).",
 ], related="Area of pedological interest, soil boreholes (BHR-P), soil trenches (SFR).",
   crs=28992),

 "bodemkaart/areaofpedologicalinterest": dict(layer="areaofpedologicalinterest", what="""
The area of pedological interest of the national Soil Map 1:50,000 (BRO object **SGM**) — 6,192
polygons delimiting where soil mapping applies. Built-up areas and large open water are excluded.
""", uses="Use as a mask/extent for the soil map; shows where soil data exists.",
   caveats=["This is a coverage/extent layer, not the soil map itself — see the *soilarea* collection."],
   related="soilarea (the soil map).", crs=28992),

 "geomorfologische_kaart/geomorphological_area": dict(layer="geomorphological_area", what="""
The **Geomorphological Map of the Netherlands 1:50,000** (Dutch *Geomorfologische kaart*, BRO
object **GMM**), produced by Wageningen Environmental Research. Each of the 80,148 polygons is a
landform, classified by **genesis** (how it formed — eolian, fluvial, marine, glacial,
periglacial, anthropogenic, …), **relief** form, and **landform subgroup**. The classification is
denormalised directly into the feature, so it is ready to map and analyse.
""", uses="""
Used in landscape ecology, archaeology (landform predicts site potential), nature development,
water management and spatial planning.
""", caveats=[
  "`genese_code` is numeric: 1=Glaciaal, 2=Periglaciaal, 3=Denudatief, 4=Fluviatiel, 5=Eolisch, "
  "6=Lacustrien, 7=Marien, 8=Organogeen, 9=Antropogeen, 0=Tectonisch (Eolisch and Fluviatiel "
  "dominate).",
  "Landform subgroup legend: https://legendageomorfologie.wur.nl/ (also in `landform_subgroup_url`).",
  "`validfrom`/`validto` fields are integer YYYYMMDD codes.",
 ], related="Area of geomorphological interest, soil map (bodemkaart), AHN elevation.",
   crs=28992),

 "geomorfologische_kaart/area_of_geomorphological_interest": dict(
   layer="area_of_geomorphological_interest", what="""
The area of geomorphological interest of the national Geomorphological Map 1:50,000 (BRO object
**GMM**) — 40,840 polygons delimiting where the geomorphological mapping applies.
""", uses="Use as a mask/extent for the geomorphological map.",
   caveats=["Coverage/extent layer, not the map itself — see *geomorphological_area*."],
   related="geomorphological_area (the map).", crs=28992),

 "geomorfologische_kaart/geomorphological_area_collection": dict(
   layer="geomorphological_area_collection", what="""
Map-area collections of the national Geomorphological Map 1:50,000 (BRO object **GMM**) — 70
polygons that group the map by survey / publication unit.
""", uses="Use to understand provenance/version groupings of the geomorphological map.",
   caveats=["A provenance/grouping layer, not the landform map — see *geomorphological_area*."],
   related="geomorphological_area (the map).", crs=28992),
}


def schema_table(coll):
    rows = ["| Column | Type | Meaning |", "|--------|------|---------|"]
    for c in coll["table:columns"]:
        rows.append(f"| `{c['name']}` | {c['type']} | {c.get('description','')} |")
    return "\n".join(rows)


def styles_section(coll, path):
    out = ["## Visualization styles\n",
           "Mapbox GL v8 style files (use with MapLibre GL JS, OpenLayers via ol-mapbox-style, or "
           "any Mapbox GL v8 renderer) live alongside the PMTiles:\n"]
    base = f"{docs.collection_url(f'vro/{path}')}/styles"
    for key, title, fname in docs.style_entries(coll):
        out.append(f"- **`{key}.json`** — {title} ({base}/{fname})")
    return "\n".join(out)


def build(path, meta):
    cdir = os.path.join(ROOT, "vro", path)
    coll = json.load(open(os.path.join(cdir, "collection.json")))
    layer = meta["layer"]
    url = f"{DATA}/vro/{path}/{layer}.parquet"
    crs = meta.get("crs", 4258)
    geomcol = coll["table:primary_geometry"]
    n = coll["table:row_count"]
    title = coll["title"]
    # group/intersect helpers based on geometry
    cat = next((c["name"] for c in (("hoofdklasse",), ("genese_code",), ("survey_purpose",),
               ("legal_status",), ("quality_regime",)) for c in [c[0]]
               if any(col["name"] == c[0] for col in coll["table:columns"])), None)
    grp = ""
    if cat:
        grp = (f"\n### Distribution by {cat}\n\n```sql\nSELECT {cat}, COUNT(*) AS n\n"
               f"FROM read_parquet('{url}')\nGROUP BY 1 ORDER BY n DESC;\n```\n")
    txt = f"""# {title}

## What this is
{meta['what'].strip()}

**Features:** {n:,}  |  **CRS:** EPSG:{crs}  |  **License:** CC0 1.0 (public domain)
**Source:** PDOK / BRO (provider VRO).  **Formats:** GeoParquet · PMTiles · GeoPackage (PDOK Atom).

## Why it matters
{meta['uses'].strip()}

{BRO_NOTE}
## How to access

DuckDB (analytics):

```python
import duckdb
con = duckdb.connect(); con.execute("INSTALL spatial; LOAD spatial;")
df = con.execute(\"\"\"
    SELECT * FROM read_parquet('{url}') LIMIT 5
\"\"\").df()
```

GeoPandas:

```python
import geopandas as gpd
gdf = gpd.read_parquet('{url}')   # CRS EPSG:{crs}
```

## Schema — field meanings

{schema_table(coll)}

Geometry is stored in `{geomcol}` (WKB, EPSG:{crs}); `{geomcol}_bbox` is a per-feature bounding-box
struct enabling fast spatial pre-filtering.
{grp}
### Spatial query (point-in-area / nearby)

```sql
INSTALL spatial; LOAD spatial;
SELECT bro_id{', ' + cat if cat else ''}
FROM read_parquet('{url}')
WHERE ST_DWithin(
    ST_GeomFromWKB({geomcol}),
    ST_Point(5.12, 52.09),            -- lon, lat (transform if data is EPSG:28992)
    0.05);
```

## Caveats
""" + "\n".join(f"- {c}" for c in meta["caveats"]) + f"""

## Related collections
{meta['related']}

{GLOSSARY}
{styles_section(coll, path)}

## Also available as
- **PMTiles** (vector tiles): [`{layer}.pmtiles`]({DATA}/vro/{path}/{layer}.pmtiles)
- **GeoPackage** (full relational model): PDOK Atom download for BRO object — see the `via` links in
  `collection.json`.

---
*Part of the Portolan NL catalog · CC0 1.0 · provider VRO (Ministerie van Volkshuisvesting en
Ruimtelijke Ordening).*
"""
    with open(os.path.join(cdir, "AGENTS.md"), "w") as f:
        f.write(txt)
    print("  wrote", os.path.join("vro", path, "AGENTS.md"), f"({len(txt)} bytes)")


if __name__ == "__main__":
    for path, meta in A.items():
        build(path, meta)
    print("DONE")

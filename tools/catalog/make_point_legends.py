#!/usr/bin/env python3
"""Add more thematic styles to the point/polygon VRO collections and make point styles
show a legend in portolan-browser.

The browser's extractLegend() only reads the first `fill` layer's `fill-color`. Point
(`circle`) styles therefore get no legend. Workaround: each point thematic style gets an
inert `fill` layer (fill-opacity 0, same `match`) ahead of the visible `circle` layer —
fill layers render nothing on point geometry but the legend extractor reads them.

Run from catalog root."""
import json
import os

import duckdb

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from tools.lib import paths

# Generators write into the published tree; paths.py owns where that is.
ROOT = str(paths.CATALOG)

def data_dir(cdir):
    """Catalog directory -> the directory holding its data files.

    The repo holds no parquet; it lives in the working directory. Generators
    still write metadata into cdir, they just read the data from here.
    """
    return str(paths.DATA_ROOT / os.path.relpath(cdir, ROOT))

QUAL = ["#1B9E77", "#D95F02", "#7570B3", "#E7298A", "#66A61E", "#E6AB02", "#A6761D",
        "#1F78B4", "#B15928", "#6A3D9A", "#666666"]


def match_expr(field, mapping, other):
    e = ["match", ["get", field]]
    for k, v in mapping.items():
        e += [k, v]
    e.append(other)
    return e


def top_map(parquet, field, n=8):
    vals = [r[0] for r in duckdb.connect().execute(
        f"SELECT {field} FROM read_parquet('{parquet}') WHERE {field} IS NOT NULL "
        f"GROUP BY 1 ORDER BY COUNT(*) DESC LIMIT {n}").fetchall()]
    return {v: QUAL[i % len(QUAL)] for i, v in enumerate(vals)}


def distinct(parquet, field):
    return duckdb.connect().execute(
        f"SELECT COUNT(DISTINCT {field}) FROM read_parquet('{parquet}')").fetchone()[0]


def write(cdir, layer, fname, name, expr, kind):
    src = {layer: {"type": "vector", "url": f"pmtiles://../{layer}.pmtiles"}}
    if kind == "point":
        layers = [
            # inert fill layer purely so portolan-browser extractLegend() finds the match
            {"id": f"{layer}-legend", "type": "fill", "source": layer, "source-layer": layer,
             "paint": {"fill-color": expr, "fill-opacity": 0}},
            {"id": f"{layer}-circle", "type": "circle", "source": layer, "source-layer": layer,
             "paint": {"circle-radius": ["interpolate", ["linear"], ["zoom"], 4, 1.5, 10, 3.5, 14, 6.5],
                       "circle-color": expr, "circle-stroke-color": "#ffffff",
                       "circle-stroke-width": 0.4, "circle-opacity": 0.85}},
        ]
    else:  # polygon
        layers = [
            {"id": f"{layer}-fill", "type": "fill", "source": layer, "source-layer": layer,
             "paint": {"fill-color": expr, "fill-opacity": 0.8}},
            {"id": f"{layer}-outline", "type": "line", "source": layer, "source-layer": layer,
             "paint": {"line-color": "#777777", "line-width": 0.3}},
        ]
    style = {"version": 8, "name": name, "sources": src, "layers": layers}
    os.makedirs(os.path.join(cdir, "styles"), exist_ok=True)
    json.dump(style, open(os.path.join(cdir, "styles", fname), "w"), indent=2, ensure_ascii=False)
    print("  ", os.path.join(os.path.basename(cdir), "styles", fname))


QUALREG = {"IMBRO": "#1B9E77", "IMBRO/A": "#D95F02"}

# (path, kind, layer, [ (slug, title, field, mapping-or-None=top) ... ])
JOBS = [
    ("wandonderzoek", "point", "wandonderzoek", [
        ("by-survey-purpose", "wandonderzoek — by survey purpose", "survey_purpose", None),
        ("by-litter", "wandonderzoek — by litter layer investigated", "litter_layer_investigated",
         {"nee": "#90A4AE", "ja": "#43A047"}),
    ]),
    ("mijnbouwconstructie", "point", "mijnbouwconstructie", [
        ("by-legal-status", "mijnbouwconstructie — by legal status", "legal_status",
         {"onbekend": "#9E9E9E", "buitenGebruikMijnbouw": "#8E24AA", "inGebruikMijnbouw": "#43A047"}),
        ("by-delivery-context", "mijnbouwconstructie — by delivery context", "delivery_context", None),
    ]),
    ("grondwatergebruiksysteem", "point", "grondwatergebruiksysteem", [
        ("by-quality-regime", "grondwatergebruiksysteem — by quality regime", "quality_regime", QUALREG),
        ("by-delivery-context", "grondwatergebruiksysteem — by delivery context", "delivery_context", None),
    ]),
    ("bodemverontreiniging_besluit", "polygon", "bodemverontreiniging_besluit", [
        ("by-quality-regime", "bodemverontreiniging_besluit — by quality regime", "quality_regime", QUALREG),
        ("by-bronhouder", "bodemverontreiniging_besluit — by data owner (bronhouder)",
         "delivery_accountable_party", None),
    ]),
]


def go():
    for path, kind, layer, themes in JOBS:
        cdir = os.path.join(ROOT, "vro", path)
        pq = os.path.join(data_dir(cdir), f"{layer}.parquet")
        for slug, title, field, mapping in themes:
            if distinct(pq, field) < 2:
                print(f"   skip {path}/{slug} ({field} is uniform)")
                continue
            m = mapping if mapping is not None else top_map(pq, field)
            other = "#999999" if field == "delivery_accountable_party" else "#BBBBBB"
            write(cdir, layer, f"{slug}.json", title, match_expr(field, m, other), kind)
    print("DONE")


if __name__ == "__main__":
    go()

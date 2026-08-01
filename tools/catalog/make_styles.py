#!/usr/bin/env python3
"""Author MapLibre styles for the three collections that publish tiles without any.

cbs/gebiedsindelingen, cbs/wijken_buurten and rijkswaterstaat/nwb_wegen shipped
PMTiles with no style asset, which Portolan flags as PTL-VIZ-002 and which left
the browser with nothing to draw.

Every class break and category here comes from the real data, measured with
DuckDB over the published GeoParquet, not from round numbers. The graduated
ramps use quantiles so each colour carries roughly the same share of features;
percentile-free ramps on Dutch population density put 90% of the country in one
bucket. Field names are checked against the PMTiles vector_layers metadata,
because a style may only reference fields the tiles actually carry.

Palettes are ColorBrewer sequential and qualitative sets, which are
colourblind-safe at these class counts.

Usage:
  python3 tools/catalog/make_styles.py            # dry run
  python3 tools/catalog/make_styles.py --confirm
"""
from __future__ import annotations
import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.lib import paths, stac, styles  # noqa: E402

CATALOG = paths.CATALOG

# ---------------------------------------------------------------------------
# Palettes (ColorBrewer)
# ---------------------------------------------------------------------------
YLORRD = ["#ffffb2", "#fed976", "#feb24c", "#fd8d3c", "#f03b20", "#bd0026"]
BLUES = ["#eff3ff", "#c6dbef", "#9ecae1", "#6baed6", "#3182bd", "#08519c"]
PURPLES = ["#f2f0f7", "#dadaeb", "#bcbddc", "#9e9ac8", "#756bb1", "#54278f"]
GREENS = ["#edf8e9", "#c7e9c0", "#a1d99b", "#74c476", "#31a354", "#006d2c"]
SET2 = ["#66c2a5", "#fc8d62", "#8da0cb", "#e78ac3", "#a6d854", "#ffd92f",
        "#e5c494", "#b3b3b3"]

WATER = "#c9dced"
LAND_OUTLINE = "#7f8c8d"


def graduated(field: str, breaks: list[float], colors: list[str]) -> list:
    """A `step` expression: first colour below breaks[0], then one per break."""
    expr: list = ["step", ["to-number", ["get", field], -1], colors[0]]
    for b, c in zip(breaks, colors[1:]):
        expr += [b, c]
    return expr


def fill(layer: str, color, opacity=0.85, outline="#ffffff", width=0.3) -> list[dict]:
    return [
        {"id": f"{layer}-fill", "type": "fill", "source": layer, "source-layer": layer,
         "paint": {"fill-color": color, "fill-opacity": opacity}},
        {"id": f"{layer}-outline", "type": "line", "source": layer, "source-layer": layer,
         "paint": {"line-color": outline, "line-width": width}},
    ]


def line(layer: str, color, width, **paint) -> list[dict]:
    return [{"id": f"{layer}-line", "type": "line", "source": layer, "source-layer": layer,
             "layout": {"line-cap": "round", "line-join": "round"},
             "paint": {"line-color": color, "line-width": width, **paint}}]


def style(name: str, layer: str, layers: list[dict]) -> dict:
    return {"version": 8, "name": name,
            "sources": styles.pmtiles_source(layer, f"pmtiles://../{{PM}}.pmtiles"),
            "layers": layers}


# Line width that stays legible from national overview to street level.
def zoom_width(*stops) -> list:
    expr: list = ["interpolate", ["linear"], ["zoom"]]
    for z, w in stops:
        expr += [z, w]
    return expr


# ---------------------------------------------------------------------------
# cbs/gebiedsindelingen -- 342 municipalities, tiles carry only names and codes
# ---------------------------------------------------------------------------
GEM = "gemeenten"
# statcode is "GM0014": the numeric tail modulo 8 gives neighbouring
# municipalities different colours without any attribute to classify on.
MOSAIC = ["match", ["%", ["to-number", ["slice", ["get", "statcode"], 2]], 8]]
for _i, _c in enumerate(SET2):
    MOSAIC += [_i, _c]
MOSAIC.append(SET2[-1])

GEBIEDSINDELINGEN = {
    "default": ("Municipalities", fill(GEM, "#dfe6e9", 0.75, LAND_OUTLINE, 0.5)),
    "mosaic": ("Municipalities — distinguishable neighbours", fill(GEM, MOSAIC, 0.75, "#ffffff", 0.5)),
    "boundaries": ("Municipal boundaries only", [
        {"id": f"{GEM}-fill", "type": "fill", "source": GEM, "source-layer": GEM,
         "paint": {"fill-color": "#000000", "fill-opacity": 0}},
        {"id": f"{GEM}-outline", "type": "line", "source": GEM, "source-layer": GEM,
         "paint": {"line-color": "#2d3436", "line-width": zoom_width((5, 0.4), (9, 1.2), (13, 2.0))}},
    ]),
    "labeled": ("Municipalities with names", fill(GEM, "#f5f6fa", 0.7, LAND_OUTLINE, 0.5) + [
        {"id": f"{GEM}-label", "type": "symbol", "source": GEM, "source-layer": GEM,
         "minzoom": 7,
         "layout": {"text-field": ["get", "statnaam"], "text-size": zoom_width((7, 9), (11, 14)),
                    "text-allow-overlap": False},
         "paint": {"text-color": "#2d3436", "text-halo-color": "#ffffff", "text-halo-width": 1.2}},
    ]),
}

# ---------------------------------------------------------------------------
# cbs/wijken_buurten -- 14,823 neighbourhoods with CBS demographics
# ---------------------------------------------------------------------------
BUU = "buurten"
# CBS uses negative sentinels for suppressed values; graduated() coerces a
# missing field to -1 so those land in the lowest class rather than breaking
# the expression. The `water` neighbourhoods are drawn as water, not data.
WATER_FILTER = ["!=", ["get", "water"], "JA"]


def demographic(field: str, breaks: list[float], palette: list[str]) -> list[dict]:
    return [
        {"id": f"{BUU}-water", "type": "fill", "source": BUU, "source-layer": BUU,
         "filter": ["==", ["get", "water"], "JA"],
         "paint": {"fill-color": WATER, "fill-opacity": 0.6}},
        {"id": f"{BUU}-fill", "type": "fill", "source": BUU, "source-layer": BUU,
         "filter": WATER_FILTER,
         "paint": {"fill-color": graduated(field, breaks, palette), "fill-opacity": 0.85}},
        {"id": f"{BUU}-outline", "type": "line", "source": BUU, "source-layer": BUU,
         "paint": {"line-color": "#ffffff", "line-width": 0.2, "line-opacity": 0.6}},
    ]


WIJKEN_BUURTEN = {
    # Breaks are measured deciles, see the module docstring.
    "default": ("Neighbourhoods", [
        {"id": f"{BUU}-water", "type": "fill", "source": BUU, "source-layer": BUU,
         "filter": ["==", ["get", "water"], "JA"],
         "paint": {"fill-color": WATER, "fill-opacity": 0.6}},
        {"id": f"{BUU}-fill", "type": "fill", "source": BUU, "source-layer": BUU,
         "filter": WATER_FILTER,
         "paint": {"fill-color": "#dfe6e9", "fill-opacity": 0.85}},
        {"id": f"{BUU}-outline", "type": "line", "source": BUU, "source-layer": BUU,
         "paint": {"line-color": LAND_OUTLINE, "line-width": 0.25}},
    ]),
    "by-population-density": (
        "Population density (inhabitants per km²)",
        demographic("bevolkingsdichtheid_inwoners_per_km2",
                    [30, 130, 2100, 5200, 8100], YLORRD)),
    "by-urbanity": (
        "CBS urbanity class (1 very urban — 5 rural)",
        [{"id": f"{BUU}-fill", "type": "fill", "source": BUU, "source-layer": BUU,
          "paint": {"fill-color": ["match", ["get", "stedelijkheid_adressen_per_km2"],
                                   1, "#54278f", 2, "#756bb1", 3, "#9e9ac8",
                                   4, "#cbc9e2", 5, "#f2f0f7", "#d9d9d9"],
                    "fill-opacity": 0.85}},
         {"id": f"{BUU}-outline", "type": "line", "source": BUU, "source-layer": BUU,
          "paint": {"line-color": "#ffffff", "line-width": 0.2}}]),
    "by-age-65-plus": (
        "Share of residents aged 65 and over (%)",
        demographic("percentage_personen_65_jaar_en_ouder", [11, 17, 22, 27, 33], BLUES)),
    "by-household-size": (
        "Average household size",
        demographic("gemiddelde_huishoudsgrootte", [1.7, 2.0, 2.3, 2.5, 2.7], GREENS)),
    "by-single-person-households": (
        "Share of single-person households (%)",
        demographic("percentage_eenpersoonshuishoudens", [19, 24, 32, 43, 56], PURPLES)),
}

# ---------------------------------------------------------------------------
# rijkswaterstaat/nwb_wegen -- 1.63M road segments
# ---------------------------------------------------------------------------
NWB = "nwb_wegen"
# wegbehsrt, road authority: R national, P provincial, G municipal,
# W water board, T other. Counts: G 1,503,598 / P 68,785 / R 20,277 /
# W 19,182 / T 14,479.
AUTHORITY = ["match", ["get", "wegbehsrt"],
             "R", "#d73027", "P", "#fc8d59", "G", "#4575b4",
             "W", "#91bfdb", "T", "#999999", "#bbbbbb"]
# bst_code, segment type. RB carriageway, FP cycle path, VP footpath,
# ERF residential yard, PP/PAR parking, HR main carriageway.
ROAD_TYPE = ["match", ["get", "bst_code"],
             "RB", "#34495e", "HR", "#2c3e50", "NRB", "#7f8c8d",
             "FP", "#e67e22", "VP", "#27ae60", "ERF", "#95a5a6",
             "PP", "#8e44ad", "PAR", "#9b59b6", "#bdc3c7"]
ROUTE_CLASS = ["match", ["get", "routeltr"],
               "A", "#d73027", "N", "#fdae61", "E", "#4575b4",
               "S", "#7f8c8d", "#d9d9d9"]

NWB_WEGEN = {
    "default": ("Road network by authority",
                line(NWB, AUTHORITY, zoom_width((6, 0.3), (10, 0.8), (14, 2.0)), **{"line-opacity": 0.9})),
    "by-road-type": ("Carriageways, cycle paths and footpaths",
                     line(NWB, ROAD_TYPE, zoom_width((6, 0.3), (10, 0.9), (14, 2.4)))),
    "cycling-network": ("Cycle paths only", [
        {"id": f"{NWB}-context", "type": "line", "source": NWB, "source-layer": NWB,
         "filter": ["!=", ["get", "bst_code"], "FP"],
         "paint": {"line-color": "#e8e8e8",
                   "line-width": zoom_width((6, 0.2), (12, 0.8))}},
        {"id": f"{NWB}-cycle", "type": "line", "source": NWB, "source-layer": NWB,
         "filter": ["==", ["get", "bst_code"], "FP"],
         "layout": {"line-cap": "round", "line-join": "round"},
         "paint": {"line-color": "#e67e22",
                   "line-width": zoom_width((6, 0.4), (10, 1.2), (14, 3.0))}},
    ]),
    "by-route-class": ("Motorways, N-roads and Euroroutes", [
        {"id": f"{NWB}-other", "type": "line", "source": NWB, "source-layer": NWB,
         "filter": ["==", ["get", "routeltr"], ""],
         "paint": {"line-color": "#e0e0e0", "line-width": zoom_width((6, 0.2), (12, 0.6))}},
        {"id": f"{NWB}-routes", "type": "line", "source": NWB, "source-layer": NWB,
         "filter": ["!=", ["get", "routeltr"], ""],
         "layout": {"line-cap": "round", "line-join": "round"},
         "paint": {"line-color": ROUTE_CLASS,
                   "line-width": zoom_width((5, 0.6), (10, 1.8), (14, 4.0))}},
    ]),
    "by-direction": ("One-way and two-way segments",
                     line(NWB, ["match", ["get", "rijrichtng"],
                                "B", "#4575b4", "H", "#d73027", "O", "#fc8d59",
                                "T", "#7f8c8d", "#bbbbbb"],
                          zoom_width((6, 0.3), (10, 0.9), (14, 2.2)))),
}

COLLECTIONS = {
    "cbs/gebiedsindelingen": (GEM, "gebiedsindelingen", GEBIEDSINDELINGEN),
    "cbs/wijken_buurten": (BUU, "wijken_buurten", WIJKEN_BUURTEN),
    "rijkswaterstaat/nwb_wegen": (NWB, "nwb_wegen", NWB_WEGEN),
}


def build(rel: str, layer: str, pmtiles_stem: str, defs: dict) -> list[tuple[Path, dict]]:
    out = []
    for slug, (title, layer_defs) in defs.items():
        doc = style(title, layer, layer_defs)
        doc["sources"] = {layer: {"type": "vector",
                                  "url": f"pmtiles://../{pmtiles_stem}.pmtiles"}}
        out.append((CATALOG / rel / "styles" / f"{slug}.json", doc))
    return out


def register(rel: str, defs: dict) -> dict | None:
    """Add the style assets and the portolan:styles manifest to collection.json."""
    p = CATALOG / rel / "collection.json"
    doc = json.loads(p.read_text())
    assets = doc.setdefault("assets", {})
    order = []
    for slug, (title, _) in defs.items():
        key = f"styles/{slug}"
        order.append(key)
        roles = ["style", "default"] if slug == "default" else ["style"]
        assets[key] = stac.style_asset(f"./styles/{slug}.json", title, roles)
    doc["portolan:styles"] = order
    return doc


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--confirm", action="store_true")
    args = ap.parse_args(argv)

    n_styles = 0
    for rel, (layer, stem, defs) in COLLECTIONS.items():
        files = build(rel, layer, stem, defs)
        n_styles += len(files)
        if args.confirm:
            (CATALOG / rel / "styles").mkdir(parents=True, exist_ok=True)
            for path, doc in files:
                stac.write_json(path, doc)
            stac.write_json(CATALOG / rel / "collection.json", register(rel, defs))
        print(f"{rel}: {len(files)} styles ({', '.join(defs)})")

    verb = "wrote" if args.confirm else "would write"
    print(f"\n{verb} {n_styles} style file(s) across {len(COLLECTIONS)} collections")
    if not args.confirm:
        print("Re-run with --confirm to write.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

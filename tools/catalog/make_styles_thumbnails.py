#!/usr/bin/env python3
"""Generate Mapbox GL v8 styles + thumbnails for the VRO/BRO vector collections.

Default style follows PDOK-style cartography; alternates are data-driven (chosen
from the actual attribute distributions). Thumbnails are rendered from the
GeoParquet with a CartoDB Positron basemap so they match the default style.

Run from catalog root:  python3 vro/scripts/make_styles_thumbnails.py
"""
import json
import os
import warnings

import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import contextily as cx

warnings.filterwarnings("ignore")
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ---- curated palettes -------------------------------------------------------
SOIL = {  # hoofdklasse (main soil class) — Dutch bodemkaart-style colours
    "Podzolgronden": "#EFA9C6", "Zeekleigronden": "#6FB36F",
    "Kalkloze zandgronden": "#FCE89B", "Moerige gronden": "#CBAEDB",
    "Veengronden": "#8E63A8", "Dikke eerdgronden": "#8D6E63",
    "Rivierkleigronden": "#2E8B57", "Gedefinieerde associaties": "#CFCFCF",
    "Kalkhoudende zandgronden": "#F6D36B", "Oude rivierkleigronden": "#57A773",
    "Brikgronden": "#E08214", "Leemgronden": "#C2A079",
    "Niet-gerijpte minerale gronden": "#7FCDC1", "Keileemgronden": "#A98274",
    "Zeer oude fluviatiele afzettingen": "#9E9D24",
    "Zeer oude mariene afzettingen": "#C0CA33",
}
SOIL_OTHER = "#E0E0E0"
# texture grouping (simplified alternate)
SOIL_GROUP = {
    "zand (sand)": (["Podzolgronden", "Kalkloze zandgronden", "Kalkhoudende zandgronden",
                     "Brikgronden", "Leemgronden", "Keileemgronden"], "#FCE08A"),
    "klei (clay)": (["Zeekleigronden", "Rivierkleigronden", "Oude rivierkleigronden",
                     "Zeer oude mariene afzettingen", "Zeer oude fluviatiele afzettingen",
                     "Niet-gerijpte minerale gronden"], "#5CA75C"),
    "veen (peat)": (["Veengronden", "Moerige gronden"], "#8E63A8"),
}
SOIL_GROUP_OTHER = "#CFCFCF"

GENESE = {  # genese_code -> colour
    "5": "#F2E6A0", "4": "#4F9DD6", "2": "#C9A0DC", "9": "#E57373",
    "7": "#66C2A5", "1": "#A6CEE3", "8": "#8E6C3A", "3": "#BDB76B",
    "0": "#B0A0A0", "6": "#80B1D3",
}
GENESE_NAME = {"5": "Eolisch (wind)", "4": "Fluviatiel (river)", "2": "Periglaciaal",
               "9": "Antropogeen (human)", "7": "Marien (sea)", "1": "Glaciaal",
               "8": "Organogeen (peat)", "3": "Denudatief", "0": "Tectonisch",
               "6": "Lacustrien"}
GENESE_OTHER = "#DDDDDD"

QUAL = {"IMBRO": "#1B9E77", "IMBRO/A": "#D95F02"}  # quality_regime
QUAL_OTHER = "#999999"

# ---- mapbox-gl style builders ----------------------------------------------
def src(name):
    return {name: {"type": "vector", "url": f"pmtiles://../{name}.pmtiles"}}

def fill_layer(layer, color, opacity=0.75, outline="#555555"):
    return [
        {"id": f"{layer}-fill", "type": "fill", "source": layer, "source-layer": layer,
         "paint": {"fill-color": color, "fill-opacity": opacity}},
        {"id": f"{layer}-outline", "type": "line", "source": layer, "source-layer": layer,
         "paint": {"line-color": outline, "line-width": 0.3}},
    ]

def circle_layer(layer, color, radius=3.5):
    return [{"id": f"{layer}-circle", "type": "circle", "source": layer, "source-layer": layer,
             "paint": {"circle-radius": ["interpolate", ["linear"], ["zoom"], 4, 1.5, 10, radius, 14, radius + 3],
                       "circle-color": color, "circle-stroke-color": "#ffffff",
                       "circle-stroke-width": 0.4, "circle-opacity": 0.85}}]

def match_expr(field, mapping, other):
    expr = ["match", ["get", field]]
    for k, v in mapping.items():
        expr += [k, v]
    expr.append(other)
    return expr

def write_style(coll_dir, layer, fname, name, layers):
    style = {"version": 8, "name": name, "sources": src(layer), "layers": layers}
    d = os.path.join(coll_dir, "styles")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, fname), "w") as f:
        json.dump(style, f, indent=2)

# ---- thumbnail renderer -----------------------------------------------------
def thumb(coll_dir, parquet, kind, color_spec):
    """color_spec: ('single', hex) or ('cat', field, {val:hex}, other, legend_title)."""
    gdf = gpd.read_parquet(parquet)
    if gdf.crs is None:
        gdf.set_crs(4258, inplace=True)
    gdf = gdf.to_crs(3857)
    fig, ax = plt.subplots(figsize=(6, 6.6), dpi=100)
    legend_handles = None
    if color_spec[0] == "single":
        col = color_spec[1]
        if kind == "point":
            gdf.plot(ax=ax, color=col, markersize=4, alpha=0.8, edgecolor="white", linewidth=0.2)
        else:
            gdf.plot(ax=ax, color=col, alpha=0.75, edgecolor="#555555", linewidth=0.2)
    else:
        _, field, mapping, other, title = color_spec
        colors = gdf[field].map(lambda v: mapping.get(str(v) if v is not None else None, other)) if False \
            else gdf[field].astype("object").map(lambda v: mapping.get(v, mapping.get(str(v), other)))
        if kind == "point":
            gdf.plot(ax=ax, color=colors, markersize=4, alpha=0.85, edgecolor="white", linewidth=0.15)
        else:
            gdf.plot(ax=ax, color=colors, alpha=0.8, edgecolor="#666666", linewidth=0.12)
        items = list(mapping.items())[:10]
        legend_handles = [Patch(facecolor=c, edgecolor="#666", label=(GENESE_NAME.get(k, k))) for k, c in items]
    try:
        cx.add_basemap(ax, source=cx.providers.CartoDB.Positron, attribution=False)
    except Exception as e:
        print("  basemap skipped:", e)
    ax.set_axis_off()
    if legend_handles:
        ax.legend(handles=legend_handles, loc="lower left", fontsize=6, framealpha=0.9,
                  title=color_spec[4], title_fontsize=6)
    out = os.path.join(coll_dir, "thumbnail.png")
    plt.tight_layout(pad=0.2)
    plt.savefig(out, bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)
    print("  thumbnail ->", out)

# ---- per-collection definitions --------------------------------------------
def soil_match():
    return match_expr("hoofdklasse", SOIL, SOIL_OTHER)

def soil_group_map():
    m = {}
    for _, (vals, col) in SOIL_GROUP.items():
        for v in vals:
            m[v] = col
    return m

def go():
    # simple point/polygon collections: (dir, layer, kind, default_color, cat_field, cat_map, cat_title)
    simple = [
        ("vro/wandonderzoek", "wandonderzoek", "point", "#8D6E63",
         "survey_purpose", None, "Survey purpose"),
        ("vro/mijnbouwconstructie", "mijnbouwconstructie", "point", "#455A64",
         "legal_status", {"onbekend": "#9E9E9E", "buitenGebruikMijnbouw": "#8E24AA",
                          "inGebruikMijnbouw": "#43A047"}, "Legal status"),
        ("vro/bodemverontreiniging_besluit", "bodemverontreiniging_besluit", "polygon", "#E57373",
         "quality_regime", QUAL, "Quality regime"),
        ("vro/grondwatergebruiksysteem", "grondwatergebruiksysteem", "point", "#1E88E5",
         "quality_regime", QUAL, "Quality regime"),
    ]
    for cdir, layer, kind, dcol, field, cmap, ctitle in simple:
        full = os.path.join(ROOT, cdir)
        pq = os.path.join(full, f"{layer}.parquet")
        # default
        dl = circle_layer(layer, dcol) if kind == "point" else fill_layer(layer, dcol)
        write_style(full, layer, "default.json", f"{layer} — default", dl)
        # data-driven alternate
        if cmap is None:
            # build a small qualitative map from data
            import duckdb
            vals = [r[0] for r in duckdb.connect().execute(
                f"SELECT {field} FROM read_parquet('{pq}') WHERE {field} IS NOT NULL GROUP BY 1 ORDER BY COUNT(*) DESC LIMIT 7").fetchall()]
            pal = ["#1B9E77", "#D95F02", "#7570B3", "#E7298A", "#66A61E", "#E6AB02", "#A6761D"]
            cmap = {v: pal[i % len(pal)] for i, v in enumerate(vals)}
        al = (circle_layer(layer, match_expr(field, cmap, "#BBBBBB")) if kind == "point"
              else fill_layer(layer, match_expr(field, cmap, "#BBBBBB")))
        slug = "by-" + field.replace("_", "-")
        write_style(full, layer, f"{slug}.json", f"{layer} — by {ctitle.lower()}", al)
        thumb(full, pq, kind, ("single", dcol))
        print(f"styles+thumb done: {cdir}")

    # bodemkaart/soilarea — default by soil class, alt by texture group
    sa = os.path.join(ROOT, "vro/bodemkaart/soilarea")
    write_style(sa, "soilarea", "default.json", "Bodemkaart — by soil class (hoofdklasse)",
                fill_layer("soilarea", soil_match(), opacity=0.8, outline="#777777"))
    write_style(sa, "soilarea", "by-texture.json", "Bodemkaart — sand / clay / peat",
                fill_layer("soilarea", match_expr("hoofdklasse", soil_group_map(), SOIL_GROUP_OTHER),
                           opacity=0.8, outline="#777777"))
    thumb(sa, os.path.join(sa, "soilarea.parquet"), "polygon",
          ("cat", "hoofdklasse", SOIL, SOIL_OTHER, "Main soil class"))
    print("styles+thumb done: bodemkaart/soilarea")

    # bodemkaart/areaofpedologicalinterest — coverage, single fill
    ap = os.path.join(ROOT, "vro/bodemkaart/areaofpedologicalinterest")
    write_style(ap, "areaofpedologicalinterest", "default.json", "Area of pedological interest",
                fill_layer("areaofpedologicalinterest", "#A1887F", opacity=0.4, outline="#6D4C41"))
    thumb(ap, os.path.join(ap, "areaofpedologicalinterest.parquet"), "polygon", ("single", "#A1887F"))
    print("styles+thumb done: bodemkaart/areaofpedologicalinterest")

    # geomorph/geomorphological_area — default by genese, alt by relief
    ga = os.path.join(ROOT, "vro/geomorfologische_kaart/geomorphological_area")
    write_style(ga, "geomorphological_area", "default.json", "Geomorfologie — by genesis (genese)",
                fill_layer("geomorphological_area", match_expr("genese_code", GENESE, GENESE_OTHER),
                           opacity=0.8, outline="#777777"))
    write_style(ga, "geomorphological_area", "by-relief.json", "Geomorfologie — by relief class",
                fill_layer("geomorphological_area",
                           ["interpolate", ["linear"], ["to-number", ["get", "relief_code"]],
                            1, "#FFFFCC", 6, "#A1DAB4", 12, "#41B6C4", 18, "#2C7FB8", 25, "#253494"],
                           opacity=0.8, outline="#777777"))
    thumb(ga, os.path.join(ga, "geomorphological_area.parquet"), "polygon",
          ("cat", "genese_code", GENESE, GENESE_OTHER, "Landform genesis"))
    print("styles+thumb done: geomorph/geomorphological_area")

    # geomorph coverage + collection — single fills
    for sub, col in [("area_of_geomorphological_interest", "#90A4AE"),
                     ("geomorphological_area_collection", "#B0BEC5")]:
        d = os.path.join(ROOT, "vro/geomorfologische_kaart", sub)
        write_style(d, sub, "default.json", sub, fill_layer(sub, col, opacity=0.4, outline="#546E7A"))
        thumb(d, os.path.join(d, f"{sub}.parquet"), "polygon", ("single", col))
        print("styles+thumb done: geomorph/" + sub)

if __name__ == "__main__":
    go()
    print("ALL DONE")

#!/usr/bin/env python3
"""Add extra thematic styles to thin/secondary layers + flagships, and render distinct
thumbnails for the secondary map collections (keeping the official PDOK preview on the
main collections). Run from catalog root."""
import json
import os
import warnings

import duckdb
import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import contextily as cx

warnings.filterwarnings("ignore")
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

QUAL = ["#1B9E77", "#D95F02", "#7570B3", "#E7298A", "#66A61E", "#E6AB02", "#A6761D", "#666666"]

# curated palettes
INTEREST = {"Water": "#4FC3F7", "Bebouwd gebied": "#BDBDBD", "Terp": "#8D6E63",
            "Sterk opgehoogd terrein": "#A1887F", "Moeras": "#66BB6A", "Dijk": "#FF8A65",
            "Sterk afgegraven terrein": "#D7CCC8", "Groeve": "#6D4C41"}
AOGI_TYPE = {"Water": "#4FC3F7", "Dijk": "#FF8A65"}
METHOD = {"Analoog met veldverkenning": "#1B9E77", "Digitaal met veldverificatie": "#D95F02",
          "Digitaal": "#7570B3", "Digitaal met veldverkenning": "#E7298A"}


def src(name):
    return {name: {"type": "vector", "url": f"pmtiles://../{name}.pmtiles"}}

def match_expr(field, mapping, other="#E0E0E0"):
    e = ["match", ["get", field]]
    for k, v in mapping.items():
        e += [k, v]
    e.append(other)
    return e

def fill_style(cdir, layer, fname, name, field, mapping, other="#E0E0E0", opacity=0.8):
    style = {"version": 8, "name": name, "sources": src(layer), "layers": [
        {"id": f"{layer}-fill", "type": "fill", "source": layer, "source-layer": layer,
         "paint": {"fill-color": match_expr(field, mapping, other), "fill-opacity": opacity}},
        {"id": f"{layer}-outline", "type": "line", "source": layer, "source-layer": layer,
         "paint": {"line-color": "#777777", "line-width": 0.3}},
    ]}
    os.makedirs(os.path.join(cdir, "styles"), exist_ok=True)
    json.dump(style, open(os.path.join(cdir, "styles", fname), "w"), indent=2, ensure_ascii=False)
    print("  style", os.path.join(os.path.basename(cdir), "styles", fname))

def top_map(parquet, field, palette, n=10):
    vals = [r[0] for r in duckdb.connect().execute(
        f"SELECT {field} FROM read_parquet('{parquet}') WHERE {field} IS NOT NULL "
        f"GROUP BY 1 ORDER BY COUNT(*) DESC LIMIT {n}").fetchall()]
    return {v: palette[i % len(palette)] for i, v in enumerate(vals)}

def thumb(cdir, parquet, field, mapping, other, title):
    gdf = gpd.read_parquet(parquet)
    if gdf.crs is None:
        gdf.set_crs(28992, inplace=True)
    gdf = gdf.to_crs(3857)
    fig, ax = plt.subplots(figsize=(6, 6.6), dpi=100)
    colors = gdf[field].astype("object").map(lambda v: mapping.get(v, other))
    gdf.plot(ax=ax, color=colors, alpha=0.85, edgecolor="#666666", linewidth=0.1)
    try:
        cx.add_basemap(ax, source=cx.providers.CartoDB.Positron, attribution=False)
    except Exception as e:
        print("  basemap skipped:", e)
    ax.set_axis_off()
    ax.legend(handles=[Patch(facecolor=c, edgecolor="#666", label=k) for k, c in list(mapping.items())[:8]],
              loc="lower left", fontsize=6, framealpha=0.9, title=title, title_fontsize=6)
    plt.tight_layout(pad=0.2)
    out = os.path.join(cdir, "thumbnail.png")
    plt.savefig(out, bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)
    print("  thumbnail", out)


def go():
    B = os.path.join(ROOT, "vro")
    # --- areaofpedologicalinterest: +by-interest, +by-collection ; distinct thumbnail
    ap = os.path.join(B, "bodemkaart/areaofpedologicalinterest")
    appq = os.path.join(ap, "areaofpedologicalinterest.parquet")
    fill_style(ap, "areaofpedologicalinterest", "by-interest.json",
               "Area of pedological interest — by type", "pedologicalinterest", INTEREST, opacity=0.7)
    fill_style(ap, "areaofpedologicalinterest", "by-collection.json",
               "Area of pedological interest — by survey campaign", "maparea_collection",
               top_map(appq, "maparea_collection", QUAL), opacity=0.7)
    thumb(ap, appq, "pedologicalinterest", INTEREST, "#E0E0E0", "Area of pedological interest")

    # --- area_of_geomorphological_interest: +by-type ; distinct thumbnail
    ag = os.path.join(B, "geomorfologische_kaart/area_of_geomorphological_interest")
    agpq = os.path.join(ag, "area_of_geomorphological_interest.parquet")
    fill_style(ag, "area_of_geomorphological_interest", "by-type.json",
               "Area of geomorphological interest — by type", "type", AOGI_TYPE, opacity=0.7)
    thumb(ag, agpq, "type", AOGI_TYPE, "#E0E0E0", "Area of geomorphological interest")

    # --- geomorphological_area_collection: +by-method ; distinct thumbnail
    gc = os.path.join(B, "geomorfologische_kaart/geomorphological_area_collection")
    gcpq = os.path.join(gc, "geomorphological_area_collection.parquet")
    fill_style(gc, "geomorphological_area_collection", "by-method.json",
               "Map area collections — by inventory method", "inventorymethod", METHOD, "#999999", opacity=0.7)
    thumb(gc, gcpq, "inventorymethod", METHOD, "#999999", "Inventory method")

    # --- flagship extras: soilarea by-collection, geomorph by-landform (top codes) ---
    sa = os.path.join(B, "bodemkaart/soilarea")
    fill_style(sa, "soilarea", "by-collection.json", "Bodemkaart — by survey campaign",
               "maparea_collection", top_map(os.path.join(sa, "soilarea.parquet"), "maparea_collection", QUAL),
               opacity=0.8)
    ga = os.path.join(B, "geomorfologische_kaart/geomorphological_area")
    fill_style(ga, "geomorphological_area", "by-landform.json", "Geomorfologie — by landform subgroup",
               "landform_subgroup_code",
               top_map(os.path.join(ga, "geomorphological_area.parquet"), "landform_subgroup_code", QUAL, 12),
               opacity=0.8)
    print("DONE")


if __name__ == "__main__":
    go()

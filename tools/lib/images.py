"""Thumbnail rendering, ending in WebP.

The renderers used to savefig a PNG. Phase 1 made every thumbnail in catalog/
WebP under 50 KB, enforced by tests/test_thumbnails.py, so rendering now ends
in the same encoder the conversion used -- otherwise the next regeneration
reintroduces PNGs and the test fails. This is the one deliberate behaviour
change in the phase 2 refactor.

What is shared between the two renderers is the scaffolding, not the drawing:
load the parquet and reproject to Web Mercator, drop a CartoDB Positron
basemap behind it, strip the axes, and write the result. How the features are
coloured differs between them and stays in each generator.
"""
from __future__ import annotations
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.catalog.make_thumbnails import encode, HARD_LIMIT

WEB_MERCATOR = 3857
FIGSIZE = (6, 6.6)
DPI = 100


def load_web_mercator(parquet, fallback_epsg: int = 28992):
    """Read a GeoParquet and reproject to Web Mercator, ready to plot."""
    import geopandas as gpd
    gdf = gpd.read_parquet(parquet)
    if gdf.crs is None:
        gdf.set_crs(fallback_epsg, inplace=True)
    return gdf.to_crs(WEB_MERCATOR)


def add_positron_basemap(ax) -> None:
    """CartoDB Positron behind the features. Never fatal -- it needs network."""
    import contextily as cx
    try:
        cx.add_basemap(ax, source=cx.providers.CartoDB.Positron, attribution=False)
    except Exception as e:
        print("  basemap skipped:", e)


def save_webp(fig, dst: Path | str, pad: float = 0.05) -> int:
    """Save a matplotlib figure straight to WebP. Returns bytes written.

    Routed through a temporary PNG because matplotlib has no WebP writer and
    cwebp is where the under-50 KB guarantee lives.
    """
    import matplotlib.pyplot as plt
    dst = Path(dst)
    plt.tight_layout(pad=0.2)
    with tempfile.TemporaryDirectory() as td:
        png = Path(td) / "render.png"
        fig.savefig(png, bbox_inches="tight", pad_inches=pad)
        size = encode(png, dst)
    plt.close(fig)
    if size > HARD_LIMIT:
        raise RuntimeError(f"{dst.name} is {size} bytes, over the {HARD_LIMIT}-byte limit")
    return size

"""Mapbox GL v8 style fragments shared by the style generators.

Deliberately small. Only two things are genuinely duplicated:

- match_expr, byte-identical in make_styles_thumbnails, make_extra_styles and
  make_point_legends.
- pmtiles_source, in make_styles_thumbnails and make_extra_styles.

Two things that look shared and are not, so they stay where they are:

- The point-legend workaround (an inert fill layer so portolan-browser's
  extractLegend() finds a match expression on circle styles) has exactly one
  caller, make_point_legends. See portolan-sdi/portolan-browser#13.
- Style *writing*. The committed style files follow three different
  conventions -- vro default.json is ASCII-escaped with no trailing newline,
  the vro extras are literal UTF-8 with no trailing newline, and the brp
  per-year copies have a trailing newline. Routing them through one writer
  would change bytes. Each generator keeps its own.
"""
from __future__ import annotations


def pmtiles_source(name: str, url: str | None = None) -> dict:
    """A vector source pointing at a sibling PMTiles file."""
    return {name: {"type": "vector", "url": url or f"pmtiles://../{name}.pmtiles"}}


def match_expr(field: str, mapping: dict, other: str = "#E0E0E0") -> list:
    """A Mapbox GL `match` expression: [match, [get, field], val, color, ..., other]."""
    expr = ["match", ["get", field]]
    for value, color in mapping.items():
        expr += [value, color]
    expr.append(other)
    return expr

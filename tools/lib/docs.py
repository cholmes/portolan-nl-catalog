"""Prose generation shared by the README and agent-guide generators.

The style listing is the important one. Both generators enumerate a
collection's styles from its `portolan:styles` manifest and take the display
title from the matching asset. That listing is why the published docs went
stale: styles added later by make_extra_styles and make_point_legends landed in
collection.json, but the docs were never regenerated, so nine style entries
were missing from the live catalog until phase 2.

Only what both generators do identically lives here. Their markdown bodies are
completely different documents and stay in their own files.
"""
from __future__ import annotations
import os

from . import paths


def style_entries(coll: dict) -> list[tuple[str, str, str]]:
    """(asset_key, title, filename) for each style, in manifest order.

    Reads `portolan:styles` rather than scanning assets for the "style" role:
    the manifest is ordered (default first) and both generators present styles
    in that order.
    """
    out = []
    for key in coll.get("portolan:styles", []):
        a = (coll.get("assets") or {}).get(key, {})
        out.append((key, a.get("title", ""), os.path.basename(a.get("href", ""))))
    return out


def collection_url(rel_dir: str) -> str:
    """Published URL of a collection directory, e.g. "vro/wandonderzoek"."""
    return f"{paths.DATA_BASE}/{rel_dir}"


def parquet_url(rel_dir: str, layer: str) -> str:
    return f"{collection_url(rel_dir)}/{layer}.parquet"


def pmtiles_url(rel_dir: str, layer: str) -> str:
    return f"{collection_url(rel_dir)}/{layer}.pmtiles"


def column_table(columns: list[dict]) -> list[str]:
    """The `| Column | Type | Description |` table both doc generators emit."""
    rows = ["| Column | Type | Description |", "|--------|------|-------------|"]
    for col in columns:
        rows.append(f"| {col['name']} | {col['type']} | {col.get('description', '')} |")
    return rows

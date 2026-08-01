"""STAC scaffolding shared by the catalog, collection and item generators.

Only builders duplicated across two or more generators live here. Anything one
generator alone needs stays in that generator, where it is easier to read.

Every writer goes through write_json so the whole catalog keeps one JSON
convention: two-space indent, literal UTF-8 (the titles are Dutch), and a
trailing newline. MapLibre style files are deliberately NOT written through
here -- they follow their own committed conventions (no trailing newline, and
the default.json files are ASCII-escaped).
"""
from __future__ import annotations
import json
from pathlib import Path

from . import paths

ROOT_TITLE = "Portolan NL — Cloud-Native Dutch Geodata"
JSON = "application/json"
STYLE_TYPE = "application/vnd.mapbox.style+json"


def write_json(path: Path | str, doc: dict) -> None:
    """The one way this catalog writes STAC JSON."""
    Path(path).write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")


def link(rel: str, href: str, type: str | None = None, title: str | None = None, **extra) -> dict:
    """A STAC link. Key order is rel, href, type, title -- match the committed files."""
    out = {"rel": rel, "href": href}
    if type:
        out["type"] = type
    if title:
        out["title"] = title
    out.update(extra)
    return out


def root_link(depth: int) -> dict:
    """rel:root, relative to an object `depth` directories below catalog/."""
    return link("root", "../" * depth + "catalog.json", JSON, ROOT_TITLE)


def parent_link(href: str = "../catalog.json", title: str | None = None) -> dict:
    return link("parent", href, JSON, title)


# No self_link. Portolan catalogs are self-contained (PTL-LNK-005): an object
# does not record where it is served from, so it stays valid wherever it moves.


def describedby_link(title: str) -> dict:
    """rel:describedby, relative (PTL-FIL-003), pointing at the sibling README."""
    return link("describedby", "./README.md", "text/markdown", f"{title} documentation")


def style_asset(href: str, title: str, roles: list[str] | None = None) -> dict:
    """A MapLibre style asset. PTL-VIZ-005 fixes the media type."""
    return asset(href, STYLE_TYPE, title, roles or ["style"])


def asset(href: str, type: str, title: str, roles: list[str], **extra) -> dict:
    out = {"href": href, "type": type, "title": title, "roles": roles}
    out.update(extra)
    return out


def thumbnail_asset(title: str = "Thumbnail (PDOK preview)",
                    href: str = "./thumbnail.webp") -> dict:
    """Thumbnails are WebP under 50 KB; tests/test_thumbnails.py enforces it."""
    return asset(href, "image/webp", title, ["thumbnail"])


def preview_link(title: str = "Thumbnail (PDOK preview)",
                 href: str = "./thumbnail.webp") -> dict:
    """The rel:preview twin of thumbnail_asset. Two vro catalogs carry both."""
    return link("preview", href, "image/webp", title)

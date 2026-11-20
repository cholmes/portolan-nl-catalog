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
FILE_SCHEMA = "https://stac-extensions.github.io/file/v2.1.0/schema.json"
PORTOLAN_SCHEMA = "https://schemas.portolan-sdi.org/portolan/v0.3.0/schema.json"

# PTL-PRV-001/002: a producer, and exactly one host, listed last.
VRO_PRODUCER = {"name": "Ministerie van Volkshuisvesting en Ruimtelijke Ordening",
                "roles": ["producer", "licensor"], "url": "https://www.rijksoverheid.nl/"}
HOST_PROVIDER = {"name": "Source Cooperative", "roles": ["host"],
                 "url": "https://source.coop/cholmes/portolan-nl"}


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


def agents_link() -> dict:
    """rel:agents -> the generated AGENTS.md next to the object (PTL-FIL-002)."""
    return link("agents", "./AGENTS.md", "text/markdown")


def style_asset(href: str, title: str, roles: list[str] | None = None,
                description: str | None = None) -> dict:
    """A MapLibre style asset. PTL-VIZ-005 fixes the media type."""
    return asset(href, STYLE_TYPE, title, roles or ["style"], description=description)


def asset(href: str, type: str, title: str, roles: list[str],
          description: str | None = None, **extra) -> dict:
    """Key order is href, type, title, description, roles -- match the committed files."""
    out = {"href": href, "type": type, "title": title}
    if description:
        out["description"] = description
    out["roles"] = roles
    out.update(extra)
    return out


def thumbnail_asset(title: str = "Thumbnail (PDOK preview)",
                    href: str = "./thumbnail.webp",
                    description: str = "WebP preview rendering of this collection"
                                       " for catalog browsing.") -> dict:
    """Thumbnails are WebP under 50 KB; tests/test_thumbnails.py enforces it."""
    return asset(href, "image/webp", title, ["thumbnail"], description=description)


def file_meta(path: Path | str) -> dict:
    """file:size and file:checksum for a file that lives in the catalog tree.

    The checksum is a multihash: 0x12 (sha2-256) + 0x20 (32 bytes) + the
    sha-256 digest, hex-encoded, per the STAC file extension. Only call this
    for files the repo holds -- data files live on S3 and are not hashed here.
    """
    import hashlib
    p = Path(path)
    digest = hashlib.sha256(p.read_bytes()).hexdigest()
    return {"file:size": p.stat().st_size, "file:checksum": "1220" + digest}


def preview_link(title: str = "Thumbnail (PDOK preview)",
                 href: str = "./thumbnail.webp") -> dict:
    """The rel:preview twin of thumbnail_asset. Two vro catalogs carry both."""
    return link("preview", href, "image/webp", title)

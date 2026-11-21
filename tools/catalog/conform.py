#!/usr/bin/env python3
"""Apply Portolan conformance fixes across catalog/, one rule at a time.

Each fix is registered against the rashid rule it closes, so what changed and
why is legible from the code rather than from a commit message. Every fix is a
dry run by default.

Fixes are applied here rather than by hand because the generators regenerate
much of this tree: a hand edit that the generator does not also make is undone
by the next regeneration, and tests/test_generators.py will say so.

Usage:
  python3 tools/catalog/conform.py --list
  python3 tools/catalog/conform.py PTL-LNK-005            # dry run
  python3 tools/catalog/conform.py PTL-LNK-005 --confirm
  python3 tools/catalog/conform.py --all --confirm
"""
from __future__ import annotations
import argparse
import json
import os
import sys
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parents[2]
CATALOG = Path(os.environ.get("PORTOLAN_NL_CATALOG", ROOT / "catalog"))

DATA_BASE = "https://data.source.coop/cholmes/portolan-nl"
SRC_BASE = "https://source.coop/cholmes/portolan-nl"

FIXES: dict[str, tuple[str, Callable[[dict, Path], bool]]] = {}


def fix(rule: str, description: str):
    """Register a fix. The function mutates doc in place, returning True if it changed it."""
    def deco(fn):
        FIXES[rule] = (description, fn)
        return fn
    return deco


def walk():
    """Every STAC JSON under catalog/: catalog, collection and item objects.

    Excludes MapLibre styles (styles/*.json and *.style.json) and Portolan's own
    versions.json bookkeeping -- neither is a STAC object.
    """
    for p in sorted(CATALOG.rglob("*.json")):
        if ".portolan" in p.parts or "styles" in p.parts:
            continue
        if p.name.endswith(".style.json") or p.name == "versions.json":
            continue
        yield p


def load(p: Path) -> dict | None:
    try:
        d = json.loads(p.read_text())
    except json.JSONDecodeError:
        return None
    return d if isinstance(d, dict) and "type" in d else None


def save(p: Path, doc: dict) -> None:
    p.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")


# --------------------------------------------------------------------------
# Link and type fixes
# --------------------------------------------------------------------------

@fix("PTL-LNK-005", "remove rel:self links (Portolan catalogs are self-contained)")
def _self_links(doc, path):
    links = doc.get("links")
    if not isinstance(links, list):
        return False
    keep = [l for l in links if not (isinstance(l, dict) and l.get("rel") == "self")]
    if len(keep) == len(links):
        return False
    doc["links"] = keep
    return True


@fix("PTL-LNK-003", "rel:item links are application/geo+json")
def _item_type(doc, path):
    changed = False
    for l in doc.get("links") or []:
        if isinstance(l, dict) and l.get("rel") == "item" \
                and l.get("type") != "application/geo+json":
            l["type"] = "application/geo+json"
            changed = True
    return changed


@fix("PTL-VIZ-005", "style assets are application/vnd.mapbox.style+json")
def _style_type(doc, path):
    changed = False
    for a in (doc.get("assets") or {}).values():
        if not isinstance(a, dict):
            continue
        if "style" in (a.get("roles") or []) \
                and a.get("type") != "application/vnd.mapbox.style+json":
            a["type"] = "application/vnd.mapbox.style+json"
            changed = True
    return changed


@fix("PTL-FIL-003", "rel:describedby is a relative ./README.md typed text/markdown")
def _describedby(doc, path):
    """Relative href, not an absolute URL.

    These pointed at source.coop, which serves an HTML *page* rendering the
    README and is correctly typed text/html -- so simply relabelling the type
    would have made the metadata lie. Portolan wants the href relative anyway,
    which is better: the catalog stays self-contained and resolves wherever it
    is served from. Only set where README.md is actually there.
    """
    if doc.get("type") not in ("Catalog", "Collection"):
        return False          # same reasoning as PTL-FIL-002
    if not (path.parent / "README.md").is_file():
        return False
    changed = False
    for l in doc.get("links") or []:
        if not isinstance(l, dict) or l.get("rel") != "describedby":
            continue
        if l.get("href") != "./README.md":
            l["href"] = "./README.md"
            changed = True
        if l.get("type") != "text/markdown":
            l["type"] = "text/markdown"
            changed = True
        return changed
    # No describedby at all, but a README sits next to the object.
    title = doc.get("title") or doc.get("id") or path.parent.name
    doc.setdefault("links", []).append(
        {"rel": "describedby", "href": "./README.md", "type": "text/markdown",
         "title": f"{title} documentation"})
    return True


@fix("PTL-FIL-002", "add the rel:agents link to AGENTS.md")
def _agents_link(doc, path):
    # Catalogs and collections only. An item shares a directory with its
    # catalog, so applying this to items would add the same link to all 373 of
    # them for a file that documents their parent, not them.
    if doc.get("type") not in ("Catalog", "Collection"):
        return False
    if not (path.parent / "AGENTS.md").is_file():
        return False
    links = doc.setdefault("links", [])
    if any(isinstance(l, dict) and l.get("rel") == "agents" for l in links):
        return False
    links.append({"rel": "agents", "href": "./AGENTS.md", "type": "text/markdown"})
    return True


@fix("PTL-LIC-003", "replace the deprecated 'proprietary' license with 'other'")
def _license(doc, path):
    if doc.get("license") != "proprietary":
        return False
    doc["license"] = "other"
    links = doc.setdefault("links", [])
    if not any(isinstance(l, dict) and l.get("rel") == "license" for l in links):
        # 'other' is only meaningful with a link saying what the terms are.
        links.append({"rel": "license",
                      "href": "https://www.pdok.nl/gebruiksvoorwaarden",
                      "type": "text/html",
                      "title": "PDOK terms of use"})
    return True


# --------------------------------------------------------------------------
# Schema declarations
# --------------------------------------------------------------------------

PORTOLAN_SCHEMA = "https://schemas.portolan-sdi.org/portolan/v0.3.0/schema.json"
PARTITION_SCHEMA = "https://schemas.portolan-sdi.org/incubating/partition/v1.0.0/schema.json"


@fix("PTL-CNF-002", "every object declares the same Portolan profile version as the root")
def _portolan_schema_version(doc, path):
    """Spec v0.3.0 upgrade: replace any older profile URI with the current one.

    rashid reads the profile version from the root and flags every object whose
    URI differs (PTL-CNF-002), so the bump has to land everywhere at once.
    """
    ext = doc.get("stac_extensions")
    if not isinstance(ext, list):
        return False
    changed = False
    for i, e in enumerate(ext):
        if isinstance(e, str) and "schemas.portolan-sdi.org/portolan/" in e \
                and e != PORTOLAN_SCHEMA:
            ext[i] = PORTOLAN_SCHEMA
            changed = True
    return changed


@fix("PTL-CNF-001", "declare the Portolan profile schema in stac_extensions")
def _portolan_schema(doc, path):
    # Catalogs and collections only. Portolan does not ask items to redeclare
    # the profile their collection already declares, and adding it to all 373
    # of them would be noise.
    if doc.get("type") not in ("Catalog", "Collection"):
        return False
    ext = doc.setdefault("stac_extensions", [])
    if any("schemas.portolan-sdi.org/portolan/" in e for e in ext):
        return False
    ext.insert(0, PORTOLAN_SCHEMA)      # the profile first, then STAC extensions
    return True


@fix("PTL-PRT-001", "drop partition:* from collections that are not actually partitioned")
def _partition_fields(doc, path):
    """kadaster/inspire_buildings claims 512 hive/kdtree partitions it does not have.

    `portolan add` wrote the partition metadata and 512 kdtree_cell=* item
    directories, but the partitioned data was never uploaded -- the published
    prefix holds a single buildings.parquet. Portolan then asks for a
    partition:glob naming the bulk-access path, and there is no such path.

    Declaring the extension, or inventing a glob, would both assert something
    false. The collection is not partitioned, so the fields come off. If it is
    ever republished as partitions, they come back with a real glob.
    """
    keys = [k for k in doc if k.startswith("partition:")]
    if not keys:
        return False
    for k in keys:
        del doc[k]
    ext = doc.get("stac_extensions") or []
    doc["stac_extensions"] = [e for e in ext if "partition/" not in e]
    return True


# --------------------------------------------------------------------------
# Providers
# --------------------------------------------------------------------------

# The subcatalog a collection sits under names its producer. Declared, not
# inferred: every URL here was checked to return 200.
PRODUCERS = {
    "kadaster": ("Het Kadaster", "https://www.kadaster.nl/"),
    "rijkswaterstaat": ("Rijkswaterstaat", "https://www.rijkswaterstaat.nl/"),
    "rce": ("Rijksdienst voor het Cultureel Erfgoed", "https://www.cultureelerfgoed.nl/"),
    "rvo": ("Rijksdienst voor Ondernemend Nederland", "https://www.rvo.nl/"),
    "tudelft": ("TU Delft — 3D Geoinformation Research Group", "https://3d.bk.tudelft.nl/"),
    "cbs": ("Centraal Bureau voor de Statistiek", "https://www.cbs.nl/"),
    "vro": ("Ministerie van Volkshuisvesting en Ruimtelijke Ordening",
            "https://www.rijksoverheid.nl/"),
    "beeldmateriaal": ("Beeldmateriaal Nederland", "https://www.beeldmateriaal.nl/"),
}
HOST = {"name": "Source Cooperative", "roles": ["host"],
        "url": "https://source.coop/cholmes/portolan-nl"}


@fix("PTL-PRV-001", "add providers: the institution as producer, Source Cooperative as host")
def _providers(doc, path):
    if doc.get("type") != "Collection" or doc.get("providers"):
        return False
    inst = path.relative_to(CATALOG).parts[0]
    if inst not in PRODUCERS:
        return False
    name, url = PRODUCERS[inst]
    # Host last, and on exactly one provider: PTL-PRV-002.
    doc["providers"] = [{"name": name, "roles": ["producer", "licensor"], "url": url},
                        dict(HOST)]
    return True


# --------------------------------------------------------------------------
# Visualization
# --------------------------------------------------------------------------

@fix("PTL-VIZ-003", "name the default-visible layers on rel:pmtiles links")
def _pmtiles_layers(doc, path):
    if doc.get("type") != "Collection":
        return False
    layers = doc.get("pmtiles:layers") or (doc.get("properties") or {}).get("pmtiles:layers")
    if not layers:
        for a in (doc.get("assets") or {}).values():
            if isinstance(a, dict) and str(a.get("type")) == "application/vnd.pmtiles":
                stem = Path(str(a.get("href", ""))).stem
                if stem:
                    layers = [stem]
                break
    if not layers:
        return False
    changed = False
    for l in doc.get("links") or []:
        if isinstance(l, dict) and l.get("rel") == "pmtiles" and "pmtiles:layers" not in l:
            l["pmtiles:layers"] = list(layers)
            changed = True
    return changed


@fix("PTL-VIZ-001", "register the collection's thumbnail.webp as a thumbnail asset")
def _thumbnail_asset(doc, path):
    if doc.get("type") != "Collection":
        return False
    if not (path.parent / "thumbnail.webp").is_file():
        return False
    assets = doc.setdefault("assets", {})
    if any(isinstance(a, dict) and "thumbnail" in (a.get("roles") or [])
           for a in assets.values()):
        return False
    assets["thumbnail"] = {"href": "./thumbnail.webp", "type": "image/webp",
                           "title": f"{doc.get('title', path.parent.name)} (preview)",
                           "roles": ["thumbnail"]}
    return True


@fix("PTL-VIZ-006", "the default style asset carries the 'default' role (spec PR #97)")
def _default_style(doc, path):
    if doc.get("type") != "Collection":
        return False
    styles = {k: a for k, a in (doc.get("assets") or {}).items()
              if isinstance(a, dict) and "style" in (a.get("roles") or [])}
    if len(styles) < 2:
        return False                      # #97 does not apply to single-style collections
    if any("default" in (a.get("roles") or []) for a in styles.values()):
        return False
    key = next((k for k in styles if k.split("/")[-1] == "default"), None)
    if key is None:
        # Fall back to whatever the portolan:styles manifest lists first, which
        # is the order the browser presents and the catalog's own idea of default.
        order = doc.get("portolan:styles") or (doc.get("properties") or {}).get("portolan:styles") or []
        key = next((k for k in order if k in styles), None)
    if key is None:
        return False
    styles[key]["roles"] = [*styles[key]["roles"], "default"]
    return True


@fix("PTL-VIZ-003b", "declare web-map-links wherever a rel:pmtiles link is used")
def _webmaplinks_schema(doc, path):
    if not any(isinstance(l, dict) and l.get("rel") in ("pmtiles", "xyz", "tilejson", "wmts")
               for l in doc.get("links") or []):
        return False
    ext = doc.setdefault("stac_extensions", [])
    uri = "https://stac-extensions.github.io/web-map-links/v1.3.0/schema.json"
    if uri in ext:
        return False
    ext.append(uri)
    return True


@fix("PTL-PRV-002", "exactly one provider carries the 'host' role")
def _one_host(doc, path):
    provs = doc.get("providers")
    if not isinstance(provs, list) or not provs:
        return False
    hosts = [p for p in provs if isinstance(p, dict) and "host" in (p.get("roles") or [])]
    if len(hosts) == 1:
        return False
    if len(hosts) > 1:                       # keep the host role on the last one only
        for p in hosts[:-1]:
            p["roles"] = [r for r in p["roles"] if r != "host"]
        return True
    provs.append(dict(HOST))                 # none: Source Cooperative serves these files
    return True


# The data working directory is where the last publish happened, and the S3
# listing records when. Read once, lazily, so a run that needs no timestamps
# does not require the file.
_S3_TIMES: dict[str, str] = {}


def _load_s3_times(listing="/tmp/s3now.txt", prefix="cholmes/portolan-nl/"):
    from datetime import datetime, timezone
    for line in Path(listing).read_text().splitlines():
        parts = line.split(maxsplit=3)
        if len(parts) != 4 or not parts[3].startswith(prefix):
            continue
        key = parts[3][len(prefix):]
        stamp = datetime.strptime(f"{parts[0]} {parts[1]}", "%Y-%m-%d %H:%M:%S") \
            .replace(tzinfo=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        _S3_TIMES[key] = stamp


@fix("PTL-PRO-003", "record the last sync in a top-level 'updated'")
def _updated(doc, path):
    """The real publish time of the collection's own objects, not today's date.

    'updated' is when this mirror last synced from upstream. The honest source
    is when its files were actually written to the published prefix, which the
    S3 listing records. Refresh it with:
      aws s3 ls s3://.../cholmes/portolan-nl/ --recursive > /tmp/s3now.txt
    """
    if doc.get("type") not in ("Collection", "Catalog") or doc.get("updated"):
        return False
    if not _S3_TIMES:
        _load_s3_times()
    base = path.parent.relative_to(CATALOG).as_posix()
    stamps = ([v for k, v in _S3_TIMES.items() if k.startswith(base + "/")]
              if base != "." else list(_S3_TIMES.values()))
    if not stamps:
        return False
    doc["updated"] = max(stamps)
    return True


# --------------------------------------------------------------------------
# Navigation and structure
# --------------------------------------------------------------------------

@fix("PTL-LNK-002", "add child links to contained objects the parent never listed")
def _child_links(doc, path):
    """Four collections exist on disk and on S3 but nothing links to them.

    They are unreachable by crawling the catalog, which is how every client
    finds anything. This is a real navigation bug, not a formality.
    """
    if doc.get("type") != "Catalog" or path.name != "catalog.json":
        return False
    links = doc.setdefault("links", [])
    have = {str(l.get("href")) for l in links if isinstance(l, dict) and l.get("rel") == "child"}
    changed = False
    for child in sorted(path.parent.iterdir()):
        if not child.is_dir() or child.name.startswith("."):
            continue
        for name in ("collection.json", "catalog.json"):
            target = child / name
            if not target.is_file():
                continue
            href = f"./{child.name}/{name}"
            if href in have:
                break
            cdoc = load(target) or {}
            links.append({"rel": "child", "href": href, "type": "application/json",
                          "title": cdoc.get("title") or cdoc.get("id") or child.name})
            changed = True
            break
    return changed


@fix("PTL-LNK-006", "rel:parent points at the containing object")
def _parent_link(doc, path):
    # Catalogs and collections only. An item's parent is the catalog sitting in
    # its own directory; walking up from the item finds the grandparent instead
    # and would repoint all 357 luchtfoto items at the wrong object.
    if doc.get("type") not in ("Catalog", "Collection"):
        return False
    target = None
    for parent in path.parent.parents:
        for name in ("catalog.json", "collection.json"):
            if (parent / name).is_file():
                target = parent / name
                break
        if target or parent == CATALOG:
            break
    if target is None:
        return False
    href = "./" + os.path.relpath(target, path.parent).replace(os.sep, "/")
    href = href.replace("./../", "../")
    changed = False
    for l in doc.get("links") or []:
        if isinstance(l, dict) and l.get("rel") == "parent" and l.get("href") != href:
            l["href"] = href
            changed = True
    return changed


@fix("PTL-TTL-001", "give every catalog and collection a title")
def _title(doc, path):
    # Items carry their title under properties; Portolan asks only catalogs and
    # collections for a top-level one.
    if doc.get("type") not in ("Catalog", "Collection"):
        return False
    if doc.get("title"):
        return False
    ident = doc.get("id") or path.parent.name
    # Turn an id like inspire_buildings into "Inspire Buildings" -- a placeholder
    # worth replacing by hand, but better than nothing for a browser's tree.
    doc["title"] = ident.replace("_", " ").replace("-", " ").title()
    return True


@fix("PTL-AST-005", "move thumbnails off catalogs, which may not declare assets")
def _catalog_assets(doc, path):
    """Two vro subcatalogs declare a thumbnail asset.

    Portolan puts assets on collections and items only. Both catalogs already
    carry a rel:preview link to the same file, so dropping the asset loses no
    reachability -- the thumbnail is still discoverable and still published.
    """
    if doc.get("type") != "Catalog" or not doc.get("assets"):
        return False
    previews = {str(l.get("href")) for l in doc.get("links") or []
                if isinstance(l, dict) and l.get("rel") == "preview"}
    if not all(str(a.get("href")) in previews for a in doc["assets"].values()
               if isinstance(a, dict)):
        return False                 # something other than the previewed thumbnail; leave it
    del doc["assets"]
    return True


@fix("PTL-MIR-002", "the collection mirror asset carries its role and media type")
def _mirror_asset(doc, path):
    a = (doc.get("assets") or {}).get("items")
    if not isinstance(a, dict):
        return False
    changed = False
    roles = a.get("roles") or []
    if "collection-mirror" not in roles:
        a["roles"] = [*roles, "collection-mirror"]
        changed = True
    if a.get("type") == "application/x-parquet":
        a["type"] = "application/vnd.apache.parquet"
        changed = True
    return changed


# --------------------------------------------------------------------------
# Spec v0.3.0 fixes (2026-11). Each closes a rule rashid 0.4.0 reports.
# --------------------------------------------------------------------------

@fix("PTL-AST-009p", "GeoParquet data assets use the registered parquet media type")
def _parquet_type(doc, path):
    """'application/x-parquet' predates the IANA registration. rashid 0.4.0
    recognises a collection's GeoParquet only under the registered type, so
    the old spelling breaks the PMTiles-to-GeoParquet reference (PORTO-FMT-062).
    """
    changed = False
    for a in (doc.get("assets") or {}).values():
        if isinstance(a, dict) and a.get("type") == "application/x-parquet":
            a["type"] = "application/vnd.apache.parquet"
            changed = True
    return changed


@fix("PTL-AST-009d", "remove PMTiles assets that duplicate the visual asset under a data role")
def _pmtiles_dupes(doc, path):
    """Eight collections register the same .pmtiles twice: once as the visual
    asset and once under a filename key with a bare data role. v0.3 forbids
    PMTiles as a data asset (PORTO-FMT-062), and the second registration adds
    nothing the visual asset does not already say.
    """
    assets = doc.get("assets")
    if not isinstance(assets, dict):
        return False
    pmtiles_hrefs = {}
    for key, a in assets.items():
        if isinstance(a, dict) and a.get("type") == "application/vnd.pmtiles" \
                and "visual" in (a.get("roles") or []):
            pmtiles_hrefs[a.get("href")] = key
    drop = [key for key, a in assets.items()
            if isinstance(a, dict) and a.get("type") == "application/vnd.pmtiles"
            and "visual" not in (a.get("roles") or [])
            and a.get("href") in pmtiles_hrefs and pmtiles_hrefs[a["href"]] != key]
    for key in drop:
        del assets[key]
    return bool(drop)


# Landing pages for the ten mirrors that had only service-endpoint via links.
# Every URL was fetched on 2026-11-20 and verified to serve the dataset's own
# page (the PDOK articles render "Dataset: <name>"; the NGR page is the
# text/html describedby the wandonderzoek Atom feed itself declares).
LANDING = {
    "rijkswaterstaat/nwb_wegen":
        ("https://www.pdok.nl/introductie/-/article/nationaal-wegen-bestand-nwb-wegen",
         "PDOK dataset page: Nationaal Wegen Bestand (NWB) - Wegen"),
    "vro/bodemkaart/soilarea":
        ("https://www.pdok.nl/introductie/-/article/bro-bodemkaart-sgm-",
         "PDOK dataset page: BRO Bodemkaart (SGM)"),
    "vro/bodemkaart/areaofpedologicalinterest":
        ("https://www.pdok.nl/introductie/-/article/bro-bodemkaart-sgm-",
         "PDOK dataset page: BRO Bodemkaart (SGM)"),
    "vro/geomorfologische_kaart/geomorphological_area":
        ("https://www.pdok.nl/introductie/-/article/bro-geomorfologische-kaart-gmm-",
         "PDOK dataset page: BRO Geomorfologische kaart (GMM)"),
    "vro/geomorfologische_kaart/geomorphological_area_collection":
        ("https://www.pdok.nl/introductie/-/article/bro-geomorfologische-kaart-gmm-",
         "PDOK dataset page: BRO Geomorfologische kaart (GMM)"),
    "vro/geomorfologische_kaart/area_of_geomorphological_interest":
        ("https://www.pdok.nl/introductie/-/article/bro-geomorfologische-kaart-gmm-",
         "PDOK dataset page: BRO Geomorfologische kaart (GMM)"),
    "vro/bodemverontreiniging_besluit":
        ("https://www.pdok.nl/introductie/-/article/bro-overheidsbesluit-bodemverontreiniging-sld-",
         "PDOK dataset page: BRO Overheidsbesluit bodemverontreiniging (SLD)"),
    "vro/grondwatergebruiksysteem":
        ("https://www.pdok.nl/introductie/-/article/bro-grondwatergebruiksysteem-guf-",
         "PDOK dataset page: BRO Grondwatergebruiksysteem (GUF)"),
    "vro/mijnbouwconstructie":
        ("https://www.pdok.nl/introductie/-/article/bro-mijnbouwconstructie-epc-",
         "PDOK dataset page: BRO Mijnbouwconstructie (EPC)"),
    "vro/wandonderzoek":
        ("https://www.nationaalgeoregister.nl/geonetwork/srv/dut/catalog.search#/metadata/"
         "6cbbecc1-753b-416d-ad72-1621695ec356",
         "NGR metadata page: BRO Wandonderzoek bodemkunde (SFR)"),
}


@fix("PTL-PRO-001", "every mirror carries one text/html via link to its source page")
def _via_landing(doc, path):
    """v0.3 (PORTO-CORE-084) wants at least one HTML via link per mirror; the
    service-endpoint via links keep their real media types beside it.
    """
    rel = path.parent.relative_to(CATALOG).as_posix()
    if rel not in LANDING:
        return False
    links = doc.setdefault("links", [])
    if any(isinstance(l, dict) and l.get("rel") == "via"
           and l.get("type") == "text/html" for l in links):
        return False
    url, title = LANDING[rel]
    after = max((i for i, l in enumerate(links)
                 if isinstance(l, dict) and l.get("rel") == "via"), default=len(links) - 1)
    links.insert(after + 1, {"rel": "via", "href": url, "type": "text/html",
                             "title": title})
    return True


@fix("PTL-AST-012", "brp_gewaspercelen: the cross-year glob moves to partition:glob")
def _brp_partition(doc, path):
    """v0.3 forbids globs in data asset hrefs (PORTO-FMT-065) and requires
    partition globs to be absolute bucket URLs that clients can list
    (PORTO-FMT-064). The 17 per-year files are a directory partition on the
    'jaar' column, so the collection declares the partition extension and the
    glob moves there as the bucket URL. The per-year items keep their
    single-file data assets.
    """
    if path.parent.relative_to(CATALOG).as_posix() != "rvo/brp_gewaspercelen":
        return False
    assets = doc.get("assets") or {}
    data = assets.get("data")
    if not (isinstance(data, dict) and "*" in str(data.get("href", ""))):
        return False
    del assets["data"]
    ext = doc.setdefault("stac_extensions", [])
    if PARTITION_SCHEMA not in ext:
        ext.append(PARTITION_SCHEMA)
    doc["partition:scheme"] = "directory"
    doc["partition:strategy"] = "temporal"
    doc["partition:keys"] = [{"name": "jaar", "type": "int32",
                              "description": "Harvest year; one subdirectory per year."}]
    doc["partition:glob"] = ("s3://us-west-2.opendata.source.coop/cholmes/portolan-nl/"
                             "rvo/brp_gewaspercelen/*/brp_gewaspercelen_*.parquet")
    doc["partition:file_count"] = 17
    return True


@fix("PTL-LNK-006", "3dbag: drop the raw XYZ-template link and asset")
def _xyz_template(doc, path):
    """A literal {z}/{x}/{y} template is not a valid URI reference, so the
    rel:xyz link and its twin asset fail link validation. The same endpoint
    stays reachable through the tilejson asset, whose document carries the
    template where a template is legal.
    """
    if doc.get("id") != "3dbag":
        return False
    changed = False
    links = doc.get("links") or []
    keep = [l for l in links
            if not (isinstance(l, dict) and "{z}" in str(l.get("href", "")))]
    if len(keep) != len(links):
        doc["links"] = keep
        changed = True
    assets = doc.get("assets") or {}
    for key in [k for k, a in assets.items()
                if isinstance(a, dict) and "{z}" in str(a.get("href", ""))]:
        del assets[key]
        changed = True
    return changed


# Standard texts for the asset kinds this catalog repeats everywhere. The
# per-collection meaning lives in the collection title these templates cite.
def _title_of(doc):
    return doc.get("title") or doc.get("id") or "this collection"


def _ast010_texts(key, a, doc):
    """(title, description) templates per asset kind; None leaves it alone."""
    roles = a.get("roles") or []
    t = _title_of(doc)
    if "thumbnail" in roles:
        return ("Thumbnail", f"WebP preview rendering of {t} for catalog browsing.")
    if "style" in roles:
        name = key.split("/", 1)[-1]
        return (f"{t} — {name}", f"MapLibre style '{name}' for the PMTiles visual asset.")
    if key == "README" or "documentation" in roles:
        return ("Documentation", f"Human-readable documentation for {t}.")
    if "collection-mirror" in roles:
        return ("STAC items (GeoParquet)",
                "All item metadata as one GeoParquet table (collection mirror).")
    if a.get("type") == "application/vnd.pmtiles":
        return (f"{t} (vector tiles)",
                f"PMTiles vector tiles of {t} for web-map display.")
    if a.get("type") == "application/vnd.apache.parquet":
        return (f"{t} (GeoParquet)", f"{t} as cloud-native GeoParquet.")
    if a.get("type") == "application/geopackage+sqlite3":
        return (f"{t} (GeoPackage)", f"{t} as a GeoPackage, matching the source format.")
    if "source" in roles:
        return ("Source download", f"The upstream source file for {t}, as downloaded.")
    if "metadata" in roles:
        return ("Source metadata", f"Metadata sidecar from the source service for {t}.")
    return (None, None)


@fix("PTL-AST-010", "every asset carries a title and a description")
def _asset_titles(doc, path):
    changed = False
    for key, a in (doc.get("assets") or {}).items():
        if not isinstance(a, dict):
            continue
        title, desc = _ast010_texts(key, a, doc)
        if title and not a.get("title"):
            a["title"] = title
            changed = True
        if desc and not a.get("description"):
            a["description"] = desc
            changed = True
    return changed


@fix("PTL-AST-003", "assets whose file is in the repo carry file:size and file:checksum")
def _file_meta(doc, path):
    """Data files live on S3 and are hashed by their own pipelines; this covers
    the files the repo itself publishes (thumbnails, styles, READMEs). The
    hash is multihash sha2-256. tests/test_file_metadata.py keeps these honest.
    """
    import hashlib
    FILE_SCHEMA = "https://stac-extensions.github.io/file/v2.1.0/schema.json"
    changed = False
    for key, a in (doc.get("assets") or {}).items():
        if not isinstance(a, dict):
            continue
        href = str(a.get("href") or "")
        if not href.startswith("./"):
            continue        # absolute hrefs point at S3, which this cannot hash
        target = (path.parent / href).resolve()
        if not target.is_file() or target == path.resolve():
            continue        # absent locally, or a self-reference (PORTO-CORE-085)
        # Recompute rather than fill a gap. An edit to a README changes its
        # size and its hash, and a stale value is a wrong value, which
        # tests/test_file_metadata.py reports.
        size = target.stat().st_size
        if a.get("file:size") != size:
            a["file:size"] = size
            changed = True
        digest = "1220" + hashlib.sha256(target.read_bytes()).hexdigest()
        if a.get("file:checksum") != digest:
            a["file:checksum"] = digest
            changed = True
    if changed and doc.get("type") in ("Catalog", "Collection", "Feature"):
        ext = doc.setdefault("stac_extensions", [])
        if FILE_SCHEMA not in ext:
            ext.append(FILE_SCHEMA)
    return changed


# --------------------------------------------------------------------------

def run(rules: list[str], confirm: bool) -> int:
    for rule in rules:
        desc, fn = FIXES[rule]
        touched = []
        for p in walk():
            doc = load(p)
            if doc is None:
                continue
            if fn(doc, p):
                touched.append(p)
                if confirm:
                    save(p, doc)
        verb = "fixed" if confirm else "would fix"
        print(f"{rule}: {verb} {len(touched)} file(s) — {desc}")
        for p in touched[:4]:
            print(f"    {p.relative_to(CATALOG)}")
        if len(touched) > 4:
            print(f"    ... and {len(touched) - 4} more")
    if not confirm:
        print("\nDry run. Re-run with --confirm to write.")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("rules", nargs="*", help="rule ids to apply")
    ap.add_argument("--all", action="store_true", help="apply every registered fix")
    ap.add_argument("--list", action="store_true", help="list registered fixes")
    ap.add_argument("--confirm", action="store_true", help="write changes")
    args = ap.parse_args(argv)

    if args.list:
        for r, (d, _) in sorted(FIXES.items()):
            print(f"{r}  {d}")
        return 0
    rules = sorted(FIXES) if args.all else args.rules
    if not rules:
        ap.print_help()
        return 2
    unknown = [r for r in rules if r not in FIXES]
    if unknown:
        print(f"error: no fix registered for {', '.join(unknown)}", file=sys.stderr)
        return 2
    return run(rules, args.confirm)


if __name__ == "__main__":
    sys.exit(main())

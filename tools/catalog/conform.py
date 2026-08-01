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

PORTOLAN_SCHEMA = "https://schemas.portolan-sdi.org/portolan/v0.1.0/schema.json"
PARTITION_SCHEMA = "https://schemas.portolan-sdi.org/incubating/partition/v1.0.0/schema.json"


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
    if doc.get("type") != "Collection" or doc.get("updated"):
        return False
    if not _S3_TIMES:
        _load_s3_times()
    base = path.parent.relative_to(CATALOG).as_posix()
    stamps = [v for k, v in _S3_TIMES.items() if k.startswith(base + "/")]
    if not stamps:
        return False
    doc["updated"] = max(stamps)
    return True


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

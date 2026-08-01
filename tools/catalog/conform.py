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

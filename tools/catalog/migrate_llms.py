#!/usr/bin/env python3
"""One-shot migration: retire llms.txt in favour of AGENTS.md.

The Portolan spec settled on AGENTS.md (rel:agents) as the single agent-guide
surface; llms.txt appears nowhere in it. This catalog had both, with AGENTS.md
mostly deferring to the richer hand-written llms.txt. This script moves the
content to where the spec looks for it:

1. Every hand-written llms.txt becomes its directory's AGENTS.md, verbatim but
   for self-references (".../llms.txt" URLs and mentions become AGENTS.md).
   The generated llms.txt (vro collections, brp year folders) are not ported
   here -- their generators now write AGENTS.md directly.
2. Every llms.txt is deleted.
3. Every STAC JSON loses its rel:llms links and any asset whose href points at
   llms.txt (per core.md, the agent guide is a link, not an asset), and
   descriptions naming llms.txt now name AGENTS.md.
4. Hand-written markdown under catalog/ that references llms.txt is updated.

Kept in the repo for the record; running it again after migration is a no-op.

Usage:
  python3 tools/catalog/migrate_llms.py            # dry run
  python3 tools/catalog/migrate_llms.py --confirm
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "catalog"

FOOTER = ("\n---\n*Hand-maintained agent guide (ported from this collection's "
          "llms.txt in August 2026). Update it alongside collection.json.*\n")

# Directories whose agent guide is written by another generator; their llms.txt
# is deleted but not ported here.
def _generator_owned(d: Path) -> bool:
    rel = d.relative_to(CATALOG).as_posix()
    if rel.startswith("vro/") and (d / "collection.json").is_file():
        return True                       # make_vro_agents.py
    parts = rel.split("/")
    return (len(parts) == 3 and parts[:2] == ["rvo", "brp_gewaspercelen"]
            and parts[2].isdigit())       # generate_year_docs.py


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--confirm", action="store_true")
    args = ap.parse_args(argv)
    w = args.confirm

    ported = deleted = 0
    for f in sorted(CATALOG.rglob("llms.txt")):
        if not _generator_owned(f.parent):
            text = f.read_text().replace("llms.txt", "AGENTS.md")
            if not text.rstrip().endswith("*"):
                text = text.rstrip() + "\n" + FOOTER
            if w:
                (f.parent / "AGENTS.md").write_text(text)
            ported += 1
        if w:
            f.unlink()
        deleted += 1

    jsons = 0
    for f in sorted(CATALOG.rglob("*.json")):
        if ".portolan" in f.parts or "styles" in f.parts or f.name == "versions.json":
            continue
        try:
            doc = json.loads(f.read_text())
        except json.JSONDecodeError:
            continue
        if not isinstance(doc, dict) or "type" not in doc:
            continue
        changed = False
        links = doc.get("links")
        if isinstance(links, list):
            keep = [l for l in links
                    if not (isinstance(l, dict) and (l.get("rel") == "llms"
                            or "llms.txt" in str(l.get("href", ""))))]
            if len(keep) != len(links):
                doc["links"] = keep
                changed = True
        assets = doc.get("assets")
        if isinstance(assets, dict):
            drop = [k for k, a in assets.items()
                    if isinstance(a, dict) and "llms.txt" in str(a.get("href", ""))]
            for k in drop:
                del assets[k]
                changed = True
        for holder in (doc, doc.get("properties") or {}):
            desc = holder.get("description")
            if isinstance(desc, str) and "llms.txt" in desc:
                holder["description"] = desc.replace("llms.txt", "AGENTS.md")
                changed = True
        if changed:
            jsons += 1
            if w:
                f.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")

    mds = 0
    for f in sorted(CATALOG.rglob("*.md")):
        if f.name == "AGENTS.md":
            continue    # ported guides already handled; the sweep would mangle their footer
        t = f.read_text()
        if "llms.txt" in t:
            mds += 1
            if w:
                f.write_text(t.replace("llms.txt", "AGENTS.md"))

    verb = "did" if w else "would"
    print(f"{verb} port {ported} agent guides, delete {deleted} llms.txt, "
          f"clean {jsons} JSON files, update {mds} markdown files")
    if not w:
        print("Re-run with --confirm to apply.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

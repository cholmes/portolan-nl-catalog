"""Verify every relative href in catalog/collection/item JSON resolves to a file.

Checks `links` only, not `assets`: asset hrefs point at data files that are
intentionally absent from this repo and live only on Source Cooperative.
"""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "catalog"

def stac_json_files():
    for name in ("catalog.json",):
        p = ROOT / name
        if p.exists():
            yield p
    yield from ROOT.glob("**/collection.json")
    yield from ROOT.glob("**/*/*.json")  # item jsons live in item subdirs

def check():
    errors = []
    seen = set()
    for jf in stac_json_files():
        if jf in seen:
            continue
        seen.add(jf)
        try:
            doc = json.loads(jf.read_text())
        except json.JSONDecodeError as e:
            errors.append(f"{jf}: invalid JSON: {e}")
            continue
        if not isinstance(doc, dict):
            continue
        for link in doc.get("links", []):
            href = link.get("href", "")
            if href.startswith("http") or href.startswith("#"):
                continue
            target = (jf.parent / href).resolve()
            if not target.exists():
                errors.append(f"{jf}: link rel={link.get('rel')} -> missing {href}")
    if errors:
        print("\n".join(errors)); sys.exit(1)
    print(f"OK: {len(seen)} STAC files, all relative links resolve")

if __name__ == "__main__":
    check()

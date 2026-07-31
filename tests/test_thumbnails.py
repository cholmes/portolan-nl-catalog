"""Every thumbnail asset under catalog/ is WebP, present, and under 50 KB.

WebP conversion is done by tools/catalog/make_thumbnails.py. The 50 KB ceiling
is a deliberate repo-size constraint, not a format requirement.

Leftover originals are caught by reference rather than by filename glob: after
conversion, every raster image under catalog/ must still be pointed at by some
asset or link. A stranded thumbnail.png is unreferenced and fails, whatever it
is called -- this catalog uses three different thumbnail namings plus one .jpg,
so a glob on "thumbnail.png" would quietly miss ten of them.
"""
import json, sys
from pathlib import Path

CATALOG = Path(__file__).resolve().parents[1] / "catalog"
LIMIT = 50 * 1024
RASTER_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}
# Byte-identical duplicate of logo-mark.png and referenced by nothing in the
# catalog, but already live on data.source.coop, so it is kept rather than
# deleted on the assumption nothing external hotlinks it.
UNREFERENCED_OK = {"beeldmateriaal/logo.png"}

errs = []
checked = 0
referenced: set[Path] = set()
for jf in CATALOG.rglob("*.json"):
    if ".portolan" in jf.parts or "styles" in jf.parts:
        continue
    try:
        doc = json.loads(jf.read_text())
    except json.JSONDecodeError:
        continue  # test_links.py owns malformed JSON
    if not isinstance(doc, dict):
        continue
    for ref in [*(doc.get("assets") or {}).values(), *(doc.get("links") or [])]:
        if isinstance(ref, dict) and not str(ref.get("href", "")).startswith("http"):
            referenced.add((jf.parent / str(ref.get("href", ""))).resolve())
    for key, asset in (doc.get("assets") or {}).items():
        if not isinstance(asset, dict):
            continue
        if "thumbnail" not in (asset.get("roles") or []):
            continue
        href = str(asset.get("href", ""))
        if href.startswith("http"):
            continue
        rel = jf.relative_to(CATALOG).as_posix()
        checked += 1
        if not href.endswith(".webp"):
            errs.append(f"{rel}: asset {key!r} href is not .webp: {href}")
            continue
        if asset.get("type") != "image/webp":
            errs.append(f"{rel}: asset {key!r} type is {asset.get('type')!r}, want image/webp")
        target = (jf.parent / href).resolve()
        if not target.exists():
            errs.append(f"{rel}: asset {key!r} -> missing {href}")
            continue
        size = target.stat().st_size
        if size > LIMIT:
            errs.append(f"{rel}: asset {key!r} is {size / 1024:.0f} KB, over the 50 KB limit")

for p in sorted(CATALOG.rglob("*")):
    if p.suffix.lower() not in RASTER_SUFFIXES or not p.is_file():
        continue
    if p.relative_to(CATALOG).as_posix() in UNREFERENCED_OK:
        continue
    if p.resolve() not in referenced:
        errs.append(f"stray image, not referenced by any asset or link: "
                    f"{p.relative_to(CATALOG).as_posix()}")

if errs:
    print("\n".join(f"FAIL {e}" for e in errs))
    print(f"\n{len(errs)} problem(s) across {checked} thumbnail assets")
    sys.exit(1)
print(f"OK: {checked} thumbnail assets, all WebP and under 50 KB")

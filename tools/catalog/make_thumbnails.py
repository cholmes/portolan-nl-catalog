#!/usr/bin/env python3
"""Convert every raster thumbnail asset under catalog/ to WebP, and rewrite refs.

Encoding rule, benchmarked over 120 of this catalog's real thumbnails:
encode at native resolution with -q 80; if the result exceeds 48 KB, re-encode
with a hard -size 46000 byte target. Measured: avg 37 KB, max 47 KB, with 38 of
120 needing the fallback. No resizing -- the byte target does the work, so
nothing is lost to downscaling.

The selector is the thumbnail *role*, not the filename: this catalog spells its
thumbnails three ways (foo-thumbnail.png, thumbnail.png, thumbnail_.png) and one
is a .jpg, so any name-based rule would miss some. The seven institution logos
are referenced from `icon` links rather than assets, carry no thumbnail role,
and stay PNG.

Usage:
  python3 tools/catalog/make_thumbnails.py            # dry run
  python3 tools/catalog/make_thumbnails.py --confirm  # convert, rewrite, delete originals
"""
from __future__ import annotations
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "catalog"
SOFT_LIMIT = 48 * 1024   # above this, re-encode with a hard byte target
HARD_LIMIT = 50 * 1024   # tests/test_thumbnails.py enforces this
BYTE_TARGET = 46000      # cwebp -size argument for the fallback
SOURCE_SUFFIXES = {".png", ".jpg", ".jpeg"}


def webp_href(href: str) -> str:
    """Swap the extension, preserving the rest of the href verbatim.

    Path.with_suffix() would drop the leading "./" these hrefs all carry.
    """
    return href[: len(href) - len(Path(href).suffix)] + ".webp"


def _cwebp(src: Path, dst: Path, quality: int) -> int:
    subprocess.run(["cwebp", "-q", str(quality), "-quiet", str(src), "-o", str(dst)],
                   check=True)
    return dst.stat().st_size


def encode(src: Path, dst: Path) -> int:
    """Raster image -> WebP at native resolution. Returns output size in bytes.

    Encodes at -q 80; if that exceeds the soft limit, binary-searches the
    quality factor for the best one that still fits under BYTE_TARGET.

    The search replaces cwebp's own -size target, which is not trustworthy on
    this catalog: for a 500x500 map thumbnail, -size 46000 overshot to 52 KB at
    the default single pass, while for a 512x640 aerial photo the same flag
    undershot to 29 KB at one pass and overshot to 59 KB at ten. Searching the
    quality factor is a handful of extra encodes and cannot miss.
    """
    size = _cwebp(src, dst, 80)
    if size <= SOFT_LIMIT:
        return size

    lo, hi, best = 1, 80, 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if _cwebp(src, dst, mid) <= BYTE_TARGET:
            best = mid
            lo = mid + 1
        else:
            hi = mid - 1
    # dst currently holds whichever quality was probed last, which may be an
    # overshoot, so write the winner. If even -q 1 was too big, best is 1 and
    # this is the smallest cwebp can do; the caller enforces the hard limit.
    return _cwebp(src, dst, best)


def find_targets() -> list[tuple[Path, str, str]]:
    """(json_file, asset_key, href) for every non-WebP thumbnail asset."""
    out = []
    for jf in sorted(CATALOG.rglob("*.json")):
        if ".portolan" in jf.parts or "styles" in jf.parts:
            continue
        try:
            doc = json.loads(jf.read_text())
        except json.JSONDecodeError:
            continue
        if not isinstance(doc, dict):
            continue
        for key, asset in (doc.get("assets") or {}).items():
            if not isinstance(asset, dict):
                continue
            href = str(asset.get("href", ""))
            if href.startswith("http"):
                continue
            if (Path(href).suffix.lower() in SOURCE_SUFFIXES
                    and "thumbnail" in (asset.get("roles") or [])):
                out.append((jf, key, href))
    return out


def retarget_links(converted: set[Path]) -> int:
    """Point any link href at the WebP that replaced its original.

    Two vro catalogs carry a rel=preview link duplicating their thumbnail
    asset. Converting only assets would leave those links dangling, so this
    sweeps every JSON for links resolving to a file we just replaced.
    Returns the number of links rewritten.
    """
    n = 0
    for jf in sorted(CATALOG.rglob("*.json")):
        if ".portolan" in jf.parts or "styles" in jf.parts:
            continue
        try:
            doc = json.loads(jf.read_text())
        except json.JSONDecodeError:
            continue
        if not isinstance(doc, dict):
            continue
        touched = False
        for link in doc.get("links") or []:
            if not isinstance(link, dict):
                continue
            href = str(link.get("href", ""))
            if href.startswith("http") or Path(href).suffix.lower() not in SOURCE_SUFFIXES:
                continue
            if (jf.parent / href).resolve() not in converted:
                continue
            link["href"] = webp_href(href)
            if "type" in link:
                link["type"] = "image/webp"
            touched = True
            n += 1
        if touched:
            jf.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
    return n


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--confirm", action="store_true",
                    help="write the WebP files, rewrite JSON, delete the originals")
    args = ap.parse_args(argv)

    if not shutil.which("cwebp"):
        print("error: cwebp not found. Install with: brew install webp", file=sys.stderr)
        return 1

    targets = find_targets()
    if not targets:
        print("Nothing to do: no non-WebP thumbnail assets found.")
        return 0

    by_json: dict[Path, list[tuple[str, str]]] = {}
    for jf, key, href in targets:
        by_json.setdefault(jf, []).append((key, href))

    if not args.confirm:
        print(f"DRYRUN {len(targets)} thumbnail assets across {len(by_json)} JSON files")
        for jf, items in list(by_json.items())[:5]:
            for key, href in items:
                print(f"  {jf.relative_to(CATALOG)}: {key} {href} -> {webp_href(href)}")
        print("  ... re-run with --confirm to convert")
        return 0

    total_before = total_after = 0
    converted: list[Path] = []
    for jf, items in by_json.items():
        doc = json.loads(jf.read_text())
        for key, href in items:
            src = (jf.parent / href).resolve()
            if not src.exists():
                print(f"error: {jf.relative_to(CATALOG)}: {key} -> missing {href}",
                      file=sys.stderr)
                return 1
            webp = src.with_suffix(".webp")
            before = src.stat().st_size
            after = encode(src, webp)
            total_before += before
            total_after += after
            if after > HARD_LIMIT:
                print(f"error: {webp.name} is {after} bytes, over the 50 KB limit",
                      file=sys.stderr)
                return 1
            doc["assets"][key]["href"] = webp_href(href)
            doc["assets"][key]["type"] = "image/webp"
            converted.append(src)
        # ensure_ascii=False keeps the Dutch titles and em-dashes as literal UTF-8,
        # so the diff is the href/type changes and nothing else.
        jf.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")

    relinked = retarget_links(set(converted))

    for src in converted:
        src.unlink()

    print(f"Done: {len(converted)} thumbnails, {len(by_json)} JSON files rewritten, "
          f"{relinked} link(s) retargeted. "
          f"{total_before / 1e6:.1f} MB -> {total_after / 1e6:.1f} MB")
    return 0


if __name__ == "__main__":
    sys.exit(main())

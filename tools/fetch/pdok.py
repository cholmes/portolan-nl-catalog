#!/usr/bin/env python3
"""Discover and download PDOK datasets from their Atom feeds.

PDOK publishes each dataset as an Atom feed of download links, which is what
vro/scripts/download_rest.sh walked for one hardcoded BRO feed. This does it
for any feed.

The feeds are two-level: the index feed lists datasets, and each entry links to
a per-dataset feed whose entries are the actual downloads. `list` follows that
second level so you see files, not feeds.

Downloads land in staging/<name>/data/, which is gitignored -- source files are
never committed and never published.

Usage:
  python3 tools/fetch/pdok.py list  https://service.pdok.nl/tno/bro-bodemkaart/atom/index.xml
  python3 tools/fetch/pdok.py fetch https://service.pdok.nl/tno/bro-bodemkaart/atom/index.xml \\
      --into bodemkaart
"""
from __future__ import annotations
import argparse
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.lib import paths

ATOM = "{http://www.w3.org/2005/Atom}"
# Anything else is a feed to follow, not a file to download.
DATA_SUFFIXES = (".gpkg", ".zip", ".gml", ".gz", ".csv", ".json", ".tif", ".xml")


def _read(url: str) -> ET.Element:
    with urllib.request.urlopen(url, timeout=60) as r:
        return ET.fromstring(r.read())


def _links(feed_url: str) -> list[tuple[str, str]]:
    """(title, absolute href) for every link in every entry of one feed."""
    out = []
    for e in _read(feed_url).iter(f"{ATOM}entry"):
        title = (e.findtext(f"{ATOM}title") or "").strip()
        for link in e.iter(f"{ATOM}link"):
            href = link.get("href")
            if href:
                out.append((title, urllib.parse.urljoin(feed_url, href)))
    return out


def downloads(feed_url: str) -> list[tuple[str, str]]:
    """(title, href) for every downloadable file reachable from a feed.

    Follows one level of sub-feed, which is how PDOK structures these: the
    index lists datasets, each dataset feed lists its files.
    """
    out, seen = [], set()
    for title, href in _links(feed_url):
        if href.lower().endswith(DATA_SUFFIXES) and not href.lower().endswith(".xml"):
            if href not in seen:
                seen.add(href)
                out.append((title, href))
        elif href.lower().endswith(".xml") and href != feed_url:
            try:
                sub = _links(href)
            except Exception as e:                      # a dead sub-feed is not fatal
                print(f"  warning: {href}: {e}", file=sys.stderr)
                continue
            for stitle, shref in sub:
                if shref.lower().endswith(DATA_SUFFIXES) and not shref.lower().endswith(".xml"):
                    if shref not in seen:
                        seen.add(shref)
                        out.append((stitle or title, shref))
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("action", choices=["list", "fetch"])
    ap.add_argument("feed")
    ap.add_argument("--into", help="staging collection name (fetch only)")
    args = ap.parse_args(argv)

    found = downloads(args.feed)
    if not found:
        print(f"error: no downloadable entries found in {args.feed}", file=sys.stderr)
        return 1

    if args.action == "list":
        for title, href in found:
            print(f"{title}\t{href}")
        print(f"\n{len(found)} download(s)", file=sys.stderr)
        return 0

    if not args.into:
        print("error: fetch needs --into <staging collection name>", file=sys.stderr)
        return 2
    dest = paths.REPO / "staging" / args.into / "data"
    dest.mkdir(parents=True, exist_ok=True)
    for _, href in found:
        name = href.rsplit("/", 1)[-1].split("?")[0] or "download"
        target = dest / name
        if target.exists():
            print(f"skip  {name} (already present)")
            continue
        print(f"fetch {name}")
        urllib.request.urlretrieve(href, target)
    print(f"Done: {len(found)} entries into {dest.relative_to(paths.REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

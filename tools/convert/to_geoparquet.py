#!/usr/bin/env python3
"""Source vector file -> GeoParquet -> PMTiles, via gpio.

gpio already produces cloud-native GeoParquet (zstd, bbox covering, Hilbert
ordered) and PMTiles with this catalog's conventions. This wrapper exists so
the exact flags this catalog is built with live in the repo instead of in shell
history.

Outputs land next to the source under staging/, never in catalog/ -- data files
do not enter the published tree.

Flags verified against gpio as installed:
  gpio convert geoparquet INPUT OUTPUT --layer L --compression zstd
  gpio pmtiles create INPUT OUTPUT --layer L --max-zoom N

Usage:
  python3 tools/convert/to_geoparquet.py staging/bodemkaart/data/soilarea.gpkg \\
      --layer soilarea --max-zoom 12
"""
from __future__ import annotations
import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd))
    subprocess.run(cmd, check=True)


def gpkg_layers(path: Path) -> list[str] | None:
    """Layer names in a GeoPackage, or None if it is not one / cannot be read."""
    if path.suffix.lower() != ".gpkg":
        return None
    import sqlite3
    try:
        with sqlite3.connect(f"file:{path}?mode=ro", uri=True) as c:
            return [r[0] for r in c.execute("SELECT table_name FROM gpkg_contents")]
    except sqlite3.Error:
        return None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source", type=Path)
    ap.add_argument("--layer", help="layer inside the source, and the output stem")
    ap.add_argument("--max-zoom", type=int, default=12)
    ap.add_argument("--compression", default="zstd",
                    choices=["zstd", "gzip", "brotli", "lz4", "snappy", "uncompressed"])
    ap.add_argument("--no-pmtiles", action="store_true")
    ap.add_argument("--force", action="store_true", help="overwrite existing outputs")
    args = ap.parse_args(argv)

    if not shutil.which("gpio"):
        print("error: gpio not found on PATH", file=sys.stderr)
        return 1
    if not args.source.exists():
        print(f"error: {args.source} does not exist", file=sys.stderr)
        return 1

    # gpio segfaults on a --layer that is not in the source rather than erroring,
    # which is a confusing way to learn you typed the name wrong.
    layers = gpkg_layers(args.source)
    if args.layer and layers is not None and args.layer not in layers:
        print(f"error: {args.source.name} has no layer {args.layer!r}. "
              f"Available: {', '.join(layers) or '(none)'}", file=sys.stderr)
        return 1

    stem = args.layer or args.source.stem
    parquet = args.source.parent / f"{stem}.parquet"
    if parquet.exists() and not args.force:
        print(f"error: {parquet} exists; pass --force to overwrite", file=sys.stderr)
        return 1

    cmd = ["gpio", "convert", "geoparquet", str(args.source), str(parquet),
           "--compression", args.compression]
    if args.layer:
        cmd += ["--layer", args.layer]
    run(cmd)

    if not args.no_pmtiles:
        if not shutil.which("tippecanoe"):
            print("error: gpio pmtiles needs tippecanoe (brew install tippecanoe)",
                  file=sys.stderr)
            return 1
        pmtiles = parquet.with_suffix(".pmtiles")
        pm = ["gpio", "pmtiles", "create", str(parquet), str(pmtiles),
              "--layer", stem, "--max-zoom", str(args.max_zoom)]
        if args.force:
            pm.append("--force")
        run(pm)

    print(f"Done: {parquet}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

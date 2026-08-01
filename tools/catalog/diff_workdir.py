#!/usr/bin/env python3
"""Report drift between this repo's catalog/ and the data working directory.

The working directory (/Users/cholmes/geodata/portolan-nl by default) was
deliberately left in place, so two metadata trees exist and both can publish to
the same S3 prefix. This reports where they disagree. It is advisory: it never
writes anything, and it is not run in CI because the working directory is not
available there. Run it before publishing.

Known, expected differences are excluded by default:

- Data files, which this repo never holds.
- The KD-tree partition directories under kadaster/inspire_buildings. Portolan
  wrote 512 kdtree_cell=* dirs of item JSON there whose assets were never
  uploaded, so the repo carries the collection without them.
- Working-directory-only scaffolding: scripts/, _downloads/, to-import/,
  context/, .claude/. These moved to tools/, staging/ and docs/, all outside
  catalog/ and so outside this comparison.
- Repo-level config that is deliberately never published: .env, CLAUDE.md.
- Editor and tool temp files (*-journal).

Everything else is reported, including workdir orphans such as the stray
top-level brp_gewaspercelen/versions.json -- publishing from the working
directory would push those to S3, which is exactly what this should surface.

Usage:
  python3 tools/catalog/diff_workdir.py
  PORTOLAN_NL_WORKDIR=/some/path python3 tools/catalog/diff_workdir.py
"""
from __future__ import annotations
import argparse
import hashlib
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "catalog"
DEFAULT_WORKDIR = Path("/Users/cholmes/geodata/portolan-nl")

DATA_SUFFIXES = {".parquet", ".pmtiles", ".gpkg", ".tif", ".zip", ".zarr"}
EXCLUDED_PARTS = {"_downloads", "scripts", "to-import", "context", ".claude", ".portolan"}
EXCLUDED_NAMES = {".DS_Store", "download.log", ".env", "CLAUDE.md"}
EXCLUDED_PREFIXES = ("kdtree_cell=",)
EXCLUDED_SUFFIXES = ("-journal",)


def digest(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def index(base: Path) -> dict[str, Path]:
    """Relative posix path -> file, for comparable metadata files only."""
    out: dict[str, Path] = {}
    if not base.is_dir():
        return out
    for p in base.rglob("*"):
        if not p.is_file():
            continue
        if p.suffix in DATA_SUFFIXES or p.name in EXCLUDED_NAMES:
            continue
        if p.name.endswith(EXCLUDED_SUFFIXES):
            continue
        rel_parts = p.relative_to(base).parts
        if EXCLUDED_PARTS.intersection(rel_parts):
            continue
        if any(part.startswith(EXCLUDED_PREFIXES) for part in rel_parts):
            continue
        out[p.relative_to(base).as_posix()] = p
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--workdir", type=Path,
                    default=Path(os.environ.get("PORTOLAN_NL_WORKDIR", DEFAULT_WORKDIR)))
    ap.add_argument("--summary", action="store_true",
                    help="counts only, no per-file lines")
    args = ap.parse_args(argv)

    if not args.workdir.is_dir():
        print(f"error: working directory not found: {args.workdir}", file=sys.stderr)
        return 2

    repo = index(CATALOG)
    work = index(args.workdir)

    only_repo = sorted(set(repo) - set(work))
    only_work = sorted(set(work) - set(repo))
    differing = sorted(r for r in set(repo) & set(work)
                       if repo[r].stat().st_size != work[r].stat().st_size
                       or digest(repo[r]) != digest(work[r]))

    if not args.summary:
        for r in only_repo:
            print(f"REPO-ONLY  {r}")
        for r in only_work:
            print(f"WORK-ONLY  {r}")
        for r in differing:
            print(f"DIFFERS    {r}")
        print()

    total = len(only_repo) + len(only_work) + len(differing)
    print(f"{len(repo)} repo files, {len(work)} workdir files, {total} difference(s): "
          f"{len(only_repo)} repo-only, {len(only_work)} workdir-only, "
          f"{len(differing)} differing.")
    if total:
        print("Large differences are expected: the repo has diverged from the working "
              "directory across three phases -- WebP thumbnails, the git extension, "
              "regenerated docs, and the Portolan 0.1 conformance pass (AGENTS.md, "
              "providers, schema URIs, no self links). The repo is the current one. "
              "Publishing from the working directory would undo all of it.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

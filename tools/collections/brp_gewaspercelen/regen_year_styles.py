#!/usr/bin/env python3
"""Regenerate per-year MapLibre style files from the base styles in styles/.

The base styles in styles/*.json are the single source of truth. They point at
the collection-level (latest year) PMTiles. This script copies each base style
into YYYY/styles/ and rewrites the source URL to point at that year's PMTiles
file (sibling of the year directory).

Run this after editing any base style, or after adding a new year.
"""

import json
import re
from pathlib import Path

YEARS = list(range(2009, 2026))  # 2009–2025, inclusive

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.lib import paths

ROOT = paths.CATALOG / "rvo" / "brp_gewaspercelen"
BASE_DIR = ROOT / "styles"

BASE_STYLES = ["default.json", "by-category.json", "by-crop.json", "landscape-elements.json"]


def regen_for_year(year: int) -> None:
    out_dir = ROOT / str(year) / "styles"
    out_dir.mkdir(parents=True, exist_ok=True)
    target_url = f"pmtiles://../brp_gewaspercelen_{year}.pmtiles"

    for name in BASE_STYLES:
        base = json.loads((BASE_DIR / name).read_text())
        base["sources"]["data"]["url"] = target_url
        original_name = base.get("name", name)
        base["name"] = re.sub(r"\s*—.*$", "", original_name) + f" — {year}" \
            if "—" in original_name else f"{original_name} ({year})"
        (out_dir / name).write_text(json.dumps(base, indent=2, ensure_ascii=False) + "\n")
        print(f"  wrote {out_dir.relative_to(ROOT)}/{name}")


def main() -> None:
    for year in YEARS:
        print(f"year {year}:")
        regen_for_year(year)


if __name__ == "__main__":
    main()

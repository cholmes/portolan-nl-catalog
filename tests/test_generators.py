"""Regenerating the catalog reproduces exactly what is committed.

This is the acceptance test for the phase 2 refactor: extract shared logic into
tools/lib/, re-run the generators, and require byte-identical output. A refactor
that changes a single byte fails here.

Only generators that need no data files run. The repo holds no parquet, so
make_collections, make_styles_thumbnails, make_extra_styles and
make_point_legends cannot run here; they are gated by
tools/catalog/regen_check.sh against the working directory instead.

The generators write into catalog/ in place, so this copies catalog/ to a temp
tree, points the generators at the copy via $PORTOLAN_NL_CATALOG, regenerates
there, and diffs. The real catalog/ is never touched.

Run: python3 tests/test_generators.py
"""
import filecmp
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CATALOG = REPO / "catalog"

# (script, what it regenerates) -- data-free only.
GENERATORS = [
    ("tools/catalog/make_catalogs.py", "vro subcatalog catalog.json"),
    ("tools/catalog/make_readmes.py", "vro README.md"),
    ("tools/catalog/make_llms.py", "vro llms.txt"),
    ("tools/collections/brp_gewaspercelen/generate_items.py", "brp item JSON"),
    ("tools/collections/brp_gewaspercelen/generate_year_docs.py", "brp year docs"),
    ("tools/collections/brp_gewaspercelen/regen_year_styles.py", "brp per-year styles"),
]


def diff_trees(a: Path, b: Path) -> list[str]:
    """Every relative path whose bytes differ, or that exists on one side only."""
    out = []
    names = {p.relative_to(a).as_posix() for p in a.rglob("*") if p.is_file()}
    names |= {p.relative_to(b).as_posix() for p in b.rglob("*") if p.is_file()}
    for rel in sorted(names):
        pa, pb = a / rel, b / rel
        if not pa.is_file():
            out.append(f"disappeared on regeneration: {rel}")
        elif not pb.is_file():
            out.append(f"only after regeneration: {rel}")
        elif not filecmp.cmp(pa, pb, shallow=False):
            out.append(f"differs: {rel}")
    return out


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        work = Path(td) / "catalog"
        shutil.copytree(CATALOG, work)
        env = {**os.environ, "PORTOLAN_NL_CATALOG": str(work)}
        for script, what in GENERATORS:
            r = subprocess.run([sys.executable, str(REPO / script)],
                               cwd=REPO, env=env, capture_output=True, text=True)
            if r.returncode != 0:
                print(f"FAIL {script} exited {r.returncode} ({what})")
                print(r.stderr[-2000:])
                return 1
        diffs = diff_trees(work, CATALOG)

    if diffs:
        print("\n".join(f"FAIL {d}" for d in diffs))
        print(f"\n{len(diffs)} file(s) changed by regeneration; the generators and the "
              f"committed catalog disagree")
        return 1
    print(f"OK: {len(GENERATORS)} generators regenerate the committed catalog byte-for-byte")
    return 0


if __name__ == "__main__":
    sys.exit(main())

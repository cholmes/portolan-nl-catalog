# Phase 2 — Refactor `tools/` Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extract the shared logic duplicated across the eleven relocated generator scripts into `tools/lib/`, behind a golden-output gate that proves the refactor changed nothing.

**Architecture:** Six `lib/` modules, each justified by two or more scripts that duplicate it today. The gate is `tests/test_generators.py`: it copies `catalog/` to a temp tree, re-runs every generator that needs no data files, and requires the result to be byte-identical to what is committed. Extraction proceeds one module at a time, and the gate runs after each.

**Tech Stack:** Python 3.11 stdlib for the lib modules and the gate. The four data-reading generators additionally need `pyarrow`, `geopandas`, `duckdb`, `matplotlib`, `contextily` — none of which CI installs.

## Global Constraints

- **Byte-identical is the gate.** After Task 2, `python3 tests/test_generators.py` must report an empty diff. Any extraction that changes output is wrong unless the change is explicitly called out in this plan.
- **Never regress phase 1.** Every thumbnail href in `catalog/` is `.webp` with type `image/webp`, enforced by `tests/test_thumbnails.py`. `make_catalogs.py` currently emits `.png` and must be fixed, not worked around.
- **JSON writing is standardized:** `json.dumps(doc, indent=2, ensure_ascii=False) + "\n"`. Trailing newline, UTF-8 literals. This is what phase 1 normalized the whole catalog to.
- **The repo holds no data.** Parquet and PMTiles live only in the working directory. Any generator that reads them takes its data root from `PORTOLAN_NL_WORKDIR` (default `/Users/cholmes/geodata/portolan-nl`) and is excluded from CI.
- **AWS profile is `default`.**
- STAC terminology: catalog / collection / item / asset. Never "dataset".

## Measured starting state (2026-08-01)

Established by running the three data-free `vro` generators against `catalog/` with `ROOT` overridden, then `git diff`:

| Fact | Value |
|---|---|
| Generator scripts | 11 (~1 800 lines), plus `publish.py`, `make_thumbnails.py`, `diff_workdir.py` written in phase 1 |
| Run without data files | 7 of 11 |
| Require working-directory parquet | 4: `make_collections`, `make_styles_thumbnails`, `make_extra_styles`, `make_point_legends` |
| Diff from regenerating the 3 data-free `vro` generators | 18 files, +28 / −10 |

The −10 and +28 have exactly three causes, all understood:

1. **A real staleness bug in the published catalog (+28).** `README.md` and `llms.txt` in nine `vro` collections list fewer styles than `collection.json` actually declares. Styles were added later by `make_extra_styles.py` / `make_point_legends.py` and the docs were never regenerated. Eighteen style entries are missing from the live catalog. Regenerating fixes this; it is a deliverable, not a regression.
2. **A phase-1 regression in `make_catalogs.py` (−8).** It writes `./thumbnail.png` / `image/png` in both the `preview` link and the `thumbnail` asset of `vro/bodemkaart/catalog.json` and `vro/geomorfologische_kaart/catalog.json`. Re-running it today would undo the WebP conversion and fail `tests/test_thumbnails.py`.
3. **Trailing newline (−2).** `make_catalogs.py` uses `json.dump` with no trailing newline; phase 1 normalized every JSON file to end in one.

## File Structure

```
tools/
├── lib/
│   ├── __init__.py
│   ├── paths.py        # repo root, catalog root, data root, public base URLs
│   ├── stac.py         # catalog/collection/item scaffolding, link + asset builders
│   ├── docs.py         # README.md / llms.txt generation from collection.json
│   ├── styles.py       # Mapbox GL v8 styles, data-driven classes, point-legend workaround
│   ├── geoparquet.py   # geometry type, CRS, columns, bbox, row count from a parquet
│   └── images.py       # matplotlib/Positron thumbnail render + WebP encode
├── fetch/
│   ├── pdok.py         # PDOK Atom-feed discovery and bulk download
│   └── pdok_download.sh  (kept; pdok.py supersedes it)
├── convert/
│   └── to_geoparquet.py  # gpio wrappers: source → GeoParquet → PMTiles
└── catalog/
    ├── publish.py, make_thumbnails.py, diff_workdir.py   (phase 1, untouched)
    └── make_*.py                                          (refactored here)
tests/
└── test_generators.py  # the golden gate
```

---

### Task 1: `tools/lib/paths.py` and rewiring `ROOT`

Every script computes its own root by walking up from `__file__`, which resolved correctly at its old depth in the working directory and does not at its new depth in the repo. This task fixes that and nothing else.

**Files:**
- Create: `tools/lib/__init__.py`, `tools/lib/paths.py`
- Modify: all 7 data-free generators plus the 4 data-reading ones — the `ROOT`/`DATA`/`SRC` lines only
- Test: manual — run the 3 data-free `vro` generators and confirm the diff is exactly the 18 files above

**Interfaces:**
- Produces: `tools.lib.paths.REPO`, `.CATALOG`, `.DATA_ROOT`, `.DATA_BASE`, `.SRC_BASE`, `.publish_manifest()`

- [ ] **Step 1: Write `tools/lib/paths.py`**

```python
"""Where things live. Every generator imports its roots from here.

Three roots, deliberately distinct:

- REPO     the git repo. Tooling, tests, docs.
- CATALOG  REPO/catalog -- the published tree. Generators write here.
- DATA_ROOT the working directory that still holds the parquet and PMTiles.
            The repo holds no data, so any generator that reads a data file
            reads it from here. Overridable with $PORTOLAN_NL_WORKDIR.

Public URL bases are read from catalog.publish.yaml rather than hardcoded, so
the publisher and the generators cannot disagree about where the catalog lives.
"""
from __future__ import annotations
import os
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CATALOG = REPO / "catalog"
DATA_ROOT = Path(os.environ.get("PORTOLAN_NL_WORKDIR", "/Users/cholmes/geodata/portolan-nl"))


def publish_manifest() -> dict:
    """Parse catalog.publish.yaml without a YAML dependency.

    The file is a flat key: value map with # comments; a real parser would be
    one more thing for CI to install for no benefit.
    """
    out = {}
    for line in (REPO / "catalog.publish.yaml").read_text().splitlines():
        line = line.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        k, v = line.split(":", 1)
        out[k.strip()] = v.strip()
    return out


_M = publish_manifest()
DATA_BASE = _M["public_base"].rstrip("/")          # https://data.source.coop/cholmes/portolan-nl
SRC_BASE = "https://source.coop/cholmes/portolan-nl"  # the HTML front end, for describedby links


def data_file(rel: str) -> Path:
    """Absolute path to a data file, e.g. data_file("vro/wandonderzoek/wandonderzoek.parquet")."""
    return DATA_ROOT / rel
```

- [ ] **Step 2: Verify the roots resolve**

```bash
cd ~/repos/portolan-nl-catalog
python3 -c "
from tools.lib import paths
print(paths.REPO); print(paths.CATALOG); print(paths.DATA_ROOT)
print(paths.DATA_BASE); print(paths.CATALOG.is_dir(), paths.DATA_ROOT.is_dir())
"
```
Expected: the repo path, `.../catalog`, `/Users/cholmes/geodata/portolan-nl`, `https://data.source.coop/cholmes/portolan-nl`, `True True`.

Create an empty `tools/lib/__init__.py`. `tools/` and `tools/catalog/` need `__init__.py` too for `from tools.lib import paths` to resolve — add empty ones.

- [ ] **Step 3: Rewire the seven `vro`/`brp` generators**

In each of `tools/catalog/make_{catalogs,collections,llms,readmes,extra_styles,point_legends,styles_thumbnails}.py`, replace:

```python
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
```

with:

```python
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from tools.lib import paths

ROOT = str(paths.CATALOG)
```

`sys.path` manipulation is deliberate: these are scripts run directly (`python3 tools/catalog/make_llms.py`), not an installed package, and requiring `python3 -m tools.catalog.make_llms` would change how every one of them is invoked.

Where a script has `DATA_BASE = "https://data.source.coop/cholmes/portolan-nl"` or `DATA = ...`, replace the literal with `paths.DATA_BASE`. Confirm the value is identical first — a changed URL would show up as diff noise later.

- [ ] **Step 4: Rewire the four data-reading generators' parquet paths**

In `make_collections.py`, `make_styles_thumbnails.py`, `make_extra_styles.py`, `make_point_legends.py`, every `os.path.join(cdir, f"{layer}.parquet")` resolves under `ROOT`, which is now `catalog/` — where no parquet exists. Point them at the data root instead. In `make_collections.py`:

```python
def build(path, cfg):
    cdir = os.path.join(ROOT, "vro", path)                       # writes here (catalog/)
    ddir = str(paths.data_file(os.path.join("vro", path)))       # reads here (working dir)
    layer = cfg["layer"]
    parquet = os.path.join(ddir, f"{layer}.parquet")
```

Apply the same `cdir` (write) / `ddir` (read) split in the other three. Leave all other logic alone.

- [ ] **Step 5: Rewire the three `brp_gewaspercelen` scripts**

They use `ROOT = Path(__file__).resolve().parent.parent`, which used to mean the collection directory `rvo/brp_gewaspercelen/`. Replace with:

```python
from tools.lib import paths
ROOT = paths.CATALOG / "rvo" / "brp_gewaspercelen"
```
(with the same `sys.path` preamble as Step 3).

- [ ] **Step 6: Run the data-free generators and confirm the expected diff**

```bash
cd ~/repos/portolan-nl-catalog
git status --porcelain | wc -l          # must be 0 before starting
python3 tools/catalog/make_catalogs.py
python3 tools/catalog/make_readmes.py
python3 tools/catalog/make_llms.py
python3 tools/collections/brp_gewaspercelen/generate_items.py
python3 tools/collections/brp_gewaspercelen/generate_year_docs.py
python3 tools/collections/brp_gewaspercelen/regen_year_styles.py
git diff --stat | tail -1
```

Expected: the 18 `vro` files from the measured baseline, plus whatever the three `brp` scripts produce. **If the `brp` scripts produce a diff, stop and inspect it before continuing** — they were not part of the baseline measurement, so their drift is unknown. Record what you find in the commit message. Categorize every changed line as one of: the missing-styles fix, the thumbnail regression, the trailing newline, or something new. Anything in the fourth category is a finding that needs its own decision.

- [ ] **Step 7: Restore and commit**

```bash
cd ~/repos/portolan-nl-catalog
git checkout -- catalog
git add tools/ && git commit -m "Rewire generator roots through tools/lib/paths.py

Each script computed its own root by walking up from __file__, which resolved
at its old depth inside the working directory and not at its new depth here.
paths.py makes the three roots explicit and distinct: the repo, the published
catalog/ tree that generators write, and the working directory that still holds
the parquet they read."
```

---

### Task 2: Fix the generators' output, and ship the docs they fix

The gate for the whole phase is "regenerate → empty diff". That cannot hold while `make_catalogs.py` reverts thumbnails and the committed docs under-report styles. This task makes it hold.

**Files:**
- Modify: `tools/catalog/make_catalogs.py`
- Modify: 18 files under `catalog/vro/` (regenerated)
- Test: `tests/test_thumbnails.py`, `tests/test_links.py`, `tests/test_stac_valid.py`

**Interfaces:**
- Consumes: `tools.lib.paths` from Task 1.
- Produces: a catalog tree that regenerates to itself.

- [ ] **Step 1: Fix the thumbnail regression in `make_catalogs.py`**

Find the two places emitting the thumbnail — one `preview` link, one `thumbnail` asset — and change `./thumbnail.png` → `./thumbnail.webp` and `image/png` → `image/webp`.

```python
{"rel": "preview", "href": "./thumbnail.webp", "type": "image/webp",
 "title": "Thumbnail (PDOK preview)"},
```
```python
"thumbnail": {"href": "./thumbnail.webp", "type": "image/webp",
              "title": "Thumbnail (PDOK preview)", "roles": ["thumbnail"]},
```

- [ ] **Step 2: Fix the trailing newline**

Replace every `json.dump(obj, f, indent=2, ...)` in `make_catalogs.py` with the standardized form:

```python
f.write(json.dumps(obj, indent=2, ensure_ascii=False) + "\n")
```

Do the same in `make_collections.py`, `make_extra_styles.py`, `make_point_legends.py`, and `generate_items.py` — any generator using `json.dump` to a file handle. This is the phase-1 convention and it is what the committed files hold.

- [ ] **Step 3: Regenerate and inspect**

```bash
cd ~/repos/portolan-nl-catalog
python3 tools/catalog/make_catalogs.py
python3 tools/catalog/make_readmes.py
python3 tools/catalog/make_llms.py
git diff --stat | tail -1
git diff | grep '^-' | grep -v '^---' | sort | uniq -c
```

Expected: 16 files changed, +28 / −0. The removals are gone (thumbnail regression and newline both fixed); only the 18 missing style listings are added. **If any line is still removed, the fix is incomplete — do not proceed.**

- [ ] **Step 4: Verify the additions are real**

Spot-check that a style the docs now list actually exists as an asset and as a file:

```bash
cd ~/repos/portolan-nl-catalog
python3 -c "
import json
d = json.load(open('catalog/vro/bodemkaart/soilarea/collection.json'))
print('asset present:', 'styles/by-collection' in d['assets'])
print('href:', d['assets']['styles/by-collection']['href'])
"
ls catalog/vro/bodemkaart/soilarea/styles/
```
Expected: `True`, `./styles/by-collection.json`, and the file listed. This confirms the docs were stale and the collection was right — not the reverse.

- [ ] **Step 5: Run the full suite**

```bash
cd ~/repos/portolan-nl-catalog
for t in publish links git_ext thumbnails stac_valid; do
  echo "=== $t ==="; python3 tests/test_$t.py || echo "FAILED: $t"
done
```
Expected: five `OK:` lines. `test_thumbnails.py` is the one that would catch a botched Step 1.

- [ ] **Step 6: Commit**

```bash
cd ~/repos/portolan-nl-catalog
git add tools/catalog/make_catalogs.py catalog/vro
git commit -m "Regenerate vro docs; stop make_catalogs reverting WebP thumbnails

The committed README.md and llms.txt in nine vro collections listed fewer
styles than collection.json declares -- styles added later by make_extra_styles
and make_point_legends, with the docs never regenerated. Eighteen style entries
were missing from the published catalog.

make_catalogs.py still emitted ./thumbnail.png, so re-running it would have
undone phase 1's WebP conversion. Fixed, along with the missing trailing
newline, so that regenerating now reproduces the committed tree exactly."
```

---

### Task 3: `tests/test_generators.py` — the golden gate

**Files:**
- Create: `tests/test_generators.py`
- Modify: `.github/workflows/ci.yml`

**Interfaces:**
- Consumes: the generators, `tools.lib.paths`.
- Produces: the acceptance test every later task in this plan runs.

- [ ] **Step 1: Write the gate**

```python
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
import filecmp, os, shutil, subprocess, sys, tempfile
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
            out.append(f"only after regeneration: {rel}")
        elif not pb.is_file():
            out.append(f"disappeared on regeneration: {rel}")
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
        print(f"\n{len(diffs)} file(s) changed by regeneration; the refactor is not "
              f"output-preserving")
        return 1
    print(f"OK: {len(GENERATORS)} generators regenerate the committed catalog byte-for-byte")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Teach `paths.py` about the override**

The gate needs the generators to write somewhere else. Add to `tools/lib/paths.py`, replacing the plain `CATALOG` assignment:

```python
# tests/test_generators.py points this at a temp copy so regeneration can be
# diffed without touching the real tree.
CATALOG = Path(os.environ.get("PORTOLAN_NL_CATALOG", REPO / "catalog"))
```

- [ ] **Step 3: Run it — it must pass**

```bash
cd ~/repos/portolan-nl-catalog
python3 tests/test_generators.py
```
Expected: `OK: 6 generators regenerate the committed catalog byte-for-byte`.

If it fails, Task 2 is incomplete: fix the generator, regenerate, commit the catalog change, and re-run. Do not weaken the test.

- [ ] **Step 4: Prove the gate actually bites**

A gate that cannot fail is worthless. Break something on purpose and confirm it is caught:

```bash
cd ~/repos/portolan-nl-catalog
python3 - <<'EOF'
from pathlib import Path
p = Path("tools/catalog/make_readmes.py")
t = p.read_text()
p.write_text(t.replace("## Styles", "## Styles "))   # one trailing space
EOF
python3 tests/test_generators.py; echo "exit=$?"
git checkout -- tools/catalog/make_readmes.py
python3 tests/test_generators.py; echo "exit=$?"
```
Expected: first run fails with `FAIL differs: vro/...` lines and `exit=1`; second run is `OK` with `exit=0`.

- [ ] **Step 5: Add to CI**

In `.github/workflows/ci.yml`, add to the `Run catalog tests` step, after `test_thumbnails.py`:

```yaml
          python3 tests/test_generators.py
```

- [ ] **Step 6: Commit**

```bash
cd ~/repos/portolan-nl-catalog
git add tests/test_generators.py tools/lib/paths.py .github/workflows/ci.yml
git commit -m "Add the golden-output gate for the tools/ refactor

Copies catalog/ to a temp tree, regenerates it with every data-free generator,
and requires byte-identical output. This is the acceptance test for every
extraction in phase 2. Verified it fails on a one-character change."
```

---

### Task 4: Extract `tools/lib/stac.py`

Duplicated today in `make_catalogs.py`, `make_collections.py`, `generate_items.py`.

**Files:**
- Create: `tools/lib/stac.py`
- Modify: `tools/catalog/make_catalogs.py`, `tools/catalog/make_collections.py`, `tools/collections/brp_gewaspercelen/generate_items.py`
- Test: `tests/test_generators.py`

**Interfaces:**
- Consumes: `tools.lib.paths`.
- Produces: `link()`, `asset()`, `root_link()`, `self_link()`, `parent_link()`, `write_json()`.

- [ ] **Step 1: Read the three scripts and list what they share**

```bash
cd ~/repos/portolan-nl-catalog
grep -n '"rel":' tools/catalog/make_catalogs.py tools/catalog/make_collections.py \
  tools/collections/brp_gewaspercelen/generate_items.py
```
Write down every distinct link shape. Only extract what appears in **two or more** of them — a helper with one caller is worse than the literal it replaced.

- [ ] **Step 2: Write `tools/lib/stac.py`**

```python
"""STAC scaffolding shared by the catalog, collection and item generators.

Only builders duplicated across two or more generators live here. Anything one
generator alone needs stays in that generator, where it is easier to read.

Every writer goes through write_json so the whole catalog keeps one JSON
convention: two-space indent, literal UTF-8 (the titles are Dutch), and a
trailing newline.
"""
from __future__ import annotations
import json
from pathlib import Path

from . import paths

ROOT_TITLE = "Portolan NL — Cloud-Native Dutch Geodata"


def write_json(path: Path | str, doc: dict) -> None:
    """The one way this catalog writes JSON."""
    Path(path).write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")


def link(rel: str, href: str, type: str | None = None, title: str | None = None, **extra) -> dict:
    """A STAC link. Key order is rel, href, type, title -- match the committed files."""
    out = {"rel": rel, "href": href}
    if type:
        out["type"] = type
    if title:
        out["title"] = title
    out.update(extra)
    return out


def root_link(depth: int) -> dict:
    """rel:root, relative to an object `depth` directories below catalog/."""
    return link("root", "../" * depth + "catalog.json", "application/json", ROOT_TITLE)


def parent_link(href: str = "../catalog.json") -> dict:
    return link("parent", href, "application/json")


def self_link(rel_path: str) -> dict:
    """rel:self as an absolute published URL, which is how this catalog spells it."""
    return link("self", f"{paths.DATA_BASE}/{rel_path}", "application/json")


def asset(href: str, type: str, title: str, roles: list[str], **extra) -> dict:
    out = {"href": href, "type": type, "title": title, "roles": roles}
    out.update(extra)
    return out


def thumbnail_asset(title: str = "Thumbnail (PDOK preview)", href: str = "./thumbnail.webp") -> dict:
    """Thumbnails are WebP under 50 KB; tests/test_thumbnails.py enforces it."""
    return asset(href, "image/webp", title, ["thumbnail"])
```

- [ ] **Step 3: Rewrite the three generators to use it, one at a time**

After each single generator is converted:

```bash
cd ~/repos/portolan-nl-catalog
python3 tests/test_generators.py
```
Expected: `OK`. If it fails, the extraction changed output — read the `FAIL differs:` lines, `git diff` the temp output, and fix the helper until the bytes match. Do not move to the next generator with a red gate.

`make_collections.py` is not covered by the gate (it needs parquet), so verify it separately with Task 8's `regen_check.sh` before committing.

- [ ] **Step 4: Commit**

```bash
cd ~/repos/portolan-nl-catalog
git add tools/
git commit -m "Extract tools/lib/stac.py

Link and asset builders duplicated across make_catalogs, make_collections and
generate_items, plus the single write_json convention. Output byte-identical."
```

---

### Task 5: Extract `tools/lib/docs.py`

Duplicated today in `make_readmes.py`, `make_llms.py`, `generate_year_docs.py`.

**Files:**
- Create: `tools/lib/docs.py`
- Modify: `tools/catalog/make_readmes.py`, `tools/catalog/make_llms.py`, `tools/collections/brp_gewaspercelen/generate_year_docs.py`
- Test: `tests/test_generators.py`

**Interfaces:**
- Consumes: `tools.lib.paths`.
- Produces: `styles_from(collection) -> list[tuple[str, str, str]]`, `parquet_url()`, `pmtiles_url()`, `md_table()`.

- [ ] **Step 1: Write `tools/lib/docs.py`**

```python
"""Prose generation shared by the README and llms.txt generators.

The style listing is the important one. Both generators enumerate a
collection's style assets, and both got it wrong the same way before phase 2:
they read a hand-maintained list instead of the collection's own assets, so
styles added later never appeared in the docs. Reading collection.json is the
single source of truth.
"""
from __future__ import annotations
from . import paths


def styles_from(collection: dict) -> list[tuple[str, str, str]]:
    """(asset_key, style_name, title) for each style asset, default first.

    Default first matches how the browser presents them and how portolan:styles
    is ordered in every collection that has one.
    """
    out = []
    for key, a in (collection.get("assets") or {}).items():
        if "style" not in (a.get("roles") or []):
            continue
        name = key.split("/", 1)[1] if "/" in key else key
        out.append((key, name, a.get("title", name)))
    out.sort(key=lambda t: (t[1] != "default", t[1]))
    return out


def parquet_url(rel_dir: str, layer: str) -> str:
    return f"{paths.DATA_BASE}/{rel_dir}/{layer}.parquet"


def pmtiles_url(rel_dir: str, layer: str) -> str:
    return f"{paths.DATA_BASE}/{rel_dir}/{layer}.pmtiles"


def md_table(header: list[str], rows: list[list[str]]) -> str:
    """A GitHub-flavored markdown table. Both generators build these by hand."""
    out = ["| " + " | ".join(header) + " |",
           "|" + "|".join("---" for _ in header) + "|"]
    out += ["| " + " | ".join(r) + " |" for r in rows]
    return "\n".join(out)
```

- [ ] **Step 2: Confirm the sort order before rewiring**

`styles_from` must reproduce the order the committed docs use. Check against a collection with several styles:

```bash
cd ~/repos/portolan-nl-catalog
python3 -c "
import json, sys; sys.path.insert(0, '.')
from tools.lib.docs import styles_from
d = json.load(open('catalog/vro/bodemkaart/soilarea/collection.json'))
print([n for _, n, _ in styles_from(d)])
print(d.get('portolan:styles'))
"
grep -n 'styles/' catalog/vro/bodemkaart/soilarea/README.md
```
Expected: the three lists agree on order. If they disagree, fix `styles_from` — the committed docs (as regenerated in Task 2) are the target.

- [ ] **Step 3: Rewire the three generators, running the gate after each**

```bash
python3 tests/test_generators.py
```
Expected `OK` after each. `md_table` may not fit every table verbatim; where a generator's table has a quirk the helper cannot reproduce, leave that call site alone rather than bending the helper.

- [ ] **Step 4: Commit**

```bash
cd ~/repos/portolan-nl-catalog
git add tools/
git commit -m "Extract tools/lib/docs.py

Style enumeration, published URLs and markdown tables shared by make_readmes,
make_llms and generate_year_docs. styles_from reads the collection's own style
assets, which is what stopped the docs from going stale. Output byte-identical."
```

---

### Task 6: Extract `tools/lib/styles.py`

Duplicated today in `make_styles_thumbnails.py`, `make_extra_styles.py`, `make_point_legends.py`, `regen_year_styles.py`.

**Files:**
- Create: `tools/lib/styles.py`
- Modify: the four style generators
- Test: `tests/test_generators.py` (covers `regen_year_styles` only), plus `regen_check.sh` from Task 8 for the other three

**Interfaces:**
- Consumes: `tools.lib.paths`.
- Produces: `pmtiles_source()`, `base_style()`, `categorical_paint()`, `point_legend_layers()`, `write_style()`.

- [ ] **Step 1: Find the shared shapes**

```bash
cd ~/repos/portolan-nl-catalog
grep -n 'pmtiles://\|"type": "vector"\|match\|circle-color\|fill-color' \
  tools/catalog/make_styles_thumbnails.py tools/catalog/make_extra_styles.py \
  tools/catalog/make_point_legends.py \
  tools/collections/brp_gewaspercelen/regen_year_styles.py | head -40
```

- [ ] **Step 2: Write `tools/lib/styles.py`**

```python
"""Mapbox GL v8 style construction, shared by the four style generators.

The point-legend workaround is the reason this module exists. MapLibre renders
no legend for a categorical circle-color match expression, so the generators
emit one invisible layer per class, each carrying the class name, purely so a
legend can be derived from the layer list. Three generators reimplemented that
trick; here it is once.
"""
from __future__ import annotations
import json
from pathlib import Path

from . import stac


def pmtiles_source(name: str, url: str | None = None) -> dict:
    """A vector source pointing at a sibling PMTiles file."""
    return {name: {"type": "vector", "url": url or f"pmtiles://../{name}.pmtiles"}}


def categorical_paint(field: str, classes: list[tuple[str, str]], fallback: str) -> list:
    """A Mapbox GL `match` expression: [match, [get, field], val, color, ..., fallback]."""
    expr = ["match", ["get", field]]
    for value, color in classes:
        expr += [value, color]
    expr.append(fallback)
    return expr


def point_legend_layers(source: str, source_layer: str, field: str,
                        classes: list[tuple[str, str]]) -> list[dict]:
    """One zero-radius layer per class, so a legend can be read off the layers.

    Purely a rendering workaround -- these draw nothing. See
    portolan-sdi/portolan-cli#489.
    """
    return [
        {"id": f"{source_layer}-legend-{i}", "type": "circle", "source": source,
         "source-layer": source_layer,
         "filter": ["==", ["get", field], value],
         "paint": {"circle-radius": 0, "circle-color": color},
         "metadata": {"legend:label": value}}
        for i, (value, color) in enumerate(classes)
    ]


def write_style(path: Path | str, style: dict) -> None:
    stac.write_json(path, style)
```

- [ ] **Step 3: Rewire `regen_year_styles.py` first**

It is the only one of the four the gate covers, so it is the one that proves the helpers are faithful.

```bash
cd ~/repos/portolan-nl-catalog
python3 tests/test_generators.py
```
Expected: `OK`.

- [ ] **Step 4: Rewire the other three, verifying against the working directory**

These need parquet and network basemap tiles. Verify with Task 8's script:

```bash
bash tools/catalog/regen_check.sh styles
```
Expected: no diff. If `contextily` cannot reach its basemap, that is an environment failure, not a refactor failure — say so explicitly rather than recording a pass.

- [ ] **Step 5: Commit**

```bash
cd ~/repos/portolan-nl-catalog
git add tools/
git commit -m "Extract tools/lib/styles.py

Vector source, categorical match expressions, and the invisible point-legend
layer workaround, all reimplemented in three or four generators. Output
byte-identical."
```

---

### Task 7: Extract `tools/lib/geoparquet.py` and `tools/lib/images.py`

Duplicated today in `make_collections.py` + `generate_items.py` (geoparquet) and `make_styles_thumbnails.py` + `make_extra_styles.py` (images).

**Files:**
- Create: `tools/lib/geoparquet.py`, `tools/lib/images.py`
- Modify: `make_collections.py`, `make_styles_thumbnails.py`, `make_extra_styles.py`, `generate_items.py`
- Test: `tools/catalog/regen_check.sh` (Task 8) — the gate cannot cover these

**Interfaces:**
- Consumes: `tools.lib.paths`, `tools.catalog.make_thumbnails.encode`.
- Produces: `geo_meta()`, `arrow_columns()`, `bounds_wgs84()`, `row_count()`; `render_thumbnail()`, `save_webp()`.

- [ ] **Step 1: Write `tools/lib/geoparquet.py`**

Lift `geo_meta` and `arrow_cols` from `make_collections.py` verbatim — they are already clean — and add the bounds/count pair that `make_collections.py` inlines:

```python
"""Facts read out of a GeoParquet file.

Two levels, deliberately: geo_meta and arrow_columns read only the Parquet
footer, which is cheap on a multi-gigabyte file; bounds_wgs84 reads the
geometry column and is not. Callers that need only the schema should not pay
for the reprojection.
"""
from __future__ import annotations
import json

import pyarrow.parquet as pq

_TYPE_MAP = {"int64": "int64", "int32": "int32", "double": "float64",
             "string": "string", "large_string": "string", "binary": "binary"}


def geo_meta(parquet) -> tuple[str, str, int | None]:
    """(primary_geometry_column, geometry_type, epsg) from the 'geo' footer key."""
    geo = json.loads(pq.read_metadata(parquet).metadata[b"geo"].decode())
    pc = geo["primary_column"]
    col = geo["columns"][pc]
    gtype = col.get("geometry_types", ["Unknown"])
    crs = col.get("crs") or {}
    cid = crs.get("id") if isinstance(crs, dict) else None
    epsg = int(cid["code"]) if cid and str(cid.get("authority", "")).upper() == "EPSG" else None
    return pc, (gtype[0] if gtype else "Unknown"), epsg


def arrow_columns(parquet) -> list[tuple[str, str]]:
    """(name, stac_table_type) for every column, in file order."""
    return [(f.name, _TYPE_MAP.get(str(f.type), str(f.type))) for f in pq.read_schema(parquet)]


def bounds_wgs84(parquet, fallback_epsg: int | None = None) -> tuple[tuple, int]:
    """((minx, miny, maxx, maxy) in EPSG:4326, feature_count). Reads the geometry."""
    import geopandas as gpd
    g = gpd.read_parquet(parquet)
    if g.crs is None:
        g.set_crs(fallback_epsg or 4258, inplace=True)
    return tuple(g.to_crs(4326).total_bounds), len(g)
```

- [ ] **Step 2: Write `tools/lib/images.py`**

This is the one module the spec allows to change behaviour: `make_styles_thumbnails.py` and `make_extra_styles.py` end in a bare `savefig` writing PNG, and every thumbnail in `catalog/` must be WebP under 50 KB.

```python
"""Thumbnail rendering, ending in WebP.

The renderers used to savefig a PNG. Phase 1 made every thumbnail in catalog/
WebP under 50 KB, enforced by tests/test_thumbnails.py, so rendering now ends
in the same encoder the conversion used -- otherwise the next regeneration
reintroduces PNGs and the test fails.
"""
from __future__ import annotations
import tempfile
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.catalog.make_thumbnails import encode, HARD_LIMIT


def save_webp(fig, dst: Path | str, dpi: int = 100) -> int:
    """Save a matplotlib figure straight to WebP. Returns bytes written.

    Routed through a temporary PNG because matplotlib has no WebP writer and
    cwebp is where the size guarantee lives.
    """
    dst = Path(dst)
    with tempfile.TemporaryDirectory() as td:
        png = Path(td) / "render.png"
        fig.savefig(png, dpi=dpi, bbox_inches="tight", pad_inches=0)
        size = encode(png, dst)
    if size > HARD_LIMIT:
        raise RuntimeError(f"{dst.name} is {size} bytes, over the {HARD_LIMIT} limit")
    return size
```

- [ ] **Step 3: Rewire, and check every `savefig` is gone**

```bash
cd ~/repos/portolan-nl-catalog
grep -rn 'savefig' tools/
```
Expected: matches only inside `tools/lib/images.py`. Any other match is a generator that still writes a PNG thumbnail directly.

- [ ] **Step 4: Verify against the working directory**

```bash
bash tools/catalog/regen_check.sh all
python3 tests/test_thumbnails.py
```
Expected: no metadata diff, and `OK: 393 thumbnail assets, all WebP and under 50 KB`. Thumbnail *bytes* will differ if a renderer is re-run — matplotlib output is not reproducible across versions — so `regen_check.sh` compares metadata and ignores image bytes. Note in the commit which images were regenerated.

- [ ] **Step 5: Commit**

```bash
cd ~/repos/portolan-nl-catalog
git add tools/
git commit -m "Extract tools/lib/geoparquet.py and tools/lib/images.py

geoparquet.py splits the cheap footer reads from the expensive geometry read.
images.py routes every renderer through the WebP encoder, so regenerating a
thumbnail can no longer reintroduce a PNG."
```

---

### Task 8: `regen_check.sh`, `tools/fetch/pdok.py`, `tools/convert/`

Three loose ends: a verification path for the four generators CI cannot run, and the fetch/convert tooling the repo was asked for.

**Files:**
- Create: `tools/catalog/regen_check.sh`, `tools/fetch/pdok.py`, `tools/convert/to_geoparquet.py`
- Modify: `tools/README.md`

**Interfaces:**
- Consumes: `tools.lib.paths`.
- Produces: nothing later tasks depend on.

- [ ] **Step 1: Write `tools/catalog/regen_check.sh`**

```bash
#!/usr/bin/env bash
# Verify the four data-reading generators against the working directory.
#
# tests/test_generators.py cannot cover these: they read parquet, which this
# repo does not hold. This runs them against $PORTOLAN_NL_WORKDIR and diffs the
# metadata they produce. Thumbnail bytes are excluded -- matplotlib output is
# not reproducible across versions, so comparing images would fail for reasons
# that have nothing to do with the refactor.
#
# Usage: bash tools/catalog/regen_check.sh [collections|styles|all]
set -euo pipefail
cd "$(dirname "$0")/../.."
WHICH="${1:-all}"

case "$WHICH" in
  collections) SCRIPTS=(tools/catalog/make_collections.py) ;;
  styles)      SCRIPTS=(tools/catalog/make_styles_thumbnails.py
                        tools/catalog/make_extra_styles.py
                        tools/catalog/make_point_legends.py) ;;
  all)         SCRIPTS=(tools/catalog/make_collections.py
                        tools/catalog/make_styles_thumbnails.py
                        tools/catalog/make_extra_styles.py
                        tools/catalog/make_point_legends.py) ;;
  *) echo "usage: $0 [collections|styles|all]" >&2; exit 2 ;;
esac

if [ -n "$(git status --porcelain catalog/)" ]; then
  echo "error: catalog/ has uncommitted changes; commit or stash first" >&2
  exit 2
fi

for s in "${SCRIPTS[@]}"; do echo "=== $s"; python3 "$s"; done

echo "=== diff (images excluded) ==="
if git diff --quiet -- catalog/ ':(exclude)catalog/**/*.webp' ':(exclude)catalog/**/*.png'; then
  echo "OK: regeneration reproduced the committed metadata"
  git checkout -- catalog/
  exit 0
fi
git diff --stat -- catalog/ ':(exclude)catalog/**/*.webp' ':(exclude)catalog/**/*.png'
echo "FAIL: regeneration changed committed metadata (above)"
echo "Restore with: git checkout -- catalog/"
exit 1
```

- [ ] **Step 2: Write `tools/fetch/pdok.py`**

Generalizes `pdok_download.sh`, which hardcodes one BRO Atom feed.

```python
#!/usr/bin/env python3
"""Discover and download PDOK datasets from their Atom feeds.

PDOK publishes each dataset as an Atom feed of download links. This resolves a
feed to its entries and fetches them, which is what vro/scripts/download_rest.sh
did for one hardcoded BRO feed.

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
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.lib import paths

ATOM = "{http://www.w3.org/2005/Atom}"


def entries(feed_url: str) -> list[tuple[str, str]]:
    """(title, href) for every downloadable entry in an Atom feed."""
    with urllib.request.urlopen(feed_url) as r:
        tree = ET.fromstring(r.read())
    out = []
    for e in tree.iter(f"{ATOM}entry"):
        title = (e.findtext(f"{ATOM}title") or "").strip()
        for link in e.iter(f"{ATOM}link"):
            href = link.get("href")
            if href and link.get("rel") in (None, "alternate", "section"):
                out.append((title, href))
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("action", choices=["list", "fetch"])
    ap.add_argument("feed")
    ap.add_argument("--into", help="staging collection name (fetch only)")
    args = ap.parse_args(argv)

    found = entries(args.feed)
    if not found:
        print(f"error: no entries in {args.feed}", file=sys.stderr)
        return 1

    if args.action == "list":
        for title, href in found:
            print(f"{title}\t{href}")
        return 0

    if not args.into:
        print("error: fetch needs --into <staging collection name>", file=sys.stderr)
        return 2
    dest = paths.REPO / "staging" / args.into / "data"
    dest.mkdir(parents=True, exist_ok=True)
    for title, href in found:
        name = href.rsplit("/", 1)[-1].split("?")[0] or "download"
        target = dest / name
        if target.exists():
            print(f"skip {name} (already present)")
            continue
        print(f"fetch {name} <- {href}")
        urllib.request.urlretrieve(href, target)
    print(f"Done: {len(found)} entries into {dest.relative_to(paths.REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 3: Verify it against a real feed**

```bash
cd ~/repos/portolan-nl-catalog
python3 tools/fetch/pdok.py list https://service.pdok.nl/tno/bro-bodemkaart/atom/index.xml
```
Expected: one or more tab-separated `title<TAB>href` lines. If PDOK has changed its feed layout, fix the parser — do not commit a downloader that finds nothing.

- [ ] **Step 4: Write `tools/convert/to_geoparquet.py`**

A thin, honest wrapper over `gpio`, which already does the conversion this catalog uses.

```python
#!/usr/bin/env python3
"""Source vector file -> GeoParquet -> PMTiles, via gpio.

gpio already produces cloud-native GeoParquet (zstd, bbox covering, spatially
sorted) and PMTiles with this catalog's conventions. This wrapper exists so the
exact flags used for this catalog live in the repo instead of in shell history.

Outputs land next to the source in staging/<name>/, not in catalog/ -- data
files never enter the published tree.

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


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source", type=Path)
    ap.add_argument("--layer", help="layer name inside the source (and the output stem)")
    ap.add_argument("--max-zoom", type=int, default=12)
    ap.add_argument("--no-pmtiles", action="store_true")
    args = ap.parse_args(argv)

    if not shutil.which("gpio"):
        print("error: gpio not found on PATH", file=sys.stderr)
        return 1
    if not args.source.exists():
        print(f"error: {args.source} does not exist", file=sys.stderr)
        return 1

    stem = args.layer or args.source.stem
    out = args.source.parent / f"{stem}.parquet"
    cmd = ["gpio", "convert", str(args.source), str(out), "--compression", "zstd"]
    if args.layer:
        cmd += ["--layer", args.layer]
    run(cmd)

    if not args.no_pmtiles:
        run(["gpio", "pmtiles", str(out), str(out.with_suffix(".pmtiles")),
             "--max-zoom", str(args.max_zoom), "--layer", stem])

    print(f"Done: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

Verify the subcommands and flags against the installed `gpio` before committing:
```bash
gpio --help; gpio convert --help; gpio pmtiles --help
```
If the CLI differs, fix the wrapper to match the installed version and say so in the commit message. **Do not commit a wrapper whose flags you have not checked.**

- [ ] **Step 5: Rewrite `tools/README.md`**

Delete the "Relocated scripts — not yet rewired" table; it is no longer true. Replace with a `lib/` index stating what each module holds and which generators use it, the `regen_check.sh` / `test_generators.py` split and why (the repo holds no data), and the third-party requirements per script.

- [ ] **Step 6: Full suite and commit**

```bash
cd ~/repos/portolan-nl-catalog
for t in publish links git_ext thumbnails generators stac_valid; do
  echo "=== $t ==="; python3 tests/test_$t.py || echo "FAILED: $t"
done
git add tools/ && git commit -m "Add regen_check.sh, tools/fetch/pdok.py and tools/convert/

regen_check.sh verifies the four generators CI cannot run, against the working
directory. pdok.py generalizes the hardcoded download_rest.sh to any PDOK Atom
feed. to_geoparquet.py records the gpio flags this catalog is built with."
```

---

### Task 9: Publish and close out phase 2

**Files:** none.

- [ ] **Step 1: Confirm the catalog changed only where expected**

```bash
cd ~/repos/portolan-nl-catalog
git diff --stat 29b3e09..HEAD -- catalog/ | tail -3
```
Expected: the 16–18 `vro` doc files from Task 2 and nothing else. Phase 2 is a tooling refactor; if other catalog files moved, find out why before publishing.

- [ ] **Step 2: Check drift, dry run, publish**

```bash
cd ~/repos/portolan-nl-catalog
python3 tools/catalog/diff_workdir.py --summary
AWS_PROFILE=default python3 tools/catalog/publish.py
AWS_PROFILE=default python3 tools/catalog/publish.py --confirm
AWS_PROFILE=default python3 tools/catalog/publish.py
```
Expected: the dry run lists only the regenerated `vro` docs; the final dry run reports `0 to upload`.

- [ ] **Step 3: Push and confirm CI**

```bash
cd ~/repos/portolan-nl-catalog
git push
gh run watch --repo cholmes/portolan-nl-catalog
```
Expected: six green tests, `test_generators.py` among them.

---

## Phase 2 completion checklist

- [ ] `tools/lib/` holds six modules, each used by two or more generators
- [ ] `python3 tests/test_generators.py` passes and is enforced in CI
- [ ] The gate was demonstrated to fail on a one-character change
- [ ] `bash tools/catalog/regen_check.sh all` passes against the working directory
- [ ] No generator writes a PNG thumbnail; `grep -rn savefig tools/` matches only `lib/images.py`
- [ ] The 18 missing style listings are published
- [ ] `tools/README.md` describes the real layout, with the stale relocation table gone
- [ ] All six tests green locally and in CI; `publish.py` dry run reports zero changes

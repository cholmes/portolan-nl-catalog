# Portolan NL Catalog — Phase 1: Land the Repo — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the unversioned 50 GB working directory `/Users/cholmes/geodata/portolan-nl` into a metadata-only git repository at `~/repos/portolan-nl-catalog` that publishes 1:1 to Source Cooperative, with tests and CI.

**Architecture:** A clean publish-directory model copied from `fieldsoftheworld/ftw-data-catalog`. `catalog/` **is** the published catalog — synced 1:1 to `s3://us-west-2.opendata.source.coop/cholmes/portolan-nl/`. Everything outside `catalog/` (`tools/`, `tests/`, `docs/`, `staging/`, root `README.md`, `CLAUDE.md`) is never published. Data files are excluded at copy time and gitignored, so they cannot leak into the repo.

**Tech Stack:** Python 3.11 (stdlib only for tests and publisher), `aws` CLI, `cwebp` (libwebp), `rsync`, `gh` CLI. `stac-check` in CI only.

## Global Constraints

- Repo root: `/Users/cholmes/repos/portolan-nl-catalog`. Remote: `github.com/cholmes/portolan-nl-catalog`. Branch: `main`.
- Source working directory (read-only in this plan — **never modify it**): `/Users/cholmes/geodata/portolan-nl`. Referred to below as `$WORKDIR`.
- `write_prefix`: `s3://us-west-2.opendata.source.coop/cholmes/portolan-nl`
- `public_base`: `https://data.source.coop/cholmes/portolan-nl`
- `region`: `us-west-2`; AWS profile: `default` (NOT `source` — the old CLAUDE.md is wrong).
- Tests are **dependency-free stdlib Python**, run as `python3 tests/test_*.py`, and print `OK: ...` on success. No pytest.
- Tests that need a third-party package (`stac-check`) must **SKIP with exit 0** when it is absent, so local runs are zero-setup.
- Never copy data files into the repo: `*.parquet`, `*.pmtiles`, `*.gpkg`, `*.tif`, `*.zip`, `*.zarr`. `.gitignore` already covers these and is committed — no task recreates it. It is a backstop, not the mechanism: the excludes at copy time are what keep 50 GB out.
- Never migrate: `kadaster/inspire_buildings/`, `vro/_downloads/`, `$WORKDIR/.env`, `$WORKDIR/.claude/`, `$WORKDIR/brp_gewaspercelen/` (a stray duplicate of `rvo/brp_gewaspercelen/`), `vro/scripts/download.log`, any `.DS_Store`.
- Phase 1 relocates the eleven generator scripts **without changing their internals**. Refactoring is phase 2.
- Spec: `docs/superpowers/specs/2026-07-31-portolan-nl-git-catalog-design.md`.

---

## File Structure

| File | Responsibility |
|---|---|
| `catalog.publish.yaml` | Publish config: write_prefix, public_base, region, publish_dir |
| `tools/catalog/publish.py` | Metadata-only S3 publisher with change detection |
| `tools/catalog/make_thumbnails.py` | PNG → WebP conversion + href rewriting |
| `tools/catalog/diff_workdir.py` | Report drift between repo `catalog/` and `$WORKDIR` |
| `tools/README.md` | Index of the relocated generator scripts |
| `tests/test_publish.py` | Publisher file selection + change detection |
| `tests/test_links.py` | Every relative href in STAC JSON resolves |
| `tests/test_stac_valid.py` | Per-file `stac-check` validation |
| `tests/test_git_ext.py` | Git extension fields on `catalog/catalog.json` |
| `tests/test_thumbnails.py` | Every thumbnail asset is WebP, exists, < 50 KB |
| `.github/workflows/ci.yml` | Run the five tests on push/PR |
| `README.md` | GitHub front door |
| `CLAUDE.md` | Developer/agent guide |

Task order is deliberate: the publisher and its test come first (Task 1) because Task 2's seeding is verified by a publisher dry run.

---

### Task 1: Publisher and publish config

**Files:**
- Create: `catalog.publish.yaml`
- Create: `tools/catalog/publish.py`
- Test: `tests/test_publish.py`

**Interfaces:**
- Consumes: nothing.
- Produces: `tools/catalog/publish.py` exposing `collect_uploads(manifest: dict, root: Path) -> list[Upload]`, `is_unchanged(u: Upload, remote: dict[str, tuple[str, int]]) -> bool`, `key_dirs(uploads: list[Upload]) -> list[str]`, `split_s3_uri(uri: str) -> tuple[str, str]`, `remote_index(uploads, write_prefix, region, workers=16) -> dict[str, tuple[str,int]]`, and a frozen dataclass `Upload(local: Path, s3_uri: str, content_type: str)`. Task 2 and Task 9 run it as a CLI.

- [ ] **Step 1: Write the failing test**

Create `tests/test_publish.py`. This is FTW's test adapted: `scripts/catalog` → `tools/catalog`, the NL `write_prefix`, an NL-shaped fixture tree, and **two new assertions for `.webp` and `.svg`** content types.

```python
"""Dependency-free test of publisher file selection and change detection.
Run: python3 tests/test_publish.py"""
import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools" / "catalog"))
from publish import collect_uploads, is_unchanged, key_dirs, split_s3_uri  # noqa: E402


def build_tree(tmp: Path):
    # Repo-root files that must NOT publish (outside catalog/)
    (tmp / "README.md").write_text("github")
    (tmp / "CLAUDE.md").write_text("guide")
    (tmp / "tools").mkdir()
    (tmp / "tools/foo.py").write_text("x")
    (tmp / "staging/natura2000").mkdir(parents=True)
    (tmp / "staging/natura2000/collection.json").write_text("{}")
    # The published catalog tree
    cat = tmp / "catalog"
    (cat / ".portolan").mkdir(parents=True)
    (cat / "catalog.json").write_text("{}")
    (cat / "llms.txt").write_text("x")
    (cat / "README.md").write_text("x")
    (cat / ".portolan/metadata.yaml").write_text("x")
    (cat / ".portolan/config.yaml").write_text("x")   # internal, must NOT publish
    (cat / ".portolan/state.json").write_text("{}")    # internal, must NOT publish
    c = cat / "rce/rijksmonumenten"
    (c / "styles").mkdir(parents=True)
    (c / "collection.json").write_text("{}")
    (c / "versions.json").write_text("{}")
    (c / "README.md").write_text("x")
    (c / "thumbnail.webp").write_text("x")
    (c / "styles/default.json").write_text("{}")
    b = cat / "beeldmateriaal/luchtfoto_2024/kb25"
    b.mkdir(parents=True)
    (b / "luchtfoto-2024-25bz1.json").write_text("{}")
    (cat / "beeldmateriaal/logo.svg").write_text("<svg/>")


def check_change_detection(tmp: Path, manifest: dict):
    """Unchanged bytes are skipped; anything else re-uploads."""
    assert split_s3_uri("s3://bucket/cholmes/portolan-nl") == ("bucket", "cholmes/portolan-nl")
    assert split_s3_uri("s3://bucket/a/b/") == ("bucket", "a/b")
    assert split_s3_uri("s3://bucket") == ("bucket", "")

    by_rel = {u.local.relative_to(tmp / "catalog").as_posix(): u
              for u in collect_uploads(manifest, tmp)}
    u = by_rel["catalog.json"]
    key = split_s3_uri(u.s3_uri)[1]
    etag = hashlib.md5(u.local.read_bytes()).hexdigest()
    size = u.local.stat().st_size

    assert is_unchanged(u, {key: (etag, size)}), "identical bytes must be skipped"
    assert is_unchanged(u, {key: (f'"{etag}"', size)}), "quoted ETag must be tolerated"
    assert not is_unchanged(u, {}), "absent object must upload"
    assert not is_unchanged(u, {key: ("0" * 32, size)}), "differing ETag must upload"
    assert not is_unchanged(u, {key: (etag, size + 1)}), "differing size must upload"
    assert not is_unchanged(u, {key: (f"{etag}-2", size)}), "multipart ETag must upload"
    assert not is_unchanged(u, {"other/key": (etag, size)}), "key must match exactly"

    # An empty index (the offline / no-credentials fallback) uploads everything.
    assert all(not is_unchanged(x, {}) for x in by_rel.values())

    # Only the directories the catalog occupies get listed -- never a bare recursive
    # sweep of write_prefix, which would walk every parquet and PMTiles sharing it.
    dirs = key_dirs(list(by_rel.values()))
    assert dirs == [
        "cholmes/portolan-nl/",
        "cholmes/portolan-nl/.portolan/",
        "cholmes/portolan-nl/beeldmateriaal/",
        "cholmes/portolan-nl/beeldmateriaal/luchtfoto_2024/kb25/",
        "cholmes/portolan-nl/rce/rijksmonumenten/",
        "cholmes/portolan-nl/rce/rijksmonumenten/styles/",
    ], dirs
    assert all(d.endswith("/") for d in dirs)
    assert len(dirs) == len(set(dirs)), "directories must be deduplicated"


def main():
    import tempfile
    manifest = {
        "write_prefix": "s3://us-west-2.opendata.source.coop/cholmes/portolan-nl",
        "public_base": "https://data.source.coop/cholmes/portolan-nl",
        "region": "us-west-2",
        "publish_dir": "catalog",
    }
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        build_tree(tmp)
        uploads = collect_uploads(manifest, tmp)
        rels = {u.local.relative_to(tmp / "catalog").as_posix() for u in uploads}
        by_rel = {u.local.relative_to(tmp / "catalog").as_posix(): u for u in uploads}
        check_change_detection(tmp, manifest)  # needs the files to still exist

        expected = {
            "catalog.json", "llms.txt", "README.md",
            ".portolan/metadata.yaml",
            "rce/rijksmonumenten/collection.json",
            "rce/rijksmonumenten/versions.json",
            "rce/rijksmonumenten/README.md",
            "rce/rijksmonumenten/thumbnail.webp",
            "rce/rijksmonumenten/styles/default.json",
            "beeldmateriaal/luchtfoto_2024/kb25/luchtfoto-2024-25bz1.json",
            "beeldmateriaal/logo.svg",
        }
        forbidden = {".portolan/config.yaml", ".portolan/state.json"}
        assert expected == rels, f"missing: {expected - rels}; leaked: {rels - expected}"
        assert not (forbidden & rels), f"leaked internal: {forbidden & rels}"

        assert by_rel["catalog.json"].s3_uri == \
            "s3://us-west-2.opendata.source.coop/cholmes/portolan-nl/catalog.json"
        assert by_rel["catalog.json"].content_type == "application/json"
        assert by_rel["rce/rijksmonumenten/versions.json"].content_type == "application/json"
        assert by_rel["beeldmateriaal/luchtfoto_2024/kb25/luchtfoto-2024-25bz1.json"] \
            .content_type == "application/geo+json"
        assert by_rel["rce/rijksmonumenten/README.md"].content_type.startswith("text/markdown")
        assert by_rel[".portolan/metadata.yaml"].content_type.startswith("text/yaml")
        # MapLibre styles are plain JSON, not GeoJSON
        assert by_rel["rce/rijksmonumenten/styles/default.json"].content_type == "application/json"
        # NL-specific additions
        assert by_rel["rce/rijksmonumenten/thumbnail.webp"].content_type == "image/webp"
        assert by_rel["beeldmateriaal/logo.svg"].content_type == "image/svg+xml"

    print("OK: publisher walks catalog/ 1:1, excludes root/staging/tools and .portolan "
          "internals, and skips objects S3 already holds")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd ~/repos/portolan-nl-catalog && python3 tests/test_publish.py
```
Expected: FAIL — `ModuleNotFoundError: No module named 'publish'`.

- [ ] **Step 3: Create the publish config**

Create `catalog.publish.yaml`:

```yaml
# What publishes, and where. Everything under publish_dir is uploaded 1:1.
# Data files are NEVER placed in publish_dir, so they cannot be published.
write_prefix: s3://us-west-2.opendata.source.coop/cholmes/portolan-nl
public_base: https://data.source.coop/cholmes/portolan-nl
region: us-west-2

# The catalog directory, synced 1:1 to write_prefix.
publish_dir: catalog
```

- [ ] **Step 4: Port the publisher**

Copy FTW's publisher verbatim, then apply the two NL changes:

```bash
mkdir -p ~/repos/portolan-nl-catalog/tools/catalog
cp /tmp/ftw-data-catalog-ref/scripts/catalog/publish.py \
   ~/repos/portolan-nl-catalog/tools/catalog/publish.py
```

If `/tmp/ftw-data-catalog-ref` is gone, re-clone: `git clone --depth 1 https://github.com/fieldsoftheworld/ftw-data-catalog.git /tmp/ftw-data-catalog-ref`.

Then edit `tools/catalog/publish.py`:

1. Replace the module docstring's first line with:
   `"""Metadata-only publisher for the Portolan NL catalog."""` (keep the rest of the docstring, changing `*.tif/*.parquet/*.zarr` to `*.parquet/*.pmtiles/*.gpkg/*.tif` and `scripts/catalog/publish.py` to `tools/catalog/publish.py` in the usage examples).
2. Add two entries to `_CT_BY_SUFFIX`:

```python
_CT_BY_SUFFIX = {
    ".json": "application/geo+json",  # items; catalog/collection overridden by name
    ".md": "text/markdown; charset=utf-8",
    ".txt": "text/markdown; charset=utf-8",  # llms.txt
    ".png": "image/png",
    ".webp": "image/webp",
    ".svg": "image/svg+xml",
    ".yaml": "text/yaml; charset=utf-8",
    ".yml": "text/yaml; charset=utf-8",
}
```

Leave everything else — including `Path(__file__).resolve().parents[2]` in `main()`, which still resolves to the repo root from `tools/catalog/` — unchanged.

- [ ] **Step 5: Run test to verify it passes**

```bash
cd ~/repos/portolan-nl-catalog && python3 tests/test_publish.py
```
Expected: `OK: publisher walks catalog/ 1:1, ...`

- [ ] **Step 6: Commit**

```bash
cd ~/repos/portolan-nl-catalog
git add catalog.publish.yaml tools/catalog/publish.py tests/test_publish.py
git commit -m "Add metadata-only S3 publisher ported from ftw-data-catalog

Syncs catalog/ 1:1 to the Source Cooperative prefix with size+MD5 change
detection. Adds image/webp and image/svg+xml content types for this catalog."
```

---

### Task 2: Seed catalog/, staging/ and docs/ from the working directory

**Files:**
- Create: `catalog/**` (~1,250 metadata files), `staging/**`, `docs/2026-05-07-styles-design.md`
- Test: `tests/test_links.py`

**Interfaces:**
- Consumes: `tools/catalog/publish.py` (Task 1) for the fidelity check.
- Produces: the `catalog/` tree that every later task operates on.

- [ ] **Step 1: Write the failing test**

Create `tests/test_links.py` (FTW's, unchanged except the docstring):

```python
"""Verify every relative href in catalog/collection/item JSON resolves to a file."""
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
```

Note: this checks `links` only, not `assets`. That is correct and deliberate — asset hrefs point at data files that are intentionally absent from the repo.

- [ ] **Step 2: Run test to verify it fails**

```bash
cd ~/repos/portolan-nl-catalog && python3 tests/test_links.py
```
Expected: `OK: 0 STAC files, all relative links resolve` — it passes vacuously because `catalog/` does not exist yet. That is the "failing" state: zero files checked. Record the count; after Step 3 it must be in the high hundreds.

- [ ] **Step 3: Copy the metadata tree**

```bash
cd ~/repos/portolan-nl-catalog
WORKDIR=/Users/cholmes/geodata/portolan-nl
mkdir -p catalog staging docs

# The eight institution subcatalogs. Excludes all data, the two script dirs
# (they go to tools/ in Task 6), and the collections we are not migrating.
rsync -a \
  --exclude='.DS_Store' \
  --exclude='*.parquet' --exclude='*.pmtiles' --exclude='*.gpkg' \
  --exclude='*.tif' --exclude='*.zip' --exclude='*.zarr' \
  --exclude='inspire_buildings/' \
  --exclude='_downloads/' \
  --exclude='scripts/' \
  "$WORKDIR"/beeldmateriaal "$WORKDIR"/cbs "$WORKDIR"/kadaster "$WORKDIR"/rce \
  "$WORKDIR"/rijkswaterstaat "$WORKDIR"/rvo "$WORKDIR"/tudelft "$WORKDIR"/vro \
  catalog/

# Root-level published files.
cp "$WORKDIR"/catalog.json "$WORKDIR"/README.md "$WORKDIR"/llms.txt catalog/
mkdir -p catalog/.portolan
cp "$WORKDIR"/.portolan/metadata.yaml "$WORKDIR"/.portolan/config.yaml catalog/.portolan/

# staging/ (was to-import/) and the design doc that was wrongly published.
rsync -a \
  --exclude='.DS_Store' \
  --exclude='*.parquet' --exclude='*.pmtiles' --exclude='*.gpkg' \
  --exclude='*.tif' --exclude='*.zip' --exclude='*.zarr' \
  "$WORKDIR"/to-import/ staging/
cp "$WORKDIR"/context/2026-05-07-styles-design.md docs/
```

- [ ] **Step 4: Verify nothing forbidden was copied**

```bash
cd ~/repos/portolan-nl-catalog
echo "--- data files (must be 0) ---"
find catalog staging -type f \( -name '*.parquet' -o -name '*.pmtiles' -o -name '*.gpkg' \
  -o -name '*.tif' -o -name '*.zip' \) | wc -l
echo "--- excluded dirs (must be 0) ---"
find catalog -type d \( -name inspire_buildings -o -name _downloads -o -name scripts \) | wc -l
echo "--- .DS_Store / .env (must be 0) ---"
find . -name '.DS_Store' -o -name '.env' | grep -v '^./.git/' | wc -l
echo "--- total size (expect ~180M before WebP) ---"
du -sh catalog
```
Expected: `0`, `0`, `0`, and roughly `180M`.

- [ ] **Step 5: Run the link test**

```bash
cd ~/repos/portolan-nl-catalog && python3 tests/test_links.py
```
Expected: `OK: <N> STAC files, all relative links resolve` with N in the high hundreds. If any link is reported missing, it points at a file the excludes dropped — investigate before continuing; do not weaken the test.

- [ ] **Step 6: Seeding fidelity check against S3**

This is the gate that proves the repo reproduces what is live.

```bash
cd ~/repos/portolan-nl-catalog
AWS_PROFILE=default python3 tools/catalog/publish.py
```
Expected: a short list, **not** hundreds of files. The only legitimate entries are files that were never published from the working directory:
- `.portolan/metadata.yaml`
- possibly `.portolan/config.yaml` — if it appears, that is a bug: `publish.py` must skip it. Investigate.

Anything else means the copy diverged from S3. Record the actual output in the commit message.

- [ ] **Step 7: Commit**

```bash
cd ~/repos/portolan-nl-catalog
git add catalog staging docs
git commit -m "Seed catalog/, staging/ and docs/ from the working directory

Metadata only: all data files excluded at copy time. Omits
kadaster/inspire_buildings (never published), vro/_downloads (source
downloads), and the two script directories (relocated to tools/ separately).
to-import/ becomes staging/; the styles design doc moves to docs/."
```

---

### Task 3: Git extension fields on the root catalog

**Files:**
- Modify: `catalog/catalog.json`
- Test: `tests/test_git_ext.py`

**Interfaces:**
- Consumes: `catalog/catalog.json` from Task 2.
- Produces: nothing consumed by later tasks.

- [ ] **Step 1: Write the failing test**

Create `tests/test_git_ext.py`:

```python
"""Verify the hand-carried git extension fields on the root catalog.

Portolan 0.1 defines no git extension and portolan-cli cannot yet emit these
(portolan-cli#485), so catalog.json carries them by hand. rashid ignores them.
"""
import json, sys
from pathlib import Path

REPO = "https://github.com/cholmes/portolan-nl-catalog"
ROOT = Path(__file__).resolve().parents[1] / "catalog"
doc = json.loads((ROOT / "catalog.json").read_text())

errs = []
if doc.get("git:repository") != REPO:
    errs.append(f"git:repository missing/wrong: {doc.get('git:repository')!r}")
if doc.get("git:ref") != "main":
    errs.append(f"git:ref missing/wrong: {doc.get('git:ref')!r}")
if doc.get("git:provider") != "github":
    errs.append(f"git:provider missing/wrong: {doc.get('git:provider')!r}")
rels = {l.get("rel"): l.get("href") for l in doc.get("links", [])}
if rels.get("vcs") != REPO:
    errs.append(f"vcs link missing/wrong: {rels.get('vcs')!r}")
if rels.get("issues") != f"{REPO}/issues":
    errs.append(f"issues link missing/wrong: {rels.get('issues')!r}")
if errs:
    print("\n".join(errs)); sys.exit(1)
print("OK: git extension fields present")
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd ~/repos/portolan-nl-catalog && python3 tests/test_git_ext.py
```
Expected: FAIL, listing all five missing fields.

- [ ] **Step 3: Add the fields**

Edit `catalog/catalog.json`. Add the three top-level keys immediately after `"stac_version": "1.1.0",`:

```json
  "git:repository": "https://github.com/cholmes/portolan-nl-catalog",
  "git:ref": "main",
  "git:provider": "github",
```

And append two links to the existing `links` array, after the `describedby` link and before the first `child` link:

```json
    {
      "rel": "vcs",
      "href": "https://github.com/cholmes/portolan-nl-catalog",
      "type": "text/html",
      "title": "Source repository"
    },
    {
      "rel": "issues",
      "href": "https://github.com/cholmes/portolan-nl-catalog/issues",
      "type": "text/html",
      "title": "Issue tracker"
    },
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd ~/repos/portolan-nl-catalog
python3 tests/test_git_ext.py && python3 tests/test_links.py
```
Expected: `OK: git extension fields present` and the link test still `OK` (the two new links are absolute `http`, so they are skipped by the resolver).

- [ ] **Step 5: Commit**

```bash
cd ~/repos/portolan-nl-catalog
git add catalog/catalog.json tests/test_git_ext.py
git commit -m "Declare the git extension on the root catalog

Hand-carried git:repository/git:ref/git:provider plus vcs and issues links,
matching ftw-data-catalog pending portolan-cli#485."
```

---

### Task 4: STAC validation test

**Files:**
- Test: `tests/test_stac_valid.py`

**Interfaces:**
- Consumes: the `catalog/` tree from Task 2.
- Produces: nothing consumed by later tasks.

- [ ] **Step 1: Port the test**

Copy FTW's `tests/test_stac_valid.py` verbatim — it is already generic (it resolves `catalog/` relative to itself and needs no FTW-specific knowledge):

```bash
cp /tmp/ftw-data-catalog-ref/tests/test_stac_valid.py \
   ~/repos/portolan-nl-catalog/tests/test_stac_valid.py
```

The file's existing exclusions already fit this catalog: it skips `.portolan/`, any path containing a `styles` directory, and `*.style.json`, so the 63 MapLibre style files are correctly not treated as STAC.

- [ ] **Step 2: Run it without stac-check to confirm the SKIP path**

```bash
cd ~/repos/portolan-nl-catalog
python3 -c "import stac_check" 2>/dev/null && echo "installed" || python3 tests/test_stac_valid.py
```
Expected (when not installed): `SKIP: stac-check not installed; STAC validation skipped (CI installs it and enforces this).` and exit 0.

- [ ] **Step 3: Install stac-check and run for real**

```bash
python3 -m pip install --quiet stac-check
cd ~/repos/portolan-nl-catalog && python3 tests/test_stac_valid.py
```
Expected: `OK: <N> STAC objects pass schema validation` possibly with best-practice `WARN` lines, which are non-fatal.

If there are hard `FAIL` lines, they are real STAC defects inherited from the working directory. Fix the offending JSON — do not weaken the test. Record each fix in the commit message.

- [ ] **Step 4: Commit**

```bash
cd ~/repos/portolan-nl-catalog
git add tests/test_stac_valid.py
git commit -m "Add per-file STAC validation via stac-check

Ported unchanged from ftw-data-catalog. SKIPs when stac-check is absent so
local runs stay zero-setup; CI installs it and enforces it."
```

---

### Task 5: WebP thumbnails

**Files:**
- Create: `tools/catalog/make_thumbnails.py`
- Modify: 388 JSON files under `catalog/` (390 thumbnail assets)
- Delete: 390 `*.png` files under `catalog/`
- Test: `tests/test_thumbnails.py`

**Interfaces:**
- Consumes: the `catalog/` tree from Task 2; `.webp` content type from Task 1.
- Produces: `tools/catalog/make_thumbnails.py` exposing `encode(src: Path, dst: Path) -> int` (returns the output size in bytes) and `main(argv=None) -> int`.

**Context:** every PNG *asset* in the catalog has `roles` containing `thumbnail` — verified, 390 of 390, zero exceptions. `beeldmateriaal/logo.png` and `logo-mark.png` are not assets and stay PNG. Requires `cwebp` (`brew install webp`).

- [ ] **Step 1: Write the failing test**

Create `tests/test_thumbnails.py`:

```python
"""Every thumbnail asset under catalog/ is WebP, present, and under 50 KB.

WebP conversion is done by tools/catalog/make_thumbnails.py. The 50 KB ceiling
is a deliberate repo-size constraint, not a format requirement.
"""
import json, sys
from pathlib import Path

CATALOG = Path(__file__).resolve().parents[1] / "catalog"
LIMIT = 50 * 1024

errs = []
checked = 0
for jf in CATALOG.rglob("*.json"):
    if ".portolan" in jf.parts or "styles" in jf.parts:
        continue
    try:
        doc = json.loads(jf.read_text())
    except json.JSONDecodeError:
        continue  # test_links.py owns malformed JSON
    if not isinstance(doc, dict):
        continue
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

stray = [p.relative_to(CATALOG).as_posix() for p in CATALOG.rglob("*-thumbnail.png")]
stray += [p.relative_to(CATALOG).as_posix() for p in CATALOG.rglob("thumbnail.png")]
for s in stray:
    errs.append(f"stray PNG thumbnail not converted: {s}")

if errs:
    print("\n".join(f"FAIL {e}" for e in errs))
    print(f"\n{len(errs)} problem(s) across {checked} thumbnail assets")
    sys.exit(1)
print(f"OK: {checked} thumbnail assets, all WebP and under 50 KB")
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd ~/repos/portolan-nl-catalog && python3 tests/test_thumbnails.py
```
Expected: FAIL with 390 `href is not .webp` errors plus 390 `stray PNG thumbnail` errors.

- [ ] **Step 3: Write the converter**

Create `tools/catalog/make_thumbnails.py`:

```python
#!/usr/bin/env python3
"""Convert every PNG thumbnail asset under catalog/ to WebP, and rewrite refs.

Encoding rule, benchmarked over 120 of this catalog's real thumbnails:
encode at native resolution with -q 80; if the result exceeds 48 KB, re-encode
with a hard -size 46000 byte target. Measured: avg 37 KB, max 47 KB, with 38 of
120 needing the fallback. No resizing -- the byte target does the work, so
nothing is lost to downscaling.

Every PNG asset in this catalog carries roles:["thumbnail"], so that role is the
selector. beeldmateriaal/logo.png and logo-mark.png are not assets and are left
as PNG.

Usage:
  python3 tools/catalog/make_thumbnails.py            # dry run
  python3 tools/catalog/make_thumbnails.py --confirm  # convert, rewrite, delete PNGs
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
BYTE_TARGET = 46000      # cwebp -size argument for the fallback


def encode(src: Path, dst: Path) -> int:
    """PNG -> WebP at native resolution. Returns the output size in bytes."""
    subprocess.run(["cwebp", "-q", "80", "-quiet", str(src), "-o", str(dst)],
                   check=True)
    if dst.stat().st_size > SOFT_LIMIT:
        subprocess.run(["cwebp", "-size", str(BYTE_TARGET), "-quiet",
                        str(src), "-o", str(dst)], check=True)
    return dst.stat().st_size


def find_targets() -> list[tuple[Path, str, str]]:
    """(json_file, asset_key, png_href) for every PNG thumbnail asset."""
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
            if href.endswith(".png") and "thumbnail" in (asset.get("roles") or []):
                out.append((jf, key, href))
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--confirm", action="store_true",
                    help="write the WebP files, rewrite JSON, delete the PNGs")
    args = ap.parse_args(argv)

    if not shutil.which("cwebp"):
        print("error: cwebp not found. Install with: brew install webp", file=sys.stderr)
        return 1

    targets = find_targets()
    if not targets:
        print("Nothing to do: no PNG thumbnail assets found.")
        return 0

    by_json: dict[Path, list[tuple[str, str]]] = {}
    for jf, key, href in targets:
        by_json.setdefault(jf, []).append((key, href))

    if not args.confirm:
        print(f"DRYRUN {len(targets)} thumbnail assets across {len(by_json)} JSON files")
        for jf, items in list(by_json.items())[:5]:
            for key, href in items:
                print(f"  {jf.relative_to(CATALOG)}: {key} {href} -> {href[:-4]}.webp")
        print(f"  ... re-run with --confirm to convert")
        return 0

    total_before = total_after = 0
    converted: list[Path] = []
    for jf, items in by_json.items():
        doc = json.loads(jf.read_text())
        for key, href in items:
            png = (jf.parent / href).resolve()
            if not png.exists():
                print(f"error: {jf.relative_to(CATALOG)}: {key} -> missing {href}",
                      file=sys.stderr)
                return 1
            webp = png.with_suffix(".webp")
            before = png.stat().st_size
            after = encode(png, webp)
            total_before += before
            total_after += after
            if after > 50 * 1024:
                print(f"error: {webp.name} is {after} bytes, over the 50 KB limit",
                      file=sys.stderr)
                return 1
            doc["assets"][key]["href"] = href[:-4] + ".webp"
            doc["assets"][key]["type"] = "image/webp"
            converted.append(png)
        jf.write_text(json.dumps(doc, indent=2) + "\n")

    for png in converted:
        png.unlink()

    print(f"Done: {len(converted)} thumbnails, {len(by_json)} JSON files rewritten. "
          f"{total_before / 1e6:.1f} MB -> {total_after / 1e6:.1f} MB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Dry run, then convert**

```bash
cd ~/repos/portolan-nl-catalog
python3 tools/catalog/make_thumbnails.py
```
Expected: `DRYRUN 390 thumbnail assets across 388 JSON files`.

```bash
python3 tools/catalog/make_thumbnails.py --confirm
```
Expected: `Done: 390 thumbnails, 388 JSON files rewritten. 169.x MB -> ~14 MB`.

- [ ] **Step 5: Run tests to verify they pass**

```bash
cd ~/repos/portolan-nl-catalog
python3 tests/test_thumbnails.py && python3 tests/test_links.py && du -sh catalog
```
Expected: `OK: 390 thumbnail assets, all WebP and under 50 KB`, the link test still `OK`, and `catalog/` around `25M`.

**Watch for:** `make_thumbnails.py` rewrites JSON with `json.dumps(indent=2)`, which may reformat files that used different spacing. Check `git diff --stat` — if the diff is far larger than the 390 href/type changes, inspect one file to confirm the reformatting is cosmetic before committing.

- [ ] **Step 6: Commit**

```bash
cd ~/repos/portolan-nl-catalog
git add tools/catalog/make_thumbnails.py tests/test_thumbnails.py catalog
git commit -m "Convert thumbnails to WebP, under 50 KB each

390 thumbnail assets across 388 JSON files: encode at native resolution with
cwebp -q 80, falling back to a hard -size 46000 target above 48 KB. Measured
avg 37 KB, max 47 KB. Shrinks catalog/ from ~180 MB to ~25 MB."
```

---

### Task 6: Relocate the generator scripts into tools/

**Files:**
- Create: `tools/fetch/pdok_download.sh`, `tools/catalog/make_*.py` (8 files), `tools/collections/brp_gewaspercelen/*.py` (3 files), `tools/README.md`

**Interfaces:**
- Consumes: nothing.
- Produces: the `tools/` layout that phase 2 refactors.

**Context:** phase 1 relocates only. **Do not change any script's internals** — not even the `ROOT` path computations, which will now be wrong relative to the repo. `tools/README.md` records that, so phase 2 knows what to fix.

- [ ] **Step 1: Move the scripts**

```bash
cd ~/repos/portolan-nl-catalog
WORKDIR=/Users/cholmes/geodata/portolan-nl
mkdir -p tools/fetch tools/collections/brp_gewaspercelen

cp "$WORKDIR"/vro/scripts/download_rest.sh        tools/fetch/pdok_download.sh
cp "$WORKDIR"/vro/scripts/make_catalogs.py        tools/catalog/
cp "$WORKDIR"/vro/scripts/make_collections.py     tools/catalog/
cp "$WORKDIR"/vro/scripts/make_extra_styles.py    tools/catalog/
cp "$WORKDIR"/vro/scripts/make_llms.py            tools/catalog/
cp "$WORKDIR"/vro/scripts/make_point_legends.py   tools/catalog/
cp "$WORKDIR"/vro/scripts/make_readmes.py         tools/catalog/
cp "$WORKDIR"/vro/scripts/make_styles_thumbnails.py tools/catalog/

cp "$WORKDIR"/rvo/brp_gewaspercelen/scripts/generate_items.py     tools/collections/brp_gewaspercelen/
cp "$WORKDIR"/rvo/brp_gewaspercelen/scripts/generate_year_docs.py tools/collections/brp_gewaspercelen/
cp "$WORKDIR"/rvo/brp_gewaspercelen/scripts/regen_year_styles.py  tools/collections/brp_gewaspercelen/
```

`vro/scripts/download.log` is deliberately not copied.

- [ ] **Step 2: Verify the count**

```bash
cd ~/repos/portolan-nl-catalog
find tools -name '*.py' -o -name '*.sh' | grep -v publish.py | grep -v make_thumbnails.py | wc -l
```
Expected: `11`.

- [ ] **Step 3: Write the index**

Create `tools/README.md`:

```markdown
# tools/

Fetch, transform and catalog-generation tooling. Nothing here is published.

## Layout

- `catalog/publish.py` — sync `catalog/` 1:1 to Source Cooperative. The publish path.
- `catalog/make_thumbnails.py` — PNG → WebP thumbnail conversion.
- `catalog/diff_workdir.py` — report drift against the data working directory.
- `catalog/make_*.py` — VRO/BRO metadata generators (relocated, see below).
- `collections/brp_gewaspercelen/` — generators specific to the BRP crop-parcel collection.
- `fetch/pdok_download.sh` — bulk PDOK/BRO downloads over Atom feeds.

## Relocated scripts — not yet rewired

The eleven scripts below were moved here verbatim from inside the collection
directories they used to live in. **They have not been adapted to the repo
layout.** Each computes its own `ROOT` by walking up from `__file__`, which
resolved correctly at its old depth and does not now. They are kept as-is so
phase 1 could land without behaviour changes.

Phase 2 extracts their shared logic into `tools/lib/` and fixes the paths, with
byte-identical regenerated output as the acceptance test.

| Script | Was |
|---|---|
| `catalog/make_catalogs.py` | `vro/scripts/` |
| `catalog/make_collections.py` | `vro/scripts/` |
| `catalog/make_extra_styles.py` | `vro/scripts/` |
| `catalog/make_llms.py` | `vro/scripts/` |
| `catalog/make_point_legends.py` | `vro/scripts/` |
| `catalog/make_readmes.py` | `vro/scripts/` |
| `catalog/make_styles_thumbnails.py` | `vro/scripts/` |
| `collections/brp_gewaspercelen/generate_items.py` | `rvo/brp_gewaspercelen/scripts/` |
| `collections/brp_gewaspercelen/generate_year_docs.py` | `rvo/brp_gewaspercelen/scripts/` |
| `collections/brp_gewaspercelen/regen_year_styles.py` | `rvo/brp_gewaspercelen/scripts/` |
| `fetch/pdok_download.sh` | `vro/scripts/download_rest.sh` |

These scripts need `duckdb`, `geopandas` and `matplotlib`; the tests and the
publisher need none of that.
```

- [ ] **Step 4: Commit**

```bash
cd ~/repos/portolan-nl-catalog
git add tools
git commit -m "Relocate the eleven generator scripts into tools/

Moved verbatim from vro/scripts/ and rvo/brp_gewaspercelen/scripts/. Their
internals are deliberately unchanged, so their ROOT path computations are now
wrong for this layout -- tools/README.md records that. Phase 2 rewires them
while extracting tools/lib/."
```

---

### Task 7: Working-directory drift reporter

**Files:**
- Create: `tools/catalog/diff_workdir.py`

**Interfaces:**
- Consumes: the `catalog/` tree.
- Produces: a CLI; nothing imports it.

**Context:** the working directory is deliberately left in place, so two metadata trees now exist and can drift. This makes that visible.

- [ ] **Step 1: Write the tool**

Create `tools/catalog/diff_workdir.py`:

```python
#!/usr/bin/env python3
"""Report drift between this repo's catalog/ and the data working directory.

The working directory (/Users/cholmes/geodata/portolan-nl by default) was
deliberately left in place, so two metadata trees exist and both can publish to
the same S3 prefix. This reports where they disagree. It is advisory: it never
writes anything, and it is not run in CI because the working directory is not
available there. Run it before publishing.

Known, expected differences are excluded by default -- the collections and
directories phase 1 chose not to migrate.

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
# Deliberately not migrated in phase 1; see the design spec.
EXCLUDED_PARTS = {"inspire_buildings", "_downloads", "scripts", ".portolan"}
EXCLUDED_NAMES = {".DS_Store", "download.log"}


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
        rel_parts = p.relative_to(base).parts
        if EXCLUDED_PARTS.intersection(rel_parts):
            continue
        out[p.relative_to(base).as_posix()] = p
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--workdir", type=Path,
                    default=Path(os.environ.get("PORTOLAN_NL_WORKDIR", DEFAULT_WORKDIR)))
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

    for r in only_repo:
        print(f"REPO-ONLY  {r}")
    for r in only_work:
        print(f"WORK-ONLY  {r}")
    for r in differing:
        print(f"DIFFERS    {r}")

    total = len(only_repo) + len(only_work) + len(differing)
    print(f"\n{len(repo)} repo files, {len(work)} workdir files, {total} difference(s).")
    if total:
        print("Differences are expected after phase 1 (WebP conversion, git extension "
              "fields). Review before publishing.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Run it**

```bash
cd ~/repos/portolan-nl-catalog && python3 tools/catalog/diff_workdir.py | tail -20
```
Expected: many `DIFFERS` lines for the 388 rewritten JSON files, `REPO-ONLY` for the 390 `.webp` files, `WORK-ONLY` for the 390 `.png` files, plus the root-level `CLAUDE.md`/`catalog.json` differences. This is the correct post-phase-1 state, and the closing note says so. The tool earns its keep from here on, once the trees are supposed to agree.

- [ ] **Step 3: Commit**

```bash
cd ~/repos/portolan-nl-catalog
git add tools/catalog/diff_workdir.py
git commit -m "Add a drift reporter for the data working directory

Two metadata trees now exist and both can publish to the same prefix. This
makes disagreement visible instead of silent. Advisory only, never writes,
not in CI."
```

---

### Task 8: Documentation and CI

**Files:**
- Create: `README.md`, `CLAUDE.md`, `.github/workflows/ci.yml`

**Interfaces:**
- Consumes: everything above.
- Produces: nothing.

- [ ] **Step 1: Write the CI workflow**

Create `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install stac-check (STAC validation)
        run: python -m pip install stac-check

      - name: Run catalog tests
        run: |
          python3 tests/test_publish.py
          python3 tests/test_links.py
          python3 tests/test_git_ext.py
          python3 tests/test_thumbnails.py
          python3 tests/test_stac_valid.py
```

- [ ] **Step 2: Write the GitHub front door**

Create `README.md`:

```markdown
# portolan-nl-catalog

Git-backed [Portolan](https://portolan-sdi.org)/STAC catalog for **Portolan NL** — open geodata
from Dutch government authorities as GeoParquet, PMTiles and STAC. Inspired by
[PDOK](https://www.pdok.nl/), built on cloud-native formats.

**This repository is the source of truth for catalog _metadata_ only.** The data itself — tens of
gigabytes of GeoParquet, PMTiles and COGs — lives on
[Source Cooperative](https://source.coop/cholmes/portolan-nl) and is never stored in or uploaded
by this repo.

- 🇳🇱 **Live catalog & data:** <https://data.source.coop/cholmes/portolan-nl/>
- 🧭 **Browse the STAC catalog:** [Portolan browser](https://browser.portolan-sdi.org/#/external/data.source.coop/cholmes/portolan-nl/catalog.json)
- 🤖 **For AI agents:** [`llms.txt`](https://data.source.coop/cholmes/portolan-nl/llms.txt)

## How this repo works

The [`catalog/`](./catalog/) directory **is** the published catalog: it is synced 1:1 to
`s3://us-west-2.opendata.source.coop/cholmes/portolan-nl/`, which Source Cooperative serves at
`https://data.source.coop/cholmes/portolan-nl/`. What you see in `catalog/` is exactly what is
live. Everything outside `catalog/` is never published.

```
catalog/    the published STAC/Portolan catalog (1:1 with Source Cooperative)
  README.md   the README rendered on Source Cooperative
staging/    collections being prepared, not yet published
tools/      fetch, transform, and publish tooling
tests/      dependency-free catalog validation
docs/       design specs and plans
CLAUDE.md   developer / agent guide
```

## Editing & publishing

1. Edit metadata under `catalog/`.
2. Validate: `python3 tests/test_links.py && python3 tests/test_publish.py`
3. Commit.
4. Publish: `python3 tools/catalog/publish.py` (dry run), then `--confirm` (needs AWS credentials).

See [CLAUDE.md](./CLAUDE.md) for the full developer guide. Corrections and additions welcome
via pull request.

## Institutions

`kadaster` · `rijkswaterstaat` · `rce` · `rvo` · `tudelft` · `cbs` · `vro` · `beeldmateriaal`

## License

Catalog metadata is CC0-1.0. Individual collections carry their own licenses — see each
`collection.json`.
```

- [ ] **Step 3: Write the developer guide**

Create `CLAUDE.md`:

```markdown
# portolan-nl-catalog — developer guide

Git-backed Portolan/STAC catalog for **Portolan NL**, open Dutch government geodata.
This repo is the **source of truth for catalog metadata only**. The data lives on Source
Cooperative and is never stored in or uploaded by this repo.

## Clean publish-directory model
`catalog/` **is** the published catalog — synced 1:1 to Source Cooperative. Everything in
`catalog/` is published; everything outside it never is.

- Write target (uploads): `s3://us-west-2.opendata.source.coop/cholmes/portolan-nl/`
- Public href base: `https://data.source.coop/cholmes/portolan-nl/`
- AWS profile: **`default`**. (Older docs said `source`; that is wrong.)

## Layout
- `catalog/` — the published catalog (STAC JSON, README.md, llms.txt, WebP thumbnails,
  MapLibre styles, `.portolan/metadata.yaml`). Synced 1:1 to S3.
- `staging/` — collections being prepared; git-tracked but NOT published.
- `tools/`, `tests/`, `docs/`, `CLAUDE.md`, root `README.md`, `catalog.publish.yaml` —
  tooling and docs, never published.
- Gitignored (never in repo): data files (`*.parquet`, `*.pmtiles`, `*.gpkg`, `*.tif`,
  `*.zip`, `*.zarr`), `.env`, caches.

Asset hrefs are **relative** (`./rijksmonumenten.parquet`). That is correct: the catalog is
synced to the same prefix the data occupies, so they resolve. The data files themselves are
simply absent locally.

## Publish workflow
Edit metadata under `catalog/` → commit → publish:
```
python3 tools/catalog/publish.py            # dry run (what would change)
python3 tools/catalog/publish.py --confirm  # upload (needs AWS creds)
```
`publish.py` syncs `catalog/` 1:1, skipping only `.portolan/config.yaml` and
`.portolan/state.json`. Config lives in `catalog.publish.yaml`.

**Change detection:** objects whose bytes already match S3 are skipped (local size+MD5 vs the
object's size+ETag), so a typical publish uploads only what you edited. The remote side is read
by listing each directory the catalog occupies **non-recursively**, 16 at a time — a recursive
listing of the prefix would walk every parquet and PMTiles sharing it. Caveats:
- A listing carries no ContentType, so a file whose bytes are unchanged but whose content-type
  mapping changed is skipped — run `--force` after editing `_content_type()`.
- If listing fails (no creds), it warns and treats every file as changed, so a dry run still
  works offline; it never silently skips.
- **It never deletes.** Removing something from `catalog/` does not unpublish it; use
  `aws s3 rm` by hand.

**`portolan push` is a supported fallback**, but note it operates from the *data working
directory*, not this repo — the two can disagree about what is current. Prefer `publish.py`.

## The data working directory
`/Users/cholmes/geodata/portolan-nl` still exists and still holds all the data plus its own
copy of the metadata. It was deliberately left in place. The two metadata trees **will drift**.

```
python3 tools/catalog/diff_workdir.py     # report disagreements; run before publishing
```

Not migrated from it, on purpose: `kadaster/inspire_buildings/` (built but never published),
`vro/_downloads/` (source downloads), the stray root `brp_gewaspercelen/`.

## Thumbnails
All thumbnails are **WebP under 50 KB**. To regenerate after adding PNGs:
```
python3 tools/catalog/make_thumbnails.py --confirm    # needs `brew install webp`
```
Encoding: `cwebp -q 80` at native resolution, falling back to a hard `-size 46000` target
above 48 KB. Measured over 120 real thumbnails: avg 37 KB, max 47 KB.

## Tests (dependency-free; run with python3)
```
python3 tests/test_publish.py      # publisher selection + change detection
python3 tests/test_links.py        # every relative link resolves
python3 tests/test_git_ext.py      # git extension fields on the root catalog
python3 tests/test_thumbnails.py   # thumbnails are WebP and under 50 KB
python3 tests/test_stac_valid.py   # per-file stac-check validation
```
`test_stac_valid.py` SKIPs when `stac-check` is not installed, so local runs are zero-setup.
CI installs it and runs all five on push/PR.

`test_links.py` checks `links` only, not `assets` — asset hrefs point at data files that are
intentionally absent from the repo.

## tools/
See [`tools/README.md`](./tools/README.md). The eleven generator scripts relocated from the
working directory have **not** been rewired to this layout yet — that is phase 2.

## Roadmap
- **Phase 2** — extract `tools/lib/`, with byte-identical regenerated output as the gate.
- **Phase 3** — Portolan 0.1 conformance plus spec PRs
  [#97](https://github.com/portolan-sdi/portolan-spec/pull/97) (default style as an asset role)
  and [#116](https://github.com/portolan-sdi/portolan-spec/pull/116) (`file:size`/`file:checksum`
  become SHOULD). See the design spec in `docs/superpowers/specs/`.

## STAC terminology
- **Catalog** — root container or subcatalog (e.g. `kadaster/`)
- **Collection** — a dataset (e.g. `kadaster/panden/`)
- **Item** — a single spatiotemporal entity within a collection
- **Asset** — an actual file (`.parquet`, `.pmtiles`, `.webp`)

Do NOT use "dataset" — say "collection".
```

- [ ] **Step 4: Run the full suite**

```bash
cd ~/repos/portolan-nl-catalog
for t in publish links git_ext thumbnails stac_valid; do
  echo "=== $t ==="; python3 tests/test_$t.py || echo "FAILED: $t"
done
```
Expected: five `OK:` lines, no `FAILED`.

- [ ] **Step 5: Commit**

```bash
cd ~/repos/portolan-nl-catalog
git add README.md CLAUDE.md .github
git commit -m "Add README, developer guide and CI

CI runs the five dependency-free tests on push and PR, installing stac-check
for the STAC validation pass."
```

---

### Task 9: Create the GitHub repo, push, and clean up S3

**Files:** none.

**Interfaces:**
- Consumes: everything above.

**Context:** this task performs two outward-facing actions — creating a public GitHub repo and deleting objects from the live S3 prefix. **Confirm with the user before each.**

- [ ] **Step 1: Confirm with the user**

Ask explicitly, before doing anything in this task:
- Should `cholmes/portolan-nl-catalog` be **public** or private?
- Confirm the S3 deletions listed in Step 4 are wanted.

Do not proceed on assumption.

- [ ] **Step 2: Create the repo and push**

```bash
cd ~/repos/portolan-nl-catalog
gh repo create cholmes/portolan-nl-catalog \
  --public \
  --source=. \
  --remote=origin \
  --description="Git-backed Portolan/STAC catalog for open Dutch government geodata" \
  --push
```
Swap `--public` for `--private` if that is what the user chose.

- [ ] **Step 3: Verify CI passes**

```bash
sleep 45 && gh run list --repo cholmes/portolan-nl-catalog --limit 3
gh run watch --repo cholmes/portolan-nl-catalog
```
Expected: the CI run completes green. If it fails, fix and push before continuing — do not publish from a red build.

- [ ] **Step 4: One-time S3 cleanup**

`publish.py` never deletes, so these stale objects must go by hand. **List before deleting.**

```bash
export AWS_PROFILE=default
P=s3://us-west-2.opendata.source.coop/cholmes/portolan-nl

# 1. CLAUDE.md and the design doc were published by mistake; neither belongs in the catalog.
aws s3 ls $P/CLAUDE.md
aws s3 ls $P/context/ --recursive

# 2. The PNG thumbnails superseded by WebP.
aws s3 ls $P/ --recursive | grep -E '(thumbnail\.png|-thumbnail\.png)$' | wc -l
```
Expected on the third command: about 390.

Review that output, then delete:

```bash
aws s3 rm $P/CLAUDE.md
aws s3 rm $P/context/ --recursive
aws s3 ls $P/ --recursive | awk '{print $4}' \
  | grep -E '(thumbnail\.png|-thumbnail\.png)$' \
  | while read -r k; do aws s3 rm "s3://us-west-2.opendata.source.coop/$k"; done
```

Note the `grep` deliberately does not match `logo.png` or `logo-mark.png`, which stay.

- [ ] **Step 5: Publish**

```bash
cd ~/repos/portolan-nl-catalog
AWS_PROFILE=default python3 tools/catalog/publish.py          # dry run — review the list
AWS_PROFILE=default python3 tools/catalog/publish.py --confirm
```
Expected on the dry run: the 390 new `.webp` objects, the 388 rewritten JSON files, the updated `catalog.json`, and `.portolan/metadata.yaml`. Nothing else. If the list is much larger, stop and investigate.

- [ ] **Step 6: Verify the published catalog**

```bash
curl -sI https://data.source.coop/cholmes/portolan-nl/catalog.json | head -3
curl -s https://data.source.coop/cholmes/portolan-nl/catalog.json | python3 -m json.tool | head -12
curl -sI https://data.source.coop/cholmes/portolan-nl/rce/rijksmonumenten/thumbnail.webp \
  | grep -i content-type
```
Expected: HTTP 200s, the catalog JSON showing `git:repository`, and `content-type: image/webp`.

- [ ] **Step 7: Final dry run must be clean**

```bash
cd ~/repos/portolan-nl-catalog
AWS_PROFILE=default python3 tools/catalog/publish.py
```
Expected: `Nothing to do: 0 to upload, <N> unchanged (skipped), <N> total.`

This is the phase 1 success criterion: the repo and the live catalog agree exactly.

- [ ] **Step 8: Commit any final fixes and push**

```bash
cd ~/repos/portolan-nl-catalog
git status --short
git push
```

---

## Phase 1 completion checklist

- [ ] `~/repos/portolan-nl-catalog` is a git repo on `main`, pushed to `github.com/cholmes/portolan-nl-catalog`
- [ ] All five tests pass locally and CI is green
- [ ] `publish.py` dry run reports zero changes
- [ ] Every thumbnail is WebP and under 50 KB; `catalog/` is ~25 MB
- [ ] All eleven generator scripts are under `tools/` and indexed in `tools/README.md`, internals unchanged
- [ ] `diff_workdir.py` runs and reports only expected differences
- [ ] `CLAUDE.md`, `context/` and the 390 PNG thumbnails are gone from the S3 prefix
- [ ] `/Users/cholmes/geodata/portolan-nl` is **unmodified**

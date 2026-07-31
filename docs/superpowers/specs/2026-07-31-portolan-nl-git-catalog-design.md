# Portolan NL as a git-backed catalog — design

**Date:** 2026-07-31
**Status:** approved
**Repo:** `~/repos/portolan-nl-catalog` → `github.com/cholmes/portolan-nl-catalog`

## Problem

`/Users/cholmes/geodata/portolan-nl` is a 50 GB working directory that doubles as the source
of truth for the Portolan/STAC catalog published at
`s3://us-west-2.opendata.source.coop/cholmes/portolan-nl/` (served as
<https://data.source.coop/cholmes/portolan-nl/>). It has no version control, no tests, no CI,
and no coherent tooling — the eleven scripts that generate its metadata are scattered inside
individual collection directories and duplicate each other.

Adopt the model proven by [`fieldsoftheworld/ftw-data-catalog`](https://github.com/fieldsoftheworld/ftw-data-catalog):
a git repository that holds catalog **metadata only**, with a clean publish directory synced
1:1 to object storage, plus reusable tooling and tests.

## Goals

1. A git repo at `~/repos/portolan-nl-catalog`, remote `github.com/cholmes/portolan-nl-catalog`.
2. FTW's clean publish-directory model: `catalog/` is exactly what is live on Source Cooperative.
3. A `tools/` directory for fetching and transforming data from PDOK and other sources,
   consolidating the eleven existing scripts behind shared helpers.
4. FTW's tests and CI, adapted.
5. Thumbnails converted to WebP, every file under 50 KB.

## Delivery phases

The work splits into three phases, each landing independently. **This spec details phase 1**;
phases 2 and 3 are scoped here and get their own plans.

| Phase | Scope | State |
|---|---|---|
| **1 — Land the repo** | git repo, `catalog/` + `staging/` split, `publish.py`, tests, CI, WebP thumbnails, scripts **relocated as-is** into `tools/` | this spec |
| **2 — Refactor `tools/`** | extract the shared `lib/` modules behind a golden-output diff | scoped in §4 |
| **3 — Portolan spec upgrade** | 0.1 plus spec PRs #97 and #116, bleeding edge | scoped in §7 |

Phase 1 deliberately relocates the eleven generator scripts without touching their internals,
so the repo can land and be verified against S3 before any behaviour changes.

## Non-goals

Explicitly deferred, each recorded here so it is not silently lost:

- **`kadaster/inspire_buildings/`.** Built locally (517 item JSONs + 512 parquet), never
  published. Not migrated; it stays in the old working directory.
- **Consolidating the two metadata trees.** See "Accepted risk" below.

## Current state (measured 2026-07-31)

| | |
|---|---|
| Working dir total | 50 GB |
| Metadata files (outside `to-import/`) | ~1,650 |
| Metadata size | ~176 MB, of which **160 MB is 358 beeldmateriaal thumbnails** |
| Assets across all collections | 270 |
| S3 objects under the prefix | 1,686 (1,136 metadata, 521 data) |

Local and S3 are close to in sync. The real differences:

- `kadaster/inspire_buildings` — 1,026 local files never published (excluded from migration).
- `vro/_downloads/` — 32 local source-download files, never published (excluded).
- `beeldmateriaal/luchtfoto_2024/*.tif` — 368 COGs on S3, never held locally (expected).
- `CLAUDE.md` and `context/` are published at the catalog root and should not be.

Asset hrefs are **relative** (`./rijksmonumenten.parquet`); `self` links are absolute to
`data.source.coop`. Relative asset hrefs are correct here and are retained — the catalog is
synced to the same prefix the data occupies, so they resolve.

`.env` sets `PORTOLAN_AWS_PROFILE=default`. The claim in the old `CLAUDE.md` that the profile
is `source` is stale and gets corrected.

## Design

### 1. Repository layout

```
~/repos/portolan-nl-catalog/
├── catalog/                  # published 1:1 to S3. Metadata only.
│   ├── catalog.json
│   ├── README.md             # the README rendered on Source Cooperative
│   ├── llms.txt
│   ├── .portolan/metadata.yaml
│   └── beeldmateriaal/ cbs/ kadaster/ rce/ rijkswaterstaat/ rvo/ tudelft/ vro/
├── staging/                  # was to-import/ — git-tracked, never published
├── tools/                    # fetch, transform, catalog generation, publish
├── tests/                    # dependency-free validation
├── docs/                     # specs and plans
├── .github/workflows/ci.yml
├── catalog.publish.yaml
├── CLAUDE.md                 # developer/agent guide (NOT published)
├── README.md                 # GitHub front door (NOT published)
└── .gitignore
```

`catalog/` **is** the published catalog. Everything in it is published; everything outside it
never is. This is the single property that makes the model easy to reason about.

**Gitignored:** `*.parquet`, `*.pmtiles`, `*.gpkg`, `*.tif`, `*.zip`, `*.zarr`, `.env`,
`__pycache__/`, `*.pyc`, `.DS_Store`.

**Migration mapping:**

| From (working dir) | To (repo) |
|---|---|
| the 8 institution dirs | `catalog/<institution>/` |
| `catalog.json`, `README.md`, `llms.txt`, `.portolan/metadata.yaml` | `catalog/` |
| `to-import/` | `staging/` |
| `context/2026-05-07-styles-design.md` | `docs/` |
| `vro/scripts/`, `rvo/brp_gewaspercelen/scripts/` | `tools/` |
| `CLAUDE.md` | repo root, rewritten |
| `kadaster/inspire_buildings/`, `vro/_downloads/`, `.env`, `.claude/` | not migrated |

**Two documented exceptions to strict 1:1**, both inherited from the FTW model:

1. `catalog/beeldmateriaal/luchtfoto_2024/items.parquet` — a generated stac-geoparquet of the
   items. Matched by the `*.parquet` gitignore, so it lives on S3 only and is regenerated by
   tooling rather than committed.
2. `.portolan/config.yaml` and `.portolan/state.json` — Portolan-internal, skipped by
   `publish.py` exactly as in FTW.

### 2. Publishing

Port `catalog.publish.yaml` and `scripts/catalog/publish.py` from FTW, logic unchanged, to
`tools/catalog/publish.py`. Config:

```yaml
write_prefix: s3://us-west-2.opendata.source.coop/cholmes/portolan-nl
public_base:  https://data.source.coop/cholmes/portolan-nl
region: us-west-2
publish_dir: catalog
```

`publish.py` retains its behaviour: dry run by default, `--confirm` to upload, `--force` to
re-upload everything, size+MD5-vs-ETag change detection via concurrent non-recursive listings,
and a graceful degrade to "treat everything as changed" when listing fails.

Two additions to `_content_type()`:

- `.webp` → `image/webp`
- `.svg` → `image/svg+xml` (for `beeldmateriaal/logo.svg`)

`publish.py` resolves the repo root from `Path(__file__).resolve().parents[2]`, which still
holds at `tools/catalog/publish.py`.

**`portolan push` remains supported** as a documented fallback, with an explicit warning in
`CLAUDE.md` that it operates from the *working directory*, not this repo, and that the two can
disagree about what is current. `publish.py` is the default path.

**One-time S3 cleanup.** `publish.py` uploads but never deletes, so stale objects must be
removed by hand once:

- `cholmes/portolan-nl/CLAUDE.md`
- `cholmes/portolan-nl/context/`
- every `*.png` thumbnail superseded by WebP

### 3. Thumbnails → WebP

`tools/catalog/make_thumbnails.py` converts all 405 PNG thumbnails (358 under
`beeldmateriaal/`, 47 collection-level) to WebP.

**Encoding rule**, benchmarked on 120 real files:

```
cwebp -q 80 <in>.png -o <out>.webp        # native 512×640, no resize
if size > 48 KB:  cwebp -size 46000 ...   # re-encode to a hard byte target
```

Measured across the 120-file sample: **avg 37 KB, max 47 KB**, 38 files needing the fallback.
Native resolution is retained — the byte target does the work, so no detail is lost to resizing.

The script also rewrites every reference: `href` `.png` → `.webp` and `type` → `image/webp`,
across the 358 beeldmateriaal item JSONs and the 47 `collection.json` files.

Expected result: **170 MB → ~14.5 MB**; whole repo ~30 MB.

`cwebp` is a hard dependency of this script (present via Homebrew). It is not needed to run the
test suite or to publish.

### 4. `tools/`

**Phase 1** relocates the eleven existing scripts into `tools/` unchanged, with a
`tools/README.md` indexing them. Only two things are new in phase 1: `tools/catalog/publish.py`
(ported from FTW) and `tools/catalog/make_thumbnails.py` (§3). Scripts keep working because
each computes its own paths; nothing is rewired.

**Phase 2** extracts the shared logic. Every `lib/` module below is justified by **two or more**
existing scripts that currently duplicate it — nothing is speculative.

```
tools/
├── lib/
│   ├── paths.py        # repo root, DATA/SRC base URLs, read from catalog.publish.yaml
│   ├── stac.py         # catalog/collection/item scaffolding, link + asset builders
│   ├── geoparquet.py   # geometry type, CRS, column list, bbox from a parquet
│   ├── styles.py       # Mapbox GL v8 styles, data-driven classes, point-legend workaround
│   ├── images.py       # matplotlib/Positron thumbnail render + WebP encode
│   └── docs.py         # README.md / llms.txt generation from collection.json
├── fetch/
│   └── pdok.py         # PDOK Atom-feed and bulk downloads (generalizes download_rest.sh)
├── convert/            # gpio wrappers: source → GeoParquet, → PMTiles
└── catalog/
    ├── publish.py
    ├── make_thumbnails.py
    ├── diff_workdir.py
    └── the ported generators (styles, llms, readmes, catalogs, items)
```

Provenance of each lib module:

| Module | Duplicated today in |
|---|---|
| `paths.py` | all five `vro/scripts/make_*.py` recompute `ROOT`/`DATA`/`SRC` by hand |
| `stac.py` | `make_catalogs`, `make_collections`, `generate_items` |
| `geoparquet.py` | `make_collections`, `generate_items` |
| `styles.py` | `make_styles_thumbnails`, `make_extra_styles`, `make_point_legends`, `regen_year_styles` |
| `images.py` | `make_styles_thumbnails`, `make_extra_styles` |
| `docs.py` | `make_readmes`, `make_llms`, `generate_year_docs` |

**Refactor safety — golden-output diff.** These scripts generate files that are already
committed to the repo. The acceptance criterion for every extraction is therefore mechanical:
regenerate, and require **byte-identical** output against the committed originals. Any script
whose output cannot be made byte-identical is left unrefactored and simply relocated, with the
reason recorded. This makes an otherwise risky refactor verifiable.

The one deliberate exception is `images.py`, which gains WebP output — a behaviour change by
design, covered by `test_thumbnails.py` instead.

### 5. Tests and CI

Ported from FTW into `tests/`:

- `test_links.py` — every relative href in catalog/collection/item JSON resolves.
- `test_publish.py` — publisher file selection and change detection, against a fixture tree.
- `test_stac_valid.py` — per-file `stac-check` validation of every STAC object under `catalog/`.
- `test_git_ext.py` — adapted to assert `git:repository ==
  https://github.com/cholmes/portolan-nl-catalog`, `git:ref == main`, `git:provider == github`,
  and the `vcs` / `issues` links.

New:

- `test_thumbnails.py` — every thumbnail asset href ends in `.webp`, the file exists, and it is
  under 50 KB.

Dropped:

- `test_scaffolds.py` — FTW-specific, and its `EXPECTED` map is already empty upstream.

Deferred:

- `test_portolan_conformance.py` — lands in phase 3 (§7).

Tests stay dependency-free and SKIP cleanly when `stac-check` is absent, so local runs are
zero-setup. CI (`.github/workflows/ci.yml`) mirrors FTW's: Ubuntu, Python 3.11,
`pip install stac-check`, run the suite on push to `main` and on PRs.

### 6. Git extension

`catalog/catalog.json` hand-carries, as FTW does pending CLI support:

```json
"git:repository": "https://github.com/cholmes/portolan-nl-catalog",
"git:ref": "main",
"git:provider": "github"
```

plus `vcs` and `issues` links. These are non-spec extras; `rashid` ignores them.

### 7. Phase 3 — Portolan spec upgrade (scoped, not detailed here)

Target **Portolan 0.1 plus two in-flight spec PRs**, deliberately bleeding edge:

- **[portolan-spec#97](https://github.com/portolan-sdi/portolan-spec/pull/97)** — the default
  style is named by a second asset role. When a collection has more than one style, exactly one
  style asset carries both `style` and `default` in `roles`. `PORTO-CORE-070` moves
  `SHOULD`/`process` → `MUST`/`validator`. The PR's earlier reserved-key idea (`style-default`)
  was dropped in review, so **asset keys need no change**. Companion: rashid#63, new
  `PTL-VIZ-006`.
- **[portolan-spec#116](https://github.com/portolan-sdi/portolan-spec/pull/116)** —
  `PORTO-CORE-028` (`file:size`, `file:checksum`) becomes a `SHOULD`. 029/030 stay `MUST` but
  bind only assets that *declare* the fields: a declared checksum must be multihash and must
  match the bytes at `href`. The profile schema drops both from asset `required`.
  Companion: rashid#90.

Both PRs are **open** as of 2026-07-31. Phase 3 must not start until their merge state is
re-checked, and it needs `rashid` at a revision that includes #63 and #90.

Measured scope against the current catalog:

| Item | Count | Note |
|---|---|---|
| Style assets already carrying `roles:["style"]` | 63 / 63 | nothing to do |
| Collections with >1 style lacking a `default` role | **18** | the #97 work |
| Collections with exactly 1 style | 11 | #97 does not apply |
| Catalogs/collections missing the Portolan schema URI | 34 / 35 | |
| Collections with `portolan:styles` | 29 / 33 | non-standard, retained to drive the browser |
| Assets lacking `file:size` / `file:checksum` | 270 / 270 | now `SHOULD` under #116 |
| Collections with `providers` | 0 | needs exactly one `host`, listed last |

#116 is what makes this phase affordable: without it, conformance required sha256 over ~50 GB
of local data. With it, `file:size` can be filled cheaply from `stat` and checksums deferred —
so long as nothing declares a value it cannot back up.

Phase 3 brings over FTW's `test_portolan_conformance.py` as the CI gate.

## Accepted risk: two metadata trees

The old working directory is left untouched, so its metadata tree and the repo's `catalog/`
tree both exist and both can publish to the same S3 prefix. They will drift. This was raised
and accepted deliberately — the working directory stays usable exactly as it is today.

**Mitigation:** `tools/catalog/diff_workdir.py` reads `$PORTOLAN_NL_WORKDIR` and reports files
that differ between the two trees or exist on only one side. It is not run in CI (the working
directory is not available there); it is run before publishing. This converts a silent failure
mode into a loud one without constraining how the working directory is used.

## Documentation

- **`README.md`** (repo root) — GitHub front door: what the catalog is, links to Source
  Cooperative and the Portolan browser, the `catalog/`-is-published model, how to edit and
  publish. Not published.
- **`catalog/README.md`** — the README rendered on Source Cooperative. Carried over from the
  working directory's current root `README.md`.
- **`CLAUDE.md`** — developer/agent guide. Rewritten from the working directory's version:
  corrects the stale `--profile source` to `default`, replaces the `portolan sync/push`-centric
  workflow with the `publish.py` one (keeping `portolan push` documented as fallback), documents
  the `catalog/`/`staging/` split, `tools/`, the tests, the WebP thumbnail rule, and the
  two-trees risk.

## Success criteria — phase 1

1. `~/repos/portolan-nl-catalog` exists, is a git repo on `main`, and pushes to
   `github.com/cholmes/portolan-nl-catalog`.
2. All five tests pass locally and in CI.
3. **Seeding fidelity**, checked *before* the WebP conversion: `python3 tools/catalog/publish.py`
   (dry run) reports **zero** changes against the current S3 state, proving the repo faithfully
   reproduces what is live. After the WebP conversion the same dry run should report exactly the
   405 new `.webp` objects plus the JSON files whose hrefs changed, and nothing else.
4. Every thumbnail in `catalog/` is WebP and under 50 KB; repo is under ~35 MB.
5. All eleven generator scripts are relocated under `tools/` and indexed in `tools/README.md`;
   none has had its internals changed.
6. `tools/catalog/diff_workdir.py` runs against the working directory and reports only the
   known, documented exclusions.
7. The one-time S3 cleanup has removed `CLAUDE.md`, `context/`, and the superseded `.png`
   thumbnails from the published prefix.

## Success criteria — phases 2 and 3

Recorded so they are not lost; each gets its own plan.

- **Phase 2:** every extraction produces byte-identical output against the committed originals,
  or the deviation is documented and the script left unrefactored.
- **Phase 3:** `rashid check catalog` passes against a build including spec PRs #97 and #116;
  `test_portolan_conformance.py` is enabled in CI.

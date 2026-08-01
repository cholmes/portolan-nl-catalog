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
- `catalog/` — the published catalog (STAC JSON, README.md, AGENTS.md, WebP thumbnails,
  MapLibre styles, the root `.portolan/metadata.yaml`). Synced 1:1 to S3.
- `staging/` — collections being prepared; git-tracked but NOT published.
- `tools/`, `tests/`, `docs/`, `CLAUDE.md`, root `README.md`, `catalog.publish.yaml` —
  tooling and docs, never published.
- Gitignored (never in repo): data files (`*.parquet`, `*.pmtiles`, `*.gpkg`, `*.tif`,
  `*.zip`, `*.zarr`), shapefile parts and GeoJSON under `staging/`, `.env`, caches.

Asset hrefs are **relative** (`./rijksmonumenten.parquet`). That is correct: the catalog is
synced to the same prefix the data occupies, so they resolve. The data files themselves are
simply absent locally.

## Publish workflow
Edit metadata under `catalog/` → commit → publish:
```
python3 tools/catalog/publish.py            # dry run (what would change)
python3 tools/catalog/publish.py --confirm  # upload (needs AWS creds)
```
`publish.py` syncs `catalog/` 1:1, skipping Portolan's internal bookkeeping: everything under
any `.portolan/` directory except the catalog root's `.portolan/metadata.yaml`, which is the
hand-authored catalog description and does belong in the published tree. Config lives in
`catalog.publish.yaml`.

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

Advisory only, and not run in CI — the working directory does not exist there. Point it
elsewhere with `--workdir` or `PORTOLAN_NL_WORKDIR`.

Not migrated from the working directory, on purpose: the 512 `kdtree_cell=*` item directories
under `kadaster/inspire_buildings/` (Portolan wrote them, but their assets were never
uploaded), `vro/_downloads/` (source downloads), and the stray top-level
`brp_gewaspercelen/versions.json`. The reporter excludes the first two and *reports* the third,
since publishing from the working directory would push it to S3.

## Thumbnails
All thumbnails are **WebP under 50 KB**. To regenerate after adding PNGs or JPEGs:
```
python3 tools/catalog/make_thumbnails.py              # dry run
python3 tools/catalog/make_thumbnails.py --confirm    # needs `brew install webp`
```
Portolan 0.1 does not accept WebP thumbnails; that is a deliberate deviation, see
`docs/phase3-baseline.md`. Encoding: `cwebp -q 80` at native resolution; above 48 KB it
binary-searches the quality factor for the highest one still under 46 000 bytes. No resizing. (`cwebp -size` was tried
first and abandoned — it overshot 50 KB on one thumbnail and, on another, swung from 29 KB at
one pass to 59 KB at ten.) Measured over the catalog's 391 thumbnails: avg 35 KB,
max 48 KB, total 14 MB.

The selector is the thumbnail **role**, not the filename — this catalog spells its thumbnails
three ways and one is a `.jpg`. The seven institution logos hang off `icon` links, carry no
thumbnail role, and stay PNG.

## Tests (dependency-free; run with python3)
```
python3 tests/test_publish.py      # publisher selection + change detection
python3 tests/test_links.py        # every relative link resolves
python3 tests/test_git_ext.py      # git extension fields on the root catalog
python3 tests/test_thumbnails.py   # thumbnails are WebP and under 50 KB
python3 tests/test_generators.py   # regenerating reproduces the committed catalog
python3 tests/test_stac_valid.py   # per-file stac-check validation
python3 tests/test_portolan_conformance.py   # Portolan 0.1 (+ spec PRs #97, #116)
```
`test_stac_valid.py` SKIPs without `stac-check`, and `test_portolan_conformance.py`
SKIPs without a purpose-built `rashid`, so local runs stay zero-setup. CI installs
both and runs all seven on push/PR.

`test_generators.py` is the phase-2 gate: it copies `catalog/` to a temp tree,
re-runs every data-free generator, and requires byte-identical output. Change
metadata by hand without changing the generator that emits it and this fails.
Four generators read parquet and cannot run in CI; `bash tools/catalog/regen_check.sh all`
covers those against the working directory.

## Portolan conformance
The catalog targets **Portolan 0.1 plus spec PRs
[#97](https://github.com/portolan-sdi/portolan-spec/pull/97) and
[#116](https://github.com/portolan-sdi/portolan-spec/pull/116)**, which were still
open when this landed. No released `rashid` contains their companion rules, so build
one:

```
bash tools/portolan/build_rashid.sh
RASHID=~/.local/share/portolan-nl/rashid-venv/bin/rashid python3 tests/test_portolan_conformance.py
```

Conformance fixes are applied by `tools/catalog/conform.py`, one registered fix per
rashid rule, dry-run by default. Never hand-edit a conformance fix: the generators
would undo it.

Four rules are knowingly left open, including the thumbnail media type — Portolan
allows only PNG and JPEG, and these thumbnails are WebP by design. Each is justified
in [`docs/phase3-baseline.md`](./docs/phase3-baseline.md); `ACCEPTED` in the test must
never grow without an entry there.

`test_links.py` checks `links` only, not `assets` — asset hrefs point at data files that are
intentionally absent from the repo.

## tools/
See [`tools/README.md`](./tools/README.md) for the `lib/` index and, importantly, the order
the generators must run in — `make_point_legends` rewrites styles `make_styles_thumbnails`
wrote, and `make_collections` reads whatever `styles/` ends up holding.

## Roadmap
Phases 1-3 are done: the repo landed, `tools/lib/` was extracted behind the golden
gate, and the catalog conforms to Portolan 0.1 plus PRs #97 and #116.

Open follow-ups, all recorded in `docs/phase3-baseline.md`:
- Give the 36 `rel:via` service links a real PDOK landing page, or a service-specific rel.
- Write MapLibre styles for the three collections that publish tiles without one.
- Raise the WebP thumbnail gap upstream.

## STAC terminology
- **Catalog** — root container or subcatalog (e.g. `kadaster/`)
- **Collection** — a dataset (e.g. `kadaster/panden/`)
- **Item** — a single spatiotemporal entity within a collection
- **Asset** — an actual file (`.parquet`, `.pmtiles`, `.webp`)

Do NOT use "dataset" — say "collection".

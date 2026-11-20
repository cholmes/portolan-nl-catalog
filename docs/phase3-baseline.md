# Phase 3 baseline — Portolan conformance

Measured 2026-08-01, before any conformance fixes.

## The rashid this is measured against

Released rashid (0.1.1, and 0.1.3 upstream) does not contain the rules this catalog
targets. Built from source with all three companion PRs merged onto `main`:

```
bash tools/portolan/build_rashid.sh
```

| PR | Repo | State on 2026-08-01 | Branch |
|---|---|---|---|
| [#97](https://github.com/portolan-sdi/portolan-spec/pull/97) | portolan-spec | **open**, mergeable | `feature/default-style-key` |
| [#116](https://github.com/portolan-sdi/portolan-spec/pull/116) | portolan-spec | **open**, mergeable | `worktree-checksum-size-should` |
| [#63](https://github.com/portolan-sdi/rashid/pull/63) | rashid | **open**, mergeable | `feature/porto-core-070-default-style-key` |
| [#90](https://github.com/portolan-sdi/rashid/pull/90) | rashid | **open**, mergeable | `feat/checksum-size-should` |
| [#120](https://github.com/portolan-sdi/portolan-spec/issues/120) / [#121](https://github.com/portolan-sdi/portolan-spec/pull/121) | portolan-spec | opened from this work | `feat/webp-thumbnails` |
| [#91](https://github.com/portolan-sdi/rashid/pull/91) | rashid | opened from this work | `feat/webp-thumbnails` |

**The PRs are verified to take effect**, which a clean build alone would not prove:

- `PTL-AST-003` reports severity **warning**, not error → #90 is live.
- `PTL-VIZ-006` **exists** and reports 19 findings → #63 is live.
- `PTL-VIZ-001` accepts `image/webp` → #91 is live.

## Baseline

`rashid check catalog --no-data`, 431 files: **593 errors**, 2 225 warnings, 1 info.

For scale, the same catalog under released rashid 0.1.1 reports **3 156 errors**.
The difference is almost entirely `PTL-AST-003` (2 224 file:checksum findings)
becoming a warning under #116, plus `PTL-LNK-006` dropping from 357 to 1 — the
newer rashid fixed a false positive where a nested item's `rel:collection` was
judged against the wrong enclosing object.

| Count | Rule | Wants | Task |
|---:|---|---|---|
| 99 | `PTL-FIL-003` | `rel:describedby` typed `text/markdown` | 3 |
| 76 | `PTL-FIL-001` | `AGENTS.md` in every object directory | 6 |
| 75 | `PTL-LNK-005` | no `rel:self` links | 3 |
| 65 | `PTL-VIZ-005` | style assets typed `application/vnd.mapbox.style+json` | 3 |
| 58 | `PTL-CNF-001` | the Portolan schema URI in `stac_extensions` | 5 |
| 58 | `PTL-FIL-002` | `rel:agents` link | 6 |
| 37 | `PTL-VIZ-003` | `pmtiles:layers` on `rel:pmtiles` links | 8 |
| 32 | `PTL-VIZ-001` | a `thumbnail` asset | 8 |
| 32 | `PTL-PRV-001` | `providers` | 7 |
| 19 | `PTL-VIZ-006` | the `default` role on one style asset (**spec #97**) | 8 |
| 17 | `PTL-LNK-003` | `rel:item` typed `application/geo+json` | 3 |
| 7 | `PTL-LIC-003` | no deprecated `proprietary` license | 3 |
| 4 | `PTL-LNK-002` | `child` link to a contained object | 10 |
| 3 | `PTL-VIZ-002` | a `style` asset where a visualization exists | 8 |
| 2 | `PTL-MIR-002` | `collection-mirror` role | 10 |
| 2 | `PTL-PRT-001` | the partition extension declared | 5 |
| 2 | `PTL-AST-005` | no assets on a catalog | 10 |
| 1 each | `PTL-PRO-001/003`, `PTL-LNK-006`, `PTL-TTL-001`, `PTL-PRV-002` | assorted | 10 |

Warnings (not gated): `PTL-AST-003` ×2 224, `PTL-COL-003` ×1, `PTL-PRO-002` ×1 (info).

## Outcome

**3 156 errors → 36**, all of the same rule and all deliberately left open (below). Everything
else was fixed at the source, and every fix is also made in the generator that
emits it, enforced by `tests/test_generators.py`.

| Stage | Errors |
|---|---:|
| Released rashid 0.1.1 | 3 156 |
| With spec PRs #97/#116 (baseline) | 593 |
| After mechanical link and type fixes | 348 |
| After schemas, providers, visualization metadata | 234 |
| After AGENTS.md, READMEs and their links | 82 |
| After the structural fixes | 71 |
| After the styles, thumbnails and WebP fix upstream | **36** |

## Findings deliberately left open

Every entry in `ACCEPTED` in `tests/test_portolan_conformance.py` is justified here.

### `PTL-PRO-001` ×36 — `rel:via` type must be `text/html`

The flagged links point at PDOK **WFS endpoints** (`application/xml`, `text/xml`) and
**Atom feeds** (`application/atom+xml`). Those are the real media types of what is
served. Relabelling them `text/html` would put a false content type in the metadata —
the same trap avoided in `PTL-FIL-003`, where the fix was to repoint the href at
something that genuinely is markdown rather than to relabel an HTML page.

The honest fix is not a relabel: 39 `via` links across the catalog already point at
PDOK article pages and are correctly `text/html`. The 36 flagged ones should either
gain a real landing-page `via` alongside their service links, or the service links
should move to a service-specific rel. Both need per-collection research into the
right PDOK page, so this is recorded as follow-up rather than guessed at.

### `PTL-COL-003` ×1 (warning) — collection id `3dbag`

Does not match the lowercase-hyphen naming convention. It is a *warning*, and `3dbag`
is the collection's published name; renaming breaks every live href pointing at it.

## Closed since the baseline

- **`PTL-VIZ-001`** — rashid allowed only PNG and JPEG thumbnails, and this catalog is
  WebP by design. Filed as [portolan-spec#120](https://github.com/portolan-sdi/portolan-spec/issues/120)
  with fixes in [portolan-spec#121](https://github.com/portolan-sdi/portolan-spec/pull/121)
  and [rashid#91](https://github.com/portolan-sdi/rashid/pull/91), citing RFC 9649,
  96.07% browser support, and the measured 169.6 MB → 14.1 MB. `build_rashid.sh` merges
  that branch alongside the other two, so CI checks against it.
  The two collections that genuinely had no thumbnail now have one.
- **`PTL-VIZ-002`** — `cbs/gebiedsindelingen`, `cbs/wijken_buurten` and
  `rijkswaterstaat/nwb_wegen` now carry 15 MapLibre styles between them, written by
  `tools/catalog/make_styles.py` from measured class breaks.
- **The stray S3 object** — `kadaster/inspire_buildings/catalog.json` has been removed
  with `aws s3 rm`; the repo and the published prefix agree again.

## v0.3.0 upgrade (2026-11-20)

The catalog moved from Portolan 0.1 (+ PRs #97/#116/#120) to released v0.3.0,
checked by released rashid 0.4.0. `tools/portolan/build_rashid.sh` is retired.
Baseline under rashid 0.4.0 before the upgrade: 55 errors, 2,906 warnings.
After: **0 errors**, and warnings reduced to the set below.

Fixes, each registered in `tools/catalog/conform.py` or made in the generator
that owns the file:

- The profile URI moved to `v0.3.0` on all 57 declaring objects (PTL-CNF-002).
- 23 collections' GeoParquet assets moved from `application/x-parquet` to the
  registered `application/vnd.apache.parquet` (PTL-AST-009). rashid recognizes
  the PMTiles-to-GeoParquet reference only under the registered type.
- 8 duplicate PMTiles assets carrying a bare `data` role were removed; v0.3
  forbids PMTiles as a data asset (PORTO-FMT-062).
- The 10 mirrors that had only service-endpoint `via` links gained a verified
  text/html landing page each (PORTO-CORE-084 now allows service links their
  real media types beside one HTML link, closing the old PTL-PRO-001 entry).
- `brp_gewaspercelen` moved its cross-year glob from a data-asset href to
  `partition:glob` as an S3 URL (PORTO-FMT-064/-065), declaring the partition
  extension with `scheme: directory`, `strategy: temporal`, key `jaar`. The
  documented DuckDB cross-year query was re-tested against the live bucket.
- The three vro mirror catalogs now carry `updated`, derived by
  `make_catalogs.py` as the max of their collections' sync times.
- 3dbag dropped its raw `{z}/{x}/{y}` link and asset; the endpoint stays
  reachable through the tilejson asset (PTL-LNK-006).
- Every asset now has a title and a description (PTL-AST-010), written by the
  owning generators and `conform.py` for unowned files.
- `file:size`/`file:checksum` (PTL-AST-003): computed from the repo for the
  554 assets the repo itself publishes, gated by `tests/test_file_metadata.py`;
  for published data files, sizes came from S3 HEAD requests and checksums
  only where the working-directory copy's md5 matched a single-part ETag.
- The root logo is served from the catalog itself (PTL-LNK-009).

### Warnings left open under v0.3

| Count | Rule | Why it stays |
|---:|---|---|
| ~513 | `PTL-AST-003` | Published data files uploaded multipart: the ETag is not an md5, so a checksum cannot be verified without downloading ~14 GB. Sizes are set. |
| 11 | `PTL-CAT-001` | Grouping 20+ children into subcatalogs changes published URLs; a publisher decision. |
| 1 | `PTL-VIZ-007` | luchtfoto_2024 wants an overview COG mosaicking 356 rasters; needs imagery generation, tracked as follow-up. |
| 1 | `PTL-COL-003` | Collection id `3dbag` is its published name; renaming breaks live hrefs. |

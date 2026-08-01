# Phase 3 baseline — Portolan conformance

Measured 2026-08-01, before any conformance fixes.

## The rashid this is measured against

Released rashid (0.1.1, and 0.1.3 upstream) does not contain the two rules this
catalog targets. Built from source with both companion PRs merged onto `main`:

```
bash tools/portolan/build_rashid.sh
```

| PR | Repo | State on 2026-08-01 | Branch |
|---|---|---|---|
| [#97](https://github.com/portolan-sdi/portolan-spec/pull/97) | portolan-spec | **open**, mergeable | `feature/default-style-key` |
| [#116](https://github.com/portolan-sdi/portolan-spec/pull/116) | portolan-spec | **open**, mergeable | `worktree-checksum-size-should` |
| [#63](https://github.com/portolan-sdi/rashid/pull/63) | rashid | **open**, mergeable | `feature/porto-core-070-default-style-key` |
| [#90](https://github.com/portolan-sdi/rashid/pull/90) | rashid | **open**, mergeable | `feat/checksum-size-should` |

Build result: rashid 0.1.3 + two merges (`3a3f3f6`, `7acbc13`).

**Both PRs verified to take effect**, which a clean build alone would not prove:

- `PTL-AST-003` reports severity **warning**, not error → #90 is live.
- `PTL-VIZ-006` **exists** and reports 19 findings → #63 is live.

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

## Findings deliberately left open

Recorded here as they are decided. Anything in `ACCEPTED` in
`tests/test_portolan_conformance.py` must have an entry here.

- **`PTL-COL-003`** — collection id `3dbag` does not match the lowercase-hyphen
  naming convention. It is a *warning*, and `3dbag` is the collection's published
  name; renaming it breaks every live href pointing at it. Left as-is.

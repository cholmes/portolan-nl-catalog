# tools/

Fetch, transform and catalog-generation tooling. Nothing here is published.

## Layout

- `catalog/publish.py` — sync `catalog/` 1:1 to Source Cooperative. The publish path.
- `catalog/make_thumbnails.py` — PNG/JPEG → WebP thumbnail conversion.
- `catalog/diff_workdir.py` — report drift against the data working directory.
- `catalog/make_*.py` — VRO/BRO metadata generators (relocated, see below).
- `collections/brp_gewaspercelen/` — generators specific to the BRP crop-parcel collection.
- `fetch/pdok_download.sh` — bulk PDOK/BRO downloads over Atom feeds.

Per-collection source downloads live with the collection they feed, in
`staging/<collection>/download.sh`.

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

One thing phase 2 must not lose: `make_styles_thumbnails.py` writes PNG
thumbnails. Every thumbnail in `catalog/` is now WebP under 50 KB, enforced by
`tests/test_thumbnails.py`, so that generator has to end in
`catalog/make_thumbnails.py`'s encoder rather than a bare `savefig`.

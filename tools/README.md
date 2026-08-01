# tools/

Fetch, transform and catalog-generation tooling. Nothing here is published.

## Layout

```
lib/          shared modules, each used by two or more generators
fetch/        getting source data out of PDOK
convert/      source file -> GeoParquet -> PMTiles
catalog/      generating and publishing catalog metadata
collections/  generators specific to one collection
```

### `lib/`

| Module | Holds | Used by |
|---|---|---|
| `paths.py` | the three roots (repo, catalog, data working dir) and the published URL bases, read from `catalog.publish.yaml` | all generators |
| `stac.py` | link and asset builders, and the one `write_json` convention | `make_catalogs`, `make_collections`, `generate_items` |
| `docs.py` | style enumeration, published URLs, the column table | `make_readmes`, `make_vro_agents`, `generate_year_docs` |
| `styles.py` | `match_expr`, `pmtiles_source` | `make_styles_thumbnails`, `make_extra_styles`, `make_point_legends` |
| `geoparquet.py` | parquet footer reads, and the top-N-values query | `make_collections`, and the three style generators |
| `images.py` | reproject, basemap, and **WebP** output | `make_styles_thumbnails`, `make_extra_styles` |

`lib/` holds only what two or more callers genuinely share. Two things that look
shared and are not, so they stay put: the point-legend workaround (one caller,
`make_point_legends`) and style *writing* — the committed style files follow
three different conventions and one writer would change bytes.

### `catalog/`

- `publish.py` — sync `catalog/` 1:1 to Source Cooperative. The publish path.
- `make_thumbnails.py` — PNG/JPEG → WebP conversion, and the encoder `lib/images.py` calls.
- `diff_workdir.py` — report drift against the data working directory.
- `regen_check.sh` — verify the data-reading generators (below).
- `make_catalogs.py`, `make_collections.py`, `make_vro_agents.py`, `make_readmes.py`,
  `make_styles_thumbnails.py`, `make_extra_styles.py`, `make_point_legends.py` — the VRO/BRO generators.

### `collections/brp_gewaspercelen/`

`generate_items.py`, `generate_year_docs.py`, `regen_year_styles.py` — the 17 per-year
items, their docs, and their per-year style copies.

## Two verification paths, because the repo holds no data

`tests/test_generators.py` copies `catalog/` to a temp tree, re-runs every generator
that needs no data files, and requires **byte-identical** output. It runs in CI.

Four generators read parquet and cannot run there — `make_collections`,
`make_styles_thumbnails`, `make_extra_styles`, `make_point_legends`. They are covered
by `regen_check.sh`, run by hand against `$PORTOLAN_NL_WORKDIR`:

```bash
bash tools/catalog/regen_check.sh all
```

It excludes rendered images: matplotlib output is not byte-reproducible, so six
thumbnails differ on every run. All metadata must match exactly.

**Order matters, and it is not obvious.** `make_point_legends` rewrites styles that
`make_styles_thumbnails` wrote, and `make_collections` reads whatever `styles/` ends
up holding. The correct order — encoded in `regen_check.sh` — is:

```
make_styles_thumbnails -> make_extra_styles -> make_point_legends -> make_collections
```

Run the first after the third and you silently revert the point-legend workaround.

## Requirements

The generators need `pyarrow`, `geopandas`, `duckdb`, `matplotlib` and `contextily`;
`make_thumbnails.py` needs `cwebp` (`brew install webp`); `convert/` needs `gpio` and
`tippecanoe`. The tests and `publish.py` need none of it — stdlib only.

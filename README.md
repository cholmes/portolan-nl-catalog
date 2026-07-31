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
live, minus the data files. Everything outside `catalog/` is never published.

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

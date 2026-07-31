# to-import — PDOK Dataset Staging Area

Staging area for 8 high-value Dutch vector datasets from [PDOK](https://www.pdok.nl/) (Publieke Dienstverlening Op de Kaart), the Dutch national geodata portal. Each dataset folder contains the downloaded source data plus comprehensive documentation — schema details, context, and query examples — intended to inform the creation of effective `llms.txt` files and Portolan catalog entries.

These datasets are **not yet part of the Portolan catalog**. They need to be converted to GeoParquet, have PMTiles generated, and get proper STAC collection metadata before being added.

## Datasets

| # | Folder | Dataset | Provider | Size | Format | Features |
|---|--------|---------|----------|------|--------|----------|
| 1 | `nationale-parken/` | National Parks (Nationale Parken) | RVO | 2.8 MB | GeoJSON | 21 |
| 2 | `natura2000/` | Natura 2000 Protected Areas | RVO | 10 MB | GeoPackage | 209 |
| 3 | `bestuurlijke-gebieden/` | Administrative Areas (Gemeenten, Provincies, Land) | Kadaster | 14 MB | GeoPackage | 342+12+1 |
| 4 | `rijksmonumenten/` | National Monuments (Rijksmonumenten) | RCE | 8 MB | Shapefile | 63,073 + 4,149 |
| 5 | `cbs-gebiedsindelingen/` | CBS Area Classifications (26 types) | CBS | 159 MB | GeoPackage | 56 layers |
| 6 | `cbs-wijken-buurten/` | CBS Neighborhoods + Demographics | CBS | 209 MB | GeoPackage | 14,823 buurten |
| 7 | `nwb-wegen/` | National Road Network (NWB Wegen) | RWS | ~1.5 GB | GeoPackage | ~1.1M segments |
| 8 | `brp-gewaspercelen/` | Agricultural Crop Parcels (BRP) | RVO | ~2.9 GB | GeoPackage | ~750K parcels |

## Institutions Represented

| Abbreviation | Full Name (Dutch) | English | Datasets |
|---|---|---|---|
| **RVO** | Rijksdienst voor Ondernemend Nederland | Netherlands Enterprise Agency | Nationale Parken, Natura 2000, BRP Gewaspercelen |
| **Kadaster** | Het Kadaster | Netherlands Cadastre, Land Registry and Mapping Agency | Bestuurlijke Gebieden |
| **RCE** | Rijksdienst voor het Cultureel Erfgoed | Cultural Heritage Agency | Rijksmonumenten |
| **CBS** | Centraal Bureau voor de Statistiek | Statistics Netherlands | Gebiedsindelingen, Wijken en Buurten |
| **RWS** | Rijkswaterstaat | Directorate-General for Public Works and Water Management | NWB Wegen |

## Per-Dataset Files

Each dataset folder contains:

```
dataset-name/
├── data/              ← Downloaded source data files
├── download.sh        ← Reproducible download script
├── dataset-info.json  ← Structured metadata (schema, provenance, context)
└── README.md          ← Comprehensive human-readable documentation
```

- **`dataset-info.json`** — Machine-readable metadata including full column schemas with Dutch→English translations, provenance URLs, license, CRS, and contextual information about what the dataset is and how it's used.
- **`README.md`** — Everything an LLM or human would need to understand the dataset: governance context, schema documentation, example queries (DuckDB, Python), conversion instructions, caveats, and relationships to other datasets.
- **`download.sh`** — Idempotent bash script to reproduce the download. Run `chmod +x download.sh` first.

## Common Properties

- **CRS**: All datasets use EPSG:28992 (Amersfoort / RD New), the Dutch national coordinate system. Web maps need reprojection to EPSG:4326 (WGS84).
- **Licenses**: Mix of CC0 (public domain) and CC BY 4.0 (attribution required). See individual dataset docs.
- **Source**: All from PDOK Atom feeds, OGC API Features, or partner download services (RCE).

## Import Pipeline (planned)

For each dataset, the Portolan import process will be:

1. Convert to GeoParquet (with zstd compression, bbox covering, Hilbert spatial sorting)
2. Reproject to EPSG:4326 if needed for web compatibility
3. Generate PMTiles for web visualization
4. Generate thumbnail
5. Create STAC collection.json with proper metadata
6. Create llms.txt for LLM/agent accessibility
7. Add to institution catalog and push to S3

## Notes

- The `rijksmonumenten/` contour Shapefile has corrupt geometry (all zeros) — use the PDOK OGC API for polygon data instead.
- CBS datasets use `-99997` as a sentinel for "data not available / privacy-suppressed".
- CBS Gebiedsindelingen has 56 layers covering 26+ types of regional classification — an extraordinary breadth.
- CBS Wijken en Buurten has 42 demographic columns per neighborhood — the premier Dutch demographic geodataset.
- Download dates: 2026-05-07. Check Atom feeds for newer editions.

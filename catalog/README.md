# Portolan NL — Cloud-Native Dutch Geodata

A proof-of-concept cloud-native catalog of Dutch government geodata, inspired by [PDOK](https://www.pdok.nl/) (Publieke Dienstverlening Op de Kaart). The same commitment to open, standards-based geodata disclosure, built on modern cloud-native formats: GeoParquet for analytics, PMTiles for visualization, and STAC for metadata.

Published on [Source Cooperative](https://source.coop/cholmes/portolan-nl).

![netherlands](https://img.shields.io/badge/netherlands-blue) ![dutch-government](https://img.shields.io/badge/dutch--government-blue) ![open-data](https://img.shields.io/badge/open--data-blue) ![geodata](https://img.shields.io/badge/geodata-blue) ![cloud-native](https://img.shields.io/badge/cloud--native-blue) ![geoparquet](https://img.shields.io/badge/geoparquet-blue) ![stac](https://img.shields.io/badge/stac-blue) ![pmtiles](https://img.shields.io/badge/pmtiles-blue)

## Data Providers

Organized by the Dutch government institution that produces the data:

| Institution | Description | Collections |
|---|---|---|
| **[Kadaster](./kadaster/)** | Cadastre, Land Registry & Mapping Agency | 3 |
| **[Rijkswaterstaat](./rijkswaterstaat/)** | Public Works & Water Management | 7 |
| **[RCE](./rce/)** | Cultural Heritage Agency | 1 |
| **[RVO](./rvo/)** | Netherlands Enterprise Agency | 2 |
| **[CBS](./cbs/)** | Statistics Netherlands | 6 |

## Collections

| Collection | Provider | Features | Geometry | Format | Description |
|---|---|---|---|---|---|
| [BAG Light](./kadaster/bag_light/) | Kadaster | 11.4M | Polygon | GeoParquet, PMTiles | All buildings in the Netherlands from the national building registry |
| [INSPIRE Buildings](./kadaster/inspire_buildings/) | Kadaster | 24.2M | Polygon | GeoParquet, PMTiles | BAG buildings harmonized to EU INSPIRE schema (incl. history) |
| [Administrative Areas](./kadaster/bestuurlijke_gebieden/) | Kadaster | 355 | MultiPolygon | GeoParquet, PMTiles | Municipalities, provinces, and national boundary (2026) |
| [Flood Retention Areas](./rijkswaterstaat/bergingsgebieden/) | RWS | 1,545 | MultiPolygon | GeoParquet, PMTiles | Designated areas for temporary water storage during floods |
| [Tunnels](./rijkswaterstaat/fme_disk_tunnels/) | RWS | 25 | Point | GeoParquet, PMTiles | Road tunnels managed by Rijkswaterstaat |
| [Fairway Depth Charts](./rijkswaterstaat/hectometervakken_vaargeul/) | RWS | 3,112 | Polygon | GeoParquet, PMTiles | Hectometer sections of Rhine branch fairways |
| [Fish Migration Routes](./rijkswaterstaat/rijksviswegen_2024/) | RWS | 2,122 | LineString | GeoParquet, PMTiles | National fish migration routes (2024) |
| [Navigation Locks](./rijkswaterstaat/sluizen/) | RWS | 92 | Point | GeoParquet, PMTiles | Locks on the recreational waterway network |
| [Flood Defenses](./rijkswaterstaat/waterkeringen/) | RWS | 238 | LineString | GeoParquet, PMTiles | Primary dike sections under the Water Act |
| [Zero Emission Zones](./rijkswaterstaat/zero_emissiezones/) | RWS | 42 | MultiPolygon | GeoParquet, PMTiles | Urban zones restricted to emission-free vehicles |
| [National Monuments](./rce/rijksmonumenten/) | RCE | 63,073 | Point | GeoParquet, PMTiles | Protected buildings and sites under the Heritage Act |
| [National Parks](./rvo/nationale_parken/) | RVO | 21 | MultiPolygon | GeoParquet, PMTiles | All 21 National Parks of the Netherlands |
| [Natura 2000](./rvo/natura2000/) | RVO | 209 | MultiPolygon | GeoParquet, PMTiles | 162 EU-protected nature areas (Birds & Habitats Directives) |
| [Wijken en Buurten](./cbs/wijken_en_buurten/) | CBS | 18,752 | MultiPolygon | GeoParquet, PMTiles | Neighborhoods, districts, municipalities with demographic statistics |
| [Postcode6](./cbs/postcode6/) | CBS | 464,964 | MultiPolygon | GeoParquet, PMTiles | 157 statistical attributes per 6-digit postcode |
| [Land Use 2017](./cbs/bestand_bodemgebruik_2017/) | CBS | 171,543 | MultiPolygon | GeoParquet, PMTiles | Complete land use classification (~40 types) |
| [Land Use INSPIRE](./cbs/existing_landuse_inspire/) | CBS | 171,543 | MultiPolygon | GeoParquet, PMTiles | INSPIRE-harmonized land use (HILUCS classification) |
| [Population Distribution](./cbs/bevolkingsspreiding/) | CBS | 31,033 | Polygon | GeoParquet, PMTiles | Population per 1km grid, province, and municipality |
| [Health Statistics](./cbs/gezondheid/) | CBS | 24 | MultiPolygon | GeoParquet, PMTiles | Doctors and deaths per 100K by province |

## Getting Started

**Use AI to explore the data.** Point [Claude Code](https://docs.anthropic.com/en/docs/claude-code) or [Gemini CLI](https://github.com/google-gemini/gemini-cli) at any collection's `AGENTS.md` and ask it to query the data, build interactive maps, or generate charts. Every collection includes an `AGENTS.md` with field descriptions, query examples, and usage context.

**Browse and download.** Navigate to any collection above to find GeoParquet files for analytics and PMTiles for instant map visualization. All files are on [Source Cooperative](https://source.coop/cholmes/portolan-nl) and can be accessed directly via HTTP — no account or API key required.

**Query directly with DuckDB.** All GeoParquet files work with remote HTTP access:

```sql
LOAD spatial;
SELECT naam, identificatie FROM read_parquet(
  'https://data.source.coop/cholmes/portolan-nl/kadaster/bestuurlijke_gebieden/gemeentegebied.parquet'
) ORDER BY naam;
```

## Formats

- **GeoParquet** — Analytics-ready columnar format. Every collection has a `.parquet` file with spatial indexing (Hilbert sort, bbox covering columns). Query remotely with DuckDB, Python (GeoPandas), R, or any Parquet reader.
- **PMTiles** — Single-file vector tile archives for instant map visualization. No tile server needed — works directly from object storage via HTTP range requests.
- **STAC** — SpatioTemporal Asset Catalog metadata in `collection.json` files. Machine-readable, standardized, and browsable.

## Coordinate Systems

Most datasets use **EPSG:28992** (RD New / Amersfoort), the Dutch national coordinate system — coordinates are in meters. CBS INSPIRE datasets use **EPSG:3035** (ETRS89-LAEA), the pan-European standard. The INSPIRE Buildings collection uses EPSG:4258 (ETRS89). All PMTiles are reprojected to WGS84 for web map display.

## Complementing PDOK

This catalog demonstrates how [PDOK](https://www.pdok.nl/)'s existing geodata services could be extended with cloud-native formats. Instead of running WFS/WMS servers, data can be served as GeoParquet for scalable analytics and PMTiles for instant map visualization — both work directly from object storage via HTTP range requests, with no server infrastructure. Adding STAC metadata and `AGENTS.md` files makes the data discoverable and queryable by AI agents, opening geodata to a much broader audience.

## AI / Agent Friendly

Every collection includes an `AGENTS.md` file with field descriptions, query examples, and usage context — designed for AI agents to understand and work with the data effectively. Built with [Portolan](https://portolan-sdi.org), a framework for cloud-native geodata infrastructure.

## License

Most data is published under [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/) (public domain). Some collections use [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/). See individual collection metadata for details.

## Status

This is a proof-of-concept. It is not affiliated with or endorsed by PDOK or any Dutch government organization. Data is sourced from publicly available PDOK services and ArcGIS Feature Services and converted to cloud-native formats.

## Contact

Chris Holmes — cholmes@9eo.org

---

*Published with [Portolan](https://portolan-sdi.org)*

# Centraal Bureau voor de Statistiek (CBS)

Statistics Netherlands. CBS publishes geographic statistical data including neighborhood boundaries, population density, land use, postcode-level demographics, and health indicators at various administrative levels.

![statistics](https://img.shields.io/badge/statistics-blue) ![netherlands](https://img.shields.io/badge/netherlands-blue) ![dutch-government](https://img.shields.io/badge/dutch--government-blue) ![open-data](https://img.shields.io/badge/open--data-blue) ![geodata](https://img.shields.io/badge/geodata-blue) ![cloud-native](https://img.shields.io/badge/cloud--native-blue) ![geoparquet](https://img.shields.io/badge/geoparquet-blue)

## Collections

| Collection | Features | Format | Description |
|------------|----------|--------|-------------|
| [Wijken en Buurten](wijken_en_buurten/) | 18,752 | GeoParquet (3 files), PMTiles | Annual boundaries and ~40 demographic/socioeconomic indicators for neighborhoods, districts, and municipalities |
| [Bestand Bodemgebruik 2017](bestand_bodemgebruik_2017/) | 171,543 | GeoParquet (795 MB), PMTiles | Complete land use classification (~40 types) of the Netherlands |
| [CBS Postcode6](postcode6/) | 464,964 | GeoParquet (86 MB), PMTiles | 157 statistical attributes per 6-digit postcode (demographics, housing, energy, income, facilities) |
| [Bevolkingsspreiding](bevolkingsspreiding/) | 31,033 | GeoParquet (3 files), PMTiles | INSPIRE population distribution per 1km² grid, province, and municipality |
| [Existing Land Use (INSPIRE)](existing_landuse_inspire/) | 171,543 | GeoParquet (956 MB), PMTiles | INSPIRE-harmonized land use with European HILUCS classification |
| [Human Health Statistics](gezondheid/) | 24 | GeoParquet (2 files), PMTiles | INSPIRE health indicators (doctors, mortality) per province |

## Links

- [cbs.nl](https://www.cbs.nl/)
- [CBS Open Data StatLine](https://opendata.cbs.nl/statline/)
- [CBS Geographic Data](https://www.cbs.nl/nl-nl/dossier/nederland-regionaal/geografische-data)
- [PDOK CBS datasets](https://www.pdok.nl/datasets?tags=CBS)

## About This Catalog

All data is available as GeoParquet for analytics and PMTiles for instant map visualization from [Source Cooperative](https://source.coop/cholmes/portolan-nl). Every collection includes an `AGENTS.md` with field descriptions and query examples for AI/agent access.

This cloud-native infrastructure demonstrates how [PDOK](https://www.pdok.nl/)'s existing CBS services could be extended — GeoParquet for scalable analytics, PMTiles for map visualization directly from object storage, and STAC+AGENTS.md for AI-friendly discovery and querying.

---

*Published with [Portolan](https://portolan-sdi.org)*

# Rijkswaterstaat

Dutch Directorate-General for Public Works and Water Management. Rijkswaterstaat manages the main road and waterway networks and the water systems in the Netherlands.

![rijkswaterstaat](https://img.shields.io/badge/rijkswaterstaat-blue) ![netherlands](https://img.shields.io/badge/netherlands-blue) ![dutch-government](https://img.shields.io/badge/dutch--government-blue) ![open-data](https://img.shields.io/badge/open--data-blue) ![geodata](https://img.shields.io/badge/geodata-blue) ![cloud-native](https://img.shields.io/badge/cloud--native-blue) ![geoparquet](https://img.shields.io/badge/geoparquet-blue)

## Collections

| Collection | Features | Geometry | Description |
|---|---|---|---|
| [Flood Retention Areas](./bergingsgebieden/) | 1,545 | MultiPolygon | Designated areas for temporary water storage during high water events. |
| [Tunnels](./fme_disk_tunnels/) | 25 | Point | Road tunnels managed by Rijkswaterstaat, with name, road number, and year opened. |
| [Fairway Depth Charts](./hectometervakken_vaargeul/) | 3,112 | Polygon | Hectometer sections of the fairway along Rhine branches (Waterdieptekaarten). |
| [Fish Migration Routes](./rijksviswegen_2024/) | 2,122 | LineString | National fish migration routes from the Nationale Visroutekaart (2024 snapshot). |
| [Navigation Locks](./sluizen/) | 92 | Point | Locks on the recreational waterway network, with operator and VHF channel info. |
| [Primary Flood Defenses](./waterkeringen/) | 238 | LineString | Primary dike sections forming the backbone of Dutch flood protection under the Water Act. |
| [Zero Emission Zones](./zero_emissiezones/) | 42 | MultiPolygon | Urban zones where only emission-free vehicles are allowed (LEZ and ZES areas). |

## Data Source

Most of these collections were downloaded from Rijkswaterstaat's public [ArcGIS Feature Services](https://services-eu1.arcgis.com/4D1GBrbE6xp1T4YG/arcgis/rest/services/), converted to GeoParquet and PMTiles for cloud-native access. The original Feature Services remain the authoritative source and may be updated more frequently.

## Links

- [rijkswaterstaat.nl](https://www.rijkswaterstaat.nl/)
- [RWS ArcGIS Feature Services](https://services-eu1.arcgis.com/4D1GBrbE6xp1T4YG/arcgis/rest/services/)

---

*Published with [Portolan](https://portolan-sdi.org)*

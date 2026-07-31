# Ministerie van Volkshuisvesting en Ruimtelijke Ordening (VRO)

Open geodata for which the **Ministry of Housing and Spatial Planning (VRO)** is the responsible
provider on [PDOK](https://www.pdok.nl/), drawn from the **Basisregistratie Ondergrond (BRO)** — the
Dutch Key Registry of the Subsurface. This subcatalog covers the BRO datasets flagged as EU
**High Value Data**, republished as cloud-native GeoParquet + PMTiles with STAC metadata.

Underlying data is produced by **TNO – Geologische Dienst Nederland** (subsurface objects) and
**Wageningen Environmental Research** (the soil and geomorphological maps). All data is **CC0 1.0**.

## Collections

| Collection | BRO | Geometry | Features |
|------------|-----|----------|----------|
| [wandonderzoek](./wandonderzoek/) | SFR | points | 2,806 |
| [mijnbouwconstructie](./mijnbouwconstructie/) | EPC | points | 4,975 |
| [bodemverontreiniging_besluit](./bodemverontreiniging_besluit/) | SLD | polygons | 121 |
| [grondwatergebruiksysteem](./grondwatergebruiksysteem/) | GUF | points | 50,637 |
| [bodemkaart](./bodemkaart/) → soilarea, areaofpedologicalinterest | SGM | polygons | 48,025 / 6,192 |
| [geomorfologische_kaart](./geomorfologische_kaart/) → geomorphological_area (+2) | GMM | polygons | 80,148 / 40,840 / 70 |

The **Soil Map** and **Geomorphological Map** are organised as sub-catalogs, with one collection per
distinct map layer in the source GeoPackage (see each sub-catalog's description for how the layers
differ).

## Coming next

- **Tabular (non-geo) collections** for objects with no own geometry: groundwater monitoring
  networks (GMN), production dossiers (GPD), and groundwater composition analyses (GAR).
- **Phase 2** point datasets: soil/geological/geotechnical boreholes (BHR-P, BHR-G, BHR-GT),
  groundwater monitoring wells (GMW), and integrated groundwater monitoring (GM).
- **Metadata-only entries** for the 3D/raster subsurface models (GeoTOP, DGM, REGIS II, WDM) and the
  large point datasets CPT and SAD.

## License

[CC0-1.0](https://creativecommons.org/publicdomain/zero/1.0/) — public domain.

---
*Part of [Portolan NL](../README.md).*

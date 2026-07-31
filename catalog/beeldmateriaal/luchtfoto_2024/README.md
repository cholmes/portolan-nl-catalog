# Luchtfoto 2024 — Aerial Orthophotos (Amersfoort Region)

High-resolution aerial orthophotos from the 2024 [Beeldmateriaal Nederland](https://www.beeldmateriaal.nl/) summer campaign. 12 tiles at 25 cm ground sampling distance covering ~450 km² around Amersfoort, each approximately 5 × 6.25 km. Available as 3-band RGB and 4-band RGBNIR Cloud-Optimized GeoTIFFs (COGs) with JPEG compression, overviews, and per-band statistics.

The NIR band is extracted from the Color InfraRed (CIR) winter capture (band 1). RGB and NIR represent different seasons within the same year — summer (full foliage) and winter (leafless) respectively.

Source imagery from [Beeldmateriaal Nederland](https://www.beeldmateriaal.nl/) via [GeoTiles (TU Delft)](https://geotiles.citg.tudelft.nl/).

> AI/Agent users: See [llms.txt](./llms.txt) for band descriptions, code examples, interactive map recipes, and cross-dataset analysis patterns.

## Spatial Coverage

- **Bounding Box:** [4.07, 52.03, 5.75, 52.37] (WGS 84)
- **Region:** Amersfoort and surroundings (kaartblad sheet 32)
- **CRS:** EPSG:28992 (Amersfoort / RD New)
- **GSD:** 0.25 m (25 cm)
- **Tile dimensions:** 20,002 × 25,002 pixels (~5 km × 6.25 km)

## Assets per Tile

| Asset | Bands | Compression | Size | Use |
|-------|-------|-------------|------|-----|
| RGB COG | Red, Green, Blue | JPEG (YCbCr, Q75) | ~80–97 MB | Visual inspection, basemap |
| RGBNIR COG | Red, Green, Blue, NIR | JPEG (Q75) | ~293–365 MB | Vegetation indices (NDVI) |

## Tiles

| Tile | Location | Notable Features |
|------|----------|------------------|
| 32DN1 | **Amersfoort city centre** | RD origin (Onze Lieve Vrouwetoren) |
| 32CN2 | Southwest of Amersfoort | Soest, Baarn |
| 32CZ1 | South of Soest | Soestduinen, A28 |
| 32CZ2 | Soesterberg / Zeist | Former airbase, forests |
| 32DZ2 | East of Amersfoort | Leusden, Stoutenburg |
| 32EN1 | North of Amersfoort | Bunschoten-Spakenburg, polders |
| 32EZ1 | Northeast of Amersfoort | Nijkerk |
| 32EZ2 | Barneveld | Mixed urban/agricultural |
| 32FZ1 | Voorthuizen | Veluwe fringe |
| 32FZ2 | East of Barneveld | Agricultural land |
| 32GN1 | Leusden / Woudenberg | Utrechtse Heuvelrug forests |
| 32HN1 | Scherpenzeel | Rural landscape |

## Quick Start

```python
import rasterio

url = 'https://data.source.coop/cholmes/portolan-nl/beeldmateriaal/luchtfoto_2024/luchtfoto-2024-32dn1-rgb.tif'
with rasterio.open(url) as src:
    window = rasterio.windows.Window(10000, 12000, 1000, 1000)
    data = src.read(window=window)  # (3, 1000, 1000)
```

```bash
# GDAL — clip 2km × 2km around Amersfoort centre
gdalwarp -te 154000 462000 156000 464000 \
  /vsicurl/https://data.source.coop/cholmes/portolan-nl/beeldmateriaal/luchtfoto_2024/luchtfoto-2024-32dn1-rgb.tif \
  amersfoort_center.tif
```

## About Beeldmateriaal Nederland

[Beeldmateriaal Nederland](https://www.beeldmateriaal.nl/) is the Dutch national partnership for aerial photography, established in 2011. Municipalities, provinces, water boards (waterschappen), Rijkswaterstaat, and Het Kadaster jointly commission annual surveys — a 25 cm summer campaign (RGB) and a 7.5 cm winter/spring campaign (high-resolution + CIR). All imagery is published as open data under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). The programme is coordinated under the Geo-Informatieberaad and also manages the AHN (Actueel Hoogtebestand Nederland) LiDAR elevation dataset.

## STAC Metadata

- **Collection:** `collection.json`
- **Root catalog:** `../../catalog.json`
- **Parent:** `../catalog.json` (Beeldmateriaal Nederland)

## Related Datasets

- **BAG Light** — 11.4M building footprints for overlay analysis
- **Rijksmonumenten** — 63K national monuments
- **Nationale Parken / Natura 2000** — Nature reserve boundaries for vegetation analysis
- **Wijken en Buurten** — Neighbourhood demographics for spatial correlation

## License

[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — Attribution: Beeldmateriaal Nederland

---

*Part of [Portolan NL](https://source.coop/cholmes/portolan-nl) — Cloud-Native Dutch Geodata*

# Luchtfoto 2024 — Aerial Orthophotos

## What This Dataset Is

High-resolution aerial orthophotos from the 2024 Beeldmateriaal Nederland summer campaign,
covering 356 tiles across 12 kaartblad sheets in the central Netherlands — from the North Sea
coast (Haarlem, IJmuiden) to the Veluwe (Apeldoorn, Harderwijk) and from Alkmaar in the north
to Gorinchem and Tiel in the south. Served as Cloud-Optimized GeoTIFFs (COGs).

Each tile covers one "kaartblad" (Dutch national map sheet) of approximately 5 km × 6.25 km
at 25 cm ground sampling distance, yielding 20,002 × 25,002 pixels per tile.

Two asset variants:
- **RGB** — 3-band natural color (Red, Green, Blue). Summer capture, full foliage. All 356 tiles.
- **RGBNIR** — 4-band multispectral (Red, Green, Blue, Near-Infrared). NIR from winter
  CIR capture band 1. Suitable for vegetation indices (NDVI, SAVI, EVI). Only 12 tiles in KB 32 (Amersfoort).

All COGs include JPEG compression (quality 75), 512×512 internal tiling, 6 overview levels
(AVERAGE resampling), and baked-in per-band statistics (min, max, mean, stddev).

**Source:** Beeldmateriaal Nederland via GeoTiles (TU Delft)
**Provider:** Beeldmateriaal Nederland — a partnership of Dutch municipalities, provinces,
water boards, Rijkswaterstaat, and Het Kadaster for joint aerial photography since 2011.
**License:** CC BY 4.0 (attribution to beeldmateriaal.nl requested)

## How to Access

The data lives on Source Cooperative as Cloud-Optimized GeoTIFF in **EPSG:28992**
(Amersfoort / RD New). COGs support HTTP range requests — GDAL, rasterio, and other tools
can read arbitrary windows without downloading entire files.

**Base URL:** `https://data.source.coop/cholmes/portolan-nl/beeldmateriaal/luchtfoto_2024/`

### Directory Structure

Tiles are organized into sub-catalogs by kaartblad sheet number:

```
luchtfoto_2024/
├── collection.json
├── items.parquet           # stac-geoparquet — all 356 items, queryable with DuckDB
├── kb19/                   # Alkmaar / Zaandam (32 tiles)
│   ├── catalog.json
│   ├── luchtfoto-2024-19an1.json
│   ├── luchtfoto-2024-19an1-rgb.tif
│   └── ...
├── kb25/                   # Amsterdam (32 tiles)
├── kb32/                   # Amersfoort (32 tiles, RGB + RGBNIR)
└── ...                     # 12 KB directories total
```

### URL Pattern

```
{base}/kb{sheet}/luchtfoto-2024-{tileid}-{variant}.tif
```

- `sheet`: Kaartblad sheet number (19, 20, 24, 25, 26, 27, 30, 31, 32, 33, 38, 39)
- `tileid`: Lowercase kaartblad tile code (e.g., `32dn1`, `25az2`)
- `variant`: `rgb` (3-band, ~80-97 MB) or `rgbnir` (4-band, ~293-365 MB, KB32 only)

### Example URLs

```
https://data.source.coop/cholmes/portolan-nl/beeldmateriaal/luchtfoto_2024/kb32/luchtfoto-2024-32dn1-rgb.tif
https://data.source.coop/cholmes/portolan-nl/beeldmateriaal/luchtfoto_2024/kb25/luchtfoto-2024-25az1-rgb.tif
https://data.source.coop/cholmes/portolan-nl/beeldmateriaal/luchtfoto_2024/kb32/luchtfoto-2024-32dn1-rgbnir.tif
```

## Tile Coverage

356 tiles across 12 kaartblad sheets in the central Netherlands:

| KB Sheet | Region | Tiles | Coverage |
|----------|--------|-------|----------|
| 19 | Alkmaar / Zaandam | 32 | Zaandam, Purmerend, Alkmaar, Castricum, Heemskerk |
| 20 | Lelystad / Markermeer | 32 | Almere, south Flevoland, Markermeer, Eemnes |
| 24 | Haarlem / IJmond | 12 | Haarlem, Heemstede, Bloemendaal, IJmuiden (coastal) |
| 25 | Amsterdam | 32 | Amsterdam, Amstelveen, Schiphol, Aalsmeer, Weesp |
| 26 | Het Gooi / Hilversum | 32 | Hilversum, Huizen, Bussum, Naarden, Baarn, Soest |
| 27 | Harderwijk / Veluwe West | 32 | Harderwijk, Ermelo, Putten, Nijkerk, western Veluwe |
| 30 | Gouda Area | 25 | Gouda, Waddinxveen, Bodegraven, Alphen aan den Rijn |
| 31 | Utrecht / Vinkeveen | 32 | Utrecht, Vinkeveen, Nieuwegein, IJsselstein, Woerden |
| 32 | Amersfoort | 32 | Amersfoort, Zeist, Leusden, Woudenberg, Veenendaal |
| 33 | Apeldoorn / Veluwe East | 31 | Apeldoorn, Ede, Wageningen, Barneveld |
| 38 | Gorinchem / Rivierenland | 32 | Gorinchem, Vianen, Leerdam, Culemborg |
| 39 | Tiel / Betuwe | 32 | Tiel, Rhenen, Wageningen (south), Betuwe |

KB 32 (Amersfoort) contains the origin of the RD New coordinate system
(X=155000, Y=463000 — the Onze Lieve Vrouwetoren church tower).

## Querying with stac-geoparquet

The `items.parquet` file contains all 356 STAC items as a GeoParquet table, queryable
with DuckDB for spatial search and filtering:

```sql
LOAD spatial;

-- All items
SELECT id, title, "beeldmateriaal:kaartblad", bbox
FROM read_parquet('beeldmateriaal/luchtfoto_2024/items.parquet');

-- Filter by kaartblad sheet
SELECT id, title FROM read_parquet('beeldmateriaal/luchtfoto_2024/items.parquet')
WHERE "beeldmateriaal:kaartblad" LIKE '25%';

-- Spatial query — tiles intersecting Amsterdam centre
SELECT id, title FROM read_parquet('beeldmateriaal/luchtfoto_2024/items.parquet')
WHERE ST_Intersects(geometry, ST_Point(4.9, 52.37));
```

## Band Information

### RGB COG (3 bands)

| Band | Name | Common Name | Description |
|------|------|-------------|-------------|
| 1 | red | red | Red channel (summer capture, 25cm) |
| 2 | green | green | Green channel (summer capture, 25cm) |
| 3 | blue | blue | Blue channel (summer capture, 25cm) |

### RGBNIR COG (4 bands, KB 32 only)

| Band | Name | Common Name | Description |
|------|------|-------------|-------------|
| 1 | red | red | Red channel (from RGB summer capture) |
| 2 | green | green | Green channel (from RGB summer capture) |
| 3 | blue | blue | Blue channel (from RGB summer capture) |
| 4 | nir | nir | Near-infrared (from CIR winter capture, band 1) |

All bands are uint8 (0–255). Per-band min/max/mean/stddev statistics are embedded in each COG.

## COG Technical Properties

- **Compression:** JPEG (quality 75)
- **Color space:** YCbCr for RGB; band-interleaved for RGBNIR
- **Internal tiling:** 512 × 512 pixels
- **Overviews:** 6 levels (AVERAGE resampling)
- **Statistics:** min, max, mean, stddev per band (baked into file metadata)
- **CRS:** EPSG:28992 (Amersfoort / RD New) — coordinates in metres
- **Pixel size:** 0.25 m × 0.25 m
- **Tile dimensions:** 20,002 × 25,002 pixels (~5 km × 6.25 km)

## Reading and Analysis

### Python (rasterio) — Read a Window

```python
import rasterio

url = 'https://data.source.coop/cholmes/portolan-nl/beeldmateriaal/luchtfoto_2024/kb32/luchtfoto-2024-32dn1-rgb.tif'
with rasterio.open(url) as src:
    # Read a 1000×1000 pixel window (250m × 250m on the ground)
    window = rasterio.windows.Window(10000, 12000, 1000, 1000)
    data = src.read(window=window)
    print(f"Shape: {data.shape}")  # (3, 1000, 1000) for RGB
    print(f"CRS: {src.crs}")       # EPSG:28992
```

### Python (rasterio) — Read by Geographic Coordinates

```python
import rasterio
from rasterio.windows import from_bounds

url = 'https://data.source.coop/cholmes/portolan-nl/beeldmateriaal/luchtfoto_2024/kb32/luchtfoto-2024-32dn1-rgb.tif'
with rasterio.open(url) as src:
    # Read a 500m × 500m area around Amersfoort city centre (RD coordinates)
    window = from_bounds(154750, 462750, 155250, 463250, src.transform)
    data = src.read(window=window)
    print(f"Shape: {data.shape}")  # (3, 2002, 2002) — 500m at 0.25m/px
```

### Python (rasterio) — Compute NDVI from RGBNIR

```python
import rasterio
import numpy as np

url = 'https://data.source.coop/cholmes/portolan-nl/beeldmateriaal/luchtfoto_2024/kb32/luchtfoto-2024-32dn1-rgbnir.tif'
with rasterio.open(url) as src:
    window = rasterio.windows.Window(10000, 12000, 2000, 2000)
    data = src.read(window=window).astype(float)
    red = data[0]   # Band 1 = Red
    nir = data[3]   # Band 4 = NIR
    ndvi = (nir - red) / (nir + red + 1e-10)
    print(f"NDVI range: {ndvi.min():.2f} to {ndvi.max():.2f}")
    # Vegetation: NDVI > 0.3, Water: NDVI < 0, Built-up: 0 < NDVI < 0.2
```

### GDAL (command line)

```bash
# Inspect a remote COG
gdalinfo /vsicurl/https://data.source.coop/cholmes/portolan-nl/beeldmateriaal/luchtfoto_2024/kb32/luchtfoto-2024-32dn1-rgb.tif

# Clip a 2km × 2km area around Amersfoort centre (RD coordinates)
gdalwarp -te 154000 462000 156000 464000 \
  /vsicurl/https://data.source.coop/cholmes/portolan-nl/beeldmateriaal/luchtfoto_2024/kb32/luchtfoto-2024-32dn1-rgb.tif \
  amersfoort_center.tif
```

## Interactive Maps

### Viewing COGs on a Web Map with TiTiler

COGs can be rendered as web map tiles using [TiTiler](https://developmentseed.org/titiler/),
which reads HTTP range requests from the COG and serves XYZ tiles on the fly.

```
https://titiler.xyz/cog/tiles/WebMercatorQuad/{z}/{x}/{y}?url={encoded_cog_url}
```

### MapLibre GL JS + TiTiler (Multiple KB Tiles)

```javascript
const baseUrl = 'https://data.source.coop/cholmes/portolan-nl/beeldmateriaal/luchtfoto_2024';

// Load tiles from different kaartblad sheets
const tiles = [
    {kb: 'kb25', id: '25az1'},  // Amsterdam
    {kb: 'kb32', id: '32dn1'},  // Amersfoort
    {kb: 'kb31', id: '31bn1'},  // Utrecht
];

tiles.forEach(({kb, id}) => {
    const cogUrl = `${baseUrl}/${kb}/luchtfoto-2024-${id}-rgb.tif`;
    const encoded = encodeURIComponent(cogUrl);
    map.addSource(`ortho-${id}`, {
        type: 'raster',
        tiles: [`https://titiler.xyz/cog/tiles/WebMercatorQuad/{z}/{x}/{y}?url=${encoded}`],
        tileSize: 256
    });
    map.addLayer({
        id: `ortho-${id}-layer`,
        type: 'raster',
        source: `ortho-${id}`
    });
});
```

## File Sizes

| Variant | Per Tile | All 356 Tiles |
|---------|----------|---------------|
| RGB COG | ~80–97 MB | ~28 GB |
| RGBNIR COG | ~293–365 MB | ~4.1 GB (12 tiles, KB32 only) |

RGBNIR files are larger because 4-band JPEG cannot use YCbCr colour space optimisation.

## Caveats

- **RGB and NIR are from different seasons.** RGB is from the summer campaign (leaves on);
  CIR/NIR is from the winter campaign (leaves off). Vegetation analysis using the combined
  RGBNIR product should account for this temporal mismatch. Only available for KB 32.
- **JPEG compression is lossy.** Pixel values are not exact radiometric measurements.
  These are visual-grade orthophotos, not calibrated reflectance data.
- **Partial coverage.** This subset covers 12 kaartblad sheets in central Netherlands
  (356 tiles) — not nationwide. See `to-import/beeldmateriaal-orthophotos.md` for how to add
  more tiles from the full nationwide archive.
- **No NoData masking.** Some tiles may have black (0,0,0) edges at tile boundaries.
  Filter these out in analysis: `valid = (red + green + blue) > 0`.

## About Beeldmateriaal Nederland

Beeldmateriaal Nederland (literally "Imagery Netherlands") is the Dutch national
collaboration for aerial photography, established in 2011. It brings together municipalities,
provinces, water boards (waterschappen), Rijkswaterstaat (public works), and Het Kadaster
(land registry) to jointly commission and share aerial surveys.

Two campaigns fly each year:
- **Summer (May–September):** 25 cm RGB orthophotos with full foliage
- **Winter/Spring (February–April):** 7.5 cm (8 cm from 2025) high-resolution stereoscopic
  imagery and Color InfraRed (CIR) during the leafless season

All imagery is published as open data under CC BY 4.0.

Website: https://www.beeldmateriaal.nl/
Open data: https://opendata.beeldmateriaal.nl/
PDOK services: https://service.pdok.nl/hwh/luchtfotorgb/wmts/v1_0

## Related Datasets in This Catalog

- **BAG Light** (kadaster/bag_light) — 11.4M building footprints, ideal for overlay
- **Bestuurlijke Gebieden** (kadaster/bestuurlijke_gebieden) — Administrative boundaries
- **Rijksmonumenten** (rce/rijksmonumenten) — 63K national monument locations
- **Nationale Parken** (rvo/nationale_parken) — 21 national park boundaries
- **Natura 2000** (rvo/natura2000) — 162 protected nature areas
- **Wijken en Buurten** (cbs/wijken_en_buurten) — Neighbourhood statistics
- **Bestand Bodemgebruik** (cbs/bestand_bodemgebruik_2017) — Land use classification

---
*Hand-maintained agent guide (ported from this collection's llms.txt in August 2026). Update it alongside collection.json.*

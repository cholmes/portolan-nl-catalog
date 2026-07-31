# Nationale Parken (National Parks of the Netherlands)

## Overview

This dataset contains the official boundaries of all 21 **Nationale Parken** (National Parks) of the Netherlands. Each feature is a Multi Polygon representing the designated boundary of a national park, along with metadata about its name, area, designation date, and source organization.

The data is published by **RVO** (Rijksdienst voor Ondernemend Nederland / Netherlands Enterprise Agency) through **PDOK** (Publieke Dienstverlening Op de Kaart), the Dutch government's central geodata platform.

| Property | Value |
|----------|-------|
| **Provider** | RVO (Rijksdienst voor Ondernemend Nederland) |
| **Source** | [PDOK OGC API Features](https://api.pdok.nl/rvo/nationale-parken/ogc/v1/) |
| **Format** | GeoJSON |
| **CRS** | EPSG:28992 (Amersfoort / RD New) |
| **Feature count** | 21 |
| **License** | CC0-1.0 (public domain, assumed) |
| **Download date** | 2026-05-07 |

---

## What Are Nationale Parken?

Nationale Parken are large, contiguous natural areas of national and international importance in the Netherlands. They were originally established starting in the 1980s (though Veluwezoom dates to 1930 and De Hoge Veluwe to 1935) to protect significant landscapes and ecosystems.

The parks cover a wide range of landscape types:

- **Coastal dunes**: Zuid-Kennemerland, Duinen van Texel
- **Forests and heathlands**: De Hoge Veluwe, Veluwezoom, Utrechtse Heuvelrug, Sallandse Heuvelrug
- **Wetlands and marshes**: De Biesbosch, Weerribben-Wieden, De Alde Feanen, Lauwersmeer
- **Peat bogs**: De Groote Peel, Dwingelderveld
- **River landscapes**: Drentsche Aa
- **Tidal estuary**: Oosterschelde
- **Island**: Schiermonnikoog
- **Cross-border**: Grenspark De Zoom - Kalmthoutse Heide (Netherlands-Belgium)
- **Reclaimed land**: Nieuw Land (Flevoland polders)

### 2023 Reform

In 2023, the Dutch government reformed the National Parks system. Key changes:

- **Provincial management**: Provinces now have primary responsibility for managing the parks, replacing the earlier system of independent park organizations.
- **Nationale Parken Bureau**: A new coordinating bureau was established to support the network of parks and ensure quality standards.
- **Expansion**: The system is open to new parks — the most recent addition is **Nationaal Park Van Gogh** in Noord-Brabant, designated on 15 October 2024 (nr 22, the largest park at nearly 49,265 hectares).

### Difference from Natura 2000

It is important to distinguish Nationale Parken from **Natura 2000** areas:

| Aspect | Nationale Parken | Natura 2000 |
|--------|-----------------|-------------|
| **Legal basis** | Dutch national policy | EU Birds Directive & Habitats Directive |
| **Designation** | By the Netherlands (provinces + Secretary of State) | By EU member states, approved by European Commission |
| **Focus** | Landscape, recreation, education, nature conservation | Strict habitat and species protection |
| **Number** | 21 parks | ~160 areas in the Netherlands |
| **Management** | Provinces (since 2023 reform) | Ministry of Agriculture, Nature and Food Quality |
| **Overlap** | Many Nationale Parken overlap with Natura 2000 areas, but they are distinct legal designations |

A third related designation is the **Natuurnetwerk Nederland (NNN)**, the national ecological network that includes all National Parks plus ecological corridors and development zones. NNN boundaries are set by individual provinces and are much more extensive.

---

## Provider: RVO

**RVO** (Rijksdienst voor Ondernemend Nederland / Netherlands Enterprise Agency) is an executive agency of the Dutch Ministry of Economic Affairs and Climate Policy. While RVO is best known for business subsidies and energy policy, it also manages several nature-related datasets on behalf of the Ministry of Agriculture, Nature and Food Quality, including:

- Nationale Parken (this dataset)
- Natura 2000 areas
- Beschermde Natuurmonumenten (Protected Nature Monuments)

RVO publishes these datasets through PDOK under a CC0 (public domain) license.

Website: [https://www.rvo.nl/](https://www.rvo.nl/)

---

## Complete Park List

The dataset contains 21 parks, listed here by designation number:

| Nr | Name | Hectares | Designated | Province/Source |
|----|------|----------|------------|-----------------|
| 1 | Veluwezoom | 5,015 | 1930 | Natuurmonumenten |
| 2 | De Hoge Veluwe | 5,105 | 1935 | St. Hoge Veluwe |
| 3 | Schiermonnikoog | 6,838 | 1989 | Friesland |
| 4 | Dwingelderveld | 3,766 | 1991 | NP2002+BIP |
| 5 | De Groote Peel | 1,314 | 1993 | NP2002+BIP+secr. |
| 6 | De Biesbosch | 8,980 | 1994 | SBB Noord-Brabant |
| 7 | De Meinweg | 2,064 | 1995 | NP2002+BIP+secr. |
| 8 | Zuid-Kennemerland | 3,568 | 1995 | NP2002+BIP |
| 9 | De Maasduinen | 4,171 | 1996 | Limburg |
| 10 | Drents-Friese Wold | 5,552 | 1999 | NP2002+BIP |
| 11 | Grenspark De Zoom - Kalmthoutse Heide | 3,833 | 2001 | NP1999+JPG secr. |
| 13 | Duinen van Texel | 4,685 | 2002 | NP2002+BIP |
| 14 | Oosterschelde | 37,989 | 2002 | Zeeland |
| 15 | Drentsche Aa | 33,123 | 2002 | Drenthe |
| 16 | Utrechtse Heuvelrug | 11,342 | 2013 | Utrecht |
| 17 | Lauwersmeer | 6,010 | 2003 | Friesland |
| 18 | Sallandse Heuvelrug | 2,733 | 2004 | NP2002+BIP+secr. |
| 19 | De Alde Feanen | 3,374 | 2006 | Friesland |
| 20 | Weerribben-Wieden | 10,270 | 2009 | Overijssel |
| 21 | Nieuw Land | 28,904 | 2018 | Flevoland |
| 22 | Van Gogh | 49,265 | 2024 | Noord-Brabant |

Note: There is no park numbered 12. The numbering skips from 11 to 13.

---

## Schema

| Column | Type | Dutch | English | Notes |
|--------|------|-------|---------|-------|
| `id` | String | Uniek ID | Unique ID | UUID format (e.g. `d002c621-6ef9-51fa-ad82-a73dae295826`) |
| `bron` | String | Bron | Source | Organization that supplied the boundary. Values include province names (e.g. "Prov. Friesland"), Staatsbosbeheer branches ("SBB Noord-Brabant"), Natuurmonumenten, and coded references like "NP2002+BIP+secr." (referring to the 2002 National Parks plan + spatial implementation program + Secretary of State approval). |
| `datum` | Date | Datum | Date | Designation or establishment date. Format: YYYY/MM/DD. Oldest: 1930-01-01 (Veluwezoom). Newest: 2024-10-15 (Van Gogh). |
| `fiat_secr` | String | Fiat secretaris | Secretary approval | Whether the Secretary of State approved the designation. Values: "Ja" (Yes), blank/whitespace (one case: Duinen van Texel). |
| `hectares` | Real | Hectares | Hectares | Area in hectares. Smallest: 1,314 (De Groote Peel). Largest: 49,265 (Van Gogh). Note: this is the official area, which may differ from area computed from geometry. |
| `instrument` | String | Instrument | Instrument | Type of protection instrument. Always "Nationaal Park" in this dataset. |
| `naam` | String | Naam | Name | Park name. Used as the human-readable identifier. |
| `nr` | Integer | Nummer | Number | Sequential designation number. Chronological order. Note: nr 12 is skipped. Range: 1-22. |
| `objectid` | Integer | Object-ID | Object ID | Internal database object identifier. Not meaningful for analysis — use `nr` or `naam` instead. |

### Understanding the `bron` (source) field

The `bron` field indicates which organization originally supplied the park boundary data. The values are not fully standardized:

- **Province names**: "Prov. Friesland", "Prov. Zeeland", "prov. Limburg" (note inconsistent capitalization)
- **Nature organizations**: "Natuurmonumenten", "St. Hoge Veluwe", "SBB Noord-Brabant" (Staatsbosbeheer)
- **Coded references**: "NP2002+BIP" and "NP2002+BIP+secr." refer to the 2002 National Parks review ("Nota Natuur voor Mensen, Mensen voor Natuur") and the "Besluit Infrastructuur en Planning" (BIP). "+secr." indicates Secretary of State approval was included.
- **Other codes**: "NP1999+JPG secr." references an earlier planning document.

---

## Data Quality Notes

- **Completeness**: The dataset is a complete enumeration of all 21 designated National Parks. No parks are missing.
- **Currency**: The most recently added park is Van Gogh (2024). The dataset appears to be actively maintained.
- **Geometry complexity**: Some parks have complex multi-polygon boundaries. Parks like Oosterschelde (a tidal estuary) and De Biesbosch (a freshwater tidal area) include water bodies within their boundaries, making them geometrically complex.
- **Area discrepancies**: The `hectares` attribute represents the official designated area, which may differ from area computed directly from the geometry (due to projection effects, water body inclusion, or boundary generalization).
- **Missing values**: Duinen van Texel has a blank `fiat_secr` value, suggesting its Secretary of State approval status is unclear or pending.
- **CRS**: The data is in EPSG:28992 (Amersfoort / RD New), the Dutch national coordinate reference system. This CRS is only valid within the Netherlands. For web mapping or international use, reproject to EPSG:4326 (WGS84).
- **Source inconsistency**: The `bron` field has inconsistent capitalization ("Prov." vs "prov.") and mixes organizational names with coded planning references.

---

## Working with the Data

### Inspecting with ogrinfo

```bash
# Summary info
ogrinfo -so data/nationale_parken.geojson nationaleparken

# All attributes (no geometry)
ogrinfo -al -geom=NO data/nationale_parken.geojson nationaleparken

# Feature count
ogrinfo -al -geom=NO data/nationale_parken.geojson nationaleparken | grep "naam" | wc -l
```

### DuckDB Queries

DuckDB can read GeoJSON directly with the spatial extension:

```sql
-- Load the spatial extension
INSTALL spatial;
LOAD spatial;

-- Read the GeoJSON file
SELECT naam, hectares, datum, bron
FROM ST_Read('data/nationale_parken.geojson')
ORDER BY hectares DESC;

-- Find the largest parks
SELECT naam, ROUND(hectares, 0) AS hectares_rounded
FROM ST_Read('data/nationale_parken.geojson')
ORDER BY hectares DESC
LIMIT 5;
-- Van Gogh (49265), Oosterschelde (37989), Drentsche Aa (33123),
-- Nieuw Land (28904), Utrechtse Heuvelrug (11342)

-- Parks designated before 2000
SELECT naam, datum, bron
FROM ST_Read('data/nationale_parken.geojson')
WHERE datum < '2000-01-01'
ORDER BY datum;

-- Total area of all parks
SELECT
  COUNT(*) AS park_count,
  ROUND(SUM(hectares), 0) AS total_hectares,
  ROUND(SUM(hectares) / 100, 0) AS total_km2
FROM ST_Read('data/nationale_parken.geojson');
-- 21 parks, ~239,296 hectares, ~2,393 km2

-- Parks by source type
SELECT bron, COUNT(*) AS count, ROUND(SUM(hectares), 0) AS total_ha
FROM ST_Read('data/nationale_parken.geojson')
GROUP BY bron
ORDER BY count DESC;

-- Compute area from geometry and compare with attribute
-- (note: geometry is in EPSG:28992, so area is in m2)
SELECT
  naam,
  hectares AS official_ha,
  ROUND(ST_Area(geom) / 10000, 2) AS computed_ha,
  ROUND(hectares - ST_Area(geom) / 10000, 2) AS difference_ha
FROM ST_Read('data/nationale_parken.geojson')
ORDER BY ABS(hectares - ST_Area(geom) / 10000) DESC;
```

### Python with GeoPandas

```python
import geopandas as gpd

# Read the GeoJSON
gdf = gpd.read_file("data/nationale_parken.geojson")

# Basic info
print(f"CRS: {gdf.crs}")        # EPSG:28992
print(f"Features: {len(gdf)}")  # 21
print(gdf.columns.tolist())

# Summary statistics
print(gdf[["naam", "hectares", "datum"]].sort_values("hectares", ascending=False))

# Reproject to WGS84 for web mapping
gdf_wgs84 = gdf.to_crs(epsg=4326)
gdf_wgs84.to_file("data/nationale_parken_4326.geojson", driver="GeoJSON")

# Quick plot
gdf.plot(column="hectares", legend=True, figsize=(10, 12),
         cmap="YlGn", edgecolor="black", linewidth=0.5)
```

### Convert to GeoParquet for Portolan

For inclusion in the Portolan catalog, the data needs to be converted to GeoParquet in EPSG:4326:

```bash
# Convert GeoJSON (EPSG:28992) to GeoParquet (EPSG:4326) using ogr2ogr
ogr2ogr -f Parquet \
  data/nationale_parken.parquet \
  data/nationale_parken.geojson \
  -t_srs EPSG:4326
```

Or in Python:

```python
import geopandas as gpd

gdf = gpd.read_file("data/nationale_parken.geojson")
gdf_4326 = gdf.to_crs(epsg=4326)
gdf_4326.to_parquet("data/nationale_parken.parquet")
```

### Generate PMTiles for Visualization

Following the Portolan project convention:

```bash
ogr2ogr -f GeoJSONSeq /vsistdout/ data/nationale_parken.parquet | \
  tippecanoe -o data/nationale_parken.pmtiles -zg \
  --drop-densest-as-needed --extend-zooms-if-still-dropping \
  -l nationale_parken --force
```

### Generate a Thumbnail

```python
import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as ctx

gdf = gpd.read_file("data/nationale_parken.geojson").to_crs(epsg=3857)

fig, ax = plt.subplots(1, 1, figsize=(8, 10))
gdf.plot(ax=ax, color="forestgreen", alpha=0.5, edgecolor="darkgreen", linewidth=1)
ctx.add_basemap(ax, source=ctx.providers.CartoDB.Positron)
ax.set_axis_off()
ax.set_title("Nationale Parken", fontsize=14, fontweight="bold")
fig.savefig("data/thumbnail_.png", dpi=100, bbox_inches="tight")
plt.close()
```

---

## CRS Information

The data is natively in **EPSG:28992** (Amersfoort / RD New), the standard Dutch national coordinate reference system. Key facts:

- **Projection**: Oblique Stereographic (Double)
- **Datum**: Amersfoort
- **Units**: Metres
- **Valid area**: Netherlands mainland only (not the Caribbean Netherlands)
- **Origin**: False easting 155000, False northing 463000

For web mapping (Leaflet, MapLibre, etc.) or Portolan catalog inclusion, reproject to **EPSG:4326** (WGS84):

```bash
ogr2ogr -f GeoJSON output_4326.geojson input_28992.geojson -t_srs EPSG:4326
```

Be aware that area calculations should be done in the native EPSG:28992 projection or using geodesic methods, not in EPSG:4326 (which would give incorrect results at Dutch latitudes).

---

## Update Frequency and Versioning

National Park boundaries change **infrequently**. Changes occur when:

- A new park is designated (most recent: Van Gogh, October 2024)
- An existing park boundary is adjusted
- The national parks system is reformed (as happened in 2023)

There is no fixed update schedule. The dataset on PDOK is updated "as needed" when official boundary changes occur. For version tracking, note the download date (2026-05-07) and compare with the PDOK metadata page for any updates.

The OGC API Features endpoint at PDOK always serves the current version of the data. There is no built-in versioning or change log.

---

## Links and References

### Official Data Sources

- **PDOK Dataset page**: [https://www.pdok.nl/introductie/-/cms/nationale-parken](https://www.pdok.nl/introductie/-/cms/nationale-parken)
- **OGC API Features endpoint**: [https://api.pdok.nl/rvo/nationale-parken/ogc/v1/](https://api.pdok.nl/rvo/nationale-parken/ogc/v1/)
- **Collection metadata**: [https://api.pdok.nl/rvo/nationale-parken/ogc/v1/collections/nationaleparken](https://api.pdok.nl/rvo/nationale-parken/ogc/v1/collections/nationaleparken)
- **Items (features)**: [https://api.pdok.nl/rvo/nationale-parken/ogc/v1/collections/nationaleparken/items](https://api.pdok.nl/rvo/nationale-parken/ogc/v1/collections/nationaleparken/items)

### About National Parks

- **Nationale Parken Bureau**: [https://www.nationaleparken.nl/](https://www.nationaleparken.nl/)
- **RVO Nationale Parken page**: [https://www.rvo.nl/onderwerpen/nationale-parken](https://www.rvo.nl/onderwerpen/nationale-parken)
- **Wikipedia (NL)**: [https://nl.wikipedia.org/wiki/Lijst_van_nationale_parken_in_Nederland](https://nl.wikipedia.org/wiki/Lijst_van_nationale_parken_in_Nederland)

### Related Datasets on PDOK

- **Natura 2000**: [https://www.pdok.nl/introductie/-/cms/natura-2000](https://www.pdok.nl/introductie/-/cms/natura-2000)
- **Beschermde Natuurmonumenten**: Published by RVO via PDOK
- **Natuurnetwerk Nederland (NNN)**: Published by individual provinces

### Provider

- **RVO**: [https://www.rvo.nl/](https://www.rvo.nl/)
- **PDOK**: [https://www.pdok.nl/](https://www.pdok.nl/)

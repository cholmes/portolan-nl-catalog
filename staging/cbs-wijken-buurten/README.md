# CBS Wijken en Buurten (Neighborhoods and Districts with Demographics)

The **CBS Wijk- en Buurtkaart** is the premier Dutch demographic geodataset. Published annually by [CBS (Centraal Bureau voor de Statistiek / Statistics Netherlands)](https://www.cbs.nl/), it provides population, household, age, marital status, migration background, urbanity, and area statistics at the finest available geographic granularity across the entire Netherlands.

If you need to answer "how many people live in neighborhood X?" or "which neighborhoods are the most urban / youngest / most diverse?" -- this is the dataset.

| Property | Value |
|----------|-------|
| **Provider** | CBS (Centraal Bureau voor de Statistiek) |
| **License** | CC BY 4.0 |
| **Format** | GeoPackage (GPKG) |
| **CRS** | EPSG:28992 (Amersfoort / RD New) |
| **Coverage** | All of the Netherlands |
| **Current year** | 2025 |
| **Available years** | 2021, 2022, 2023, 2024, 2025 |
| **Download** | [wijkenbuurten_2025.gpkg](https://service.pdok.nl/cbs/wijkenbuurten/2025/atom/downloads/wijkenbuurten_2025.gpkg) (~209 MB) |
| **Atom feed** | [index.xml](https://service.pdok.nl/cbs/wijkenbuurten/2025/atom/index.xml) |
| **OGC API** | [ogc/v1](https://api.pdok.nl/cbs/wijken-en-buurten-2025/ogc/v1) |

---

## What are Wijken en Buurten?

The Netherlands uses a hierarchical system of statistical areas defined by CBS for demographic reporting:

```
Nederland (country)
 └── Provincie (province) — 12 total
      └── Gemeente (municipality) — 342 as of 2025
           └── Wijk (district) — statistical subdivision of a municipality
                └── Buurt (neighborhood) — finest-grained unit, ~14,800 total
```

- A **buurt** (neighborhood) is the smallest statistical area, typically containing a few hundred to a few thousand residents. Examples: "Binnenstad-Noord" in Groningen, "Jordaan" in Amsterdam.
- A **wijk** (district) is an aggregation of one or more buurten within a municipality. Larger municipalities may have dozens of wijken; small villages may have just one.
- A **gemeente** (municipality) is the main Dutch administrative unit. Each gemeente contains all the wijken and buurten within its territory.

This dataset provides **all three levels** as separate layers in a single GeoPackage, each carrying the same ~40 statistical columns.

---

## The Three Layers

### 1. buurten (Neighborhoods)

The finest-grained layer. **14,823 features** total, of which approximately 14,230 carry actual demographic data. The remainder are water-only areas or the "Buitenland" (foreign territory) boundary marker with suppressed statistics.

- **Geometry:** Multi Polygon
- **ID column:** `buurtcode` (e.g., `BU00140000`)
- **Name column:** `buurtnaam` (e.g., "Binnenstad-Noord")
- **Parent references:** `wijkcode`, `gemeentecode`, `gemeentenaam`

### 2. wijken (Districts)

Mid-level aggregation. Each wijk aggregates one or more buurten.

- **Geometry:** Multi Polygon
- **ID column:** `wijkcode` (e.g., `WK001400`)
- **Name column:** `wijknaam`
- **Parent references:** `gemeentecode`, `gemeentenaam`

### 3. gemeenten (Municipalities)

Top-level administrative units. **424 features** (more than the 342 current municipalities -- includes some historical/special entries).

- **Geometry:** Multi Polygon
- **ID column:** `gemeentecode` (e.g., `GM0014`)
- **Name column:** `gemeentenaam` (e.g., "Groningen")

---

## The CBS Code System

CBS area codes encode the hierarchical relationship between levels. Understanding the code structure is essential for joining layers or building parent-child relationships.

```
BU 0014 00 00
│  │    │  │
│  │    │  └── Buurt number within wijk (00)
│  │    └───── Wijk number within gemeente (00)
│  └────────── Gemeente code (0014 = Groningen)
└───────────── Prefix: BU=buurt, WK=wijk, GM=gemeente
```

**Examples:**

| Code | Level | Meaning |
|------|-------|---------|
| `GM0014` | Gemeente | Municipality of Groningen |
| `WK001400` | Wijk | District 00 within Groningen |
| `WK001401` | Wijk | District 01 within Groningen |
| `BU00140000` | Buurt | Neighborhood 00 in wijk 00 in Groningen |
| `BU00140103` | Buurt | Neighborhood 03 in wijk 01 in Groningen |

**Extracting parent codes:**
- Gemeente from buurt: strip "BU", take first 4 digits, prepend "GM" -> `BU00140000` -> `GM0014`
- Wijk from buurt: strip "BU", take first 6 digits, prepend "WK" -> `BU00140000` -> `WK001400`
- Gemeente from wijk: strip "WK", take first 4 digits, prepend "GM" -> `WK001400` -> `GM0014`

---

## Complete Column Schema

All three layers share the same statistical columns (42 total). The only difference is the ID/name columns at the top (buurtcode/wijkcode/gemeentecode, buurtnaam/wijknaam/gemeentenaam).

### Identification Columns

| Column | Type | Dutch | English | Notes |
|--------|------|-------|---------|-------|
| `buurtcode` / `wijkcode` / `gemeentecode` | String | Code | Area code | CBS hierarchical code with BU/WK/GM prefix |
| `buurtnaam` / `wijknaam` / `gemeentenaam` | String | Naam | Area name | Human-readable name |
| `wijkcode` | String | Wijkcode | Parent district code | Buurten layer only |
| `gemeentecode` | String | Gemeentecode | Municipality code | On buurten and wijken layers |
| `gemeentenaam` | String | Gemeentenaam | Municipality name | On buurten and wijken layers |

### Administrative Metadata

| Column | Type | Dutch | English | Notes |
|--------|------|-------|---------|-------|
| `indelingswijziging_wijken_en_buurten` | Integer | Indelingswijziging | Boundary change flag | 1 = boundaries changed vs. previous year, 0 = unchanged |
| `water` | String | Water | Water area | "JA" = water body, "NEE" = land area |
| `meest_voorkomende_postcode` | String | Meest voorkomende postcode | Most common postal code | Dominant 4-digit postal code (PC4) |
| `dekkingspercentage` | Integer | Dekkingspercentage | Coverage percentage | How well the area aligns with the dominant postal code |

### Urbanity and Density

| Column | Type | Dutch | English | Notes |
|--------|------|-------|---------|-------|
| `omgevingsadressendichtheid` | Integer | Omgevingsadressendichtheid | Surrounding address density | Average addresses within 1 km radius of each address |
| `stedelijkheid_adressen_per_km2` | Integer | Stedelijkheid | Urbanity class | 1-5 scale (see below) |
| `bevolkingsdichtheid_inwoners_per_km2` | Integer | Bevolkingsdichtheid | Population density | Residents per km2 of land area |

**Stedelijkheid (Urbanity) Classification:**

| Value | Dutch | English | Address density |
|-------|-------|---------|-----------------|
| 1 | Zeer sterk stedelijk | Very highly urban | >= 2,500 addresses/km2 |
| 2 | Sterk stedelijk | Highly urban | 1,500 - 2,500 addresses/km2 |
| 3 | Matig stedelijk | Moderately urban | 1,000 - 1,500 addresses/km2 |
| 4 | Weinig stedelijk | Slightly urban | 500 - 1,000 addresses/km2 |
| 5 | Niet stedelijk | Rural | < 500 addresses/km2 |

### Population

| Column | Type | Dutch | English |
|--------|------|-------|---------|
| `aantal_inwoners` | Integer | Aantal inwoners | Total population |
| `mannen` | Integer | Mannen | Male population |
| `vrouwen` | Integer | Vrouwen | Female population |

### Age Distribution (percentages)

| Column | Type | Dutch | English |
|--------|------|-------|---------|
| `percentage_personen_0_tot_15_jaar` | Integer | % 0 tot 15 jaar | % children (0-14) |
| `percentage_personen_15_tot_25_jaar` | Integer | % 15 tot 25 jaar | % young adults (15-24) |
| `percentage_personen_25_tot_45_jaar` | Integer | % 25 tot 45 jaar | % young working age (25-44) |
| `percentage_personen_45_tot_65_jaar` | Integer | % 45 tot 65 jaar | % older working age (45-64) |
| `percentage_personen_65_jaar_en_ouder` | Integer | % 65 jaar en ouder | % elderly (65+) |

These five percentages should sum to approximately 100 for valid areas.

### Marital Status (percentages)

| Column | Type | Dutch | English |
|--------|------|-------|---------|
| `percentage_ongehuwd` | Integer | % ongehuwd | % never married |
| `percentage_gehuwd` | Integer | % gehuwd | % married |
| `percentage_gescheid` | Integer | % gescheid | % divorced |
| `percentage_verweduwd` | Integer | % verweduwd | % widowed |

These four percentages should sum to approximately 100 for valid areas.

### Households

| Column | Type | Dutch | English |
|--------|------|-------|---------|
| `aantal_huishoudens` | Integer | Aantal huishoudens | Number of households |
| `percentage_eenpersoonshuishoudens` | Integer | % eenpersoonshuishoudens | % single-person households |
| `percentage_huishoudens_zonder_kinderen` | Integer | % huishoudens zonder kinderen | % couples without children |
| `percentage_huishoudens_met_kinderen` | Integer | % huishoudens met kinderen | % families with children |
| `gemiddelde_huishoudsgrootte` | Real | Gemiddelde huishoudgrootte | Average household size |

### Migration Background (herkomstland)

CBS uses the concept of "herkomstland" (country of origin / migration background) to classify the population. The definition is based on the birthplace of a person and their parents:

- **Dutch background (herkomstland Nederland):** Both parents were born in the Netherlands.
- **Migration background:** At least one parent was born abroad. Further subdivided by:
  - **European (excl. NL)** vs. **non-European** origin
  - **First generation** (born abroad) vs. **second generation** (born in the Netherlands)

Note: CBS updated its terminology in 2022, replacing "westers/niet-westers" (Western/non-Western) with "European/non-European" and "herkomstland" (country of origin). The column names in this dataset reflect the new terminology.

#### Summary columns (total for each background)

| Column | Type | Dutch | English |
|--------|------|-------|---------|
| `percentage_met_herkomstland_nederland` | Integer | % herkomstland Nederland | % Dutch background |
| `percentage_met_herkomstland_uit_europa_excl_nl` | Integer | % herkomstland Europa (excl. NL) | % European background |
| `percentage_met_herkomstland_buiten_europa` | Integer | % herkomstland buiten Europa | % non-European background |

These three percentages should sum to approximately 100 for valid areas.

#### Detailed columns (by generation)

| Column | Type | Dutch | English |
|--------|------|-------|---------|
| `percentage_geb_in_nl_met_herkomstland_nederland` | Integer | % geboren in NL, herkomstland NL | % born in NL, Dutch background |
| `perc_geb_in_nl_met_herkomstland_in_europa_ex_nl` | Integer | % geboren in NL, herkomstland Europa | % born in NL, European background (2nd gen) |
| `perc_geb_in_nl_met_herkomstland_buiten_europa` | Integer | % geboren in NL, herkomstland buiten Europa | % born in NL, non-European background (2nd gen) |
| `perc_geb_buiten_nl_met_herkomstlnd_in_europa_ex_nl` | Integer | % geboren buiten NL, herkomstland Europa | % born abroad, European background (1st gen) |
| `perc_geb_buiten_nl_met_herkomstlnd_buiten_europa` | Integer | % geboren buiten NL, herkomstland buiten Europa | % born abroad, non-European background (1st gen) |

### Area Measurements

| Column | Type | Dutch | English |
|--------|------|-------|---------|
| `oppervlakte_totaal_in_ha` | Integer | Oppervlakte totaal (ha) | Total area in hectares |
| `oppervlakte_land_in_ha` | Integer | Oppervlakte land (ha) | Land area in hectares |
| `oppervlakte_water_in_ha` | Integer | Oppervlakte water (ha) | Water area in hectares |

Total = land + water. Population density is calculated from land area only.

### Year and Composite Key

| Column | Type | Dutch | English |
|--------|------|-------|---------|
| `jrstatcode` | String | Jaar + statistisch code | Year + area code composite | e.g., "2025BU00140000" |
| `jaar` | Integer | Jaar | Year | Reference year (e.g., 2025) |

---

## The -99997 Sentinel Value

CBS uses **-99997** as a sentinel value meaning "data not available or suppressed." This is NOT a valid statistical value -- it must be filtered out before any analysis.

### Why values are suppressed

1. **Privacy protection:** Areas with too few residents (typically fewer than 50) have their statistics suppressed to prevent identification of individuals. This is required under Dutch statistical disclosure rules.

2. **Water-only areas:** Areas where `water = "JA"` (seas, lakes, major rivers) have no residential population and all demographic columns are -99997.

3. **Buitenland:** A special boundary-marker entry labeled "Buitenland" (Foreign) exists in each layer with all values set to -99997. It represents the area outside the Netherlands.

4. **Not applicable:** Some statistics may genuinely not apply to certain areas.

### How to handle -99997

**In SQL / DuckDB:**
```sql
-- Filter out suppressed values
SELECT buurtnaam, aantal_inwoners
FROM buurten
WHERE aantal_inwoners != -99997;

-- Replace with NULL for aggregations
SELECT AVG(CASE WHEN aantal_inwoners != -99997 THEN aantal_inwoners END) AS avg_pop
FROM buurten;
```

**In Python / pandas:**
```python
import geopandas as gpd

gdf = gpd.read_file("wijkenbuurten_2025.gpkg", layer="buurten")
gdf = gdf.replace(-99997, pd.NA)
```

**In DuckDB with spatial extension:**
```sql
-- DuckDB automatically handles GeoPackage
SELECT * FROM st_read('wijkenbuurten_2025.gpkg', layer='buurten')
WHERE aantal_inwoners != -99997;
```

---

## Water Areas

The `water` column distinguishes land areas from water bodies:

- **`NEE`** (No): Land area with potential residential population
- **`JA`** (Yes): Water body (North Sea, IJsselmeer, major lakes and rivers)

Water areas exist at all three levels. A buurt can be entirely water (e.g., a section of the Wadden Sea assigned to a coastal municipality). For most demographic analyses, filter to `water = 'NEE'`.

---

## Multi-Year Availability and Boundary Changes

CBS publishes a new edition every year. Currently available years: **2021, 2022, 2023, 2024, 2025**.

### Download URLs

Each year follows the same URL pattern:
```
https://service.pdok.nl/cbs/wijkenbuurten/{year}/atom/downloads/wijkenbuurten_{year}.gpkg
```

### Boundary changes over time

Dutch municipalities merge regularly (herindelingen). When a municipality merges, all its buurten and wijken are renumbered with the new gemeente code. This means:

- A buurtcode from 2024 may not exist in 2025 (if the gemeente merged)
- The same physical neighborhood may have different codes in different years
- The `indelingswijziging_wijken_en_buurten` column flags areas whose boundaries changed compared to the previous year (1 = changed, 0 = unchanged)

**Implication for time-series analysis:** You cannot simply join two years by buurtcode unless `indelingswijziging_wijken_en_buurten = 0` for both years. For areas that changed boundaries, you need spatial joins or CBS's mutation tables.

### Reference date

All statistics reflect the situation as of **1 January** of the publication year. The 2025 file contains population data as of 1 January 2025.

---

## Example Queries

### DuckDB

DuckDB can read GeoPackage files directly with the spatial extension.

```sql
-- Install and load spatial extension (first time only)
INSTALL spatial;
LOAD spatial;

-- Most populated neighborhoods in the Netherlands
SELECT buurtnaam, gemeentenaam, aantal_inwoners, bevolkingsdichtheid_inwoners_per_km2
FROM st_read('data/wijkenbuurten_2025.gpkg', layer='buurten')
WHERE aantal_inwoners != -99997
ORDER BY aantal_inwoners DESC
LIMIT 20;

-- Youngest neighborhoods (highest % under 25)
SELECT buurtnaam, gemeentenaam, aantal_inwoners,
       percentage_personen_0_tot_15_jaar + percentage_personen_15_tot_25_jaar AS pct_under_25
FROM st_read('data/wijkenbuurten_2025.gpkg', layer='buurten')
WHERE aantal_inwoners > 1000
  AND percentage_personen_15_tot_25_jaar != -99997
ORDER BY pct_under_25 DESC
LIMIT 20;

-- Most diverse neighborhoods (lowest % Dutch background)
SELECT buurtnaam, gemeentenaam, aantal_inwoners,
       percentage_met_herkomstland_nederland AS pct_dutch,
       percentage_met_herkomstland_uit_europa_excl_nl AS pct_european,
       percentage_met_herkomstland_buiten_europa AS pct_non_european
FROM st_read('data/wijkenbuurten_2025.gpkg', layer='buurten')
WHERE aantal_inwoners > 500
  AND percentage_met_herkomstland_nederland != -99997
ORDER BY percentage_met_herkomstland_nederland ASC
LIMIT 20;

-- Compare urbanity across municipalities
SELECT gemeentenaam, 
       AVG(CASE WHEN stedelijkheid_adressen_per_km2 != -99997 
           THEN stedelijkheid_adressen_per_km2 END) AS avg_urbanity,
       SUM(CASE WHEN aantal_inwoners != -99997 THEN aantal_inwoners ELSE 0 END) AS total_pop
FROM st_read('data/wijkenbuurten_2025.gpkg', layer='buurten')
WHERE water = 'NEE'
GROUP BY gemeentenaam
ORDER BY total_pop DESC
LIMIT 20;

-- Neighborhoods with the most single-person households
SELECT buurtnaam, gemeentenaam, aantal_inwoners,
       percentage_eenpersoonshuishoudens, gemiddelde_huishoudsgrootte
FROM st_read('data/wijkenbuurten_2025.gpkg', layer='buurten')
WHERE aantal_inwoners > 500
  AND percentage_eenpersoonshuishoudens != -99997
ORDER BY percentage_eenpersoonshuishoudens DESC
LIMIT 20;

-- Rural municipalities (highest proportion of stedelijkheid=5 buurten)
SELECT gemeentenaam,
       COUNT(*) AS total_buurten,
       SUM(CASE WHEN stedelijkheid_adressen_per_km2 = 5 THEN 1 ELSE 0 END) AS rural_buurten,
       ROUND(100.0 * SUM(CASE WHEN stedelijkheid_adressen_per_km2 = 5 THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_rural
FROM st_read('data/wijkenbuurten_2025.gpkg', layer='buurten')
WHERE water = 'NEE' AND stedelijkheid_adressen_per_km2 != -99997
GROUP BY gemeentenaam
HAVING COUNT(*) > 5
ORDER BY pct_rural DESC
LIMIT 20;
```

### Python with GeoPandas

```python
import geopandas as gpd
import pandas as pd

# Read the buurten layer
gdf = gpd.read_file("data/wijkenbuurten_2025.gpkg", layer="buurten")

# Replace sentinel values with NaN
numeric_cols = gdf.select_dtypes(include='number').columns
gdf[numeric_cols] = gdf[numeric_cols].replace(-99997, pd.NA)

# Filter to land areas with data
land = gdf[(gdf['water'] == 'NEE') & (gdf['aantal_inwoners'].notna())]

# Top 10 most populated neighborhoods
print(land.nlargest(10, 'aantal_inwoners')[['buurtnaam', 'gemeentenaam', 'aantal_inwoners']])

# Average household size by municipality
print(land.groupby('gemeentenaam')['gemiddelde_huishoudsgrootte'].mean().sort_values())

# Elderly neighborhoods (>40% aged 65+)
elderly = land[land['percentage_personen_65_jaar_en_ouder'] > 40]
print(f"{len(elderly)} neighborhoods with >40% elderly population")

# Join buurten with wijk-level data
wijken = gpd.read_file("data/wijkenbuurten_2025.gpkg", layer="wijken")
# Use wijkcode to join
merged = land.merge(
    wijken[['wijkcode', 'wijknaam']].rename(columns={'wijknaam': 'wijk_naam_from_wijken'}),
    on='wijkcode',
    how='left'
)
```

### Joining with Other Datasets

The `buurtcode`, `wijkcode`, `gemeentecode`, and `meest_voorkomende_postcode` columns enable joins with many other Dutch datasets:

```sql
-- Join with BAG (building register) data aggregated to buurt level
-- Join on buurtcode or via spatial join
SELECT b.buurtnaam, b.aantal_inwoners, bag.num_buildings
FROM buurten b
JOIN bag_per_buurt bag ON b.buurtcode = bag.buurtcode;

-- Join with postal-code-based data via meest_voorkomende_postcode
SELECT b.buurtnaam, b.aantal_inwoners, pc4.avg_income
FROM buurten b
JOIN postcode4_income pc4 ON b.meest_voorkomende_postcode = pc4.postcode4;

-- Join with CBS Gebiedsindelingen for COROP regions
-- (requires spatial join since COROP codes are not in this dataset)
```

---

## Converting to GeoParquet

The source GeoPackage uses EPSG:28992 (RD New). For cloud-native workflows, convert to GeoParquet in EPSG:4326 (WGS 84):

```bash
# Convert buurten layer to GeoParquet (WGS 84)
ogr2ogr -f Parquet data/buurten_2025.parquet \
  data/wijkenbuurten_2025.gpkg \
  -nln buurten \
  -sql "SELECT * FROM buurten" \
  -t_srs EPSG:4326

# Convert wijken layer
ogr2ogr -f Parquet data/wijken_2025.parquet \
  data/wijkenbuurten_2025.gpkg \
  -nln wijken \
  -sql "SELECT * FROM wijken" \
  -t_srs EPSG:4326

# Convert gemeenten layer
ogr2ogr -f Parquet data/gemeenten_2025.parquet \
  data/wijkenbuurten_2025.gpkg \
  -nln gemeenten \
  -sql "SELECT * FROM gemeenten" \
  -t_srs EPSG:4326
```

### Generating PMTiles for web visualization

```bash
# Convert GeoParquet to PMTiles via GeoJSONSeq
ogr2ogr -f GeoJSONSeq /vsistdout/ data/buurten_2025.parquet | \
  tippecanoe -o data/buurten_2025.pmtiles -zg \
  --drop-densest-as-needed --extend-zooms-if-still-dropping \
  -l buurten --force
```

---

## CRS Notes

The source data uses **EPSG:28992 (Amersfoort / RD New)**, the standard Dutch national coordinate reference system (Rijksdriehoekstelsel). This is a projected CRS in meters, optimized for the Netherlands.

- **For spatial analysis in the Netherlands:** Keep EPSG:28992. Area and distance calculations will be accurate.
- **For web mapping:** Convert to EPSG:4326 (WGS 84) or EPSG:3857 (Web Mercator).
- **For GeoParquet / cloud-native:** Convert to EPSG:4326 (required by the GeoParquet specification for interoperability).

```python
import geopandas as gpd

gdf = gpd.read_file("data/wijkenbuurten_2025.gpkg", layer="buurten")
print(gdf.crs)  # EPSG:28992

# Convert to WGS 84
gdf_wgs84 = gdf.to_crs(epsg=4326)
```

---

## Relationship to Other Dutch Geographic Datasets

### CBS Gebiedsindelingen (Area Classifications)

CBS also publishes **Gebiedsindelingen** via PDOK, which provides boundary geometries for a wider range of geographic levels: provinces, COROP regions, labor market regions (arbeidsmarktregio's), police regions, health regions, and more. However, Gebiedsindelingen does **not** include demographic statistics -- it is boundaries only.

**Use Wijken en Buurten** when you need demographic/statistical data at the neighborhood level.
**Use Gebiedsindelingen** when you need boundaries for higher-level regions (COROP, provinces) or non-statistical administrative units.

### Kadaster Bestuurlijke Gebieden (Administrative Boundaries)

Kadaster publishes the **authoritative** administrative boundaries for municipalities, provinces, and the national territory. CBS derives its gemeente boundaries from Kadaster but may simplify them slightly for statistical purposes. The Kadaster boundaries are the legal reference; CBS boundaries are the statistical reference.

### BAG (Basisregistratie Adressen en Gebouwen)

The BAG contains individual addresses and buildings. It can be aggregated to buurt level for analysis that goes beyond what CBS provides (e.g., building age, building function, number of addresses). The `omgevingsadressendichtheid` column in this dataset is derived from BAG data.

### BRT (Basisregistratie Topografie)

The topographic base register. Not directly related, but useful as a basemap when visualizing buurt-level data.

---

## Sample Data

As an illustration, here is the data for **Binnenstad-Noord** in Groningen (buurtcode `BU00140000`):

| Statistic | Value | Interpretation |
|-----------|-------|----------------|
| Population | 4,765 | Medium-sized neighborhood |
| Men / Women | 2,495 / 2,270 | Slightly more men (university students) |
| % aged 15-25 | 48% | Nearly half the population are young adults -- classic university neighborhood |
| Population density | 12,845/km2 | Very dense urban area |
| % single-person households | 82% | Overwhelmingly people living alone (students) |
| Average household size | 1.2 | Among the lowest in the country |
| % Dutch background | 65% | |
| % European background | 20% | International student population |
| % non-European background | 15% | |
| Land area | 37 ha | |
| Water area | 2 ha | |

This neighborhood perfectly illustrates how the data reveals local character: the extreme youth skew and single-person households immediately identify it as a university district.

---

## Tips and Gotchas

1. **Always filter -99997.** Forgetting to exclude sentinel values will produce wildly incorrect averages and sums. A neighborhood with -99997 residents would drag down any mean calculation.

2. **Water areas distort statistics.** Include `WHERE water = 'NEE'` in queries unless you specifically want to analyze water bodies.

3. **Percentages are integers.** All percentage columns are rounded to whole numbers (e.g., 48, not 48.3). This introduces small rounding errors when summing percentage columns.

4. **Year-over-year comparison requires care.** Municipal mergers renumber all affected buurten and wijken. Check `indelingswijziging_wijken_en_buurten` before comparing across years.

5. **The GeoPackage is large.** At ~209 MB, reading the full buurten layer takes a moment. Use layer-specific reads (`layer='buurten'`) rather than loading the entire file.

6. **Feature counts exceed administrative counts.** The gemeenten layer has 424 features vs. 342 actual municipalities because it includes special/historical entries. Similarly, buurten includes water-only areas and boundary markers.

7. **Postal code coverage varies.** The `meest_voorkomende_postcode` and `dekkingspercentage` columns are approximations. A buurt may span multiple postal codes; only the most common one is reported.

8. **Migration background terminology changed.** Before 2022, CBS used "westers/niet-westers" (Western/non-Western). Current datasets use "herkomstland" (country of origin) with European/non-European classification. The column names in this dataset use the current terminology.

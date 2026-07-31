# CBS Gebiedsindelingen (Area Classifications)

The CBS Gebiedsindelingen dataset is the single most comprehensive official source of Dutch regional boundary classifications. Published annually by Statistics Netherlands (CBS) and distributed via PDOK, it defines the geographic boundaries for **26 distinct regional classification systems** used across Dutch governance, policy, and statistics.

While other datasets provide individual boundary types (Bestuurlijke Gebieden for precise administrative borders, Wijken en Buurten for neighborhood statistics), Gebiedsindelingen is unique in that it consolidates _every_ classification system into one file and provides a crosswalk table that maps between them all.

## Why So Many Classification Systems?

The Netherlands has a remarkably organized administrative geography, but different government functions require different regional aggregations:

- **Healthcare** is organized by GGD regions and zorgkantoor regions
- **Public safety** is organized by veiligheidsregio (safety regions) and police regional units
- **The judiciary** is organized by arrondissementen (court districts) and ressorten (appeal court districts)
- **Economic analysis** uses COROP regions (comparable to NUTS-3)
- **Employment policy** uses arbeidsmarktregio (labour market regions)
- **Energy transition** uses RES (Regional Energy Strategy) areas
- **Agriculture** uses landbouwgebieden and landbouwgroepen
- **Tourism** uses toeristengebieden and toeristengroepen

All of these classification systems ultimately compose from the same 342 gemeenten (municipalities). The gebiedsindelingen_register table makes this explicit: one row per gemeente, with columns mapping it to every classification it belongs to.

## Area Classification Types

The 2025 edition contains the following 26 area classification types:

### Administrative / Governmental

| Layer | English | Code | Count | Description |
|-------|---------|------|-------|-------------|
| gemeente | Municipalities | GM | 342 | The fundamental unit of Dutch local government. All other classifications aggregate from gemeenten. |
| wijk | Districts | WK | 3,423 | Sub-municipal districts for statistical purposes. Each gemeente is subdivided into wijken. |
| buurt | Neighborhoods | BU | 14,729 | The finest-grained statistical unit. Each wijk is subdivided into buurten. |
| provincie | Provinces | PV | 12 | The 12 Dutch provinces: the primary regional government layer. |
| landsdeel | Country parts | LD | 4 | Four macro-regions: Noord-, Oost-, West-, and Zuid-Nederland. |

### Justice / Safety

| Layer | English | Code | Count | Description |
|-------|---------|------|-------|-------------|
| veiligheidsregio | Safety regions | VR | 25 | Coordinate fire services, disaster response, crisis management, and medical emergency services. |
| regionale_eenheid | Police regional units | RE | 10 | Operational units of the Dutch National Police (since 2013 reorganization). |
| arrondissementsgebied | Court districts | AR | 11 | Jurisdictions of the 11 district courts (rechtbanken). |
| ressort | Appeal court districts | RT | 4 | Jurisdictions of the 4 courts of appeal (gerechtshoven). |
| veiligthuisregio | Safe Home regions | VT | 25 | Service areas for Veilig Thuis organizations handling domestic violence and child abuse reports. |

### Healthcare / Social Services

| Layer | English | Code | Count | Description |
|-------|---------|------|-------|-------------|
| ggdregio | Public health (GGD) regions | GG | 25 | Service areas of the Municipal Health Services, responsible for public health and epidemiology. |
| zorgkantoorregio | Health insurance office regions | ZK | 31 | Regions of health insurance offices administering long-term care (Wlz). |
| jeugdregio | Youth care regions | JZ | 42 | Regions for youth care services, established after the 2015 decentralization. |

### Economy / Labour

| Layer | English | Code | Count | Description |
|-------|---------|------|-------|-------------|
| coropgebied | COROP regions | CR | 40 | The standard classification for regional economic analysis, roughly comparable to EU NUTS-3. Named after the Coordinatiecommissie Regionaal Onderzoeksprogramma. |
| coropsubgebied | COROP sub-regions | CS | 43 | Finer-grained subdivisions of COROP regions. |
| coropplusgebied | COROP+ regions | CP | 52 | Extended COROP classification with additional subdivisions for metropolitan areas. |
| arbeidsmarktregio | Labour market regions | AM | 35 | Regions where labour supply and demand are geographically matched. Used for UWV employment services. |
| regioplus_arbeidsmarktregio | RegioPlus labour market regions | RA | 28 | Alternative labour market classification used by the RegioPlus network. |
| kamervankoophandelregio | Chamber of Commerce regions | KK | 5 | Regions of the KvK for business registration and economic services. |

### Energy / Environment

| Layer | English | Code | Count | Description |
|-------|---------|------|-------|-------------|
| regionale_energiestrategie | Regional Energy Strategy (RES) areas | ES | 30 | Regions designated under the National Climate Agreement for coordinating the energy transition. |
| subres_regio | Sub-RES regions | ET | 40 | Sub-regions within RES areas for localized energy planning. |

### Agriculture / Tourism

| Layer | English | Code | Count | Description |
|-------|---------|------|-------|-------------|
| landbouwgebied | Agricultural areas | LB | 65 | Fine-grained agricultural classification for farm statistics and policy. |
| landbouwgroep | Agricultural groups | LG | 14 | Aggregated groupings of agricultural areas by farming type and landscape. |
| toeristengebied | Tourist areas | TR | 17 | Regions for tourism statistics and visitor pattern analysis. |
| toeristengroep | Tourist groups | TG | 6 | Higher-level tourism aggregation by type (coastal, nature, urban, watersport, etc.). |

### Education

| Layer | English | Code | Count | Description |
|-------|---------|------|-------|-------------|
| regionaalmeld_coordinatiepunt | Regional reporting/coordination points (RMC) | MC | 40 | Regions for combating school dropout, where coordinators track early school leavers. |

## Layer Variants

Each classification type exists in up to three variants:

### Gegeneraliseerd (Generalized)
Simplified polygon geometries suitable for thematic mapping at national and regional scales. Available for all 26 classification types. These are the layers most users want -- the boundaries are cartographically clean and render well at typical map zoom levels.

### Niet-gegeneraliseerd (Non-generalized)
Precise, detailed polygon geometries. Available **only** for the three finest-grained administrative levels:
- `gemeente_niet_gegeneraliseerd` (342 features)
- `wijk_niet_gegeneraliseerd` (3,423 features)
- `buurt_niet_gegeneraliseerd` (14,729 features)

Use these when you need exact boundary precision, for example when determining which buurt a specific address falls in. Note that these layers include an additional `gm_code` column (for wijk and buurt) linking each feature to its parent gemeente.

### Labelpoint
Point geometries representing the centroid of each area, positioned for optimal label placement. Available for all 26 classification types. Useful when you need to place labels on a map or need representative points rather than full polygons.

## Uniform Schema

All generalized and labelpoint layers share the same five-column schema:

| Column | Type | Example | Description |
|--------|------|---------|-------------|
| `statcode` | String(10) | `VR01` | CBS statistical code, unique within each classification type |
| `jrstatcode` | String(14) | `2025VR01` | Year-prefixed code for temporal disambiguation |
| `statnaam` | String(70) | `Groningen` | Human-readable name of the area |
| `rubriek` | String(70) | `veiligheidsregio` | Classification category/rubric |
| `id` | Integer | `1` | Internal sequential identifier |

### The jrstatcode System

Because regional boundaries change over time (municipalities merge, regions are reorganized), CBS prefixes each code with the reference year. The code `GM0014` refers to Groningen in any year, but `2025GM0014` unambiguously refers to Groningen as defined in the 2025 edition. This is essential when working with time series data, as the set of valid codes changes between editions.

### Code Prefix Conventions

Every classification has a consistent two-letter prefix:

```
GM = gemeente           PV = provincie          LD = landsdeel
WK = wijk               BU = buurt              AM = arbeidsmarktregio
RA = regioplus          AR = arrondissement      RT = ressort
CR = COROP              CS = COROP-sub           CP = COROP-plus
VR = veiligheidsregio   GG = GGD-regio           JZ = jeugdregio
ZK = zorgkantoorregio   VT = veiligthuisregio    RE = regionale eenheid
MC = RMC                ES = RES                 ET = sub-RES
KK = KvK-regio          LB = landbouwgebied      LG = landbouwgroep
TR = toeristengebied    TG = toeristengroep
```

## The Register Table

The `gebiedsindelingen_register` table is a non-spatial crosswalk table with 342 rows (one per gemeente). Each row maps a gemeente to every classification it belongs to, with paired `_code` and `_naam` columns:

```
gm_code=GM0014, gm_naam=Groningen
am_code=AM01,   am_naam=Groningen
vr_code=VR01,   vr_naam=Groningen
gg_code=GG0111, gg_naam=GGD Groningen
pv_code=PV20,   pv_naam=Groningen
ld_code=LD01,   ld_naam=Noord-Nederland
...
```

This table is extraordinarily useful for cross-referencing between classification systems without needing spatial operations. For example, to find which veiligheidsregio a gemeente belongs to, simply look up the row by `gm_code` and read the `vr_code` and `vr_naam` columns.

## Example Queries

### List all areas of a specific type
```sql
-- All 25 veiligheidsregio names and codes
SELECT statcode, statnaam FROM veiligheidsregio_gegeneraliseerd ORDER BY statcode;
```

### Find which classification regions a gemeente belongs to
```sql
-- What regions does Amsterdam (GM0363) belong to?
SELECT * FROM gebiedsindelingen_register WHERE gm_code = 'GM0363';
```

### Cross-reference between systems
```sql
-- Which gemeenten are in veiligheidsregio "Amsterdam-Amstelland"?
SELECT gm_code, gm_naam FROM gebiedsindelingen_register
WHERE vr_naam = 'Amsterdam-Amstelland';
```

### Join with CBS StatLine statistics
CBS statistical tables on [StatLine](https://opendata.cbs.nl/statline/) use the same `statcode` values. To map any table's regional data to geographic boundaries:

```python
import geopandas as gpd
import cbsodata  # pip install cbsodata

# Load boundaries
gdf = gpd.read_file("cbsgebiedsindelingen2025.gpkg", layer="gemeente_gegeneraliseerd")

# Load statistics from CBS StatLine (example: population by gemeente)
data = cbsodata.get_data("70072ned")
# Join on statcode
merged = gdf.merge(data, left_on="statcode", right_on="RegioCode")
```

## Relationship to Other Datasets

### Bestuurlijke Gebieden (Kadaster)
The Kadaster's Bestuurlijke Gebieden provides legally precise administrative boundaries for gemeente, provincie, and land (country), derived from cadastral records. Gebiedsindelingen uses CBS-defined generalized boundaries instead, which are better suited for thematic mapping. Use Bestuurlijke Gebieden when you need legally authoritative boundaries; use Gebiedsindelingen when you need the full breadth of classification systems.

### CBS Wijken en Buurten (Kerncijfers)
The Wijken en Buurten dataset enriches buurt/wijk/gemeente boundaries with dozens of demographic and socioeconomic statistics (population, age distribution, income, housing, land use, energy consumption). It covers the same three administrative levels that Gebiedsindelingen provides as non-generalized layers, but adds the statistical payload. Use Gebiedsindelingen for the boundaries themselves and for the full range of classification types; use Wijken en Buurten when you need the statistics.

### CBS StatLine
StatLine is the national statistics database. Its tables reference areas by `statcode`, making Gebiedsindelingen the geographic key for mapping any StatLine dataset.

## Coordinate Reference System

All layers use **EPSG:28992 (Amersfoort / RD New)**, the standard Dutch national coordinate system. To convert to WGS 84 (EPSG:4326) for web mapping:

```bash
ogr2ogr -t_srs EPSG:4326 output.gpkg cbsgebiedsindelingen2025.gpkg layer_name
```

Or in Python:
```python
gdf = gpd.read_file("cbsgebiedsindelingen2025.gpkg", layer="gemeente_gegeneraliseerd")
gdf_wgs84 = gdf.to_crs(epsg=4326)
```

## Available Years

CBS publishes a new edition annually. The following editions are available via PDOK:

| Year | Size | Notes |
|------|------|-------|
| 2016 | 18.1 MB | Earlier editions have fewer layers (no non-generalized buurt/wijk) |
| 2017 | 16.9 MB | |
| 2018 | 17.0 MB | |
| 2019 | 149.2 MB | First edition with non-generalized buurt/wijk/gemeente layers |
| 2020 | 149.9 MB | |
| 2021 | 153.2 MB | |
| 2022 | 155.6 MB | |
| 2023 | 223.1 MB | Largest edition (may contain additional experimental layers) |
| 2024 | 156.0 MB | |
| 2025 | 158.9 MB | Current complete edition (56 layers, 342 gemeenten) |
| 2026 | 2.9 MB | Provisional: basic boundaries only, no buurt/wijk yet |

Historical editions (1995-2015) were previously available but are not in the current PDOK Atom feed. They may be obtainable through CBS directly.

The year-over-year changes primarily reflect:
- **Municipal mergers** (the number of gemeenten decreases almost every year)
- **Region boundary adjustments** (some classification systems are periodically revised)
- **New classification types** being added (e.g., RES areas were added when the Climate Agreement introduced them)

## Data Source

- **Provider:** CBS (Centraal Bureau voor de Statistiek / Statistics Netherlands)
- **Distribution:** PDOK (Publieke Dienstverlening Op de Kaart)
- **Atom feed:** https://service.pdok.nl/cbs/gebiedsindelingen/atom/v1_0/index.xml
- **OGC API:** https://api.pdok.nl/cbs/gebiedsindelingen/ogc/v1
- **Direct download (2025):** https://service.pdok.nl/cbs/gebiedsindelingen/atom/v1_0/downloads/cbsgebiedsindelingen2025.gpkg
- **License:** [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- **Format:** GeoPackage
- **CRS:** EPSG:28992 (Amersfoort / RD New)

# Bestuurlijke Gebieden (Administrative Areas)

The **Bestuurlijke Gebieden** dataset contains the official administrative boundaries of the Netherlands, published by the **Kadaster** (Netherlands Cadastre, Land Registry and Mapping Agency). It defines the three tiers of Dutch government territory: the national boundary, 12 provinces, and 342 municipalities (as of 2026).

This is the single most fundamental reference dataset in Dutch geodata. Nearly every other government dataset uses CBS municipality codes or province codes to identify locations, making these boundaries the essential spatial join key for all Dutch open data work.

## Dutch Administrative Hierarchy

The Netherlands has a three-level administrative structure:

```
Rijk (National Government)
  └── 1 landgebied (national territory)
        └── 12 provincies (provinces)
              └── 342 gemeenten (municipalities, 2026 count)
```

Each level nests cleanly within the one above. Every municipality belongs to exactly one province, and every province belongs to the nation. The dataset encodes these relationships explicitly through `ligt_in_provincie_code` and `ligt_in_land_code` fields.

### The 12 Provinces

| Code | Name |
|------|------|
| PV20 | Groningen |
| PV21 | Friesland (Fryslan) |
| PV22 | Drenthe |
| PV23 | Overijssel |
| PV24 | Flevoland |
| PV25 | Gelderland |
| PV26 | Utrecht |
| PV27 | Noord-Holland |
| PV28 | Zuid-Holland |
| PV29 | Zeeland |
| PV30 | Noord-Brabant |
| PV31 | Limburg |

## Code System

### CBS Municipality Codes

CBS (Centraal Bureau voor de Statistiek / Statistics Netherlands) assigns every municipality a unique 4-digit numeric code. These codes are the universal identifier across all Dutch government data.

In this dataset, codes appear in two forms:

- **`identificatie`**: The raw 4-digit CBS code (e.g., `0363` for Amsterdam)
- **`code`**: The CBS code with a type prefix (e.g., `GM0363`)

The prefix indicates the administrative level:
- **GM** = Gemeente (municipality)
- **PV** = Provincie (province)

### Code Stability

CBS codes are **stable and never reused**. When municipalities merge (herindeling), the merged entity receives a **new** code. The old codes are retired permanently. This means:

- You can safely use CBS codes as foreign keys across datasets from different years
- You must be aware that a code valid in 2020 may not exist in 2026 (the municipality merged)
- Historical analysis requires mapping old codes to new ones

For example, when Weesp merged into Amsterdam in 2022, Weesp's code (GM0457) was retired and its territory absorbed into Amsterdam (GM0363).

## Municipal Mergers (Herindelingen)

The number of Dutch municipalities has been declining for decades as smaller municipalities merge to gain administrative capacity:

| Year | Municipalities | Notable mergers |
|------|---------------|-----------------|
| 2020 | 355 | |
| 2021 | 352 | Beemster merged into Purmerend |
| 2022 | 345 | Weesp into Amsterdam; several Groningen mergers |
| 2023 | 342 | Brielle, Hellevoetsluis, Westvoorne merged into Voorne aan Zee |
| 2024 | 342 | No mergers |
| 2025 | 342 | No mergers |
| 2026 | 342 | No mergers |

Mergers always take effect on January 1st. The dataset is published annually in January to reflect the new situation. Historical editions (2021 through 2026) are available from the same Atom feed for time-series analysis.

## Why This Dataset is Foundational

Almost every Dutch government dataset references administrative areas:

- **CBS statistics** (population, income, housing) are published per municipality
- **BAG** (building/address register) assigns every address to a municipality
- **BRT/BGT** (topographic maps) use administrative boundaries as organizing units
- **Environmental data** (noise, air quality, natura 2000) reference municipalities for reporting
- **Election results** are aggregated by municipality and province
- **Healthcare, education, safety** regions are all defined in terms of which municipalities they contain

Without this dataset, you cannot spatially join or aggregate any of these sources. It is the glue that connects Dutch open data.

## Dataset Details

### Source Information

| Field | Value |
|-------|-------|
| **Provider** | Kadaster |
| **License** | CC BY 4.0 (attribution required) |
| **Format** | GeoPackage (.gpkg) |
| **CRS** | EPSG:28992 (Amersfoort / RD New) |
| **Extent (RD)** | (10425, 306846) - (278026, 621876) |
| **Update frequency** | Annual (January) |
| **Coverage** | European Netherlands (excl. Caribbean municipalities) |
| **Atom feed** | https://service.pdok.nl/kadaster/bestuurlijkegebieden/atom/v1_0/bestuurlijke_gebieden.xml |
| **OGC API** | https://api.pdok.nl/kadaster/brk-bestuurlijke-gebieden/ogc/v1/ |
| **Download** | https://service.pdok.nl/kadaster/brk-bestuurlijke-gebieden/atom/downloads/BestuurlijkeGebieden_2026.gpkg |

### Layer 1: gemeentegebied (Municipal Areas)

**342 features** -- all municipalities of the Netherlands.

| Column | Type | Description |
|--------|------|-------------|
| `identificatie` | String | CBS municipality code, 4-digit (e.g., `0363` for Amsterdam) |
| `naam` | String | Municipality name (e.g., `Amsterdam`) |
| `code` | String | Municipality code with GM prefix (e.g., `GM0363`) |
| `ligt_in_provincie_code` | String | Province code this municipality belongs to (e.g., `PV27`) |
| `ligt_in_provincie_naam` | String | Province name (e.g., `Noord-Holland`) |
| `geom` | MultiPolygon | Municipality boundary geometry |

### Layer 2: provinciegebied (Provincial Areas)

**12 features** -- all provinces of the Netherlands.

| Column | Type | Description |
|--------|------|-------------|
| `identificatie` | String | Province identifier |
| `naam` | String | Province name (e.g., `Noord-Holland`) |
| `code` | String | Province code with PV prefix (e.g., `PV27`) |
| `ligt_in_land_code` | String | Country code |
| `ligt_in_land_naam` | String | Country name (`Nederland`) |
| `geom` | MultiPolygon | Province boundary geometry |

### Layer 3: landgebied (National Territory)

**1 feature** -- the national boundary of the Netherlands.

| Column | Type | Description |
|--------|------|-------------|
| `identificatie` | String | Country identifier |
| `naam` | String | Country name (`Nederland`) |
| `code` | String | Country code |
| `geom` | MultiPolygon | National boundary geometry |

## CRS Notes

The data is published in **EPSG:28992** (Amersfoort / RD New), the standard projected coordinate system for the Netherlands. This is a Stereographic projection optimized for the Netherlands with sub-meter accuracy across the country.

For use in web maps or cloud-native formats, you will typically want to reproject to **EPSG:4326** (WGS84). GDAL/ogr2ogr handles this transformation well:

```bash
ogr2ogr -t_srs EPSG:4326 output.gpkg input.gpkg
```

Note that for applications requiring high geometric accuracy within the Netherlands (e.g., cadastral work, construction), EPSG:28992 is preferred. For visualization and web mapping, EPSG:4326 or EPSG:3857 is standard.

## Converting to GeoParquet

To import into a cloud-native catalog, convert each layer to a separate GeoParquet file, reprojected to WGS84:

```bash
# Convert each layer to GeoParquet (WGS84)
ogr2ogr -f Parquet -t_srs EPSG:4326 \
  gemeentegebied.parquet \
  data/BestuurlijkeGebieden_2026.gpkg \
  gemeentegebied

ogr2ogr -f Parquet -t_srs EPSG:4326 \
  provinciegebied.parquet \
  data/BestuurlijkeGebieden_2026.gpkg \
  provinciegebied

ogr2ogr -f Parquet -t_srs EPSG:4326 \
  landgebied.parquet \
  data/BestuurlijkeGebieden_2026.gpkg \
  landgebied
```

Or using Python with GeoPandas:

```python
import geopandas as gpd

for layer in ['gemeentegebied', 'provinciegebied', 'landgebied']:
    gdf = gpd.read_file(
        'data/BestuurlijkeGebieden_2026.gpkg',
        layer=layer
    )
    gdf = gdf.to_crs(epsg=4326)
    gdf.to_parquet(f'{layer}.parquet')
```

## Example Queries with DuckDB

DuckDB can read GeoParquet files directly, making it ideal for analytical queries.

### Basic exploration

```sql
-- Load the spatial extension
INSTALL spatial; LOAD spatial;

-- List all municipalities in Noord-Holland
SELECT naam, code
FROM read_parquet('gemeentegebied.parquet')
WHERE ligt_in_provincie_naam = 'Noord-Holland'
ORDER BY naam;

-- Count municipalities per province
SELECT ligt_in_provincie_naam AS provincie,
       COUNT(*) AS aantal_gemeenten
FROM read_parquet('gemeentegebied.parquet')
GROUP BY ligt_in_provincie_naam
ORDER BY aantal_gemeenten DESC;
```

### Joining with CBS statistics

The real power of this dataset is joining it with other data sources using the CBS codes:

```sql
-- Join municipality boundaries with CBS population data
-- (assuming you have a CBS Kerncijfers table)
SELECT g.naam,
       g.code,
       s.bevolking_totaal,
       s.bevolkingsdichtheid,
       g.geometry
FROM read_parquet('gemeentegebied.parquet') g
JOIN read_parquet('cbs_kerncijfers.parquet') s
  ON g.code = s.gemeentecode
ORDER BY s.bevolking_totaal DESC;
```

### Joining with BAG addresses

```sql
-- Count BAG addresses per municipality
SELECT g.naam AS gemeente,
       g.ligt_in_provincie_naam AS provincie,
       COUNT(*) AS aantal_adressen
FROM read_parquet('gemeentegebied.parquet') g
JOIN read_parquet('bag_adressen.parquet') a
  ON g.code = a.gemeente_code
GROUP BY g.naam, g.ligt_in_provincie_naam
ORDER BY aantal_adressen DESC
LIMIT 20;
```

### Spatial joins with point data

```sql
-- Find which municipality each RWS monitoring station falls in
SELECT g.naam AS gemeente,
       g.ligt_in_provincie_naam AS provincie,
       m.station_naam
FROM read_parquet('gemeentegebied.parquet') g
JOIN read_parquet('meetstations.parquet') m
  ON ST_Contains(g.geometry, m.geometry);
```

### Aggregating other datasets to province level

```sql
-- Aggregate any municipality-level data to province level
-- using province boundaries for spatial output
SELECT p.naam AS provincie,
       p.code,
       SUM(s.woningvoorraad) AS totaal_woningen,
       p.geometry
FROM read_parquet('provinciegebied.parquet') p
JOIN read_parquet('gemeentegebied.parquet') g
  ON g.ligt_in_provincie_code = p.code
JOIN read_parquet('cbs_woningen.parquet') s
  ON g.code = s.gemeentecode
GROUP BY p.naam, p.code, p.geometry
ORDER BY totaal_woningen DESC;
```

## PMTiles Generation

To generate PMTiles for web map visualization:

```bash
# Municipalities
ogr2ogr -f GeoJSONSeq /vsistdout/ gemeentegebied.parquet | \
  tippecanoe -o gemeentegebied.pmtiles -zg \
  --drop-densest-as-needed --extend-zooms-if-still-dropping \
  -l gemeentegebied --force

# Provinces
ogr2ogr -f GeoJSONSeq /vsistdout/ provinciegebied.parquet | \
  tippecanoe -o provinciegebied.pmtiles -zg \
  --drop-densest-as-needed --extend-zooms-if-still-dropping \
  -l provinciegebied --force
```

## Relationship to CBS Gebiedsindelingen

CBS publishes a broader dataset called **Gebiedsindelingen** (area classifications) that includes many additional boundary types beyond the three core administrative levels:

| Boundary type | Dutch name | Count (approx.) |
|---------------|------------|-----------------|
| COROP regions | COROP-gebieden | 40 |
| Labor market regions | Arbeidsmarktregio's | 35 |
| Safety regions | Veiligheidsregio's | 25 |
| GGD regions | GGD-regio's | 25 |
| Water boards | Waterschappen | 21 |
| RES regions | RES-regio's | 30 |
| Urban areas | Stadsgewesten | ~22 |

All of these higher-level regions are defined as aggregations of municipalities. The CBS codes from Bestuurlijke Gebieden are the linking key. If you need any of these additional boundary types, look at the CBS Gebiedsindelingen dataset -- but the Kadaster Bestuurlijke Gebieden remains the authoritative source for the three core levels (land, provincie, gemeente).

The CBS dataset is available at: https://www.cbs.nl/nl-nl/dossier/nederland-regionaal/geografische-data

## License

This dataset is published under **CC BY 4.0** (Creative Commons Attribution 4.0 International).

You are free to:
- **Share** -- copy and redistribute the material in any medium or format
- **Adapt** -- remix, transform, and build upon the material for any purpose, including commercially

Under the following terms:
- **Attribution** -- You must give appropriate credit to **Kadaster**, provide a link to the license, and indicate if changes were made

Full license text: https://creativecommons.org/licenses/by/4.0/

## File Structure

```
bestuurlijke-gebieden/
  data/
    BestuurlijkeGebieden_2026.gpkg   -- Source GeoPackage (13.8 MB, 3 layers)
  download.sh                         -- Download script
  dataset-info.json                   -- Structured metadata
  README.md                           -- This file
```

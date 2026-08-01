# CBS Gebiedsindelingen (Area Classifications) — Netherlands

## What This Dataset Is

All 26 types of regional area classifications used in Dutch governance and statistics,
published by CBS (Statistics Netherlands) via PDOK. This is the single most comprehensive
official source of Dutch regional boundary classifications — the Rosetta Stone that maps
between every regional subdivision system used in the Netherlands.

Each classification type is a separate GeoParquet file containing generalized (simplified)
polygon boundaries in EPSG:28992 (Amersfoort / RD New). These boundaries are suitable for
thematic mapping and statistical visualization, not precision boundary work. For legally
precise administrative boundaries, use Bestuurlijke Gebieden from Kadaster.

The 342 gemeenten (municipalities) are the fundamental building block — every other
classification is an aggregation of gemeenten. The gebiedsindelingen_register crosswalk
table (not included in this extract) maps each gemeente to all parent classifications.

**Source:** https://service.pdok.nl/cbs/gebiedsindelingen/atom/v1_0/index.xml
**Provider:** CBS (Centraal Bureau voor de Statistiek / Statistics Netherlands)
**License:** CC-BY-4.0
**CRS:** EPSG:28992 (Amersfoort / RD New)
**Year:** 2025

## How to Access

Each classification type is a separate GeoParquet file. Pick the file matching the
regional classification you need. All files share the same schema.

Base URL: `https://data.source.coop/cholmes/portolan-nl/cbs/gebiedsindelingen/`

File naming pattern: `{type}_gegeneraliseerd.parquet`

```python
import duckdb

con = duckdb.connect()
con.execute("INSTALL spatial; LOAD spatial;")

# Example: load gemeente boundaries
URL = 'https://data.source.coop/cholmes/portolan-nl/cbs/gebiedsindelingen/gemeente_gegeneraliseerd.parquet'
df = con.execute(f"SELECT * FROM read_parquet('{URL}') LIMIT 5").df()
```

Files are small (170 KB to 3 MB) so they load quickly in full.

## All 26 Area Classification Types

| File | Dutch Name | English Name | Code | Count |
|------|-----------|--------------|------|-------|
| `gemeente_gegeneraliseerd.parquet` | Gemeente | Municipalities | GM | 342 |
| `wijk_gegeneraliseerd.parquet` | Wijk | Districts | WK | 3,423 |
| `buurt_gegeneraliseerd.parquet` | Buurt | Neighborhoods | BU | 14,729 |
| `provincie_gegeneraliseerd.parquet` | Provincie | Provinces | PV | 12 |
| `landsdeel_gegeneraliseerd.parquet` | Landsdeel | Country parts | LD | 4 |
| `coropgebied_gegeneraliseerd.parquet` | COROP-gebied | COROP regions (~ NUTS-3) | CR | 40 |
| `coropsubgebied_gegeneraliseerd.parquet` | COROP-subgebied | COROP sub-regions | CS | 43 |
| `coropplusgebied_gegeneraliseerd.parquet` | COROP-plusgebied | COROP+ regions | CP | 52 |
| `arbeidsmarktregio_gegeneraliseerd.parquet` | Arbeidsmarktregio | Labour market regions | AM | 35 |
| `regioplus_arbeidsmarktregio_gegeneraliseerd.parquet` | RegioPlus Arbeidsmarktregio | RegioPlus labour market regions | RA | 28 |
| `veiligheidsregio_gegeneraliseerd.parquet` | Veiligheidsregio | Safety regions | VR | 25 |
| `ggdregio_gegeneraliseerd.parquet` | GGD-regio | Public health (GGD) regions | GG | 25 |
| `jeugdregio_gegeneraliseerd.parquet` | Jeugdregio | Youth care regions | JZ | 42 |
| `zorgkantoorregio_gegeneraliseerd.parquet` | Zorgkantoorregio | Health insurance office regions | ZK | 31 |
| `veiligthuisregio_gegeneraliseerd.parquet` | Veilig Thuis-regio | Safe Home regions | VT | 25 |
| `regionale_eenheid_gegeneraliseerd.parquet` | Regionale eenheid | Police regional units | RE | 10 |
| `arrondissementsgebied_gegeneraliseerd.parquet` | Arrondissementsgebied | Court districts | AR | 11 |
| `ressort_gegeneraliseerd.parquet` | Ressort | Appeal court districts | RT | 4 |
| `regionaalmeld_coordinatiepunt_gegeneraliseerd.parquet` | Regionaal Meld- en Coordinatiepunt | School dropout regions (RMC) | MC | 40 |
| `regionale_energiestrategie_gegeneraliseerd.parquet` | Regionale Energiestrategie (RES) | Regional Energy Strategy areas | ES | 30 |
| `subres_regio_gegeneraliseerd.parquet` | Sub-RES-regio | Sub-RES regions | ET | 40 |
| `kamervankoophandelregio_gegeneraliseerd.parquet` | Kamer van Koophandel-regio | Chamber of Commerce regions | KK | 5 |
| `landbouwgebied_gegeneraliseerd.parquet` | Landbouwgebied | Agricultural areas | LB | 65 |
| `landbouwgroep_gegeneraliseerd.parquet` | Landbouwgroep | Agricultural groups | LG | 14 |
| `toeristengebied_gegeneraliseerd.parquet` | Toeristengebied | Tourist areas | TR | 17 |
| `toeristengroep_gegeneraliseerd.parquet` | Toeristengroep | Tourist groups | TG | 6 |

## Schema — Field Meanings

All 26 layer files share the same column schema:

| Field | Type | Meaning |
|-------|------|---------|
| `statcode` | string | CBS statistical code, unique within each classification type. Prefix indicates type (e.g., `GM0363` = Amsterdam, `PV27` = Noord-Holland, `VR13` = Amsterdam-Amstelland). |
| `jrstatcode` | string | Year-prefixed code for temporal disambiguation (e.g., `2025GM0363`). Use this when joining across years. |
| `statnaam` | string | Human-readable name of the area (e.g., `Amsterdam`, `Noord-Holland`). |
| `rubriek` | string | Classification category name (e.g., `gemeente`, `provincie`, `veiligheidsregio`). Same for all rows in a given file. |
| `id` | int | Internal sequential identifier. Not meaningful for analysis. |
| `geom` | WKB | Generalized polygon boundary in **EPSG:28992** (Amersfoort / RD New). |

### Code Prefix Reference

The first two letters of `statcode` tell you the classification type:

GM=gemeente, WK=wijk, BU=buurt, PV=provincie, LD=landsdeel, AM=arbeidsmarktregio,
RA=regioplus, AR=arrondissement, RT=ressort, CR=coropgebied, CS=coropsubgebied,
CP=coropplusgebied, VR=veiligheidsregio, GG=ggdregio, JZ=jeugdregio, ZK=zorgkantoorregio,
VT=veiligthuisregio, RE=regionale_eenheid, MC=RMC, ES=RES, ET=sub-RES, KK=KvK,
LB=landbouwgebied, LG=landbouwgroep, TR=toeristengebied, TG=toeristengroep.

## Geometry Notes

- CRS is **EPSG:28992** (Amersfoort / RD New) — the Dutch national coordinate system in meters.
  To convert to WGS84 for web maps, transform to EPSG:4326.
- Geometry column is named `geom` (WKB encoded).
- Boundaries are **generalized** (simplified) for thematic cartography. They will not align
  precisely with cadastral or topographic boundaries.
- Coverage: entire Netherlands including Wadden Islands.
- WGS84 bounding box: longitude 3.21 to 7.24, latitude 50.73 to 53.58.

## Useful Query Patterns

### List all gemeenten (municipalities)

```sql
SELECT statcode, statnaam
FROM read_parquet('https://data.source.coop/cholmes/portolan-nl/cbs/gebiedsindelingen/gemeente_gegeneraliseerd.parquet')
ORDER BY statnaam
```

### Find a specific municipality

```sql
SELECT statcode, statnaam, ST_AsText(ST_GeomFromWKB(geom)) AS wkt
FROM read_parquet('https://data.source.coop/cholmes/portolan-nl/cbs/gebiedsindelingen/gemeente_gegeneraliseerd.parquet')
WHERE statnaam = 'Amsterdam'
```

### List all provinces with their codes

```sql
SELECT statcode, statnaam
FROM read_parquet('https://data.source.coop/cholmes/portolan-nl/cbs/gebiedsindelingen/provincie_gegeneraliseerd.parquet')
ORDER BY statcode
```

### List all safety regions

```sql
SELECT statcode, statnaam
FROM read_parquet('https://data.source.coop/cholmes/portolan-nl/cbs/gebiedsindelingen/veiligheidsregio_gegeneraliseerd.parquet')
ORDER BY statnaam
```

### Query multiple classification types together

```sql
-- Compare how many features each classification level has
SELECT rubriek, COUNT(*) AS count
FROM (
  SELECT rubriek FROM read_parquet('https://data.source.coop/cholmes/portolan-nl/cbs/gebiedsindelingen/gemeente_gegeneraliseerd.parquet')
  UNION ALL
  SELECT rubriek FROM read_parquet('https://data.source.coop/cholmes/portolan-nl/cbs/gebiedsindelingen/provincie_gegeneraliseerd.parquet')
  UNION ALL
  SELECT rubriek FROM read_parquet('https://data.source.coop/cholmes/portolan-nl/cbs/gebiedsindelingen/coropgebied_gegeneraliseerd.parquet')
  UNION ALL
  SELECT rubriek FROM read_parquet('https://data.source.coop/cholmes/portolan-nl/cbs/gebiedsindelingen/veiligheidsregio_gegeneraliseerd.parquet')
)
GROUP BY rubriek
ORDER BY count DESC
```

### Compute area of each province in km2

```sql
INSTALL spatial; LOAD spatial;

SELECT statnaam,
       ROUND(ST_Area(ST_GeomFromWKB(geom)) / 1e6, 1) AS area_km2
FROM read_parquet('https://data.source.coop/cholmes/portolan-nl/cbs/gebiedsindelingen/provincie_gegeneraliseerd.parquet')
ORDER BY area_km2 DESC
```

Note: Because the data is in EPSG:28992 (a projected CRS in meters), `ST_Area` returns
square meters directly — no spheroidal calculation needed.

### Find which COROP region a point falls in (using RD coordinates)

```sql
INSTALL spatial; LOAD spatial;

-- Amsterdam Centraal in RD New coordinates: x=121687, y=487357
SELECT statcode, statnaam
FROM read_parquet('https://data.source.coop/cholmes/portolan-nl/cbs/gebiedsindelingen/coropgebied_gegeneraliseerd.parquet')
WHERE ST_Contains(
    ST_GeomFromWKB(geom),
    ST_Point(121687, 487357)
)
```

### Load into GeoPandas

```python
import geopandas as gpd

# Load COROP regions
gdf = gpd.read_parquet(
    'https://data.source.coop/cholmes/portolan-nl/cbs/gebiedsindelingen/coropgebied_gegeneraliseerd.parquet'
)
print(gdf.crs)  # EPSG:28992

# Convert to WGS84 for web mapping
gdf_wgs84 = gdf.to_crs(epsg=4326)
```

### Join CBS StatLine data to boundaries

```python
import duckdb
import geopandas as gpd

# 1. Load gemeente boundaries
gdf = gpd.read_parquet(
    'https://data.source.coop/cholmes/portolan-nl/cbs/gebiedsindelingen/gemeente_gegeneraliseerd.parquet'
)

# 2. Load your CBS StatLine table (example: population by gemeente)
# StatLine tables use the same statcode (GM0363 etc.) for joining
# gdf = gdf.merge(statline_df, left_on='statcode', right_on='RegioCode')
```

## Hierarchical Relationships

The Netherlands has a strict administrative hierarchy:

```
Landsdeel (4)  →  Provincie (12)  →  COROP (40)  →  Gemeente (342)  →  Wijk (3,423)  →  Buurt (14,729)
```

Functional regions (veiligheidsregio, GGD, arbeidsmarktregio, etc.) are each independent
groupings of gemeenten that do NOT nest within the administrative hierarchy. A
veiligheidsregio may span multiple provinces, and a GGD region may differ from a
veiligheidsregio even though both are groupings of the same gemeenten.

## Related Datasets

- **Bestuurlijke Gebieden (Kadaster):** Legally precise administrative boundaries for
  gemeente, provincie, and land. Use that dataset when you need exact boundaries (e.g.,
  for parcel-level analysis). Gebiedsindelingen uses generalized boundaries instead.

- **CBS Wijken en Buurten:** Adds demographic and socioeconomic statistics (population,
  income, housing, energy, etc.) to buurt/wijk/gemeente boundaries. The boundaries in
  Wijken en Buurten overlap with the buurt/wijk/gemeente layers here — use Wijken en
  Buurten when you need statistics, use Gebiedsindelingen when you need the other 23
  classification types.

- **CBS StatLine:** The national statistics database (opendata.cbs.nl). Its tables use
  the same `statcode` values for joining to these geographic boundaries.

## Caveats

- **Generalized boundaries:** These boundaries are simplified for thematic mapping. They
  will NOT align exactly with cadastral boundaries, topographic features, or satellite
  imagery. Do not use them for determining whether a specific address or parcel falls
  within a region — use Bestuurlijke Gebieden or BAG for that.

- **CRS is EPSG:28992 (RD New), not WGS84:** Coordinates are in meters (Dutch national
  grid), not degrees. You must transform to EPSG:4326 for web maps or lat/lon queries.
  In DuckDB: `ST_Transform(ST_GeomFromWKB(geom), 'EPSG:28992', 'EPSG:4326')`.
  In GeoPandas: `gdf.to_crs(epsg=4326)`.

- **Year-specific boundaries:** These are 2025 boundaries. Dutch gemeente boundaries
  change due to mergers (herindelingen) — a statcode from 2020 may not exist in 2025.
  Use `jrstatcode` for year-aware joins.

- **No demographic data:** This dataset has boundaries and names only. For population,
  income, housing statistics, etc., join with CBS Wijken en Buurten or CBS StatLine.

- **Functional regions overlap:** Different functional classifications (veiligheidsregio,
  GGD, arbeidsmarktregio) each partition the country differently. They are all built
  from gemeenten but do NOT nest within each other.

- **Geometry column is `geom`, not `geometry`:** Unlike many other datasets in this
  catalog that use `geometry`, these files use `geom` as the geometry column name.

## Also Available As

- **PMTiles (vector tiles):** `gebiedsindelingen.pmtiles` — shows gemeente boundaries
  for web map visualization with MapLibre GL JS.
- **OGC API:** `https://api.pdok.nl/cbs/gebiedsindelingen/ogc/v1` — live access to all
  layers with filtering support.
- **GeoPackage (original):** Available from PDOK Atom feed for years 2016-2026 at
  `https://service.pdok.nl/cbs/gebiedsindelingen/atom/v1_0/downloads/`

---
*Hand-maintained agent guide (ported from this collection's llms.txt in August 2026). Update it alongside collection.json.*

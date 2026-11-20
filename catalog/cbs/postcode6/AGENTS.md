# CBS Postcode6 — Statistics per 6-Digit Postcode / Netherlands

## What This Dataset Is

Statistical data for all 6-digit postcodes (e.g. "1011AB") in the Netherlands, published
by **CBS** (Centraal Bureau voor de Statistiek / Statistics Netherlands) via PDOK. Contains
**130 statistical variables** covering demographics, households, housing, energy
consumption, social security, and proximity to facilities, from the CBS publication
'Statistische gegevens per vierkant en postcode 2022-2023-2024'. Counts are measured
on 1 January; energy figures cover a calendar year. Income is not published at PC6
level. See the CBS documentation for the reference year per variable.

**Source:** https://www.pdok.nl/introductie/-/article/cbspostcode6
**CBS documentation:** https://www.cbs.nl/nl-nl/longread/diversen/2025/statistische-gegevens-per-vierkant-en-postcode-2022-2023-2024
**OGC API Features:** https://api.pdok.nl/cbs/postcode6/ogc/v1_0/
**Provider:** CBS (Statistics Netherlands)
**License:** CC BY 4.0
**Geometry type:** MultiPolygon

## How to Access

GeoParquet and PMTiles files are available from Source Cooperative. Native CRS is
**EPSG:28992** (RD New / Amersfoort) — coordinates are in meters, not degrees.

| File | Features | Size | Contents |
|------|----------|------|----------|
| `postcode6.parquet` | 464,964 | 134 MB | All postcodes with 130 statistical variables |
| `postcode6.pmtiles` | — | 77 MB | Postcode area polygons as vector tiles |

**Base URL:** `https://data.source.coop/cholmes/portolan-nl/cbs/postcode6/`

```python
import duckdb

con = duckdb.connect()
con.execute("INSTALL spatial; LOAD spatial;")

URL = 'https://data.source.coop/cholmes/portolan-nl/cbs/postcode6/postcode6.parquet'

df = con.execute(f"""
    SELECT * EXCLUDE (geom) FROM read_parquet('{URL}')
    LIMIT 5    -- EXCLUDE skips the large geometry column chunk
""").df()
```

Also available via OGC API Features from PDOK:
- **OGC API:** `https://api.pdok.nl/cbs/postcode6/ogc/v1_0/`

## Statistical Domains and Fields

The file has **134 columns**: `postcode6`, three technical columns (`fid`, `geom`,
`geom_bbox`) and **130 statistical variables**. Every column carries a sourced
description in `collection.json` (`table:columns`), grounded in the CBS
documentation linked above.

**Measured completeness (2026-11-20):** 34 of the 130 variables carry values in the
published file (demographics, households, housing stock, and the benefits count).
The other 96 — energy, WOZ value, and all facility-proximity variables — hold the
CBS sentinel **-99995** on every row: CBS publishes those for this edition in a
later release. Check `MAX(column) >= 0` before relying on a variable. Counts are rounded to multiples of 5 and percentages to tens of percent; areas with fewer than 5 inhabitants, households or dwellings are suppressed with sentinel -99997 ('0 t/m 4 / geheim / niet aanwezig'), and -99995 marks a topic to be published in a later version.

### 1. Demographics (14 fields)

| Field | Meaning |
|-------|---------|
| `aantal_inwoners` | Number of inhabitants on 1 January (registered population); rounded to multiples of 5, -99997 if fewer than 5. |
| `aantal_mannen` | Number of male inhabitants on 1 January; rounded to multiples of 5. |
| `aantal_vrouwen` | Number of female inhabitants on 1 January; rounded to multiples of 5. |
| `aantal_inwoners_0_tot_15_jaar` | Inhabitants younger than 15 on 1 January; rounded to multiples of 5. |
| `aantal_inwoners_15_tot_25_jaar` | Inhabitants aged 15 up to 25 on 1 January; rounded to multiples of 5. |
| `aantal_inwoners_25_tot_45_jaar` | Inhabitants aged 25 up to 45 on 1 January; rounded to multiples of 5. |
| `aantal_inwoners_45_tot_65_jaar` | Inhabitants aged 45 up to 65 on 1 January; rounded to multiples of 5. |
| `aantal_inwoners_65_jaar_en_ouder` | Inhabitants aged 65 or older on 1 January; rounded to multiples of 5. |
| `aantal_geboorten` | Live births during the calendar year (1 January through 31 December); rounded to multiples of 5. |
| `percentage_geb_nederland_herkomst_nederland` | Share of inhabitants born in the Netherlands with both parents born in the Netherlands; rounded to tens of percent. |
| `percentage_geb_nederland_herkomst_overig_europa` | Share of inhabitants born in the Netherlands whose origin (parental birth country) is elsewhere in Europe; rounded to tens of percent. |
| `percentage_geb_nederland_herkomst_buiten_europa` | Share of inhabitants born in the Netherlands whose origin (parental birth country) is outside Europe; rounded to tens of percent. |
| `percentage_geb_buiten_nederland_herkomst_europa` | Share of inhabitants born abroad in another European country; rounded to tens of percent. |
| `percentage_geb_buiten_nederland_herkmst_buiten_europa` | Share of inhabitants born outside Europe (Africa, Americas, Asia, Oceania); rounded to tens of percent. |

### 2. Households (6 fields)

| Field | Meaning |
|-------|---------|
| `aantal_part_huishoudens` | Private households on 1 January (institutional households excluded); rounded to multiples of 5, -99997 if fewer than 5. |
| `aantal_eenpersoonshuishoudens` | Private households consisting of one person, on 1 January. |
| `aantal_meerpersoonshuishoudens_zonder_kind` | Multi-person private households without children (couples without children and other households), on 1 January. |
| `aantal_eenouderhuishoudens` | Private households of one parent with children living at home, on 1 January. |
| `aantal_tweeouderhuishoudens` | Private households of two parents with at least one child living at home, on 1 January. |
| `gemiddelde_huishoudensgrootte` | Average household size: persons living in private households divided by the number of private households, on 1 January. |

### 3. Housing (15 fields)

| Field | Meaning |
|-------|---------|
| `aantal_woningen` | Total dwellings on 1 January: BAG residence objects with a residential function; rounded to multiples of 5, -99997 if fewer than 5. |
| `aantal_woningen_bouwjaar_voor_1945` | Dwellings with construction year before 1945, on 1 January. |
| `aantal_woningen_bouwjaar_45_tot_65` | Dwellings with construction year 1945 up to 1965, on 1 January. |
| `aantal_woningen_bouwjaar_65_tot_75` | Dwellings with construction year 1965 up to 1975, on 1 January. |
| `aantal_woningen_bouwjaar_75_tot_85` | Dwellings with construction year 1975 up to 1985, on 1 January. |
| `aantal_woningen_bouwjaar_85_tot_95` | Dwellings with construction year 1985 up to 1995, on 1 January. |
| `aantal_woningen_bouwjaar_95_tot_05` | Dwellings with construction year 1995 up to 2005, on 1 January. |
| `aantal_woningen_bouwjaar_05_tot_15` | Dwellings with construction year 2005 up to 2015, on 1 January. |
| `aantal_woningen_bouwjaar_15_en_later` | Dwellings with construction year 2015 or later, on 1 January. |
| `aantal_meergezins_woningen` | Multi-family dwellings: flats, gallery/porch flats, upstairs/downstairs units, apartments and dwellings above business premises, 1 January. |
| `percentage_koopwoningen` | Share of dwellings owned by the (future) occupants or used as second homes; rounded to tens of percent; needs >=10 dwellings, <=50% unknown ownership. |
| `percentage_huurwoningen` | Share of rental dwellings (not owner-occupied; vacant dwellings counted to the rental market); rounded to tens of percent, same thresholds as koop. |
| `aantal_huurwoningen_in_bezit_woningcorporaties` | Rental dwellings owned by housing corporations (toegelaten instellingen volkshuisvesting); ownership status, not social-rent price level. |
| `aantal_niet_bewoonde_woningen` | Dwellings with nobody registered in the population register (BRP) on reference date 1 January. |
| `gemiddelde_woz_waarde_woning` | Average provisional WOZ value of dwellings with a known WOZ value, in 1,000 euro; values below 10,000 or above 5 million euro excluded (since 2022). |

### 4. Energy (2 fields)

| Field | Meaning |
|-------|---------|
| `gemiddeld_gasverbruik_woning` | Average annual natural gas consumption of private dwellings (m3), calendar year; rounded to multiples of 50, published at 6+ occupied dwellings. |
| `gemiddeld_elektriciteitsverbruik_woning` | Average annual electricity use on individual connections of private dwellings (kWh); excl. collective use and own solar generation; rounded to 50s. |

### 5. Social security (1 field)

| Field | Meaning |
|-------|---------|
| `aantal_personen_met_uitkering_onder_aowlft` | Residents below AOW (state pension) age receiving unemployment (WW), social assistance or disability benefits on 1 January; each person counted once. |

### 6. Facility proximity (92 fields)

Average distance by road to the nearest facility, and average counts within
1/3/5/10/20 km radii, computed over all residents ("berekend over de weg").
Representative fields (all 92 are described in `collection.json`):

| Field | Meaning |
|-------|---------|
| `dichtstbijzijnde_grote_supermarkt_afstand_in_km` | Average distance by road (km) for all residents to the nearest large supermarket (daily-goods shop of at least 150 m2). |
| `grote_supermarkt_aantal_binnen_1_km` | Average number of large supermarkets (>=150 m2) within 1 km by road, averaged over all residents. |
| `grote_supermarkt_aantal_binnen_3_km` | Average number of large supermarkets (>=150 m2) within 3 km by road, averaged over all residents. |
| `grote_supermarkt_aantal_binnen_5_km` | Average number of large supermarkets (>=150 m2) within 5 km by road, averaged over all residents. |
| `dichtstbijzijnde_winkels_ov_dagel_levensm_afst_in_km` | Average distance by road (km) for all residents to the nearest other shop for daily food (baker, butcher, greengrocer, delicatessen, mini-supermarket, etc.). |
| `winkels_ov_dagel_levensm_aantal_binnen_1_km` | Average number of other daily-food shops within 1 km by road, averaged over all residents. |
| `winkels_ov_dagel_levensm_aantal_binnen_3_km` | Average number of other daily-food shops within 3 km by road, averaged over all residents. |
| `winkels_ov_dagel_levensm_aantal_binnen_5_km` | Average number of other daily-food shops within 5 km by road, averaged over all residents. |
| `dichtstbijzijnde_warenhuis_afstand_in_km` | Average distance by road (km) for all residents to the nearest department store. |
| `warenhuis_aantal_binnen_5_km` | Average number of department stores within 5 km by road, averaged over all residents. |

### Identifier and technical fields

| Field | Meaning |
|-------|---------|
| `postcode6` | Full 6-position Dutch postal code (4 digits + 2 letters) identifying the PC6 area the statistics describe. |
| `fid` | Technical: sequential feature id added in the cloud-native conversion; not a CBS variable. |
| `geom` | Technical: PC6 area polygon geometry (CBS source data in EPSG:28992 RD New); mirror geometry column, not a CBS statistical variable. |
| `geom_bbox` | Technical: per-feature bounding box struct added in the GeoParquet conversion for spatial indexing; not a CBS variable. |

## Privacy Suppression

Values of **-99997** indicate the data is suppressed for privacy. CBS applies suppression
when a postcode has fewer than **5 residents** or **5 housing units**. This is important:
always filter out -99997 before computing averages or aggregations.

```sql
-- Correct: exclude suppressed values
SELECT AVG(aantal_inwoners)
FROM read_parquet('https://data.source.coop/cholmes/portolan-nl/cbs/postcode6/postcode6.parquet')
WHERE aantal_inwoners >= 0
```

## Geometry Notes

- CRS is **EPSG:28992** (RD New / Amersfoort) — coordinates are in **meters**, not
  degrees. X ranges from ~13,600 to ~278,000; Y ranges from ~306,900 to ~617,100.
- Geometry type is **MultiPolygon**
- To convert to WGS84 (lon/lat) for web mapping:
  ```sql
  ST_Transform(geom, 'EPSG:28992', 'EPSG:4326', always_xy := true)
  ```
- Bounding box in WGS84: [3.37, 50.73, 7.24, 53.55] (all of Netherlands)

## Useful Query Patterns

### Postcodes with highest population

```sql
SELECT postcode6, aantal_inwoners, aantal_woningen
FROM read_parquet('https://data.source.coop/cholmes/portolan-nl/cbs/postcode6/postcode6.parquet')
WHERE aantal_inwoners >= 0
ORDER BY aantal_inwoners DESC
LIMIT 20
```

### Housing stock age profile

```sql
-- Every count column carries its own sentinels, so filter per column,
-- not only on the total.
SELECT ROUND(100.0 * SUM(aantal_woningen_bouwjaar_voor_1945) / SUM(aantal_woningen), 1) AS pct_pre_1945,
       ROUND(100.0 * SUM(aantal_woningen_bouwjaar_15_en_later) / SUM(aantal_woningen), 1) AS pct_2015_plus
FROM read_parquet('https://data.source.coop/cholmes/portolan-nl/cbs/postcode6/postcode6.parquet')
WHERE aantal_woningen >= 0
  AND aantal_woningen_bouwjaar_voor_1945 >= 0
  AND aantal_woningen_bouwjaar_15_en_later >= 0
```

### Rental share where published

```sql
SELECT postcode6, percentage_huurwoningen
FROM read_parquet('https://data.source.coop/cholmes/portolan-nl/cbs/postcode6/postcode6.parquet')
WHERE percentage_huurwoningen >= 0
ORDER BY percentage_huurwoningen DESC
LIMIT 20
```

The energy, WOZ and proximity variables hold -99995 throughout this edition
(not yet published by CBS); queries on them return no rows with `>= 0` filters.

### Find postcodes near a specific location (bbox filter)

```sql
INSTALL spatial; LOAD spatial;

-- Amsterdam city center (RD New coordinates)
SELECT postcode6, aantal_inwoners, aantal_woningen, mediaan_inkomen_huishouden
FROM read_parquet('https://data.source.coop/cholmes/portolan-nl/cbs/postcode6/postcode6.parquet')
WHERE jaarcode = 2024
  AND bbox.xmin >= 119000 AND bbox.xmax <= 123000
  AND bbox.ymin >= 484000 AND bbox.ymax <= 488000
```

### Distance to facilities — find underserved postcodes

```sql
SELECT postcode6, aantal_inwoners,
       afstand_tot_huisartsenpraktijk,
       afstand_tot_supermarkt,
       afstand_tot_basisonderwijs
FROM read_parquet('https://data.source.coop/cholmes/portolan-nl/cbs/postcode6/postcode6.parquet')
WHERE jaarcode = 2024
  AND aantal_inwoners > 100
  AND afstand_tot_huisartsenpraktijk > 5
ORDER BY afstand_tot_huisartsenpraktijk DESC
LIMIT 20
```

### Load into GeoPandas

```python
import geopandas as gpd

gdf = gpd.read_parquet(
    'https://data.source.coop/cholmes/portolan-nl/cbs/postcode6/postcode6.parquet',
    columns=['postcode6', 'jaarcode', 'aantal_inwoners', 'aantal_woningen',
             'mediaan_inkomen_huishouden', 'geom']
)
print(f"CRS: {gdf.crs}")  # EPSG:28992
print(f"Rows: {len(gdf):,}")
```

## Temporal Coverage

Data covers years **2015 to 2024**. Each row has a `jaarcode` indicating the reference
year. The dataset contains multiple years stacked — filter by `jaarcode` to get a single
year's snapshot. Most demographic and housing data reflects the situation on January 1st
of that year. Energy and income data reflect the full preceding year.

## Caveats

- **Privacy suppression (-99997):** Always filter out -99997 values before computing
  statistics. Postcodes with <5 residents or <5 dwellings are suppressed across most
  fields.
- **Supplementation over 3 years:** CBS supplements the data over a 3-year period. The
  most recent year may have fewer variables filled in than older years.
- **EPSG:28992 coordinates:** Coordinates are in meters (RD New), not degrees. You must
  transform to WGS84 for web maps.
- **Mixed types:** Some numeric-looking fields (e.g. `mediaan_inkomen_huishouden`) are
  stored as strings due to the -99997 suppression marker. Cast to numeric after filtering.
- **Multi-year dataset:** The file contains all years stacked. Always filter by `jaarcode`
  unless you specifically want time-series analysis.


## Visualization Styles

Three Mapbox GL v8 styles are available for interactive map visualization via the PMTiles file. Privacy-suppressed values (-99997) are filtered out.

Style files are Mapbox GL v8 JSON with relative PMTiles source paths. They can be
used with MapLibre GL JS, OpenLayers (via ol-mapbox-style), or any Mapbox GL v8-compatible renderer.

- **`styles/default.json`** — **Population density.** Red sequential ramp on `aantal_inwoners`. White (few) to dark red (500+). Shows population concentration patterns at the 6-digit postcode level.
- **`styles/by-homeownership.json`** — **Housing tenure analysis.** Diverging purple-to-green ramp on `percentage_koopwoningen` (homeownership rate, 0-100%). Purple = mostly rental, green = mostly owner-occupied. Reveals the stark urban/suburban divide in Dutch housing markets — city centers are predominantly rental while suburbs and rural areas are owner-occupied.
- **`styles/by-housing-age.json`** — **Historic housing stock.** Brown ramp on `aantal_woningen_bouwjaar_voor_1945` (pre-1945 housing count). Dark brown = many pre-war buildings, cream = modern neighborhoods. Highlights historic city centers and early 20th-century expansion areas.

Style files are at: `https://data.source.coop/cholmes/portolan-nl/cbs/postcode6/styles/`
## Also Available As

- **GeoParquet:** `postcode6.parquet` (134 MB, 464,964 features, EPSG:28992)
- **PMTiles:** `postcode6.pmtiles` (77 MB, for web map visualization)
- **OGC API Features:** https://api.pdok.nl/cbs/postcode6/ogc/v1_0/
- **WFS:** Available for years 2015-2024
- **WMS:** Available for years 2015-2024
- **ATOM download:** Available from PDOK

---
*Hand-maintained agent guide (ported from this collection's llms.txt in August 2026). Update it alongside collection.json.*

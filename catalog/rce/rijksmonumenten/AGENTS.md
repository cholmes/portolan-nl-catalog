# National Monuments (Rijksmonumenten) — RCE / Netherlands

## What This Dataset Is

Point locations of all **63,073 nationally listed monuments** (rijksmonumenten) in the Netherlands.
These are buildings, objects, and sites protected under the Heritage Act (Erfgoedwet) for their
beauty, scientific significance, or cultural-historical value. The designation means the owner must
obtain a permit for any modifications, and demolition is generally prohibited.

98% are built structures (onroerend gebouwd) — houses, churches, farms, castles, mills, bridges.
2% are archaeological sites. About 22% belong to a "complex" — an ensemble of related monuments
(e.g., a church with its rectory, or a farm with outbuildings).

The dataset includes a rich **classification system** (13 main categories, 66 subcategories)
and direct URLs to each monument's register page.

**Source:** https://api.pdok.nl/rce/beschermde-gebieden-cultuurhistorie/ogc/v1/
**Provider:** RCE (Rijksdienst voor het Cultureel Erfgoed / Cultural Heritage Agency)
**License:** Public domain (Dutch government open data)

## How to Access

The data is a GeoParquet file in **EPSG:28992** (Amersfoort / RD New). Use DuckDB with the
spatial extension.

```python
import duckdb

con = duckdb.connect()
con.execute("INSTALL spatial; LOAD spatial;")

URL = 'https://data.source.coop/cholmes/portolan-nl/rce/rijksmonumenten/rijksmonumenten.parquet'

df = con.execute(f"""
    SELECT * FROM read_parquet('{URL}')
    LIMIT 5
""").df()
```

The file is ~3.7 MB (63,073 points). Loads entirely into memory.

## Schema — Field Meanings

| Field | Type | Meaning |
|-------|------|---------|
| `geometry` | WKB Point | Monument location in **EPSG:28992**. |
| `rijksmonum` | float64 | **Monument number** (rijksmonumentnummer) — the primary key. Integer stored as float due to Shapefile origin. |
| `complex_nu` | float64 | **Complex number** — groups related monuments into ensembles. Null for standalone monuments. |
| `aard_monum` | string | Monument nature: `onroerend gebouwd` (built, 61,612) or `archeologisch` (archaeological, 1,461). |
| `hoofdcateg` | string | **Main category** (Dutch): 13 values. See category table below. |
| `subcategor` | string | **Subcategory** with legacy codes: 66 values (e.g. `Woonhuis(K)`, `Boerderij(M)`). |
| `herkomst` | string | Source of point geometry: `BAG` (45,499), `divers`, `RCE dico`, `Bridgis`, etc. |
| `kwaliteit_` | string | Location quality: `globaal` (approximate, 60%), `exact` (33%), `besluit` (by decree, 7%). |
| `juridische` | string | Legal status (always `rijksmonument`). |
| `rijksurl` | string | **Direct URL** to monument register page. Pattern: `https://monumentenregister.cultureelerfgoed.nl/monumenten/{nr}` |
| `gml_id` | string | GML identifier (`NationalListedMonumentPoints.NNNNN`). |
| `gml_parent` | string | Always null. |

## Important Columns

The columns you'll actually use:

- **`rijksmonum`** — monument number (primary key, use `CAST(rijksmonum AS INT)` for cleaner output)
- **`hoofdcateg`** — main category (13 values)
- **`subcategor`** — subcategory (66 values)
- **`aard_monum`** — built vs archaeological
- **`complex_nu`** — complex grouping (null = standalone)
- **`rijksurl`** — link to monument register
- **`geometry`** — point location

## Main Categories

| Category (Dutch) | English | Count |
|-------------------|---------|-------|
| Woningen en woningbouwcomplexen | Residences and housing | 31,503 |
| Boerderijen, molens en bedrijven | Farms, mills, businesses | 9,888 |
| Kastelen, landhuizen en parken | Castles, country houses, parks | 5,529 |
| Religieuze gebouwen | Religious buildings | 4,351 |
| Verdedigingswerken en militaire gebouwen | Fortifications, military | 2,402 |
| Handelsgebouwen, opslag- en transportgebouwen | Commercial, storage, transport | 2,204 |
| Archeologie (N) | Archaeology | 1,461 |
| Cultuur, gezondheid en wetenschap | Culture, health, science | 1,331 |
| Voorwerpen op pleinen en dergelijke | Objects in public spaces | 1,240 |
| Weg- en waterbouwkundige werken | Road and hydraulic works | 969 |
| Uitvaartcentra en begraafplaatsen | Cemeteries | 929 |
| Bestuursgebouwen, rechtsgebouwen en overheidsgebouwen | Government buildings | 724 |
| Sport, recreatie, vereniging en horeca | Sports, recreation, hospitality | 541 |

## Location Quality

60% of point locations are **approximate** (`globaal`) — they may be off by tens to hundreds
of metres. Only 33% are `exact`. This matters for spatial analysis: use buffered queries
rather than point-in-polygon for precision-sensitive work.

| Quality | Count | Meaning |
|---------|-------|---------|
| globaal | 37,881 | Approximate (may be off by 10–100+ m) |
| exact | 21,041 | Directly on or very close to the monument |
| besluit | 4,151 | As specified in the designation decree |

## Geometry Notes

- CRS is **EPSG:28992** (Amersfoort / RD New). Reproject to EPSG:4326 for web maps.
- All geometries are Point (no polygons — contour data from the provider has corrupt geometry).
- Bounding box (RD): X 13,854–277,502, Y 306,993–617,910.
- `rijksmonum` is stored as float64 due to Shapefile origin. Cast to int for display.

## Useful Query Patterns

### Count monuments by main category

```sql
SELECT hoofdcateg, COUNT(*) AS count
FROM read_parquet('https://data.source.coop/cholmes/portolan-nl/rce/rijksmonumenten/rijksmonumenten.parquet')
GROUP BY hoofdcateg
ORDER BY count DESC
```

### Find all churches

```sql
SELECT CAST(rijksmonum AS INT) AS monument_nr, subcategor, rijksurl
FROM read_parquet('https://data.source.coop/cholmes/portolan-nl/rce/rijksmonumenten/rijksmonumenten.parquet')
WHERE subcategor LIKE '%Kerk%'
```

### Monuments near a location (within 500m)

```sql
INSTALL spatial; LOAD spatial;

SELECT CAST(rijksmonum AS INT) AS nr, hoofdcateg, subcategor, rijksurl,
       ST_Distance(ST_GeomFromWKB(geometry),
           ST_Transform(ST_Point(4.9003, 52.3792), 'EPSG:4326', 'EPSG:28992')
       ) AS distance_m
FROM read_parquet('https://data.source.coop/cholmes/portolan-nl/rce/rijksmonumenten/rijksmonumenten.parquet')
WHERE distance_m < 500
ORDER BY distance_m
```

### Find all monuments in a complex

```sql
SELECT CAST(rijksmonum AS INT) AS monument_nr,
       CAST(complex_nu AS INT) AS complex_nr,
       hoofdcateg, subcategor
FROM read_parquet('https://data.source.coop/cholmes/portolan-nl/rce/rijksmonumenten/rijksmonumenten.parquet')
WHERE complex_nu = 507388
ORDER BY rijksmonum
```

### Count monuments per municipality (spatial join)

```sql
INSTALL spatial; LOAD spatial;

SELECT g.naam AS gemeente, COUNT(*) AS monuments
FROM read_parquet('.../rce/rijksmonumenten/rijksmonumenten.parquet') m
JOIN read_parquet('.../kadaster/bestuurlijke_gebieden/gemeentegebied.parquet') g
  ON ST_Intersects(ST_GeomFromWKB(g.geometry), ST_GeomFromWKB(m.geometry))
GROUP BY g.naam
ORDER BY monuments DESC
LIMIT 20
```

### Archaeological vs built monuments

```sql
SELECT aard_monum, COUNT(*) AS count
FROM read_parquet('https://data.source.coop/cholmes/portolan-nl/rce/rijksmonumenten/rijksmonumenten.parquet')
GROUP BY aard_monum
```

### Load into GeoPandas

```python
import geopandas as gpd

gdf = gpd.read_parquet(
    'https://data.source.coop/cholmes/portolan-nl/rce/rijksmonumenten/rijksmonumenten.parquet'
)
# Reproject to WGS84:
gdf_wgs = gdf.to_crs(epsg=4326)
```

## Related Datasets

- **Bestuurlijke Gebieden** (also in this catalog): Municipality boundaries for spatial joins
  to count monuments per gemeente.
- **BAG / INSPIRE Buildings** (also in this catalog): Building footprints — join via BAG ID
  to get building geometry for monuments with `herkomst = 'BAG'`.
- **Beschermde stads- en dorpsgezichten**: Protected townscapes (areas rather than individual
  buildings), available from the same RCE/PDOK source.

## Caveats

- **Point locations only** — no building footprints. The contour Shapefile from RCE has
  corrupt geometry. Use the PDOK OGC API for polygon data if needed.
- **60% approximate locations** — `kwaliteit_ = 'globaal'` means the point may be tens to
  hundreds of metres from the actual monument.
- **`rijksmonum` is float64** — cast to int for display (Shapefile artifact).
- **`complex_nu` is null for 78% of monuments** — only 22% belong to a complex.
- Legacy classification codes in parentheses (e.g., `Woonhuis(K)`, `Boerderij(M)`) are from
  an older system. They're part of the subcategory string, not a separate field.
- Field names are truncated (e.g., `hoofdcateg` not `hoofdcategorie`, `kwaliteit_` not
  `kwaliteit`) due to Shapefile's 10-character limit.


## Visualization Styles

Three Mapbox GL v8 styles are available for interactive map visualization via the PMTiles file.

Style files are Mapbox GL v8 JSON with relative PMTiles source paths. They can be
used with MapLibre GL JS, OpenLayers (via ol-mapbox-style), or any Mapbox GL v8-compatible renderer.

- **`styles/default.json`** — Amber/gold circles with orange stroke. Heritage-evoking warm tones. Circle size scales with zoom.
- **`styles/by-category.json`** — **Monument category analysis.** Colors 63,000+ monuments by `hoofdcateg` (13 main categories): amber for housing, brown for farms/mills, gold for castles/estates, orange for religious buildings, dark brown for military fortifications, etc. Reveals the spatial distribution of different heritage types — church-dense medieval cities, farm-rich rural areas, military coastal fortifications.
- **`styles/by-type.json`** — **Built vs. archaeological.** Two-tone classification by `aard_monum`: gold for built heritage (61,600), dark brown for archaeological sites (1,460). Shows the overwhelming dominance of built monuments and the sparse but interesting distribution of archaeological sites.

Style files are at: `https://data.source.coop/cholmes/portolan-nl/rce/rijksmonumenten/styles/`
## Also Available As

- **PMTiles (vector tiles):** `rijksmonumenten.pmtiles` — for web map visualization.
  Points are dropped at lower zoom levels.
- **OGC API Features:** `https://api.pdok.nl/rce/beschermde-gebieden-cultuurhistorie/ogc/v1/`.
- **Monument Register:** `https://monumentenregister.cultureelerfgoed.nl/` — look up any
  monument by number.

---
*Hand-maintained agent guide (ported from this collection's llms.txt in August 2026). Update it alongside collection.json.*

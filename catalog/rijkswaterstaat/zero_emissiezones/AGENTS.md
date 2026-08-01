# Zero Emission Zones — Rijkswaterstaat / Netherlands

## What This Dataset Is

Boundaries of **42 zero emission zones** (zero-emissiezones) in Dutch cities — areas where
vehicle emissions are restricted. These zones are part of the Netherlands' transition to
zero-emission urban logistics and cleaner air in city centres.

Two types of zones exist:
- **LEZ** (Low Emission Zone / Milieuzone) — restricts older, more polluting vehicles
- **ZES** (Zero Emissie Stadslogistiek) — requires zero-emission delivery vehicles

Each zone has defined start and end dates, reflecting the phased rollout of emission
restrictions across Dutch municipalities.

**Provider:** Rijkswaterstaat (Directorate-General for Public Works and Water Management)
**License:** Public domain (Dutch government open data)

## How to Access

The data is a GeoParquet file in **EPSG:28992** (Amersfoort / RD New). Use DuckDB with the
spatial extension.

```python
import duckdb

con = duckdb.connect()
con.execute("INSTALL spatial; LOAD spatial;")

URL = 'https://data.source.coop/cholmes/portolan-nl/rijkswaterstaat/zero_emissiezones/zero_emissiezones.parquet'

df = con.execute(f"""
    SELECT * FROM read_parquet('{URL}')
    LIMIT 5
""").df()
```

The file is small (42 features) — loads instantly.

## Schema — Field Meanings

| Field | Type | Meaning |
|-------|------|---------|
| `geometry` | WKB MultiPolygon | Zone boundary in **EPSG:28992**. |
| `Naam` | string | **Zone name** (e.g., `"LEZ Amsterdam"`, `"ZES Utrecht"`). |
| `Startdatum` | timestamp | **Start date** — when the emission restriction takes effect. |
| `Einddatum` | timestamp | **End date** — when the restriction expires (may be far future). |
| `Soort` | string | **Zone type**: `"LEZ"` (Low Emission Zone) or `"ZES"` (Zero Emissie Stadslogistiek). |
| `Shape__Area` | float64 | Zone area in m². |

## Useful Query Patterns

### List all zones by type

```sql
SELECT Soort, Naam, Startdatum, Einddatum, Shape__Area / 1e6 AS area_km2
FROM read_parquet('https://data.source.coop/cholmes/portolan-nl/rijkswaterstaat/zero_emissiezones/zero_emissiezones.parquet')
ORDER BY Soort, Naam
```

### Count zones by type

```sql
SELECT Soort, COUNT(*) AS zones,
       SUM(Shape__Area) / 1e6 AS total_area_km2
FROM read_parquet('https://data.source.coop/cholmes/portolan-nl/rijkswaterstaat/zero_emissiezones/zero_emissiezones.parquet')
GROUP BY Soort
```

### Find currently active zones

```sql
SELECT Naam, Soort, Startdatum, Einddatum, Shape__Area / 1e6 AS area_km2
FROM read_parquet('https://data.source.coop/cholmes/portolan-nl/rijkswaterstaat/zero_emissiezones/zero_emissiezones.parquet')
WHERE Startdatum <= CURRENT_DATE
  AND (Einddatum >= CURRENT_DATE OR Einddatum IS NULL)
ORDER BY Naam
```

### Find the largest zones

```sql
SELECT Naam, Soort, Shape__Area / 1e6 AS area_km2
FROM read_parquet('https://data.source.coop/cholmes/portolan-nl/rijkswaterstaat/zero_emissiezones/zero_emissiezones.parquet')
ORDER BY Shape__Area DESC
LIMIT 10
```

### Check if a point falls within an emission zone

```sql
INSTALL spatial; LOAD spatial;

SELECT Naam, Soort, Startdatum, Einddatum
FROM read_parquet('https://data.source.coop/cholmes/portolan-nl/rijkswaterstaat/zero_emissiezones/zero_emissiezones.parquet')
WHERE ST_Intersects(
    ST_GeomFromWKB(geometry),
    ST_Transform(ST_Point(4.9003, 52.3676), 'EPSG:4326', 'EPSG:28992')
)
```

## Geometry Notes

- CRS is **EPSG:28992** (Amersfoort / RD New). Coordinates are in metres.
- All geometries are MultiPolygon.
- Reproject to EPSG:4326 for web maps.


## Visualization Styles

One Mapbox GL v8 style is available for interactive map visualization via the PMTiles file.

Style files are Mapbox GL v8 JSON with relative PMTiles source paths. They can be
used with MapLibre GL JS, OpenLayers (via ol-mapbox-style), or any Mapbox GL v8-compatible renderer.

- **`styles/default.json`** — **Zone type classification.** Blue fill colored by `Soort`: dark blue for Zero Emission (ZE/ZES) zones, medium blue for Low Emission Zones (LEZ), light blue for environmental zones (Milieuzone). Labels show city names. Shows where the Netherlands is implementing vehicle emission restrictions.

Style files are at: `https://data.source.coop/cholmes/portolan-nl/rijkswaterstaat/zero_emissiezones/styles/`
## Caveats

- **`Startdatum` and `Einddatum` are timestamps**, not date strings — they include time components.
- Zone types are in Dutch abbreviations: `LEZ` = Low Emission Zone (milieuzone),
  `ZES` = Zero Emissie Stadslogistiek (zero emission city logistics).
- The specific vehicle restrictions (which Euro classes are banned, which vehicle types)
  are **not in this dataset** — only the spatial boundaries and dates.
- `Shape__Area` uses double underscores (ArcGIS convention).
- Zone boundaries may change as municipalities adjust their policies.

---
*Hand-maintained agent guide (ported from this collection's llms.txt in August 2026). Update it alongside collection.json.*

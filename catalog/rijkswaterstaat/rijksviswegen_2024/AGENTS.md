# Fish Migration Routes (2024) — Rijkswaterstaat / Netherlands

## What This Dataset Is

The national fish migration route network (**rijksviswegen**) of the Netherlands — **2,122
LineString features** representing waterways that are part of the national fish passage network.
This dataset tracks the **connectivity status** of each route segment over time, from 2009
through projected targets in 2033.

Fish migration is critical in the Netherlands because the extensive system of dams, weirs, and
locks can block fish from reaching spawning grounds, feeding areas, or the sea. The Dutch
government has committed to making these routes passable, and this dataset records progress
toward that goal.

**Provider:** Rijkswaterstaat (Directorate-General for Public Works and Water Management)
**License:** Public domain (Dutch government open data)

## How to Access

The data is a GeoParquet file in **EPSG:28992** (Amersfoort / RD New). Use DuckDB with the
spatial extension.

```python
import duckdb

con = duckdb.connect()
con.execute("INSTALL spatial; LOAD spatial;")

URL = 'https://data.source.coop/cholmes/portolan-nl/rijkswaterstaat/rijksviswegen_2024/rijksviswegen_2024.parquet'

df = con.execute(f"""
    SELECT * FROM read_parquet('{URL}')
    LIMIT 5
""").df()
```

## Schema — Field Meanings

| Field | Type | Meaning |
|-------|------|---------|
| `geometry` | WKB LineString | Route geometry in **EPSG:28992**. |
| `NAAM` | string | **Waterway name** (e.g., "Maas", "IJssel", "Noordzeekanaal"). |
| `CODE` | string | Route segment code. |
| `BEHEERDER` | string | Manager/operator. Mostly null. |
| `MIGR_TYPE` | string | Migration type — always `"rijk"` (national). |
| `Status2009` | string | Connectivity status in 2009. |
| `Status2015` | string | Connectivity status in 2015. |
| `Status2019` | string | Connectivity status in 2019. |
| `Status2021` | string | Connectivity status in 2021. |
| `Status2024` | string | Connectivity status in 2024. |
| `Status2027` | string | Projected connectivity status in 2027. |
| `Status2030` | string | Projected connectivity status in 2030. |
| `Status2033` | string | Projected connectivity status in 2033. |

### Status Values

- `"Verbonden"` — Connected (fish can pass)
- `"Niet verbonden"` — Not connected (fish passage blocked)
- `"Geen onderdeel visroutenetwerk"` — Not part of the fish route network

## Useful Query Patterns

### Track connectivity improvement over time

```sql
SELECT
    COUNT(*) FILTER (WHERE Status2009 = 'Verbonden') AS connected_2009,
    COUNT(*) FILTER (WHERE Status2015 = 'Verbonden') AS connected_2015,
    COUNT(*) FILTER (WHERE Status2019 = 'Verbonden') AS connected_2019,
    COUNT(*) FILTER (WHERE Status2021 = 'Verbonden') AS connected_2021,
    COUNT(*) FILTER (WHERE Status2024 = 'Verbonden') AS connected_2024,
    COUNT(*) FILTER (WHERE Status2027 = 'Verbonden') AS connected_2027,
    COUNT(*) FILTER (WHERE Status2030 = 'Verbonden') AS connected_2030,
    COUNT(*) FILTER (WHERE Status2033 = 'Verbonden') AS connected_2033
FROM read_parquet('https://data.source.coop/cholmes/portolan-nl/rijkswaterstaat/rijksviswegen_2024/rijksviswegen_2024.parquet')
```

### Count connected vs not connected for current year

```sql
SELECT Status2024, COUNT(*) AS count
FROM read_parquet('https://data.source.coop/cholmes/portolan-nl/rijkswaterstaat/rijksviswegen_2024/rijksviswegen_2024.parquet')
GROUP BY Status2024
ORDER BY count DESC
```

### Find routes that became connected between 2009 and 2024

```sql
SELECT NAAM, CODE
FROM read_parquet('https://data.source.coop/cholmes/portolan-nl/rijkswaterstaat/rijksviswegen_2024/rijksviswegen_2024.parquet')
WHERE Status2009 = 'Niet verbonden'
  AND Status2024 = 'Verbonden'
```

### Routes by waterway name

```sql
SELECT NAAM, COUNT(*) AS segments,
       COUNT(*) FILTER (WHERE Status2024 = 'Verbonden') AS connected_2024
FROM read_parquet('https://data.source.coop/cholmes/portolan-nl/rijkswaterstaat/rijksviswegen_2024/rijksviswegen_2024.parquet')
GROUP BY NAAM
ORDER BY segments DESC
LIMIT 20
```

## Geometry Notes

- CRS is **EPSG:28992** (Amersfoort / RD New). Coordinates are in metres.
- All geometries are LineString.
- Reproject to EPSG:4326 for web maps.


## Visualization Styles

Two Mapbox GL v8 styles are available for interactive map visualization via the PMTiles file.

Style files are Mapbox GL v8 JSON with relative PMTiles source paths. They can be
used with MapLibre GL JS, OpenLayers (via ol-mapbox-style), or any Mapbox GL v8-compatible renderer.

- **`styles/default.json`** — Teal-colored line network showing all national fish migration routes. Clean single-color rendering of the full network.
- **`styles/by-status.json`** — **Fish passage connectivity analysis.** Colors routes by `Status2024`: green = connected (fish can pass), red = not connected (blocked), gray = not part of the network. Visualizes progress on fish passage restoration — nearly all routes (2,086 of 2,122) are now connected.

Style files are at: `https://data.source.coop/cholmes/portolan-nl/rijkswaterstaat/rijksviswegen_2024/styles/`
## Caveats

- **`BEHEERDER` is mostly null** — manager information is largely missing.
- **`MIGR_TYPE` is always `"rijk"`** — this dataset only covers national-level routes,
  not regional fish migration paths.
- Status years from 2027 onward are **projected targets**, not observed status.
- Column names use uppercase (e.g., `NAAM`, `STATUS2024`).
- The "Geen onderdeel visroutenetwerk" status means the segment was redefined as outside
  the network — it does not indicate a physical barrier.

---
*Hand-maintained agent guide (ported from this collection's llms.txt in August 2026). Update it alongside collection.json.*

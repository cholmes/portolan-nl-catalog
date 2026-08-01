# Rijkswaterstaat — Public Works & Water Management / Netherlands

## What This Is

Seven collections from Rijkswaterstaat, the executive agency of the Dutch Ministry of
Infrastructure and Water Management. Rijkswaterstaat manages the main waterway network,
flood defenses, and national road infrastructure. The Netherlands' geography — much of it
below sea level — makes water management existentially important.

These collections are grouped thematically below.

## Water Management

### waterkeringen/ — Primary Flood Defenses (Dike Sections)
238 primary flood defense sections (primaire waterkeringen) — the dike rings and storm
surge barriers that protect the Netherlands from the sea and major rivers. Each section
has a legally mandated safety standard under the Water Act (Waterwet).

- File: `waterkeringen.parquet`
- Key fields: `wk_naam` (name), `wk_type` (dike type), `geometry` (line/polygon)

### bergingsgebieden/ — Flood Retention Areas
1,545 designated flood retention areas (bergingsgebieden) — locations where water can
be temporarily stored during extreme high water events. Part of the national flood risk
management strategy.

- File: `bergingsgebieden.parquet`
- Key fields: `naam` (name), `geometry` (polygon)

### hectometervakken_vaargeul/ — Fairway Depth Sections
3,112 fairway depth measurement sections along the Rhine branches (Waal, Nederrijn, Lek,
IJssel, Pannerdensch Kanaal). Each section covers 100 metres (one hectometre) and records
guaranteed navigation depth and actual measured depth.

- File: `hectometervakken_vaargeul.parquet`
- Key fields: depth measurements, river identification, hectometre markers

### sluizen/ — Navigation Locks
92 navigation locks (sluizen) on recreational waterways managed by Rijkswaterstaat.
Includes lock dimensions (length, width), operating hours, and location.

- File: `sluizen.parquet`
- Key fields: `naam` (name), `lengte` (length), `breedte` (width), `geometry` (point)

## Ecology

### rijksviswegen_2024/ — Fish Migration Routes
2,122 fish migration route segments (rijksviswegen) showing connectivity status for fish
passage. Tracks the passability of barriers (dams, weirs, locks) for migratory fish, with
status assessments spanning 2009–2033. Critical for EU Water Framework Directive reporting.

- File: `rijksviswegen_2024.parquet`
- Key fields: connectivity status, barrier type, route segment, assessment year

## Transport & Environment

### fme_disk_tunnels/ — Road Tunnels
25 road tunnels managed by Rijkswaterstaat, including their locations and basic attributes.

- File: `fme_disk_tunnels.parquet`
- Key fields: tunnel name, geometry (point/line)

### zero_emissiezones/ — Zero Emission Zones
42 low-emission zones (zero-emissiezones, ZES) and low-emission zones for logistics (LEZ)
in Dutch cities. These zones restrict access for polluting vehicles — passenger cars,
delivery vans, or trucks depending on the zone type. Part of the national Clean Air Agreement.

- File: `zero_emissiezones.parquet`
- Key fields: zone name, municipality, zone type, geometry (polygon)

## Coordinate System

All Rijkswaterstaat collections use **EPSG:28992** (Amersfoort / RD New) — coordinates in
metres. Convert to WGS84 with:

```sql
ST_Transform(geometry, 'EPSG:28992', 'EPSG:4326')
```

## Data Source

Most of these collections were downloaded from Rijkswaterstaat's public ArcGIS Feature
Services at https://services-eu1.arcgis.com/4D1GBrbE6xp1T4YG/arcgis/rest/services/
and converted to GeoParquet and PMTiles for cloud-native access. The original Feature
Services remain the authoritative source and may be updated more frequently.

## License

Some collections are CC0 or CC-BY-4.0. Several list "proprietary" in metadata but are
sourced from publicly accessible Rijkswaterstaat ArcGIS Feature Services.

## Example Queries

### List all primary flood defense sections

```sql
SELECT *
FROM read_parquet('https://data.source.coop/cholmes/portolan-nl/rijkswaterstaat/waterkeringen/waterkeringen.parquet')
ORDER BY 1
```

### Count zero emission zones by municipality

```sql
SELECT COUNT(*) AS zones
FROM read_parquet('https://data.source.coop/cholmes/portolan-nl/rijkswaterstaat/zero_emissiezones/zero_emissiezones.parquet')
```

### List navigation locks

```sql
SELECT *
FROM read_parquet('https://data.source.coop/cholmes/portolan-nl/rijkswaterstaat/sluizen/sluizen.parquet')
LIMIT 10
```

### Count flood retention areas

```sql
SELECT COUNT(*) AS retention_areas
FROM read_parquet('https://data.source.coop/cholmes/portolan-nl/rijkswaterstaat/bergingsgebieden/bergingsgebieden.parquet')
```

### Fish migration routes overview

```sql
SELECT COUNT(*) AS segments
FROM read_parquet('https://data.source.coop/cholmes/portolan-nl/rijkswaterstaat/rijksviswegen_2024/rijksviswegen_2024.parquet')
```

## Cross-Collection Analysis Ideas

- **Flood protection inventory**: Combine waterkeringen (dike sections) with
  bergingsgebieden (retention areas) for a complete picture of flood risk management
- **Urban environment**: Overlay zero_emissiezones with administrative boundaries to
  see which municipalities have emission restrictions
- **Inland waterway network**: Combine sluizen (locks), hectometervakken_vaargeul
  (fairway depths), and rijksviswegen (fish migration) for a comprehensive view of
  Dutch waterway infrastructure and ecology

---
*Hand-maintained agent guide (ported from this collection's llms.txt in August 2026). Update it alongside collection.json.*

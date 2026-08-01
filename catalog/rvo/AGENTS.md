# RVO — Netherlands Enterprise Agency (Rijksdienst voor Ondernemend Nederland) / Netherlands

## What This Is

Two nature conservation collections from RVO. Although RVO is primarily a business and
subsidy agency, it also manages the spatial data for the Dutch protected areas system —
both the national designation (Nationale Parken) and the EU designation (Natura 2000).

## Collections

### nationale_parken/ — National Parks
All 21 National Parks in the Netherlands — large contiguous natural areas designated for
their ecological, landscape, and recreational value. Parks range from coastal dunes to
forests, wetlands, heathlands, and a tidal estuary (Oosterschelde, the largest at ~38,000 ha).

- File: `nationale_parken.parquet` (~800 KB, 21 features)
- CRS: EPSG:28992 (RD New)
- Key fields: `naam` (name), `hectares` (area), `datum` (designation date), `geometry` (boundary)

### natura2000/ — Natura 2000 Protected Areas
162 Natura 2000 EU-protected areas (209 features) designated under the EU Birds Directive
and Habitats Directive. These carry the strongest nature protection in Dutch law — any
plan or project that may significantly affect a Natura 2000 area requires an appropriate
assessment. Politically critical due to the Dutch nitrogen crisis (stikstofcrisis).

- File: `natura2000.parquet` (~7.5 MB, 209 features)
- CRS: EPSG:28992 (RD New)
- Key fields: `naam_n2k` (name), `nr` (official number), `beschermin` (designation type: VR/HR/VR+HR), `shape_area` (area in m2)
- Note: 209 features for 162 areas — some areas have separate features for Birds vs Habitats Directive designations. Always use `COUNT(DISTINCT nr)` for area counts.

## National Parks vs Natura 2000

These are two separate legal protection systems with significant spatial overlap:

| | National Parks | Natura 2000 |
|---|----------------|-------------|
| Legal basis | National policy (since 1930) | EU Birds & Habitats Directives |
| Count | 21 | 162 |
| Focus | Landscape, recreation, ecology | Habitat & species protection |
| Protection strength | Moderate (governance framework) | Strongest in Dutch law |
| Managed by | Provinces (since 2023 reform) | National government (via RVO) |
| Political impact | Low | Very high (nitrogen crisis) |

Many National Parks overlap wholly or partially with Natura 2000 areas. For example,
De Biesbosch, Schiermonnikoog, and Oosterschelde are both National Parks and Natura 2000
sites. However, the boundaries do not always match exactly, and the legal consequences
of each designation differ.

## Example Queries

### List all National Parks by size

```sql
SELECT naam, hectares, datum
FROM read_parquet('https://data.source.coop/cholmes/portolan-nl/rvo/nationale_parken/nationale_parken.parquet')
ORDER BY hectares DESC
```

### List all Natura 2000 areas by size

```sql
SELECT nr, naam_n2k, SUM(shape_area) / 1e6 AS area_km2,
       STRING_AGG(DISTINCT beschermin, ', ') AS designations
FROM read_parquet('https://data.source.coop/cholmes/portolan-nl/rvo/natura2000/natura2000.parquet')
GROUP BY nr, naam_n2k
ORDER BY area_km2 DESC
LIMIT 10
```

### Find spatial overlap between National Parks and Natura 2000

```sql
INSTALL spatial; LOAD spatial;

SELECT np.naam AS national_park, n2k.naam_n2k AS natura2000_area
FROM read_parquet('https://data.source.coop/cholmes/portolan-nl/rvo/nationale_parken/nationale_parken.parquet') np
JOIN read_parquet('https://data.source.coop/cholmes/portolan-nl/rvo/natura2000/natura2000.parquet') n2k
  ON ST_Intersects(ST_GeomFromWKB(np.geometry), ST_GeomFromWKB(n2k.geometry))
ORDER BY np.naam
```

### Total protected area under each system

```sql
SELECT 'National Parks' AS system, SUM(hectares) AS total_hectares
FROM read_parquet('https://data.source.coop/cholmes/portolan-nl/rvo/nationale_parken/nationale_parken.parquet')
UNION ALL
SELECT 'Natura 2000', SUM(shape_area) / 10000
FROM read_parquet('https://data.source.coop/cholmes/portolan-nl/rvo/natura2000/natura2000.parquet')
```

## See Also

Each collection has its own `AGENTS.md` with detailed field descriptions and query patterns:
- `nationale_parken/AGENTS.md`
- `natura2000/AGENTS.md`

---
*Hand-maintained agent guide (ported from this collection's llms.txt in August 2026). Update it alongside collection.json.*

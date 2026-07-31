# Natura 2000 - Protected Areas in the Netherlands

## Overview

This dataset contains the boundaries of all 162 Natura 2000 protected areas in the Netherlands, as published by RVO (Rijksdienst voor Ondernemend Nederland) via PDOK.

**Natura 2000** is the largest coordinated network of protected areas in the world, established by the European Union to ensure the long-term survival of Europe's most threatened species and habitats. The network spans all EU member states and is governed by two directives:

- **Birds Directive** (Vogelrichtlijn, VR) -- Directive 2009/147/EC, for the protection of wild bird species and their habitats.
- **Habitats Directive** (Habitatrichtlijn, HR) -- Directive 92/43/EEC, for the conservation of natural habitats and species other than birds.

In the Netherlands, 162 areas have been designated under one or both of these directives.

| Property | Value |
|----------|-------|
| Provider | RVO (Rijksdienst voor Ondernemend Nederland) |
| Format | GeoPackage |
| File size | ~10.2 MB |
| Feature count | 209 |
| Distinct areas | 162 |
| Geometry type | 3D Measured MultiPolygon |
| CRS | EPSG:28992 (Amersfoort / RD New) |
| License | CC0 1.0 (public domain) |

## Why This Dataset Matters

### Legal Significance

Natura 2000 areas carry the strongest nature protection under Dutch law (Wet natuurbescherming, now integrated into the Omgevingswet since 2024). Any plan or project that may significantly affect a Natura 2000 area requires:

1. A **voortoets** (preliminary assessment) to determine whether significant effects can be excluded.
2. If significant effects cannot be excluded: a full **passende beoordeling** (appropriate assessment).
3. If the assessment shows adverse effects: the project can only proceed under strict conditions (no alternatives, imperative reasons of overriding public interest, compensatory measures).

### The Nitrogen Crisis (Stikstofcrisis)

Since May 2019, this dataset has been at the center of one of the Netherlands' most disruptive policy crises. The Council of State (Raad van State) struck down the PAS (Programma Aanpak Stikstof) in a landmark ruling because nitrogen deposition from agriculture, traffic, and industry exceeded critical loads in Natura 2000 areas. This decision:

- Halted approximately 18,000 construction and infrastructure projects
- Forced reductions in livestock farming near Natura 2000 areas
- Led to temporary speed limit reductions on highways (100 km/h)
- Generated ongoing political debate about the balance between nature protection and economic activity

The AERIUS Calculator (maintained by RIVM) uses the Natura 2000 boundaries from this dataset as receptor areas for nitrogen deposition modeling.

## Provider: RVO

RVO (Rijksdienst voor Ondernemend Nederland) is an agency of the Dutch Ministry of Economic Affairs and Climate Policy (now Ministry of Agriculture, Nature and Food Quality - LNV). RVO manages the Natura 2000 spatial data and publishes it through PDOK. Despite the name suggesting a focus on business, RVO handles significant environmental and agricultural data responsibilities.

## Data Sources

| Resource | URL |
|----------|-----|
| PDOK Atom feed | https://service.pdok.nl/rvo/natura2000/atom/index.xml |
| Direct download | https://service.pdok.nl/rvo/natura2000/atom/downloads/natura2000.gpkg |
| OGC API | https://api.pdok.nl/rvo/natura2000/ogc/v1 |

## Feature Count vs. Area Count

The dataset has **209 features** but only **162 distinct Natura 2000 areas**. This is because some areas have multiple features with different designation types. For example:

- **De Wieden** (nr=35) has 2 features: one for VR and one for VR+HR
- **Brabantse Wal** (nr=128) has 3 features with different designation types
- **Hollands Diep** (nr=111) has 3 features

In total, 41 of the 162 areas have multiple features. When counting protected areas, always aggregate by `nr` (the official area number), not by feature count.

## Schema

### Layer: `n2000`

| Column | Type | Dutch | English | Notes |
|--------|------|-------|---------|-------|
| `objectid` | Integer | Object-ID | Object ID | Auto-incrementing identifier |
| `naam_n2k` | String(50) | Naam Natura 2000-gebied | Area name | Official Dutch name of the protected area |
| `vhn_new` | Int16 | Code aanwijzingstype | Designation type code | 1=VR, 2=HR, 3=VR+HR, 9=HR groeve |
| `nr` | Integer | Gebiedsnummer | Area number | Official Natura 2000 area number (1-166) |
| `beschermin` | String(50) | Beschermingstype | Protection type | Human-readable designation label |
| `sitecode_v` | String(16) | EU-sitecode Vogelrichtlijn | Birds Directive site code | Empty if area is HR-only |
| `sitecode_h` | String(16) | EU-sitecode Habitatrichtlijn | Habitats Directive site code | Empty if area is VR-only |
| `status` | String(150) | Juridische status | Legal status | Free-text designation decision and date |
| `kadaster` | String(30) | Kadastrale referentie | Cadastral reference | Link to Kadaster land registry |
| `staatscour` | String(30) | Staatscourant-referentie | Government Gazette ref. | Publication reference for the decision |
| `shape_area` | Real | Oppervlakte (m2) | Area (m2) | Per-feature area in square meters |
| `shape_len` | Real | Omtrek (m) | Perimeter (m) | Per-feature perimeter in meters |
| `puuid` | String | Persistent UUID | Persistent UUID | Persistent unique identifier |
| `fuuid` | String | Feature UUID | Feature UUID | Feature unique identifier |

### Designation Types (beschermin / vhn_new)

| `vhn_new` | `beschermin` | EU Directive | Count | Description |
|-----------|-------------|--------------|-------|-------------|
| 1 | VR | Birds Directive (2009/147/EC) | 39 | Areas designated for bird species protection |
| 2 | HR | Habitats Directive (92/43/EEC) | 108 | Areas designated for habitat and non-bird species protection |
| 3 | VR+HR | Both directives | 58 | Areas designated under both directives |
| 9 | HR groeve | Habitats Directive (quarry) | 4 | Special designation for limestone quarries (mergelgroeven) in South Limburg |

### Status Field

The `status` field contains free-text legal information about the designation decision. Common patterns:

- `Natura 2000-besluit <date>` -- original designation decision
- `Natura 2000-besluit <date>, wijzigingsbesluit <date>` -- designation with amendment
- `Uitvoeringsbesluit EU <number>` -- EU implementing decision
- `Bijzonder nationaal natuurgebied ex artikel 2.11 WN` -- special national nature area

Dates are formatted inconsistently (some with full dates, others year-only). This field is not suitable for programmatic date parsing without cleaning.

## CRS Notes

The data is in **EPSG:28992** (Amersfoort / RD New), the standard Dutch national coordinate reference system.

- The extent reaches from approximately (-15520, 307155) to (276784, 852886) in RD coordinates.
- The extent extends into the **North Sea** because several Natura 2000 areas are marine: Noordzeekustzone, Voordelta, Doggerbank, Klaverbank, and Friese Front.
- For web mapping or international use, transform to **EPSG:4326** (WGS 84) or **EPSG:3857** (Web Mercator).

### Geometry Note

The geometry type is "3D Measured Multi Polygon" (has Z and M coordinate dimensions), but these extra dimensions appear to be unused (typically 0 or NaN). For all practical purposes, this is a 2D MultiPolygon dataset.

## Working with the Data

### Download

```bash
curl -L -o natura2000.gpkg \
  https://service.pdok.nl/rvo/natura2000/atom/downloads/natura2000.gpkg
```

Or use the provided `download.sh` script.

### Convert to GeoParquet

```bash
# Convert to GeoParquet, reprojecting to WGS 84
ogr2ogr -f Parquet natura2000.parquet natura2000.gpkg n2000 -t_srs EPSG:4326
```

### Generate PMTiles

```bash
ogr2ogr -f GeoJSONSeq /vsistdout/ natura2000.parquet | \
  tippecanoe -o natura2000.pmtiles -zg \
  --drop-densest-as-needed --extend-zooms-if-still-dropping \
  -l natura2000 --force
```

### DuckDB Queries

```sql
-- Load the spatial extension
INSTALL spatial;
LOAD spatial;

-- Read the GeoPackage directly
SELECT * FROM ST_Read('natura2000.gpkg', layer='n2000') LIMIT 5;

-- Count areas by designation type
SELECT beschermin, COUNT(*) as features, COUNT(DISTINCT nr) as areas
FROM ST_Read('natura2000.gpkg', layer='n2000')
GROUP BY beschermin
ORDER BY features DESC;

-- Find the largest areas (aggregate by area number)
SELECT naam_n2k, nr,
       SUM(shape_area) / 1e6 AS total_area_km2,
       STRING_AGG(DISTINCT beschermin, ', ') AS designations
FROM ST_Read('natura2000.gpkg', layer='n2000')
GROUP BY naam_n2k, nr
ORDER BY total_area_km2 DESC
LIMIT 10;

-- Areas with multiple features (multi-designation)
SELECT naam_n2k, nr, COUNT(*) AS parts,
       STRING_AGG(DISTINCT beschermin, ', ') AS types
FROM ST_Read('natura2000.gpkg', layer='n2000')
GROUP BY naam_n2k, nr
HAVING COUNT(*) > 1
ORDER BY parts DESC;
```

### Python with GeoPandas

```python
import geopandas as gpd

# Read the data
gdf = gpd.read_file("natura2000.gpkg", layer="n2000")

# Basic info
print(f"Features: {len(gdf)}")
print(f"Distinct areas: {gdf['nr'].nunique()}")
print(f"CRS: {gdf.crs}")

# Designation breakdown
print(gdf["beschermin"].value_counts())

# Total area in km2 (summing per unique area number to avoid double-counting)
area_totals = gdf.groupby("nr")["shape_area"].max()  # Take largest feature per area
print(f"Approx. total area: {area_totals.sum() / 1e6:.0f} km2")

# Reproject to WGS 84 for web mapping
gdf_wgs84 = gdf.to_crs(epsg=4326)

# Save as GeoParquet
gdf_wgs84.to_parquet("natura2000.parquet")
```

### Thumbnail Generation

```python
import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as ctx

gdf = gpd.read_file("natura2000.gpkg", layer="n2000").to_crs(epsg=3857)
fig, ax = plt.subplots(1, 1, figsize=(8, 10))
gdf.plot(ax=ax, color="blue", alpha=0.5, edgecolor="darkblue", linewidth=0.5)
ctx.add_basemap(ax, source=ctx.providers.CartoDB.Positron)
ax.set_axis_off()
ax.set_title("Natura 2000 Areas - Netherlands", fontsize=14)
fig.savefig("thumbnail_natura2000.png", dpi=100, bbox_inches="tight")
```

## Related Datasets

| Dataset | Provider | Relationship |
|---------|----------|-------------|
| **Nationale Parken** | RVO | Dutch national parks -- many overlap with Natura 2000 areas but are a separate, national-level designation with different legal implications |
| **Natuurnetwerk Nederland (NNN)** | Provinces | The broader Dutch ecological network (formerly EHS). Natura 2000 areas are generally embedded within NNN but carry stronger EU-level legal protection |
| **CDDA** | EEA | The Common Database on Designated Areas maintained by the European Environment Agency includes Dutch Natura 2000 sites alongside other nationally designated areas |
| **Habitattypenkaart** | RVO/Provinces | Detailed mapping of EU habitat types within each Natura 2000 area, used for conservation objective monitoring |
| **AERIUS** | RIVM | Nitrogen deposition calculations are modeled per Natura 2000 area; the boundaries from this dataset define the receptor zones |
| **BRP Gewaspercelen** | RVO | Agricultural field boundaries -- spatial proximity to Natura 2000 areas determines nitrogen emission restrictions for livestock farming |

## Caveats

1. **Feature count does not equal area count.** 209 features represent 162 distinct areas. Always use `nr` to identify unique areas.

2. **3D/M geometry dimensions are unused.** The geometry is typed as 3D Measured MultiPolygon but the Z and M values are not meaningful. Most tools will handle this transparently, but some may require explicit 2D conversion.

3. **shape_area may double-count.** For areas with multiple features under different designations, geometries may overlap. Summing all `shape_area` values overestimates the total protected area. Aggregate carefully by `nr`.

4. **Inconsistent status dates.** The `status` field uses free-text dates in various formats. Do not attempt programmatic date extraction without cleaning.

5. **Marine areas extend into the North Sea.** The spatial extent reaches well beyond the Dutch mainland into the EEZ. This is correct -- areas like Doggerbank, Klaverbank, and Friese Front are marine Natura 2000 sites.

6. **HR groeve is a special case.** The 4 features with `beschermin = "HR groeve"` are limestone quarry (mergelgroeve) sites in South Limburg with special habitat designations.

7. **CRS is Netherlands-only.** EPSG:28992 is only valid for the Netherlands and its immediate surroundings. Reproject for any international or web mapping use.

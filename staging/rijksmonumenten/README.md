# Rijksmonumenten (National Monuments of the Netherlands)

## What are Rijksmonumenten?

A **Rijksmonument** (national monument) is a building, structure, object, or site in the Netherlands that has been designated as being of national significance for its beauty, scientific importance, or cultural-historical value. The designation is a legal protection status under the **Erfgoedwet** (Heritage Act, 2016), which succeeded the Monumentenwet 1988.

The Netherlands has approximately **63,000 rijksmonumenten**. The vast majority (~98%) are built structures ("onroerend gebouwd") -- residential houses, churches, windmills, canal houses, farms, fortifications, bridges, and industrial heritage. About 2% are archaeological sites.

### Legal implications

A Rijksmonument designation has real consequences for property owners:

- **Permit requirement**: Any modification to the monument (including interior changes) requires an *omgevingsvergunning* (environmental/building permit). The municipality consults the RCE before granting such permits.
- **Demolition prohibition**: Demolition of a rijksmonument is generally prohibited.
- **Subsidies and tax benefits**: Owners may be eligible for maintenance and restoration subsidies from the *Nationaal Restauratiefonds* and can deduct certain maintenance costs from income tax.
- **Obligation to maintain**: Owners have a duty to maintain the monument in reasonable condition.

### Governance

- The **Rijksdienst voor het Cultureel Erfgoed (RCE)** -- Cultural Heritage Agency of the Netherlands -- maintains the national monument register and provides expert advice on designations and permit applications.
- The **Minister of Education, Culture and Science** makes the formal designation decisions.
- **Municipalities** are responsible for enforcement through the building permit system.


## Data Source

### RCE Download Service (used here)

The data in this directory was downloaded from the RCE's download service:

- **Atom feed**: https://services.rce.geovoorziening.nl/www/download/nl.xml
- **Points ZIP**: https://services.rce.geovoorziening.nl/www/download/data/Rijksmonumentpunten_28992.zip
- **Contours ZIP**: https://services.rce.geovoorziening.nl/www/download/data/Rijksmonumentcontouren_28992.zip

The download provides Shapefiles in **EPSG:28992** (Amersfoort / RD New), the standard Dutch national coordinate reference system. Files are UTF-8 encoded.

**License**: Public domain / no restrictions stated in the Atom download feed. Dutch government open data.

### PDOK OGC API (alternative)

The same data is also available through PDOK's OGC API Features service:

- **Landing page**: https://api.pdok.nl/rce/beschermde-gebieden-cultuurhistorie/ogc/v1/
- **Collections**: https://api.pdok.nl/rce/beschermde-gebieden-cultuurhistorie/ogc/v1/collections

The PDOK API serves data in GeoJSON (EPSG:4326 by default) and supports CRS negotiation, spatial filtering, and attribute filtering. It may be more current than the download service. It also includes the related *beschermde stads- en dorpsgezichten* (protected townscapes) collections.

**Important**: The PDOK OGC API is the recommended source for the contour data -- see the [data quality note](#contour-data-quality-issue) below.

### Monument Register

Individual monuments can be looked up via the public web interface:

- **Register**: https://monumentenregister.cultureelerfgoed.nl/
- **Per monument**: `https://monumentenregister.cultureelerfgoed.nl/monumenten/{rijksmonumentnummer}`

Each feature in the dataset includes a `rijksurl` field that links directly to the monument's register page.


## Files in `data/`

| File | Description | Geometry | Features |
|------|-------------|----------|----------|
| `Rijksmonumentpunten_28992.shp` (+.dbf, .prj, .shx, .cpg) | Point locations of all monuments | Point | 63,073 |
| `Rijksmonumentcontouren_28992.shp` (+.dbf, .prj, .shx, .cpg) | Contour/outline polygons (subset) | *see note* | 4,149 |


## The Monument Number (`rijksmonumentnummer`)

The `rijksmonum` field (truncated from "rijksmonumentnummer" by the Shapefile 10-character limit) is the **primary key** for each monument. It is:

- A unique integer assigned to each monument at the time of designation
- Used across all RCE systems and in the monument register URL
- Stable over time (numbers are not reused)
- Stored as `Real(20)` in the Shapefile due to Shapefile format limitations, but is logically an integer

Examples:
- `341971` -- an archaeological site
- `10657` -- a residential house
- `32116` -- a farm

The monument number is embedded in the `rijksurl`:
```
https://monumentenregister.cultureelerfgoed.nl/monumenten/341971
```


## Complexes (`complex_nu`)

About **14,033 monuments (22%)** belong to a "complex" -- a group of related monuments that together form an ensemble. The `complex_nu` field (truncated from "complexnummer") links them.

Examples of complexes:
- A **church** with its associated rectory, churchyard wall, and gate
- A **country estate** with its main house, coach house, orangery, gardens, and entrance gate
- A **farm complex** with the farmhouse, barn, haystack base, and well
- A **fortress** with its walls, moats, bastions, and guard houses

The complex number is itself a rijksmonumentnummer -- typically that of the "main" monument in the group. Multiple monuments share the same `complex_nu` value.

Monuments without a complex affiliation have `complex_nu = NULL`.


## Category Classification System

The RCE uses a two-level classification: **hoofdcategorie** (main category) and **subcategorie** (subcategory). Some include legacy alphanumeric codes in parentheses from an older classification system.

### Main Categories (hoofdcategorie)

| Dutch name | English | Count |
|-----------|---------|-------|
| Woningen en woningbouwcomplexen | Residences and housing complexes | 31,503 |
| Boerderijen, molens en bedrijven | Farms, mills, and businesses | 9,888 |
| Kastelen, landhuizen en parken | Castles, country houses, and parks | 5,529 |
| Religieuze gebouwen | Religious buildings | 4,351 |
| Verdedigingswerken en militaire gebouwen | Fortifications and military buildings | 2,402 |
| Handelsgebouwen, opslag- en transportgebouwen | Commercial, storage, and transport buildings | 2,204 |
| Archeologie (N) | Archaeology | 1,461 |
| Cultuur, gezondheid en wetenschap | Culture, health, and science | 1,331 |
| Voorwerpen op pleinen en dergelijke | Objects in public spaces | 1,240 |
| Weg- en waterbouwkundige werken | Road and hydraulic engineering works | 969 |
| Uitvaartcentra en begraafplaatsen | Funeral centres and cemeteries | 929 |
| Bestuursgebouwen, rechtsgebouwen en overheidsgebouwen | Government and judicial buildings | 724 |
| Sport, recreatie, vereniging en horeca | Sports, recreation, clubs, and hospitality | 541 |

One feature has a null main category.

### Example Subcategories

| Subcategory (Dutch) | English | Main category |
|---------------------|---------|---------------|
| Woonhuis(K) | Residential house | Woningen |
| Boerderij (M) | Farm | Boerderijen |
| Kerk en kerkonderdeel | Church and church component | Religieuze gebouwen |
| Kasteel, buitenplaats | Castle, country estate | Kastelen |
| Fort, vesting en -onderdelen | Fort, fortress, and components | Verdedigingswerken |
| Brug(C) | Bridge | Weg- en waterbouwkundige werken |
| Industrie- en poldermolen | Industrial and polder mill | Boerderijen, molens |
| Archeologie (N1) | Archaeology | Archeologie (N) |
| Gedenkteken(D) | Memorial/monument | Voorwerpen op pleinen |
| Bomvrij militair object | Bombproof military structure | Verdedigingswerken |

There are **66 distinct subcategories** in total. The letter-number codes in parentheses (K, M, C, D, N1, etc.) are legacy codes from an older classification system.


## Monument Nature (`aard_monum`)

| Dutch | English | Count | Description |
|-------|---------|-------|-------------|
| `onroerend gebouwd` | Built / immovable property | 61,612 | Buildings, structures, and built objects |
| `archeologisch` | Archaeological | 1,461 | Archaeological sites and terrain monuments |


## Geometry Origin (`herkomst`)

This field indicates the source from which the point location was derived:

| Value | English | Count | Description |
|-------|---------|-------|-------------|
| `BAG` | Building & Address Register | 45,499 | From the authoritative Dutch building and address registry. Most reliable source. |
| `divers` | Various/miscellaneous | 4,763 | Mixed or unspecified sources |
| `RCE dico` | RCE geocoder | 3,513 | Geocoded using the RCE's own 'dico' geocoding tool |
| `Bridgis` | Bridgis geocoding service | 3,076 | Commercial geocoding service |
| `RCE handmatig` | RCE manual | 1,767 | Manually positioned by RCE staff |
| `BRK` | Cadastral Register | 1,647 | From the Dutch cadastral registration |
| `AMR dico` | AMR geocoder | 1,476 | Geocoded via AMR/Archis archaeological data system |
| `GBKN` | Large-Scale Base Map | 1,199 | From the Grootschalige Basiskaart (now superseded by BGT) |
| `RCE bulk` | RCE bulk processing | 33 | Bulk-processed by RCE |
| `BGT` | Large-Scale Topography | 17 | From the Basisregistratie Grootschalige Topografie |
| *(null)* | Unknown | 83 | Source not recorded |


## Location Quality (`kwaliteit_`)

| Value | English | Count | Description |
|-------|---------|-------|-------------|
| `globaal` | Approximate | 37,881 (60%) | May be off by tens to hundreds of metres |
| `exact` | Exact | 21,041 (33%) | Directly on or very close to the monument |
| `besluit` | By decree/decision | 4,151 (7%) | As specified in the official designation decree; mainly archaeological monuments |

Note: The field name is truncated from "kwaliteit" due to the Shapefile 10-character field name limit.


## Contour Data Quality Issue

The contour file (`Rijksmonumentcontouren_28992.shp`) has a **significant data quality problem**:

- **ogrinfo** reports the geometry type as **Point** with an extent of **(0,0) - (0,0)**
- The `.shp` file is only **49 KB** for 4,149 features -- far too small to contain polygon data
- However, the `gml_id` values reference `NationalListedMonumentPolygons` (e.g., `NationalListedMonumentPolygons.10001`), confirming these should be polygon geometries
- The attribute data in the `.dbf` file (9.6 MB) appears intact

This strongly suggests the **polygon geometries were lost or corrupted** during the GML-to-Shapefile conversion by the data provider.

### Workarounds

1. **Use the PDOK OGC API** to obtain contour polygons with intact geometry:
   ```bash
   ogr2ogr -f GeoJSON rijksmonumentcontouren.geojson \
     "OAPIF:https://api.pdok.nl/rce/beschermde-gebieden-cultuurhistorie/ogc/v1" \
     rijksmonumentcontouren
   ```

2. **Use the points layer** as a fallback -- it covers all 63,073 monuments including those in the contours layer. The `rijksmonum` number can be used to join attributes if polygon geometry is obtained from elsewhere.


## Full Schema Reference

### Rijksmonumentpunten (Points) -- 63,073 features

| Field | Type | Truncated from | English | Nullable | Notes |
|-------|------|---------------|---------|----------|-------|
| `gml_parent` | String(254) | -- | GML Parent ID | Yes | Always null in this export |
| `gml_id` | String(254) | -- | GML ID | No | `NationalListedMonumentPoints.NNNNN` |
| `rijksmonum` | Real(20) | rijksmonumentnummer | Monument Number | No | Primary key; integer stored as real |
| `complex_nu` | Real(20) | complexnummer | Complex Number | Yes | Groups related monuments |
| `juridische` | String(254) | juridische status | Legal Status | No | Always "rijksmonument" |
| `aard_monum` | String(254) | aard monument | Monument Nature | No | "archeologisch" or "onroerend gebouwd" |
| `herkomst` | String(254) | -- | Geometry Origin | Yes | Source of point coordinates |
| `kwaliteit_` | String(254) | kwaliteit | Location Quality | No | "globaal", "exact", or "besluit" |
| `hoofdcateg` | String(254) | hoofdcategorie | Main Category | Yes | 13 categories |
| `subcategor` | String(254) | subcategorie | Subcategory | Yes | 66 subcategories |
| `rijksurl` | String(254) | -- | Register URL | No | Link to monument register |
| `geom` | String(254) | -- | Extra Geometry | Yes | Always null; GML conversion artifact |

### Rijksmonumentcontouren (Contours) -- 4,149 features

Same schema as points but **without** the `geom` string field. See [contour data quality issue](#contour-data-quality-issue) regarding geometry.

All 1,461 archaeological monuments have contours. Only 2,688 of ~61,600 built monuments (~4.4%) have contours.


## Coordinate Reference System

- **EPSG:28992** -- Amersfoort / RD New (Rijksdriehoekstelsel)
- Oblique Stereographic projection centered near Amersfoort
- Units: metres
- Valid for: Netherlands onshore, including Waddenzee, Dutch Wadden Islands, and 12-mile offshore coastal zone
- Geographic bounds: approximately 50.75N-53.7N, 3.2E-7.22E

The extent in RD coordinates is:
- Points: (13854, 306993) to (277502, 617910) -- covers the full Netherlands including Wadden Islands and the southern border areas

To convert to WGS 84 (EPSG:4326):
```bash
ogr2ogr -f GeoJSON -t_srs EPSG:4326 points_wgs84.geojson Rijksmonumentpunten_28992.shp
```


## Example Queries

### DuckDB

```sql
-- Install and load the spatial extension
INSTALL spatial;
LOAD spatial;

-- Read the Shapefile directly
SELECT * FROM ST_Read('data/Rijksmonumentpunten_28992.shp') LIMIT 10;

-- Count monuments by main category
SELECT hoofdcateg, COUNT(*) as count
FROM ST_Read('data/Rijksmonumentpunten_28992.shp')
GROUP BY hoofdcateg
ORDER BY count DESC;

-- Find all monuments in a complex
SELECT rijksmonum, complex_nu, hoofdcateg, subcategor
FROM ST_Read('data/Rijksmonumentpunten_28992.shp')
WHERE complex_nu = 507388
ORDER BY rijksmonum;

-- Count monuments by quality level
SELECT kwaliteit_ as quality, COUNT(*) as count,
       ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) as pct
FROM ST_Read('data/Rijksmonumentpunten_28992.shp')
GROUP BY kwaliteit_
ORDER BY count DESC;

-- Find all windmills (molens)
SELECT rijksmonum, subcategor, rijksurl
FROM ST_Read('data/Rijksmonumentpunten_28992.shp')
WHERE subcategor LIKE '%molen%';

-- After converting to GeoParquet, read directly:
SELECT * FROM 'rijksmonumentpunten.parquet' LIMIT 10;
```

### Python (GeoPandas)

```python
import geopandas as gpd

# Read the Shapefile
gdf = gpd.read_file("data/Rijksmonumentpunten_28992.shp")

# Basic info
print(f"Features: {len(gdf)}")
print(f"CRS: {gdf.crs}")
print(f"Columns: {list(gdf.columns)}")

# Count by main category
print(gdf["hoofdcateg"].value_counts())

# Filter to churches
churches = gdf[gdf["subcategor"] == "Kerk en kerkonderdeel"]
print(f"Churches: {len(churches)}")

# Find all monuments in a specific complex
complex_507388 = gdf[gdf["complex_nu"] == 507388]
print(complex_507388[["rijksmonum", "subcategor", "rijksurl"]])

# Convert to WGS 84 for web mapping
gdf_wgs84 = gdf.to_crs(epsg=4326)

# Save as GeoParquet
gdf.to_parquet("rijksmonumentpunten.parquet")
```

### ogr2ogr

```bash
# Convert to GeoJSON in WGS 84
ogr2ogr -f GeoJSON -t_srs EPSG:4326 \
  rijksmonumentpunten.geojson \
  data/Rijksmonumentpunten_28992.shp

# Convert to GeoParquet (keeps EPSG:28992)
ogr2ogr -f Parquet \
  rijksmonumentpunten.parquet \
  data/Rijksmonumentpunten_28992.shp

# Convert to GeoParquet in WGS 84
ogr2ogr -f Parquet -t_srs EPSG:4326 \
  rijksmonumentpunten_4326.parquet \
  data/Rijksmonumentpunten_28992.shp

# Filter to just archaeological monuments
ogr2ogr -f Parquet \
  -where "aard_monum = 'archeologisch'" \
  rijksmonumenten_archeologie.parquet \
  data/Rijksmonumentpunten_28992.shp
```


## Converting to GeoParquet

For cloud-native workflows (e.g., publishing to a Portolan catalog), convert the Shapefile to GeoParquet:

```bash
# Convert points to GeoParquet, reprojecting to WGS 84
ogr2ogr -f Parquet -t_srs EPSG:4326 \
  rijksmonumentpunten.parquet \
  data/Rijksmonumentpunten_28992.shp

# For the contours, use the PDOK OGC API instead of the broken Shapefile:
ogr2ogr -f Parquet -t_srs EPSG:4326 \
  rijksmonumentcontouren.parquet \
  "OAPIF:https://api.pdok.nl/rce/beschermde-gebieden-cultuurhistorie/ogc/v1" \
  rijksmonumentcontouren
```

Note on field names: When converting from Shapefile, consider renaming truncated field names to their full versions for clarity:

| Shapefile name | Full name |
|---------------|-----------|
| `rijksmonum` | `rijksmonumentnummer` |
| `complex_nu` | `complexnummer` |
| `juridische` | `juridische_status` |
| `aard_monum` | `aard_monument` |
| `kwaliteit_` | `kwaliteit` |
| `hoofdcateg` | `hoofdcategorie` |
| `subcategor` | `subcategorie` |

This can be done with ogr2ogr's `-sql` option:

```bash
ogr2ogr -f Parquet -t_srs EPSG:4326 \
  rijksmonumentpunten.parquet \
  data/Rijksmonumentpunten_28992.shp \
  -sql "SELECT gml_id, \
    rijksmonum AS rijksmonumentnummer, \
    complex_nu AS complexnummer, \
    juridische AS juridische_status, \
    aard_monum AS aard_monument, \
    herkomst, \
    kwaliteit_ AS kwaliteit, \
    hoofdcateg AS hoofdcategorie, \
    subcategor AS subcategorie, \
    rijksurl \
  FROM Rijksmonumentpunten_28992"
```

(The `gml_parent` and `geom` fields are dropped since they are always null.)


## Related Datasets

### Beschermde stads- en dorpsgezichten (Protected Townscapes)

While rijksmonumenten protect individual buildings and sites, **beschermde stads- en dorpsgezichten** protect entire *areas* for their historical character. These are designated by the national government and impose additional planning restrictions on new construction within the protected zone.

Available from the same RCE/PDOK source:
- https://api.pdok.nl/rce/beschermde-gebieden-cultuurhistorie/ogc/v1/collections/beschermdestadsendorpsgezichtpunten/items
- https://api.pdok.nl/rce/beschermde-gebieden-cultuurhistorie/ogc/v1/collections/beschermdestadsendorpsgezichtcontouren/items

### UNESCO World Heritage Sites

Some rijksmonumenten are part of UNESCO World Heritage Sites. Dutch examples include:
- Canal Ring Area of Amsterdam (Grachtengordel)
- Defence Line of Amsterdam (Stelling van Amsterdam)
- Rietveld Schroderhuis in Utrecht
- Ir.D.F. Woudagemaal (steam pumping station in Lemmer)
- Van Nellefabriek in Rotterdam
- Colonies of Benevolence (Kolonieen van Weldadigheid)

### Gemeentelijke monumenten (Municipal Monuments)

Beyond the ~63,000 national monuments, an estimated 50,000-100,000 additional monuments are protected at the municipal level (*gemeentelijke monumenten*). These are maintained by individual municipalities and are not available as a single national dataset.

### Provinciaal monumenten

A small number of monuments are designated at the provincial level. North Holland, for instance, maintains its own provincial monument list.


## Using `rijksurl` for Lookups

Every monument has a `rijksurl` field with a direct link to its page in the online monument register:

```
https://monumentenregister.cultureelerfgoed.nl/monumenten/341971
```

The register page for each monument typically includes:
- Full address and municipality
- Description (function, architectural style, notable features)
- Photographs
- Designation date and legal basis
- Complex membership (if applicable)
- Category and subcategory classification
- Cadastral parcel references

This is useful for enriching the geodata with additional context not included in the Shapefile attributes.


## Notes and Caveats

1. **Shapefile field name truncation**: Several field names are truncated to 10 characters (the Shapefile format limit). See the schema reference for the full names.

2. **Geometry precision varies**: The `kwaliteit_` field indicates location accuracy. 60% of points are only "globaal" (approximate). For precise spatial analysis, filter to `kwaliteit_ = 'exact'` or `'besluit'`.

3. **Contour coverage is partial**: Only 4,149 of 63,073 monuments (6.6%) have contours. All archaeological sites have contours, but only ~4% of built monuments do. The contour Shapefile also has a geometry corruption issue (see above).

4. **Monument numbers as floats**: The `rijksmonum` and `complex_nu` fields are stored as `Real(20)` in the Shapefile. When converting to other formats, cast these to integers to avoid trailing `.0` in IDs.

5. **Single legal status**: All features in this dataset have `juridische = 'rijksmonument'`. Municipal and provincial monuments are separate datasets.

6. **The `geom` field is an artifact**: The string field named `geom` in the points layer is always null -- it is a remnant of the GML-to-Shapefile conversion, not actual geometry data. The real geometry is in the Shapefile's native geometry column.

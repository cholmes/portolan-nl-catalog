# RCE — Cultural Heritage Agency (Rijksdienst voor het Cultureel Erfgoed) / Netherlands

## What This Is

One collection from the RCE, the Dutch national agency for cultural heritage. The RCE
advises the government on heritage policy, maintains the national monument register, and
manages heritage data infrastructure.

## Collections

### rijksmonumenten/ — National Monuments
63,073 nationally listed monuments (rijksmonumenten) — buildings, objects, and sites
protected under the Heritage Act (Erfgoedwet, 2016; successor to the Monumentenwet 1988).
National monument designation means the owner must obtain a permit for modifications, and
demolition is generally prohibited.

- File: `rijksmonumenten.parquet` (3.7 MB)
- CRS: EPSG:28992 (RD New)
- Geometry: Points only (no building footprints)
- Key fields: `rijksmonum` (monument number), `hoofdcateg` (main category), `subcategor` (subcategory), `rijksurl` (register link)

## The 13 Main Categories

Monuments are classified into 13 hoofdcategorien with 66 subcategories:

| Category | English | Count |
|----------|---------|-------|
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

Half of all monuments are residential buildings. 22% belong to a "complex" — an ensemble
of related monuments (e.g., a church with its rectory).

## The Monument Register

Every monument has a direct URL to its register page:
`https://monumentenregister.cultureelerfgoed.nl/monumenten/{nummer}`

The `rijksurl` field in the data contains this link. The register page shows the full
description, photos, legal status, and complex membership.

## Heritage Act (Erfgoedwet)

The Erfgoedwet (2016) replaced the Monumentenwet 1988 and consolidated several heritage
laws. Under the Act:
- The national government designates rijksmonumenten
- Municipalities can designate gemeentelijke monumenten (not in this dataset)
- Provinces can designate provinciale monumenten (not in this dataset)
- Protected townscapes (beschermde stads- en dorpsgezichten) are area-level designations

This dataset only covers national monuments (rijksmonumenten).

## Example Queries

### Count monuments by category

```sql
SELECT hoofdcateg, COUNT(*) AS count
FROM read_parquet('https://data.source.coop/cholmes/portolan-nl/rce/rijksmonumenten/rijksmonumenten.parquet')
GROUP BY hoofdcateg
ORDER BY count DESC
```

### Find castles and country houses

```sql
SELECT CAST(rijksmonum AS INT) AS monument_nr, subcategor, rijksurl
FROM read_parquet('https://data.source.coop/cholmes/portolan-nl/rce/rijksmonumenten/rijksmonumenten.parquet')
WHERE hoofdcateg = 'Kastelen, landhuizen en parken'
ORDER BY subcategor
```

### Monuments near Utrecht (within 2 km of city center)

```sql
INSTALL spatial; LOAD spatial;

SELECT CAST(rijksmonum AS INT) AS nr, hoofdcateg, subcategor, rijksurl,
       ST_Distance(
           ST_GeomFromWKB(geometry),
           ST_Transform(ST_Point(5.1214, 52.0907), 'EPSG:4326', 'EPSG:28992')
       ) AS distance_m
FROM read_parquet('https://data.source.coop/cholmes/portolan-nl/rce/rijksmonumenten/rijksmonumenten.parquet')
WHERE distance_m < 2000
ORDER BY distance_m
LIMIT 20
```

## See Also

The `rijksmonumenten/AGENTS.md` file has detailed field descriptions, location quality notes,
complex groupings, and more query patterns.

---
*Hand-maintained agent guide (ported from this collection's llms.txt in August 2026). Update it alongside collection.json.*

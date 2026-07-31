# Portolan-NL Styles Design Spec

**Date:** 2026-05-07

## Overview

Create rich, data-driven Mapbox GL v8 style files for all 19 collections in portolan-nl. Each collection gets a `styles/` directory with a default style and, where the data supports it, additional thematic styles highlighting interesting attributes. The goal is a visually diverse catalog where every collection has its own color identity and the most attribute-rich collections offer multiple viewing perspectives.

## Convention

All styles follow the portolan STAC asset convention (ADR-0044):

- Style files live in `{collection}/styles/{name}.json`
- Each style is a complete Mapbox GL v8 JSON file
- PMTiles source paths are relative: `../{filename}.pmtiles`
- Collections declare `portolan:styles` manifest (first entry = default)
- Assets use key prefix `styles/`, role `["style"]`, type `application/json`

After creating the style files, run `portolan add --collection {id}` to register them as STAC assets, or manually update `collection.json`.

## Color Strategy

Each subcatalog gets a distinct color family to create visual variety across the catalog:

| Subcatalog | Color Family | Rationale |
|------------|-------------|-----------|
| **kadaster** | Warm oranges/reds | Built environment, buildings, boundaries |
| **cbs** | Cool blues/purples | Statistics, data visualization |
| **rijkswaterstaat** | Teals/aquas | Water infrastructure |
| **rce** | Golds/ambers | Heritage, historic |
| **rvo** | Greens | Nature, environment |

Within each subcatalog, individual collections use variations within their family.

---

## Kadaster Collections

### 1. bag_light (BAG Buildings)

**PMTiles:** `bag-light.pmtiles` | **Layer:** `panden` | **Geometry:** polygon
**Key fields:** `bouwjaar` (int, construction year), `gebruiksdoel` (string, usage), `status` (string)

**Styles:**

| Style | File | Description |
|-------|------|-------------|
| **default** | `styles/default.json` | Warm coral fill with darker outlines. Simple, clean building footprints. |
| by-age | `styles/by-age.json` | Construction year color ramp: dark brown (pre-1800) → brick red (1800-1900) → orange (1900-1960) → gold (1960-2000) → light yellow (post-2000). Uses `step` expression on `bouwjaar`. |
| by-use | `styles/by-use.json` | Color by `gebruiksdoel`: residential (coral), commercial (blue), industrial (gray), healthcare (green), education (purple), mixed (orange). Uses `match` expression. |

**Default style example:**

```json
{
  "version": 8,
  "name": "BAG Buildings — Default",
  "sources": {
    "bag": {
      "type": "vector",
      "url": "pmtiles://../bag-light.pmtiles"
    }
  },
  "layers": [
    {
      "id": "buildings-fill",
      "type": "fill",
      "source": "bag",
      "source-layer": "panden",
      "paint": {
        "fill-color": "#E07050",
        "fill-opacity": 0.7
      }
    },
    {
      "id": "buildings-outline",
      "type": "line",
      "source": "bag",
      "source-layer": "panden",
      "paint": {
        "line-color": "#A04030",
        "line-width": 0.5
      }
    }
  ]
}
```

**By-age style — key paint expression:**

```json
{
  "fill-color": [
    "step", ["get", "bouwjaar"],
    "#5C3317",
    1800, "#8B4513",
    1900, "#CD6600",
    1940, "#E8A040",
    1970, "#F0C060",
    2000, "#FCE88A"
  ],
  "fill-opacity": 0.8
}
```

**By-use style — key paint expression:**

```json
{
  "fill-color": [
    "match", ["get", "gebruiksdoel"],
    "woonfunctie", "#E07050",
    "winkelfunctie", "#4A90D9",
    "kantoorfunctie", "#4A90D9",
    "industriefunctie", "#888888",
    "gezondheidszorgfunctie", "#50B060",
    "onderwijsfunctie", "#9B59B6",
    "bijeenkomstfunctie", "#E67E22",
    "logiesfunctie", "#F1C40F",
    "sportfunctie", "#2ECC71",
    "overige gebruiksfunctie", "#BDC3C7",
    "#CCCCCC"
  ]
}
```

---

### 2. bestuurlijke_gebieden (Administrative Areas)

**PMTiles:** `bestuurlijke_gebieden.pmtiles` | **Layer:** `gemeenten` | **Geometry:** polygon
**Key fields:** `naam` (string), `code` (string), `ligt_in_provincie_naam` (string)

**Styles:**

| Style | File | Description |
|-------|------|-------------|
| **default** | `styles/default.json` | Light peach fill with thin boundaries. Clean administrative look. |

Only one style — the data is purely boundary/label data with no numeric attributes.

**Default style:**

```json
{
  "version": 8,
  "name": "Administrative Areas — Default",
  "sources": {
    "admin": {
      "type": "vector",
      "url": "pmtiles://../bestuurlijke_gebieden.pmtiles"
    }
  },
  "layers": [
    {
      "id": "municipalities-fill",
      "type": "fill",
      "source": "admin",
      "source-layer": "gemeenten",
      "paint": {
        "fill-color": "#FDEBD0",
        "fill-opacity": 0.5
      }
    },
    {
      "id": "municipalities-line",
      "type": "line",
      "source": "admin",
      "source-layer": "gemeenten",
      "paint": {
        "line-color": "#C0392B",
        "line-width": 1.2
      }
    },
    {
      "id": "municipalities-label",
      "type": "symbol",
      "source": "admin",
      "source-layer": "gemeenten",
      "layout": {
        "text-field": "{naam}",
        "text-size": 11,
        "text-font": ["Open Sans Regular"]
      },
      "paint": {
        "text-color": "#333333",
        "text-halo-color": "#FFFFFF",
        "text-halo-width": 1
      }
    }
  ]
}
```

---

### 3. inspire_buildings (INSPIRE Buildings)

**PMTiles:** `buildings.pmtiles` | **Layer:** `buildings` | **Geometry:** polygon
**Key fields:** `anyPoint` (string, construction date ISO 8601)

**Styles:**

| Style | File | Description |
|-------|------|-------------|
| **default** | `styles/default.json` | Muted terra cotta fill. Distinct from BAG to show these are the INSPIRE harmonized version. |
| by-construction-date | `styles/by-construction-date.json` | Parse year from `anyPoint` string, color ramp similar to BAG by-age but using `slice` expression. |

**Default style — distinct from BAG:**

```json
{
  "layers": [
    {
      "id": "buildings-fill",
      "type": "fill",
      "source": "inspire",
      "source-layer": "buildings",
      "paint": {
        "fill-color": "#C4956A",
        "fill-opacity": 0.65
      }
    },
    {
      "id": "buildings-outline",
      "type": "line",
      "source": "inspire",
      "source-layer": "buildings",
      "paint": {
        "line-color": "#8B6914",
        "line-width": 0.4
      }
    }
  ]
}
```

---

## CBS Collections

### 4. bestand_bodemgebruik_2017 (Land Use)

**PMTiles:** `bbg2017.pmtiles` | **Layer:** `bbg2017` | **Geometry:** polygon
**Key fields:** `bodemgebruik` (string, land use type), `categorie` (string, category), `bg2017` (int, code)

**Styles:**

| Style | File | Description |
|-------|------|-------------|
| **default** | `styles/default.json` | Color by `categorie` — green (agriculture), gray (built), blue (water), dark green (forest), yellow (recreation). Classic land use map. |
| by-detailed-use | `styles/by-detailed-use.json` | Color by `bodemgebruik` for finer granularity. 20+ classes with varied hues. |

**Default style — categorie match:**

```json
{
  "fill-color": [
    "match", ["get", "categorie"],
    "Agrarisch terrein", "#A8D08D",
    "Bos en open natuurlijk terrein", "#2E7D32",
    "Bebouwd terrein", "#9E9E9E",
    "Recreatieterrein", "#FDD835",
    "Semi-bebouwd terrein", "#BDBDBD",
    "Verkeersterrein", "#666666",
    "Binnenwater", "#42A5F5",
    "Buitenwater", "#1565C0",
    "#EEEEEE"
  ]
}
```

---

### 5. bevolkingsspreiding (Population Distribution)

**PMTiles:** `bevolkingsspreiding.pmtiles` | **Layers:** `grid`, `lau`, `nuts2` | **Geometry:** polygon
**Key fields:** `obsvalue` (float, population count), `periodofreference` (string, year)

**Styles:**

| Style | File | Description |
|-------|------|-------------|
| **default** | `styles/default.json` | Population density heatmap on `grid` layer. Blue-to-red sequential ramp on `obsvalue`. |

**Default style — grid layer with population ramp:**

```json
{
  "fill-color": [
    "interpolate", ["linear"], ["get", "obsvalue"],
    0, "#F7FBFF",
    100, "#C6DBEF",
    500, "#6BAED6",
    1000, "#2171B5",
    5000, "#08306B"
  ],
  "fill-opacity": 0.75
}
```

---

### 6. existing_landuse_inspire (INSPIRE Land Use)

**PMTiles:** `existing_landuse.pmtiles` | **Layer:** `existing_landuse` | **Geometry:** polygon
**Key fields:** `description` (string, English land use type)

**Styles:**

| Style | File | Description |
|-------|------|-------------|
| **default** | `styles/default.json` | Color by `description` — INSPIRE harmonized land use types with European-standard colors. |

**Default style — description match:**

```json
{
  "fill-color": [
    "match", ["get", "description"],
    "Residential area", "#E8B4B8",
    "Railroad", "#666666",
    "Road", "#999999",
    "Industrial area", "#C0A0C0",
    "Commercial area", "#D4A0A0",
    "Agricultural grassland", "#A8D08D",
    "Agricultural crops", "#C5E1A5",
    "Deciduous forest", "#2E7D32",
    "Coniferous forest", "#1B5E20",
    "Mixed forest", "#388E3C",
    "Inland water", "#42A5F5",
    "Sea", "#1565C0",
    "Recreational area", "#FDD835",
    "#DDDDDD"
  ]
}
```

---

### 7. gezondheid (Health Statistics)

**PMTiles:** `gezondheid.pmtiles` | **Layers:** `doctors`, `deaths` | **Geometry:** polygon
**Key fields (doctors):** `HH_NL_NUTS2_doctors_STATCODE`, province-level stats
**Key fields (deaths):** `HH_NL_NUTS2_nrdeath_OBS_VALUE`

**Styles:**

| Style | File | Description |
|-------|------|-------------|
| **default** | `styles/default.json` | Purple choropleth showing doctors per province. Light lavender to deep purple. |

Small dataset (12 provinces) — one style is sufficient.

---

### 8. postcode6 (Statistics per Postcode)

**PMTiles:** `postcode6.pmtiles` | **Layer:** `postcode6` | **Geometry:** polygon
**Key fields:** `aantal_inwoners` (int), `gemiddeld_aardgasverbruik_totaal` (int), `gemiddeld_elektriciteitsverbruik_totaal` (int), `mediaan_inkomen_huishouden` (string), `aantal_woningen_bouwjaar_voor_1945` (int)

**Styles:**

| Style | File | Description |
|-------|------|-------------|
| **default** | `styles/default.json` | Population density: blue sequential ramp on `aantal_inwoners`. |
| by-income | `styles/by-income.json` | Median household income choropleth. Green-to-purple diverging ramp. |
| by-energy | `styles/by-energy.json` | Gas consumption: yellow-to-red ramp on `gemiddeld_aardgasverbruik_totaal`. Highlights energy transition patterns. |
| by-housing-age | `styles/by-housing-age.json` | Ratio of pre-1945 housing. Brown-to-cream ramp showing historic vs modern neighborhoods. |

**Default style — population ramp:**

```json
{
  "fill-color": [
    "step", ["get", "aantal_inwoners"],
    "#F7FBFF",
    10, "#DEEBF7",
    50, "#9ECAE1",
    100, "#4292C6",
    300, "#2171B5",
    500, "#08306B"
  ],
  "fill-opacity": 0.8
}
```

**By-energy style — gas consumption:**

```json
{
  "fill-color": [
    "step", ["get", "gemiddeld_aardgasverbruik_totaal"],
    "#FFFFCC",
    500, "#FED976",
    1000, "#FEB24C",
    1500, "#FD8D3C",
    2000, "#FC4E2A",
    2500, "#E31A1C",
    3000, "#B10026"
  ],
  "fill-opacity": 0.8
}
```

---

### 9. wijken_en_buurten (Districts and Neighborhoods)

**PMTiles:** `wijken_en_buurten.pmtiles` | **Layers:** `buurten`, `wijken`, `gemeenten` | **Geometry:** polygon
**Key fields:** `aantalInwoners` (int), `bevolkingsdichtheidInwonersPerKm2` (int), `percentagePersonen65JaarEnOuder` (int), `gemiddeldeHuishoudsgrootte` (float), `percentageEenpersoonshuishoudens` (int)

**Styles:**

| Style | File | Description |
|-------|------|-------------|
| **default** | `styles/default.json` | Population density on `buurten` layer. Blue sequential ramp on `bevolkingsdichtheidInwonersPerKm2`. |
| by-aging | `styles/by-aging.json` | Percentage 65+ population. White-to-purple ramp on `percentagePersonen65JaarEnOuder`. Shows aging patterns. |
| by-household-size | `styles/by-household-size.json` | Average household size. Diverging ramp (blue=small, red=large) on `gemiddeldeHuishoudsgrootte`. |

**Default style — population density:**

```json
{
  "fill-color": [
    "step", ["get", "bevolkingsdichtheidInwonersPerKm2"],
    "#F7FBFF",
    500, "#C6DBEF",
    1000, "#6BAED6",
    3000, "#3182BD",
    5000, "#2171B5",
    10000, "#08306B"
  ],
  "fill-opacity": 0.75
}
```

---

## Rijkswaterstaat Collections

### 10. bergingsgebieden (Flood Retention Areas)

**PMTiles:** `bergingsgebieden.pmtiles` | **Layer:** `bergingsgebieden` | **Geometry:** polygon
**Key fields:** `bergendvermogen` (double, retention capacity), `naam` (string)

**Styles:**

| Style | File | Description |
|-------|------|-------------|
| **default** | `styles/default.json` | Teal fill with dashed outline, evoking water/flood zones. Labels with `naam`. |

```json
{
  "layers": [
    {
      "id": "retention-fill",
      "type": "fill",
      "source": "rws",
      "source-layer": "bergingsgebieden",
      "paint": {
        "fill-color": "#80CBC4",
        "fill-opacity": 0.5
      }
    },
    {
      "id": "retention-outline",
      "type": "line",
      "source": "rws",
      "source-layer": "bergingsgebieden",
      "paint": {
        "line-color": "#00695C",
        "line-width": 1.5,
        "line-dasharray": [4, 2]
      }
    }
  ]
}
```

---

### 11. fme_disk_tunnels (Tunnels)

**PMTiles:** `fme_disk_tunnels.pmtiles` | **Layer:** `fme_disk_tunnels` | **Geometry:** point
**Key fields:** `tunnelnaam` (string), `wegnummer` (string), `jaar_openstelling` (string), `status` (string)

**Styles:**

| Style | File | Description |
|-------|------|-------------|
| **default** | `styles/default.json` | Teal circles with white border, sized by zoom. Labels with `tunnelnaam`. |

```json
{
  "layers": [
    {
      "id": "tunnels-circle",
      "type": "circle",
      "source": "rws",
      "source-layer": "fme_disk_tunnels",
      "paint": {
        "circle-radius": ["interpolate", ["linear"], ["zoom"], 6, 4, 12, 10],
        "circle-color": "#009688",
        "circle-stroke-color": "#FFFFFF",
        "circle-stroke-width": 1.5
      }
    },
    {
      "id": "tunnels-label",
      "type": "symbol",
      "source": "rws",
      "source-layer": "fme_disk_tunnels",
      "minzoom": 8,
      "layout": {
        "text-field": "{tunnelnaam}",
        "text-size": 11,
        "text-offset": [0, 1.5],
        "text-font": ["Open Sans Regular"]
      },
      "paint": {
        "text-color": "#004D40",
        "text-halo-color": "#FFFFFF",
        "text-halo-width": 1
      }
    }
  ]
}
```

---

### 12. hectometervakken_vaargeul (Water Depth Fairway Sections)

**PMTiles:** `hectometervakken_vaargeul.pmtiles` | **Layer:** `hectometervakken_vaargeul` | **Geometry:** polygon
**Key fields:** `vak_ID` (string) — minimal attributes

**Styles:**

| Style | File | Description |
|-------|------|-------------|
| **default** | `styles/default.json` | Light aqua fill with darker outline. Clean navigational chart appearance. |

---

### 13. rijksviswegen_2024 (Fish Migration Routes)

**PMTiles:** `rijksviswegen_2024.pmtiles` | **Layer:** `rijksviswegen_2024` | **Geometry:** line
**Key fields:** `Status2024` (string), `MIGR_TYPE` (string), `NAAM` (string)

**Styles:**

| Style | File | Description |
|-------|------|-------------|
| **default** | `styles/default.json` | Color lines by `Status2024` connectivity status. Green=connected, red=blocked, orange=partial. |
| by-migration-type | `styles/by-migration-type.json` | Color by `MIGR_TYPE` — upstream, downstream, bidirectional. |

**Default style — connectivity status:**

```json
{
  "line-color": [
    "match", ["get", "Status2024"],
    "passeerbaar", "#2E7D32",
    "deels passeerbaar", "#FF9800",
    "niet passeerbaar", "#C62828",
    "onbekend", "#9E9E9E",
    "#BDBDBD"
  ],
  "line-width": 2.5
}
```

---

### 14. sluizen (Navigation Locks)

**PMTiles:** `sluizen.pmtiles` | **Layer:** `sluizen` | **Geometry:** point
**Key fields:** `NAAM` (string), `NR_KOLKEN` (int, number of chambers), `BHR_NAAM` (string, operator)

**Styles:**

| Style | File | Description |
|-------|------|-------------|
| **default** | `styles/default.json` | Dark teal circles sized by `NR_KOLKEN`. Labels with `NAAM`. |

```json
{
  "circle-radius": [
    "step", ["get", "NR_KOLKEN"],
    5,
    2, 7,
    3, 10,
    4, 13
  ],
  "circle-color": "#00796B"
}
```

---

### 15. waterkeringen (Flood Defenses)

**PMTiles:** `waterkeringen.pmtiles` | **Layer:** `waterkeringen` | **Geometry:** line
**Key fields:** `NORMTYP_O` (string, norm type), `TRAJECT_ID` (string)

**Styles:**

| Style | File | Description |
|-------|------|-------------|
| **default** | `styles/default.json` | Bold teal lines with width scaled by zoom. Evokes the critical infrastructure character of Dutch dike systems. |

```json
{
  "line-color": "#00897B",
  "line-width": ["interpolate", ["linear"], ["zoom"], 6, 1.5, 12, 4]
}
```

---

### 16. zero_emissiezones (Zero Emission Zones)

**PMTiles:** `zero_emissiezones.pmtiles` | **Layer:** `zero_emissiezones` | **Geometry:** polygon
**Key fields:** `Naam` (string), `Soort` (string, LEZ/ZES type), `Startdatum` (timestamp)

**Styles:**

| Style | File | Description |
|-------|------|-------------|
| **default** | `styles/default.json` | Color by `Soort` zone type. Green for ZES, blue-green for LEZ. Labels with `Naam`. |

```json
{
  "fill-color": [
    "match", ["get", "Soort"],
    "ZES", "#26A69A",
    "ZEZ", "#26A69A",
    "Milieuzone", "#80CBC4",
    "#B2DFDB"
  ],
  "fill-opacity": 0.5
}
```

---

## RCE Collections

### 17. rijksmonumenten (National Monuments)

**PMTiles:** `rijksmonumenten.pmtiles` | **Layer:** `rijksmonumenten` | **Geometry:** point
**Key fields:** `hoofdcateg` (string, main category), `subcategor` (string, subcategory), `aard_monum` (string, archaeological/built)

**Styles:**

| Style | File | Description |
|-------|------|-------------|
| **default** | `styles/default.json` | Amber/gold circles. Evokes heritage and age. |
| by-category | `styles/by-category.json` | Color by `hoofdcateg`: Woningen (amber), Boerderijen (brown), Kastelen (gold), Religieuze gebouwen (deep gold), Molens (olive), etc. |
| by-type | `styles/by-type.json` | Two-tone by `aard_monum`: built heritage (gold) vs archaeological (dark sienna). |

**Default style:**

```json
{
  "circle-radius": ["interpolate", ["linear"], ["zoom"], 6, 2, 14, 6],
  "circle-color": "#F9A825",
  "circle-stroke-color": "#F57F17",
  "circle-stroke-width": 0.8
}
```

**By-category — key expression:**

```json
{
  "circle-color": [
    "match", ["get", "hoofdcateg"],
    "Woningen en woningbouwcomplexen", "#FFB300",
    "Boerderijen en molens", "#8D6E63",
    "Kastelen, landhuizen en buitenplaatsen", "#FDD835",
    "Religieuze gebouwen", "#FF8F00",
    "Losse objecten en straatmeubilair", "#A1887F",
    "Handels- en kantoorgebouwen", "#FFD54F",
    "Industrie- en poldermolens", "#795548",
    "Weg- en waterwerken", "#BCAAA4",
    "Verdedigingswerken en militaire gebouwen", "#6D4C41",
    "Gezondheidszorg en wetenschap", "#FFCA28",
    "Overheidsgebouwen", "#FFC107",
    "#E0E0E0"
  ]
}
```

---

## RVO Collections

### 18. nationale_parken (National Parks)

**PMTiles:** `nationale_parken.pmtiles` | **Layer:** `nationale_parken` | **Geometry:** polygon
**Key fields:** `naam` (string), `hectares` (float), `nr` (int)

**Styles:**

| Style | File | Description |
|-------|------|-------------|
| **default** | `styles/default.json` | Deep green fill with darker borders. Labels with `naam`. Nature-reserve green distinct from generic green. |

```json
{
  "layers": [
    {
      "id": "parks-fill",
      "type": "fill",
      "source": "rvo",
      "source-layer": "nationale_parken",
      "paint": {
        "fill-color": "#388E3C",
        "fill-opacity": 0.45
      }
    },
    {
      "id": "parks-outline",
      "type": "line",
      "source": "rvo",
      "source-layer": "nationale_parken",
      "paint": {
        "line-color": "#1B5E20",
        "line-width": 2
      }
    },
    {
      "id": "parks-label",
      "type": "symbol",
      "source": "rvo",
      "source-layer": "nationale_parken",
      "layout": {
        "text-field": "{naam}",
        "text-size": 12,
        "text-font": ["Open Sans Regular"]
      },
      "paint": {
        "text-color": "#1B5E20",
        "text-halo-color": "#FFFFFF",
        "text-halo-width": 1.5
      }
    }
  ]
}
```

---

### 19. natura2000 (Natura 2000 Protected Areas)

**PMTiles:** `natura2000.pmtiles` | **Layer:** `natura2000` | **Geometry:** polygon
**Key fields:** `beschermin` (string, protection type: VR/HR/VR+HR), `naam_n2k` (string)

**Styles:**

| Style | File | Description |
|-------|------|-------------|
| **default** | `styles/default.json` | Forest green fill with hatched feel (dashed outline). Lighter than Nationale Parken to distinguish the two. |
| by-directive | `styles/by-directive.json` | Color by `beschermin`: Birds Directive = sky blue, Habitats Directive = forest green, Both = teal. Shows EU legal framework. |

**Default style:**

```json
{
  "fill-color": "#66BB6A",
  "fill-opacity": 0.4
}
```

**By-directive — key expression:**

```json
{
  "fill-color": [
    "match", ["get", "beschermin"],
    "VR", "#42A5F5",
    "HR", "#388E3C",
    "VR+HR", "#00897B",
    "HR groeve", "#795548",
    "#A5D6A7"
  ],
  "fill-opacity": 0.55
}
```

---

## Summary

| Collection | Subcatalog | Default Color | # Styles | Multi-style Attributes |
|------------|-----------|--------------|----------|----------------------|
| bag_light | kadaster | Coral | 3 | bouwjaar, gebruiksdoel |
| bestuurlijke_gebieden | kadaster | Peach | 1 | — |
| inspire_buildings | kadaster | Terra cotta | 2 | anyPoint |
| bestand_bodemgebruik_2017 | cbs | Multi (land use) | 2 | categorie, bodemgebruik |
| bevolkingsspreiding | cbs | Blue ramp | 1 | obsvalue |
| existing_landuse_inspire | cbs | Multi (land use) | 1 | description |
| gezondheid | cbs | Purple | 1 | — |
| postcode6 | cbs | Blue ramp | 4 | inwoners, income, gas, housing age |
| wijken_en_buurten | cbs | Blue ramp | 3 | density, aging, household |
| bergingsgebieden | rws | Teal | 1 | — |
| fme_disk_tunnels | rws | Teal circles | 1 | — |
| hectometervakken_vaargeul | rws | Aqua | 1 | — |
| rijksviswegen_2024 | rws | Green/red status | 2 | Status2024, MIGR_TYPE |
| sluizen | rws | Dark teal | 1 | NR_KOLKEN |
| waterkeringen | rws | Teal lines | 1 | — |
| zero_emissiezones | rws | Green/teal | 1 | Soort |
| rijksmonumenten | rce | Gold | 3 | hoofdcateg, aard_monum |
| nationale_parken | rvo | Deep green | 1 | — |
| natura2000 | rvo | Forest green | 2 | beschermin |

**Total: 19 collections, 32 style files**

## Implementation Order

1. Start with the richest collections: bag_light, postcode6, wijken_en_buurten
2. Then the thematic ones: bestand_bodemgebruik_2017, rijksmonumenten, rijksviswegen_2024
3. Then simple single-style collections: all Rijkswaterstaat infrastructure, RVO nature areas
4. Run `portolan add` to register all styles as STAC assets
5. Push to source.coop

## Open Questions

1. **Font availability:** Mapbox GL labels require font glyphs. `Open Sans Regular` is used throughout — verify that portolan-browser / ol-mapbox-style can resolve this or provide a glyph source.
2. **PMTiles source URL format:** Style JSON uses `pmtiles://../{file}.pmtiles`. Confirm portolan-browser resolves this relative to the style file location, not the collection.json location.
3. **Privacy-suppressed values:** postcode6 uses `-99997` for suppressed values. Styles should filter these out (add `["!=", ["get", "aantal_inwoners"], -99997]` filter) or map them to a neutral color.

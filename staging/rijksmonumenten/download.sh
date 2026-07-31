#!/usr/bin/env bash
# download.sh — Download Rijksmonumenten (National Monuments) data from RCE
#
# Source: Rijksdienst voor het Cultureel Erfgoed (RCE) — Cultural Heritage Agency
# Download service: https://services.rce.geovoorziening.nl/www/download/nl.xml
#
# Two layers are available:
#   1. Rijksmonumentpunten  — Point locations of all ~63,000 national monuments
#   2. Rijksmonumentcontouren — Contour/outline polygons (subset: ~4,100 monuments)
#
# Both files are in EPSG:28992 (Amersfoort / RD New), the Dutch national CRS.
# Shapefiles are UTF-8 encoded (.cpg file confirms this).
#
# NOTE: The contour Shapefile has a known data quality issue — ogrinfo reports
# geometry type as Point with extent (0,0)-(0,0), even though the gml_id values
# reference "NationalListedMonumentPolygons". The .shp header shape type should
# be inspected; the actual polygon geometry data may be stored but not recognized
# correctly. Consider using the PDOK OGC API as an alternative source for
# contour data (see below).
#
# License: Public domain / no restrictions stated in the Atom download feed.

set -euo pipefail

DATA_DIR="$(cd "$(dirname "$0")" && pwd)/data"
mkdir -p "$DATA_DIR"
cd "$DATA_DIR"

BASE_URL="https://services.rce.geovoorziening.nl/www/download/data"

echo "=== Downloading Rijksmonumentpunten (Monument Points) ==="
curl -L -o Rijksmonumentpunten_28992.zip \
  "${BASE_URL}/Rijksmonumentpunten_28992.zip"

echo "=== Downloading Rijksmonumentcontouren (Monument Contours) ==="
curl -L -o Rijksmonumentcontouren_28992.zip \
  "${BASE_URL}/Rijksmonumentcontouren_28992.zip"

echo ""
echo "=== Unzipping ==="
unzip -o Rijksmonumentpunten_28992.zip
unzip -o Rijksmonumentcontouren_28992.zip

echo ""
echo "=== Done ==="
echo "Files in ${DATA_DIR}:"
ls -lh "$DATA_DIR"/*.shp "$DATA_DIR"/*.dbf

echo ""
echo "=== Quick summary ==="
echo "Points:"
ogrinfo -so "$DATA_DIR/Rijksmonumentpunten_28992.shp" Rijksmonumentpunten_28992 \
  2>/dev/null | grep -E "(Feature Count|Geometry|Extent)"
echo ""
echo "Contours:"
ogrinfo -so "$DATA_DIR/Rijksmonumentcontouren_28992.shp" Rijksmonumentcontouren_28992 \
  2>/dev/null | grep -E "(Feature Count|Geometry|Extent)"

# ---------------------------------------------------------------------------
# ALTERNATIVE: PDOK OGC API Features
# ---------------------------------------------------------------------------
# The same data (and potentially more up-to-date) is available through the
# PDOK OGC API for the RCE "beschermde gebieden cultuurhistorie" dataset:
#
#   Landing page:
#     https://api.pdok.nl/rce/beschermde-gebieden-cultuurhistorie/ogc/v1/
#
#   Collections:
#     https://api.pdok.nl/rce/beschermde-gebieden-cultuurhistorie/ogc/v1/collections
#
#   Get items (GeoJSON, paginated, max 1000 per page):
#     https://api.pdok.nl/rce/beschermde-gebieden-cultuurhistorie/ogc/v1/collections/rijksmonumentpunten/items?limit=1000
#     https://api.pdok.nl/rce/beschermde-gebieden-cultuurhistorie/ogc/v1/collections/rijksmonumentcontouren/items?limit=1000
#
#   The PDOK API returns data in EPSG:4326 (WGS 84) by default and supports
#   CRS negotiation. It also includes additional collections like
#   "beschermdestadsendorpsgezichtpunten" and "beschermdestadsendorpsgezichtcontouren"
#   (protected townscapes, a related but separate dataset).
#
#   To download all features via the OGC API using ogr2ogr:
#     ogr2ogr -f GeoJSON rijksmonumentpunten.geojson \
#       "OAPIF:https://api.pdok.nl/rce/beschermde-gebieden-cultuurhistorie/ogc/v1" \
#       rijksmonumentpunten
#
#   Advantages of the PDOK OGC API:
#   - Potentially more current data (continuously updated vs periodic downloads)
#   - Proper polygon geometries for contours (avoids the Shapefile issue)
#   - CRS negotiation (get WGS 84 directly)
#   - Spatial/attribute filtering via OGC API query parameters
#   - No need to download and unzip large files
#
#   Disadvantages:
#   - Paginated (max 1000 features per request), so bulk download is slower
#   - Requires network access during processing
# ---------------------------------------------------------------------------

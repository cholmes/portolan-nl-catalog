#!/usr/bin/env bash
#
# download.sh — Download Nationale Parken (National Parks) from PDOK
#
# Source: RVO (Rijksdienst voor Ondernemend Nederland) via PDOK
# OGC API Features endpoint: https://api.pdok.nl/rvo/nationale-parken/ogc/v1/
# Collection: nationaleparken
#
# The dataset contains 21 National Parks of the Netherlands as Multi Polygon
# geometries in EPSG:28992 (Amersfoort / RD New).
#
# Requirements:
#   - ogr2ogr (GDAL) >= 3.6 (for OGC API Features driver support)
#
# Usage:
#   chmod +x download.sh
#   ./download.sh
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATA_DIR="${SCRIPT_DIR}/data"
OUTPUT_FILE="${DATA_DIR}/nationale_parken.geojson"

OGC_API_URL="https://api.pdok.nl/rvo/nationale-parken/ogc/v1/"
COLLECTION="nationaleparken"

mkdir -p "${DATA_DIR}"

echo "Downloading Nationale Parken from PDOK OGC API Features..."
echo "  Endpoint: ${OGC_API_URL}"
echo "  Collection: ${COLLECTION}"
echo "  Output: ${OUTPUT_FILE}"
echo ""

# Download all features from the OGC API Features endpoint.
# The OAPIF driver in GDAL handles pagination automatically.
# The dataset is small (21 features) so no special pagination config is needed.
ogr2ogr \
  -f GeoJSON \
  "${OUTPUT_FILE}" \
  "OAPIF:${OGC_API_URL}" \
  "${COLLECTION}" \
  -progress

echo ""
echo "Download complete."
echo ""

# Print summary
ogrinfo -so "${OUTPUT_FILE}" "${COLLECTION}" 2>/dev/null | grep -E "Feature Count|Geometry|Extent" || true

echo ""
echo "File size: $(du -h "${OUTPUT_FILE}" | cut -f1)"
echo "Done."

#!/bin/bash
# Download CBS Gebiedsindelingen (Area Classifications) from PDOK
#
# Source: https://service.pdok.nl/cbs/gebiedsindelingen/atom/v1_0/index.xml
# Provider: CBS (Centraal Bureau voor de Statistiek / Statistics Netherlands)
# License: CC BY 4.0
# Format: GeoPackage (EPSG:28992 - Amersfoort / RD New)
#
# Available years: 2016-2026 via PDOK Atom feed
# Note: 2016-2018 are ~17 MB (no buurt/wijk non-generalized layers)
#       2019-2025 are ~150-160 MB (include non-generalized buurt/wijk/gemeente)
#       2023 is ~223 MB (likely included additional layers that year)
#       2026 is ~3 MB (provisional, only basic boundaries, no buurt/wijk yet)
#
# Historical editions (1995-2015) were previously available but are not in
# the current PDOK Atom feed. They may be obtainable through CBS directly.

set -euo pipefail

BASE_URL="https://service.pdok.nl/cbs/gebiedsindelingen/atom/v1_0/downloads"
OUTPUT_DIR="data"

mkdir -p "$OUTPUT_DIR"

# Default: download the most recent complete edition (2025)
YEAR="${1:-2025}"

if [[ "$YEAR" == "all" ]]; then
    echo "Downloading ALL available years (2016-2026)..."
    for y in $(seq 2016 2026); do
        FILE="cbsgebiedsindelingen${y}.gpkg"
        URL="${BASE_URL}/${FILE}"
        if [ -f "${OUTPUT_DIR}/${FILE}" ]; then
            echo "  Skipping ${FILE} (already exists)"
        else
            echo "  Downloading ${FILE}..."
            curl -L -o "${OUTPUT_DIR}/${FILE}" "$URL"
        fi
    done
    echo "Done. All files saved to ${OUTPUT_DIR}/"
else
    if [[ "$YEAR" -lt 2016 || "$YEAR" -gt 2026 ]]; then
        echo "Error: Year must be between 2016 and 2026 (inclusive)."
        echo "  Historical editions (1995-2015) are not available via PDOK Atom feed."
        exit 1
    fi

    FILE="cbsgebiedsindelingen${YEAR}.gpkg"
    URL="${BASE_URL}/${FILE}"

    if [ -f "${OUTPUT_DIR}/${FILE}" ]; then
        echo "${FILE} already exists in ${OUTPUT_DIR}/"
        echo "Delete it first if you want to re-download."
        exit 0
    fi

    echo "Downloading CBS Gebiedsindelingen ${YEAR}..."
    echo "  URL: ${URL}"
    curl -L -o "${OUTPUT_DIR}/${FILE}" "$URL"
    echo "Done. Saved to ${OUTPUT_DIR}/${FILE}"
    ls -lh "${OUTPUT_DIR}/${FILE}"
fi

echo ""
echo "To inspect layers:  ogrinfo -so ${OUTPUT_DIR}/cbsgebiedsindelingen${YEAR}.gpkg"
echo "OGC API endpoint:   https://api.pdok.nl/cbs/gebiedsindelingen/ogc/v1"

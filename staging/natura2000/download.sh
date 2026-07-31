#!/bin/bash
# Download Natura 2000 protected areas dataset from PDOK (RVO)
#
# Source: Rijksdienst voor Ondernemend Nederland (RVO) via PDOK
# Atom feed: https://service.pdok.nl/rvo/natura2000/atom/index.xml
# License: CC0 (public domain)
# Format: GeoPackage (~10 MB)
# CRS: EPSG:28992 (Amersfoort / RD New)
#
# The dataset contains 209 features representing 162 Natura 2000
# protected areas in the Netherlands. Some areas appear as multiple
# features due to separate designation types (HR, VR, VR+HR).

set -euo pipefail

DOWNLOAD_URL="https://service.pdok.nl/rvo/natura2000/atom/downloads/natura2000.gpkg"
OUTPUT_DIR="$(dirname "$0")/data"
OUTPUT_FILE="${OUTPUT_DIR}/natura2000.gpkg"

mkdir -p "${OUTPUT_DIR}"

echo "Downloading Natura 2000 dataset from PDOK..."
curl -L -o "${OUTPUT_FILE}" "${DOWNLOAD_URL}"

echo "Download complete: ${OUTPUT_FILE}"
echo "File size: $(du -h "${OUTPUT_FILE}" | cut -f1)"

# Quick verification with ogrinfo if available
if command -v ogrinfo &> /dev/null; then
    echo ""
    echo "Layer summary:"
    ogrinfo -so "${OUTPUT_FILE}" n2000
fi

#!/usr/bin/env bash
# Download BRP Gewaspercelen (Basic Registration of Crop Parcels) from PDOK
#
# Source: RVO via PDOK Atom feed
# Atom: https://service.pdok.nl/rvo/brpgewaspercelen/atom/v1_0/basisregistratie_gewaspercelen_brp.xml
# License: CC0 (Public Domain)
# Size: ~2.9 GB (2025 definitive edition)
# Format: GeoPackage (EPSG:28992)
#
# Available editions:
#   2020-2025: GeoPackage (definitief = final, voorlopig = preliminary)
#   2009-2019: Shapefile ZIP only
#
# Each year's data is a snapshot from May 15 (the annual registration deadline).
# "definitief" editions are finalized after verification; "voorlopig" are preliminary.
#
# Usage:
#   ./download.sh          # Download 2025 definitive edition
#   ./download.sh 2024     # Download 2024 definitive edition

set -euo pipefail
cd "$(dirname "$0")"

YEAR="${1:-2025}"
BASE_URL="https://service.pdok.nl/rvo/gewaspercelen/atom/downloads"
FILENAME="brpgewaspercelen_definitief_${YEAR}.gpkg"
OUTPUT="data/${FILENAME}"

mkdir -p data

if [ -f "$OUTPUT" ]; then
    echo "File already exists: $OUTPUT ($(du -h "$OUTPUT" | cut -f1))"
    echo "Delete it first to re-download."
    exit 0
fi

echo "Downloading BRP Gewaspercelen ${YEAR} (~2.9 GB for 2025)..."
curl -L -o "$OUTPUT" "${BASE_URL}/${FILENAME}"

echo "Verifying..."
ogrinfo -so "$OUTPUT" 2>/dev/null | head -5

echo "Done. Downloaded to $OUTPUT ($(du -h "$OUTPUT" | cut -f1))"

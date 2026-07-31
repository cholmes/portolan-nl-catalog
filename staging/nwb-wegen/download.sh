#!/usr/bin/env bash
# Download NWB Wegen (National Road Network) from PDOK
#
# Source: Rijkswaterstaat via PDOK Atom feed
# URL: https://service.pdok.nl/rws/nationaal-wegenbestand-wegen/atom/index.xml
# License: CC0 (Public Domain)
# Size: ~1.5 GB
# Format: GeoPackage (EPSG:28992)
#
# The NWB is updated monthly. This downloads the latest version.
# For the waterways dataset (vaarwegen), use a separate download from:
# https://service.pdok.nl/rws/nwbvaarwegen/atom/index.xml

set -euo pipefail
cd "$(dirname "$0")"

DOWNLOAD_URL="https://service.pdok.nl/rws/nationaal-wegenbestand-wegen/atom/downloads/nwb_wegen.gpkg"
OUTPUT="data/nwb_wegen.gpkg"

mkdir -p data

if [ -f "$OUTPUT" ]; then
    echo "File already exists: $OUTPUT ($(du -h "$OUTPUT" | cut -f1))"
    echo "Delete it first to re-download."
    exit 0
fi

echo "Downloading NWB Wegen (~1.5 GB)..."
curl -L -o "$OUTPUT" "$DOWNLOAD_URL"

echo "Verifying..."
ogrinfo -so "$OUTPUT" 2>/dev/null | head -5

echo "Done. Downloaded to $OUTPUT ($(du -h "$OUTPUT" | cut -f1))"

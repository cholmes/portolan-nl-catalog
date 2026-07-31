#!/usr/bin/env bash
#
# Download Bestuurlijke Gebieden (Administrative Areas) from PDOK / Kadaster
#
# Source: Kadaster (Netherlands Cadastre, Land Registry and Mapping Agency)
# Atom feed: https://service.pdok.nl/kadaster/bestuurlijkegebieden/atom/v1_0/bestuurlijke_gebieden.xml
# OGC API:   https://api.pdok.nl/kadaster/brk-bestuurlijke-gebieden/ogc/v1/
# License:   CC BY 4.0
#
# The dataset is published annually in January, reflecting any municipal mergers
# (herindelingen) that took effect on January 1st of that year.
#
# Historical editions available from the same Atom feed:
#   - BestuurlijkeGebieden_2021.gpkg
#   - BestuurlijkeGebieden_2022.gpkg
#   - BestuurlijkeGebieden_2023.gpkg
#   - BestuurlijkeGebieden_2024.gpkg
#   - BestuurlijkeGebieden_2025.gpkg
#   - BestuurlijkeGebieden_2026.gpkg
#
# To download a different year, change YEAR below.

set -euo pipefail

YEAR="${1:-2026}"
OUTDIR="$(dirname "$0")/data"
FILENAME="BestuurlijkeGebieden_${YEAR}.gpkg"
URL="https://service.pdok.nl/kadaster/brk-bestuurlijke-gebieden/atom/downloads/${FILENAME}"

mkdir -p "$OUTDIR"

echo "Downloading Bestuurlijke Gebieden ${YEAR}..."
echo "  URL: ${URL}"
echo "  Output: ${OUTDIR}/${FILENAME}"

curl -L -o "${OUTDIR}/${FILENAME}" "${URL}"

echo ""
echo "Download complete: ${OUTDIR}/${FILENAME}"
echo ""
echo "Contents (layers):"
echo "  - gemeentegebied    (342 municipalities in 2026)"
echo "  - provinciegebied   (12 provinces)"
echo "  - landgebied        (1 national territory)"
echo ""
echo "Inspect with: ogrinfo -so ${OUTDIR}/${FILENAME}"

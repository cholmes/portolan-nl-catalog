#!/usr/bin/env bash
# download.sh — Download CBS Wijken en Buurten (Neighborhoods & Districts) GeoPackage
#
# Dataset: CBS Wijk- en Buurtkaart
# Provider: CBS (Centraal Bureau voor de Statistiek / Statistics Netherlands)
# License: CC BY 4.0
# Format: GeoPackage (EPSG:28992 — Amersfoort / RD New)
#
# This dataset contains three layers:
#   - buurten (neighborhoods) — finest granularity, ~14,800 areas
#   - wijken (districts) — aggregated from buurten
#   - gemeenten (municipalities) — aggregated from wijken
#
# Each layer carries ~40 demographic/statistical columns (population, age,
# households, migration background, urbanity, area).
#
# Multi-year availability:
#   CBS publishes a new edition each year. The following years are available
#   via the PDOK Atom feed, all at predictable URLs:
#
#     2021: https://service.pdok.nl/cbs/wijkenbuurten/2021/atom/downloads/wijkenbuurten_2021.gpkg
#     2022: https://service.pdok.nl/cbs/wijkenbuurten/2022/atom/downloads/wijkenbuurten_2022.gpkg
#     2023: https://service.pdok.nl/cbs/wijkenbuurten/2023/atom/downloads/wijkenbuurten_2023.gpkg
#     2024: https://service.pdok.nl/cbs/wijkenbuurten/2024/atom/downloads/wijkenbuurten_2024.gpkg
#     2025: https://service.pdok.nl/cbs/wijkenbuurten/2025/atom/downloads/wijkenbuurten_2025.gpkg
#
#   Atom feed index: https://service.pdok.nl/cbs/wijkenbuurten/{year}/atom/index.xml
#   OGC API:         https://api.pdok.nl/cbs/wijken-en-buurten-{year}/ogc/v1
#
#   Boundary definitions change when municipalities merge or split. Each year's
#   file reflects the administrative divisions as of 1 January of that year.
#   The column `indelingswijziging_wijken_en_buurten` flags areas whose
#   boundaries changed compared to the previous year (1 = changed, 0 = unchanged).
#
# Usage:
#   ./download.sh              # Downloads 2025 (default / latest)
#   ./download.sh 2023         # Downloads a specific year
#   ./download.sh all          # Downloads all available years (2021-2025)
#
# Files are saved to data/ in the current directory.

set -euo pipefail

BASE_URL="https://service.pdok.nl/cbs/wijkenbuurten"
YEARS_AVAILABLE=(2021 2022 2023 2024 2025)
DEFAULT_YEAR=2025
OUTPUT_DIR="data"

mkdir -p "$OUTPUT_DIR"

download_year() {
    local year="$1"
    local url="${BASE_URL}/${year}/atom/downloads/wijkenbuurten_${year}.gpkg"
    local output="${OUTPUT_DIR}/wijkenbuurten_${year}.gpkg"

    if [[ -f "$output" ]]; then
        echo "Already exists: $output ($(du -h "$output" | cut -f1) — skipping)"
        return 0
    fi

    echo "Downloading wijkenbuurten_${year}.gpkg ..."
    curl -L --progress-bar -o "$output" "$url"
    echo "Saved: $output ($(du -h "$output" | cut -f1))"
}

if [[ "${1:-}" == "all" ]]; then
    echo "Downloading all available years: ${YEARS_AVAILABLE[*]}"
    for year in "${YEARS_AVAILABLE[@]}"; do
        download_year "$year"
    done
    echo "Done. All years downloaded to ${OUTPUT_DIR}/"
else
    year="${1:-$DEFAULT_YEAR}"
    # Validate year
    valid=false
    for y in "${YEARS_AVAILABLE[@]}"; do
        [[ "$y" == "$year" ]] && valid=true && break
    done
    if ! $valid; then
        echo "Error: Year '$year' not available. Choose from: ${YEARS_AVAILABLE[*]}" >&2
        exit 1
    fi
    download_year "$year"
    echo "Done."
fi

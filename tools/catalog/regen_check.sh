#!/usr/bin/env bash
# Verify the four data-reading generators against the working directory.
#
# tests/test_generators.py cannot cover these: they read parquet, which this
# repo does not hold. This runs them against $PORTOLAN_NL_WORKDIR and diffs the
# metadata they produce. Rendered images are excluded -- matplotlib output is
# not byte-reproducible across runs, so comparing them would fail for reasons
# that have nothing to do with the refactor. Every metadata file must match.
#
# ORDER MATTERS, and it is not obvious:
#
#   1. make_styles_thumbnails  writes default.json and one thematic style per
#                              collection, plus the thumbnails
#   2. make_extra_styles       adds thematic styles to the secondary collections
#   3. make_point_legends      REWRITES some of the styles from step 1, adding
#                              the inert fill layer that makes point styles
#                              show a legend in portolan-browser
#   4. make_collections        reads whatever styles/ ended up holding to build
#                              the portolan:styles manifest and the style assets
#
# Run step 1 after step 3 and you silently revert the legend workaround; run
# step 4 first and the manifest misses whatever the style steps add.
#
# Usage: bash tools/catalog/regen_check.sh [styles|collections|all]
set -euo pipefail
cd "$(dirname "$0")/../.."
WHICH="${1:-all}"

STYLE_SCRIPTS=(tools/catalog/make_styles_thumbnails.py
               tools/catalog/make_extra_styles.py
               tools/catalog/make_point_legends.py)

case "$WHICH" in
  styles)      SCRIPTS=("${STYLE_SCRIPTS[@]}") ;;
  collections) SCRIPTS=(tools/catalog/make_collections.py) ;;
  all)         SCRIPTS=("${STYLE_SCRIPTS[@]}" tools/catalog/make_collections.py) ;;
  *) echo "usage: $0 [styles|collections|all]" >&2; exit 2 ;;
esac

if [ -n "$(git status --porcelain catalog/)" ]; then
  echo "error: catalog/ has uncommitted changes; commit or stash first" >&2
  exit 2
fi

WORKDIR="${PORTOLAN_NL_WORKDIR:-/Users/cholmes/geodata/portolan-nl}"
if [ ! -d "$WORKDIR" ]; then
  echo "error: working directory not found: $WORKDIR" >&2
  echo "These generators read parquet, which this repo does not hold." >&2
  exit 2
fi

for s in "${SCRIPTS[@]}"; do echo "=== $s"; python3 "$s" >/dev/null; done

echo "=== diff (rendered images excluded) ==="
if git diff --quiet -- catalog/ ':(exclude)catalog/**/*.webp'; then
  n=$(git status --porcelain catalog/ | wc -l | tr -d ' ')
  echo "OK: regeneration reproduced every committed metadata file"
  [ "$n" -gt 0 ] && echo "     ($n rendered image(s) differ, which is expected)"
  git checkout -- catalog/
  exit 0
fi
git diff --stat -- catalog/ ':(exclude)catalog/**/*.webp'
echo "FAIL: regeneration changed committed metadata (above)"
echo "Restore with: git checkout -- catalog/"
exit 1

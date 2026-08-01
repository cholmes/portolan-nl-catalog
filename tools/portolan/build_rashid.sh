#!/usr/bin/env bash
# Build rashid with the three in-flight PRs this catalog targets.
#
#   portolan-sdi/rashid#63  enforces PORTO-CORE-070 (spec PR #97): the default
#                           style carries a `default` asset role.
#   portolan-sdi/rashid#90  downgrades PTL-AST-003 (spec PR #116): file:size
#                           and file:checksum become SHOULD, not MUST.
#   portolan-sdi/rashid#91  accepts image/webp thumbnails (spec issue #120).
#                           Opened from this catalog; see docs/phase3-baseline.md.
#
# All three were open and MERGEABLE as of 2026-08-01. If any has since merged this
# still works -- merging an already-merged branch is a no-op.
#
# Usage: bash tools/portolan/build_rashid.sh [venv-path]
set -euo pipefail
VENV="${1:-$HOME/.local/share/portolan-nl/rashid-venv}"
SRC="$(dirname "$VENV")/rashid-src"
mkdir -p "$(dirname "$VENV")"

rm -rf "$SRC"
git clone --quiet https://github.com/portolan-sdi/rashid.git "$SRC"
cd "$SRC"
git config user.email "build@localhost"
git config user.name "phase3 build"
for br in feature/porto-core-070-default-style-key feat/checksum-size-should \
         feat/webp-thumbnails; do
  echo "=== merging $br"
  git fetch --quiet origin "$br"
  if ! git merge --no-edit --quiet "FETCH_HEAD"; then
    echo "error: $br no longer merges cleanly onto main." >&2
    echo "Re-check the PR before continuing; do not hand-resolve spec semantics." >&2
    exit 1
  fi
done

python3 -m venv "$VENV"
"$VENV/bin/pip" install --quiet --upgrade pip
"$VENV/bin/pip" install --quiet "$SRC"
echo
echo "rashid: $VENV/bin/rashid"
"$VENV/bin/rashid" --version
git -C "$SRC" log --oneline -3

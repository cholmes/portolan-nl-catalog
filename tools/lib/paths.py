"""Where things live. Every generator imports its roots from here.

Three roots, deliberately distinct:

- REPO      the git repo. Tooling, tests, docs.
- CATALOG   REPO/catalog -- the published tree. Generators write here.
- DATA_ROOT the working directory that still holds the parquet and PMTiles.
            The repo holds no data, so any generator that reads a data file
            reads it from here. Overridable with $PORTOLAN_NL_WORKDIR.

Before this module, each script recomputed its root by walking up from
__file__. That resolved correctly at the old depth inside the working
directory and does not at the new depth here.

Public URL bases are read from catalog.publish.yaml rather than hardcoded, so
the publisher and the generators cannot disagree about where the catalog lives.
"""
from __future__ import annotations
import os
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

# tests/test_generators.py points this at a temp copy so regeneration can be
# diffed without touching the real tree.
CATALOG = Path(os.environ.get("PORTOLAN_NL_CATALOG", REPO / "catalog"))

DATA_ROOT = Path(os.environ.get("PORTOLAN_NL_WORKDIR", "/Users/cholmes/geodata/portolan-nl"))


def publish_manifest() -> dict:
    """Parse catalog.publish.yaml without a YAML dependency.

    The file is a flat key: value map with # comments; a real parser would be
    one more thing for CI to install for no benefit.
    """
    out = {}
    for line in (REPO / "catalog.publish.yaml").read_text().splitlines():
        line = line.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        k, v = line.split(":", 1)
        out[k.strip()] = v.strip()
    return out


_M = publish_manifest()
DATA_BASE = _M["public_base"].rstrip("/")             # https://data.source.coop/cholmes/portolan-nl
SRC_BASE = "https://source.coop/cholmes/portolan-nl"  # the HTML front end, for describedby links


def data_file(rel: str) -> Path:
    """Absolute path to a data file, e.g. data_file("vro/wandonderzoek/wandonderzoek.parquet")."""
    return DATA_ROOT / rel

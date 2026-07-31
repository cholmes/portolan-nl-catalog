"""Verify the hand-carried git extension fields on the root catalog.

Portolan 0.1 defines no git extension and portolan-cli cannot yet emit these
(portolan-cli#485), so catalog.json carries them by hand. rashid ignores them.
"""
import json, sys
from pathlib import Path

REPO = "https://github.com/cholmes/portolan-nl-catalog"
ROOT = Path(__file__).resolve().parents[1] / "catalog"
doc = json.loads((ROOT / "catalog.json").read_text())

errs = []
if doc.get("git:repository") != REPO:
    errs.append(f"git:repository missing/wrong: {doc.get('git:repository')!r}")
if doc.get("git:ref") != "main":
    errs.append(f"git:ref missing/wrong: {doc.get('git:ref')!r}")
if doc.get("git:provider") != "github":
    errs.append(f"git:provider missing/wrong: {doc.get('git:provider')!r}")
rels = {l.get("rel"): l.get("href") for l in doc.get("links", [])}
if rels.get("vcs") != REPO:
    errs.append(f"vcs link missing/wrong: {rels.get('vcs')!r}")
if rels.get("issues") != f"{REPO}/issues":
    errs.append(f"issues link missing/wrong: {rels.get('issues')!r}")
if errs:
    print("\n".join(errs)); sys.exit(1)
print("OK: git extension fields present")

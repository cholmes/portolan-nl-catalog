# Phase 3 — Portolan spec upgrade Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bring `catalog/` into conformance with Portolan 0.1 plus spec PRs #97 and #116, and make `rashid check` a CI gate.

**Architecture:** Build a local `rashid` with both companion PRs merged, take a baseline, then close the findings rule-group by rule-group, largest first. Every fix is applied by a script under `tools/catalog/`, never by hand, so the next regeneration cannot undo it — and the phase-2 generators are updated in the same commit, with `tests/test_generators.py` as the proof.

**Tech Stack:** Python 3.11 stdlib. `rashid` built from source in a venv. No new runtime dependencies in the catalog itself.

## Global Constraints

- **Bleeding edge is intended.** All four upstream PRs are open. This targets them anyway, as agreed.
- **Never regress phases 1 and 2.** All six existing tests stay green after every task. In particular `tests/test_generators.py` means any metadata change must also be made in the generator that emits it, or the gate fails.
- JSON writing convention: `json.dumps(doc, indent=2, ensure_ascii=False) + "\n"`.
- Every thumbnail is WebP under 50 KB.
- AWS profile is `default`.
- **A rule the catalog should not satisfy is a finding to argue upstream, not to silently suppress.** Where conformance conflicts with truth (Task 3, Step 1), fix the underlying data, and if that is impossible, record the reason in `docs/` and file upstream.
- STAC terminology: catalog / collection / item / asset. Never "dataset".

## Upstream state, re-checked 2026-08-01

The spec required this be re-checked before starting. It was:

| PR | Repo | State | Head branch | Mergeable |
|---|---|---|---|---|
| [#97](https://github.com/portolan-sdi/portolan-spec/pull/97) | portolan-spec | **OPEN** | `feature/default-style-key` | MERGEABLE |
| [#116](https://github.com/portolan-sdi/portolan-spec/pull/116) | portolan-spec | **OPEN** | `worktree-checksum-size-should` | MERGEABLE |
| [#63](https://github.com/portolan-sdi/rashid/pull/63) | rashid | **OPEN** | `feature/porto-core-070-default-style-key` | MERGEABLE |
| [#90](https://github.com/portolan-sdi/rashid/pull/90) | rashid | **OPEN** | `feat/checksum-size-should` | MERGEABLE |

All four are unmerged, all four merge cleanly onto `main`. Installed `rashid` is 0.1.1, which predates both companions.

## Measured baseline (rashid 0.1.1, `check catalog --no-data`, 2026-08-01)

`passed=False`, 431 files checked, **3 156 errors**, 1 warning, 1 info.

| Count | Rule | What it wants | Task |
|---:|---|---|---|
| 2 224 | `PTL-AST-003` | `file:checksum` on every asset | 9 |
| 357 | `PTL-LNK-006` | `rel:collection` must point at the item's own collection | 4 |
| 101 | `PTL-FIL-003` | `rel:describedby` type must be `text/markdown` | 3 |
| 76 | `PTL-FIL-001` | every object directory needs `AGENTS.md` | 6 |
| 75 | `PTL-LNK-005` | no `rel:self` links | 3 |
| 65 | `PTL-VIZ-005` | style assets must be `application/vnd.mapbox.style+json` | 3 |
| 58 | `PTL-CNF-001` | declare the Portolan schema URI | 5 |
| 58 | `PTL-FIL-002` | `rel:agents` link to `AGENTS.md` | 6 |
| 37 | `PTL-VIZ-003` | `rel:pmtiles` links need `pmtiles:layers` | 8 |
| 32 | `PTL-VIZ-001` | collection needs a `thumbnail` asset | 8 |
| 32 | `PTL-PRV-001` | collection needs `providers` | 7 |
| 17 | `PTL-LNK-003` | `rel:item` type must be `application/geo+json` | 3 |
| 7 | `PTL-LIC-003` | `license: proprietary` is deprecated | 3 |
| 4 | `PTL-LNK-002` | contained object needs a `child` link | 10 |
| 3 | `PTL-VIZ-002` | visualization derivative needs a `style` asset | 8 |
| 2+2+2 | `PTL-MIR-002`, `PTL-PRT-001`, `PTL-AST-005` | mirror role, partition extension, assets on a catalog | 10 |
| 1 each | `PTL-PRO-001/002/003`, `PTL-TTL-001`, `PTL-PRV-002`, `PTL-COL-003` | assorted | 10 |

`PTL-AST-003` is 70 % of the total and is exactly what rashid #90 downgrades. **Rebuild rashid before judging the size of this phase.**

Not in the baseline at all: the #97 work. rashid 0.1.1 has no `PTL-VIZ-006`, so the 18 collections with multiple styles and no `default` role are currently invisible. They appear only after Task 1.

---

### Task 1: Build rashid with #63 and #90, and take the real baseline

**Files:**
- Create: `tools/portolan/build_rashid.sh`, `docs/phase3-baseline.md`

**Interfaces:**
- Produces: a `rashid` binary at a known path, and the finding counts every later task is measured against.

- [ ] **Step 1: Write `tools/portolan/build_rashid.sh`**

```bash
#!/usr/bin/env bash
# Build rashid with the two in-flight PRs this catalog targets.
#
#   portolan-sdi/rashid#63  enforces PORTO-CORE-070 (spec PR #97): the default
#                           style carries a `default` asset role.
#   portolan-sdi/rashid#90  downgrades PTL-AST-003 (spec PR #116): file:size
#                           and file:checksum become SHOULD, not MUST.
#
# Both were open and MERGEABLE as of 2026-08-01. If either has since merged,
# this still works -- merging an already-merged branch is a no-op.
#
# Usage: bash tools/portolan/build_rashid.sh [/path/to/venv]
set -euo pipefail
VENV="${1:-$HOME/.local/share/portolan-nl/rashid-venv}"
SRC="$(dirname "$VENV")/rashid-src"

rm -rf "$SRC"
git clone --quiet https://github.com/portolan-sdi/rashid.git "$SRC"
cd "$SRC"
git config user.email "build@localhost"
git config user.name "phase3 build"
for br in feature/porto-core-070-default-style-key feat/checksum-size-should; do
  echo "=== merging $br"
  git fetch --quiet origin "$br"
  git merge --no-edit --quiet "origin/$br" || {
    echo "error: $br no longer merges cleanly onto main." >&2
    echo "Re-check the PR before continuing; do not hand-resolve spec semantics." >&2
    exit 1
  }
done

python3 -m venv "$VENV"
"$VENV/bin/pip" install --quiet --upgrade pip
"$VENV/bin/pip" install --quiet "$SRC"
echo
echo "rashid: $VENV/bin/rashid"
"$VENV/bin/rashid" --version
cd "$SRC" && git log --oneline -3
```

- [ ] **Step 2: Build it**

```bash
cd ~/repos/portolan-nl-catalog
bash tools/portolan/build_rashid.sh
export RASHID="$HOME/.local/share/portolan-nl/rashid-venv/bin/rashid"
$RASHID --version
```
Expected: a version string, and three commits showing the two merges on top of `main`. If either merge fails, **stop** — the PR has diverged and this plan's assumptions need re-checking.

- [ ] **Step 3: Confirm the two PRs actually took effect**

A clean build proves nothing about whether the rules changed. Check both directly:

```bash
cd ~/repos/portolan-nl-catalog
$RASHID check catalog --no-data --json > /tmp/rashid-new.json || true
python3 -c "
import json; from collections import Counter
d = json.load(open('/tmp/rashid-new.json'))
c = Counter((f['rule_id'], f['severity']) for f in d['findings'])
print('AST-003:', {k: v for k, v in c.items() if k[0]=='PTL-AST-003'})
print('VIZ-006:', {k: v for k, v in c.items() if k[0]=='PTL-VIZ-006'})
print('total errors:', d['error_count'], 'warnings:', d['warning_count'])
"
```
Expected: `PTL-AST-003` now carries severity `warning` (#90 took effect), and `PTL-VIZ-006` **appears** with a non-zero count (#63 took effect, and it should be near 18 — the collections with multiple styles and no `default` role). If `AST-003` is still `error`, or `VIZ-006` is absent, the merge did not do what this plan assumes — stop and investigate.

- [ ] **Step 4: Record the baseline**

Write `docs/phase3-baseline.md`: the rashid build (commit hashes of the two merges), the date, the full rule/severity/count table from the new build, and a one-line note per rule saying which task closes it. This is what "did phase 3 work" is measured against.

- [ ] **Step 5: Commit**

```bash
cd ~/repos/portolan-nl-catalog
git add tools/portolan docs/phase3-baseline.md
git commit -m "Build rashid with spec PRs #97 and #116 companions; record baseline

Both companion PRs (rashid#63, rashid#90) are open and merge cleanly onto main.
Verified the merge took effect: PTL-AST-003 is now a warning and PTL-VIZ-006
exists."
```

---

### Task 2: The fix harness

Every later task is "rewrite N JSON files under a rule". They should share one loader, one writer and one dry-run convention rather than each inventing them.

**Files:**
- Create: `tools/catalog/conform.py`
- Test: `tests/test_links.py`, `tests/test_stac_valid.py`, `tests/test_generators.py`

**Interfaces:**
- Produces: `walk()`, `load()`, `save()`, `Fixer` — used by every fix in Tasks 3–10.

- [ ] **Step 1: Write `tools/catalog/conform.py`**

```python
#!/usr/bin/env python3
"""Apply Portolan conformance fixes across catalog/, one rule at a time.

Each fix is a function registered against the rashid rule it closes, so what
changed and why is legible from the code rather than from a commit message.
Every fix is dry-run by default and reports the files it would touch.

Usage:
  python3 tools/catalog/conform.py --list
  python3 tools/catalog/conform.py PTL-LNK-005            # dry run
  python3 tools/catalog/conform.py PTL-LNK-005 --confirm
  python3 tools/catalog/conform.py --all --confirm
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "catalog"

FIXES: dict[str, tuple[str, Callable[[dict, Path], bool]]] = {}


def fix(rule: str, description: str):
    """Register a fix. The function mutates doc in place and returns True if it changed it."""
    def deco(fn):
        FIXES[rule] = (description, fn)
        return fn
    return deco


def walk():
    """Every STAC JSON under catalog/: catalog, collection and item objects.

    Excludes MapLibre styles (styles/*.json and *.style.json) and Portolan's
    own versions.json bookkeeping -- neither is a STAC object.
    """
    for p in sorted(CATALOG.rglob("*.json")):
        if ".portolan" in p.parts or "styles" in p.parts:
            continue
        if p.name.endswith(".style.json") or p.name == "versions.json":
            continue
        yield p


def load(p: Path) -> dict | None:
    try:
        d = json.loads(p.read_text())
    except json.JSONDecodeError:
        return None
    return d if isinstance(d, dict) and "type" in d else None


def save(p: Path, doc: dict) -> None:
    p.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")


def run(rules: list[str], confirm: bool) -> int:
    total = 0
    for rule in rules:
        desc, fn = FIXES[rule]
        touched = []
        for p in walk():
            doc = load(p)
            if doc is None:
                continue
            if fn(doc, p):
                touched.append(p)
                if confirm:
                    save(p, doc)
        total += len(touched)
        verb = "fixed" if confirm else "would fix"
        print(f"{rule}: {verb} {len(touched)} file(s) — {desc}")
        for p in touched[:5]:
            print(f"    {p.relative_to(CATALOG)}")
        if len(touched) > 5:
            print(f"    ... and {len(touched) - 5} more")
    if not confirm:
        print("\nDry run. Re-run with --confirm to write.")
    return 0 if total or confirm else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("rules", nargs="*", help="rule ids to apply")
    ap.add_argument("--all", action="store_true", help="apply every registered fix")
    ap.add_argument("--list", action="store_true", help="list registered fixes")
    ap.add_argument("--confirm", action="store_true", help="write changes")
    args = ap.parse_args(argv)

    if args.list:
        for r, (d, _) in sorted(FIXES.items()):
            print(f"{r}  {d}")
        return 0
    rules = sorted(FIXES) if args.all else args.rules
    if not rules:
        ap.print_help()
        return 2
    unknown = [r for r in rules if r not in FIXES]
    if unknown:
        print(f"error: no fix registered for {', '.join(unknown)}", file=sys.stderr)
        return 2
    return run(rules, args.confirm)


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Verify the walker sees the right objects**

```bash
cd ~/repos/portolan-nl-catalog
python3 -c "
import sys; sys.path.insert(0, 'tools/catalog')
import conform
ps = list(conform.walk())
docs = [p for p in ps if conform.load(p)]
print(len(ps), 'json files,', len(docs), 'STAC objects')
"
```
Expected: 431 STAC objects — the same number `rashid check` and `tests/test_stac_valid.py` report. A different number means the walker disagrees with the validator about what a STAC object is; reconcile before writing any fix.

- [ ] **Step 3: Commit**

```bash
cd ~/repos/portolan-nl-catalog
git add tools/catalog/conform.py
git commit -m "Add the conformance fix harness

One loader, one writer, one dry-run convention for every Portolan rule fix,
each registered against the rashid rule it closes."
```

---

### Task 3: Mechanical link and type fixes — 265 findings

Closes `PTL-LNK-005` (75), `PTL-FIL-003` (101), `PTL-VIZ-005` (65), `PTL-LNK-003` (17), `PTL-LIC-003` (7).

**Files:**
- Modify: `tools/catalog/conform.py`, many files under `catalog/`, and the generators that emit these shapes
- Test: all six

**Interfaces:**
- Consumes: the Task 2 harness.

- [ ] **Step 1: Decide the `describedby` fix before writing it**

`PTL-FIL-003` wants `rel:describedby` to be `text/markdown`. This catalog's describedby links point at `https://source.coop/cholmes/portolan-nl/<path>/README.md` — a Source Cooperative **HTML page** that renders the README, correctly typed `text/html` today. Relabelling an HTML page as markdown would make the metadata lie.

Check what the raw URL serves, and prefer repointing the href over mislabelling the type:

```bash
curl -sI https://source.coop/cholmes/portolan-nl/rce/rijksmonumenten/README.md | head -3
curl -sI https://data.source.coop/cholmes/portolan-nl/rce/rijksmonumenten/README.md | head -3
```
The `data.` host serves the raw file. If it returns 200 with a markdown-ish content type, the fix is to repoint `href` to the `data.` URL **and** set the type — both true. Record which you chose and why in the commit. If neither URL serves real markdown, leave the rule open and note it in `docs/phase3-baseline.md` as a finding to raise upstream.

- [ ] **Step 2: Write the five fixes**

Append to `tools/catalog/conform.py`:

```python
@fix("PTL-LNK-005", "remove rel:self links (Portolan catalogs are self-contained)")
def _self_links(doc, path):
    links = doc.get("links")
    if not isinstance(links, list):
        return False
    keep = [l for l in links if not (isinstance(l, dict) and l.get("rel") == "self")]
    if len(keep) == len(links):
        return False
    doc["links"] = keep
    return True


@fix("PTL-LNK-003", "rel:item links are application/geo+json")
def _item_type(doc, path):
    changed = False
    for l in doc.get("links") or []:
        if isinstance(l, dict) and l.get("rel") == "item" and l.get("type") != "application/geo+json":
            l["type"] = "application/geo+json"
            changed = True
    return changed


@fix("PTL-VIZ-005", "style assets are application/vnd.mapbox.style+json")
def _style_type(doc, path):
    changed = False
    for a in (doc.get("assets") or {}).values():
        if not isinstance(a, dict):
            continue
        if "style" in (a.get("roles") or []) and a.get("type") != "application/vnd.mapbox.style+json":
            a["type"] = "application/vnd.mapbox.style+json"
            changed = True
    return changed


@fix("PTL-LIC-003", "replace the deprecated 'proprietary' license with 'other'")
def _license(doc, path):
    if doc.get("license") != "proprietary":
        return False
    doc["license"] = "other"
    links = doc.setdefault("links", [])
    if not any(isinstance(l, dict) and l.get("rel") == "license" for l in links):
        # 'other' requires a rel:license link saying what the terms actually are.
        links.append({"rel": "license",
                      "href": "https://www.pdok.nl/gebruiksvoorwaarden",
                      "type": "text/html",
                      "title": "PDOK terms of use"})
    return True


DESCRIBEDBY_HOST = "https://data.source.coop/cholmes/portolan-nl"  # set per Step 1


@fix("PTL-FIL-003", "rel:describedby points at raw markdown and is typed text/markdown")
def _describedby(doc, path):
    changed = False
    for l in doc.get("links") or []:
        if not isinstance(l, dict) or l.get("rel") != "describedby":
            continue
        href = str(l.get("href", ""))
        if href.startswith("https://source.coop/cholmes/portolan-nl"):
            l["href"] = href.replace("https://source.coop/cholmes/portolan-nl",
                                     DESCRIBEDBY_HOST, 1)
            changed = True
        if l.get("type") != "text/markdown":
            l["type"] = "text/markdown"
            changed = True
    return changed
```

- [ ] **Step 3: Dry run, then apply**

```bash
cd ~/repos/portolan-nl-catalog
python3 tools/catalog/conform.py PTL-LNK-005 PTL-LNK-003 PTL-VIZ-005 PTL-LIC-003 PTL-FIL-003
```
Expected counts close to 75 / 17 / 65 / 7 / 101. A count far off the baseline means the fix's selector disagrees with rashid's — reconcile before writing.

```bash
python3 tools/catalog/conform.py PTL-LNK-005 PTL-LNK-003 PTL-VIZ-005 PTL-LIC-003 PTL-FIL-003 --confirm
```

- [ ] **Step 4: The `self`-link removal is the risky one — verify it**

`rel:self` is a STAC best practice, and `tests/test_stac_valid.py` runs stac-check. Removing 75 of them may produce new best-practice warnings.

```bash
cd ~/repos/portolan-nl-catalog
python3 tests/test_stac_valid.py 2>&1 | tail -3
```
Expected: still `OK:`, possibly with a higher warning count. **If it now FAILs, self links are load-bearing for validation** — restore them (`git checkout -- catalog`), leave `PTL-LNK-005` open, and record the conflict in `docs/phase3-baseline.md` as something to raise upstream. Conformance does not outrank valid STAC.

- [ ] **Step 5: Update the generators to match**

```bash
cd ~/repos/portolan-nl-catalog
python3 tests/test_generators.py
```
This will FAIL: `make_catalogs.py`, `make_collections.py` and `generate_items.py` still emit self links, `application/json` style assets and the old describedby. Fix each generator — `stac.self_link()` from phase 2 should be deleted outright — until the gate passes. **This step is the whole reason the gate exists; do not skip it.**

- [ ] **Step 6: Full suite, re-measure, commit**

```bash
cd ~/repos/portolan-nl-catalog
for t in publish links git_ext thumbnails generators stac_valid; do
  echo "=== $t ==="; python3 tests/test_$t.py || echo "FAILED: $t"
done
$RASHID check catalog --no-data --json > /tmp/r.json || true
python3 -c "import json; d=json.load(open('/tmp/r.json')); print('errors:', d['error_count'])"
git add -A && git commit -m "Close 265 mechanical Portolan link and type findings

PTL-LNK-005 self links, PTL-LNK-003 item link types, PTL-VIZ-005 style media
types, PTL-LIC-003 deprecated license, PTL-FIL-003 describedby. Generators
updated in the same commit so regeneration cannot undo any of it."
```

---

### Task 4: `PTL-LNK-006` — 357 wrong `rel:collection` hrefs

Every item under `beeldmateriaal/luchtfoto_2024/kb*/` links `rel:collection` to `../collection.json`, which resolves to the **kb subcatalog's** directory, not the collection that actually contains the item.

**Files:**
- Modify: `tools/catalog/conform.py`, ~357 item files, the item generator
- Test: `tests/test_links.py`, `tests/test_generators.py`

- [ ] **Step 1: Establish where each item's collection actually is**

```bash
cd ~/repos/portolan-nl-catalog
ls catalog/beeldmateriaal/luchtfoto_2024/
python3 -c "
import json
d = json.load(open('catalog/beeldmateriaal/luchtfoto_2024/kb19/luchtfoto-2024-19an1.json'))
print('collection field:', d.get('collection'))
for l in d['links']:
    print(' ', l['rel'], l['href'])
"
```
Expected: the item sits two levels below `luchtfoto_2024/collection.json`, so the correct href is `../collection.json` **relative to the kb directory** → `../../collection.json`. Confirm against the real layout before writing the fix; do not assume the depth.

- [ ] **Step 2: Write the fix**

```python
@fix("PTL-LNK-006", "rel:collection points at the item's own enclosing collection")
def _collection_link(doc, path):
    if doc.get("type") != "Feature":
        return False
    # Walk up from the item to the nearest collection.json -- that is its collection
    # by definition, regardless of how deep the subcatalogs nest.
    target = None
    for parent in path.parents:
        cand = parent / "collection.json"
        if cand.is_file():
            target = cand
            break
        if parent == CATALOG:
            break
    if target is None:
        return False
    import os
    href = "./" + os.path.relpath(target, path.parent).replace(os.sep, "/")
    href = href.replace("./../", "../")
    changed = False
    for l in doc.get("links") or []:
        if isinstance(l, dict) and l.get("rel") == "collection" and l.get("href") != href:
            l["href"] = href
            changed = True
    return changed
```

- [ ] **Step 3: Dry run and check one result by hand**

```bash
cd ~/repos/portolan-nl-catalog
python3 tools/catalog/conform.py PTL-LNK-006
python3 tools/catalog/conform.py PTL-LNK-006 --confirm
python3 -c "
import json, os
p = 'catalog/beeldmateriaal/luchtfoto_2024/kb19/luchtfoto-2024-19an1.json'
d = json.load(open(p))
h = [l['href'] for l in d['links'] if l['rel'] == 'collection'][0]
print('href:', h, '-> resolves:', os.path.exists(os.path.join(os.path.dirname(p), h)))
"
```
Expected: `357 file(s)`, and the resolved path exists.

- [ ] **Step 4: Verify links and generator, then commit**

```bash
cd ~/repos/portolan-nl-catalog
python3 tests/test_links.py
python3 tests/test_generators.py
```
Both must pass; fix the item generator if the second fails.

```bash
git add -A && git commit -m "Point every item's rel:collection at its own collection

357 luchtfoto items linked ../collection.json, which resolves to the kb
subcatalog's directory rather than the collection that contains them."
```

---

### Task 5: `PTL-CNF-001` and `PTL-PRT-001` — declare the schemas — 60 findings

- [ ] **Step 1: Confirm the schema URI the build expects**

```bash
cd ~/repos/portolan-nl-catalog
$RASHID check catalog --no-data --json 2>/dev/null | python3 -c "
import json, sys
d = json.load(sys.stdin)
f = next(x for x in d['findings'] if x['rule_id'] == 'PTL-CNF-001')
print(f['fix_hint'])
"
```
Use the URI this build names, not the one written here — it moves with the spec version.

- [ ] **Step 2: Write both fixes**

```python
PORTOLAN_SCHEMA = "https://schemas.portolan-sdi.org/portolan/v0.1.0/schema.json"  # per Step 1
PARTITION_SCHEMA = "https://schemas.portolan-sdi.org/incubating/partition/v1.0.0/schema.json"


@fix("PTL-CNF-001", "declare the Portolan profile schema in stac_extensions")
def _portolan_schema(doc, path):
    ext = doc.setdefault("stac_extensions", [])
    if any("schemas.portolan-sdi.org/portolan/" in e for e in ext):
        return False
    ext.insert(0, PORTOLAN_SCHEMA)   # profile first, then the STAC extensions
    return True


@fix("PTL-PRT-001", "declare the partition extension where partition:* fields are used")
def _partition_schema(doc, path):
    if not any(k.startswith("partition:") for k in doc):
        return False
    ext = doc.setdefault("stac_extensions", [])
    if PARTITION_SCHEMA in ext:
        return False
    ext.append(PARTITION_SCHEMA)
    return True
```

- [ ] **Step 3: Apply, and expect `test_stac_valid.py` to route around it**

```bash
cd ~/repos/portolan-nl-catalog
python3 tools/catalog/conform.py PTL-CNF-001 PTL-PRT-001 --confirm
python3 tests/test_stac_valid.py 2>&1 | tail -4
```
Expected: `OK:`, with the warning count up by ~58. `test_stac_valid.py` already downgrades "stac-validator cannot process the Portolan profile schema" to a warning — that path was written in phase 1 for exactly this moment, and its firing now is the expected outcome, not a regression.

- [ ] **Step 4: Generators, then commit**

```bash
cd ~/repos/portolan-nl-catalog
python3 tests/test_generators.py
git add -A && git commit -m "Declare the Portolan profile and partition schemas"
```

---

### Task 6: `PTL-FIL-001` / `PTL-FIL-002` — `AGENTS.md` — 134 findings

Portolan requires an `AGENTS.md` in every object directory plus a `rel:agents` link. 76 directories need one.

**Files:**
- Create: `tools/catalog/make_agents.py`, 76 `AGENTS.md` files under `catalog/`
- Modify: `tools/catalog/conform.py`, `tests/test_links.py` expectations

- [ ] **Step 1: Decide what `AGENTS.md` says**

This catalog already ships `llms.txt` in most collections — a hand-written agent guide with query examples. `AGENTS.md` should not duplicate it: generate a short file that states what the object is, points at `llms.txt` where one exists, and lists the assets. Generic filler in 76 files helps nobody.

- [ ] **Step 2: Write `tools/catalog/make_agents.py`**

```python
#!/usr/bin/env python3
"""Generate AGENTS.md for every catalog and collection directory.

Portolan requires one per object directory (PTL-FIL-001) plus a rel:agents link
(PTL-FIL-002). Content is derived from the object's own metadata -- title,
description, assets, children -- and defers to llms.txt for query examples
rather than restating them.

Usage:
  python3 tools/catalog/make_agents.py            # dry run
  python3 tools/catalog/make_agents.py --confirm
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "catalog"


def objects():
    for p in sorted(CATALOG.rglob("*.json")):
        if p.name not in ("catalog.json", "collection.json"):
            continue
        if ".portolan" in p.parts or "styles" in p.parts:
            continue
        yield p


def render(doc: dict, path: Path) -> str:
    rel = path.parent.relative_to(CATALOG).as_posix() or "."
    title = doc.get("title") or doc.get("id") or rel
    kind = "collection" if doc.get("type") == "Collection" else "catalog"
    lines = [f"# {title}", "",
             f"Portolan {kind} — `{rel}`", ""]
    desc = (doc.get("description") or "").split("\n\n")[0].strip()
    if desc:
        lines += [desc, ""]

    if (path.parent / "llms.txt").is_file():
        lines += ["## For agents", "",
                  "Field descriptions, query examples and usage notes are in "
                  "[`llms.txt`](./llms.txt). Start there.", ""]

    assets = doc.get("assets") or {}
    if assets:
        lines += ["## Assets", "", "| Key | File | Roles |", "|---|---|---|"]
        for k, a in assets.items():
            if not isinstance(a, dict):
                continue
            lines.append(f"| `{k}` | `{a.get('href','')}` | {', '.join(a.get('roles') or [])} |")
        lines.append("")

    children = [l for l in (doc.get("links") or [])
                if isinstance(l, dict) and l.get("rel") in ("child", "item")]
    if children:
        lines += [f"## Contains", "", f"{len(children)} child object(s). "
                  f"See the `child` and `item` links in `{path.name}`.", ""]

    lines += ["## Editing", "",
              "This file is generated by `tools/catalog/make_agents.py` from "
              f"`{path.name}`. Edit the metadata, not this file.", ""]
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--confirm", action="store_true")
    args = ap.parse_args(argv)

    n = 0
    for p in objects():
        doc = json.loads(p.read_text())
        out = p.parent / "AGENTS.md"
        text = render(doc, p)
        if out.is_file() and out.read_text() == text:
            continue
        n += 1
        if args.confirm:
            out.write_text(text)
    verb = "wrote" if args.confirm else "would write"
    print(f"{verb} {n} AGENTS.md file(s)")
    if not args.confirm:
        print("Re-run with --confirm to write.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 3: Generate, and read three of them**

```bash
cd ~/repos/portolan-nl-catalog
python3 tools/catalog/make_agents.py
python3 tools/catalog/make_agents.py --confirm
cat catalog/rce/rijksmonumenten/AGENTS.md
cat catalog/beeldmateriaal/luchtfoto_2024/kb19/AGENTS.md
cat catalog/catalog.json >/dev/null && cat catalog/AGENTS.md
```
Read them properly. If any reads as filler, improve `render()` and regenerate — 76 useless files is worse than 76 findings.

- [ ] **Step 4: Add the `rel:agents` links**

```python
@fix("PTL-FIL-002", "add the rel:agents link to AGENTS.md")
def _agents_link(doc, path):
    if not (path.parent / "AGENTS.md").is_file():
        return False
    links = doc.setdefault("links", [])
    if any(isinstance(l, dict) and l.get("rel") == "agents" for l in links):
        return False
    links.append({"rel": "agents", "href": "./AGENTS.md", "type": "text/markdown"})
    return True
```

```bash
python3 tools/catalog/conform.py PTL-FIL-002 --confirm
python3 tests/test_links.py
```

- [ ] **Step 5: Make it part of regeneration, then commit**

Add `make_agents.py` to `GENERATORS` in `tests/test_generators.py` so `AGENTS.md` cannot drift from the metadata.

```bash
cd ~/repos/portolan-nl-catalog
python3 tests/test_generators.py
git add -A && git commit -m "Generate AGENTS.md for every catalog and collection

76 files derived from each object's own metadata, deferring to llms.txt for
query examples rather than restating them, plus the rel:agents links.
Regeneration is covered by the golden gate."
```

---

### Task 7: `PTL-PRV-001` / `PTL-PRV-002` — providers — 33 findings

Thirty-two collections declare no `providers`; one has no `host`.

- [ ] **Step 1: Map each institution to its provider entry**

The subcatalog a collection lives under names its producer. Build the table explicitly — do not infer at runtime:

```python
PRODUCERS = {
    "kadaster": ("Het Kadaster", "https://www.kadaster.nl/"),
    "rijkswaterstaat": ("Rijkswaterstaat", "https://www.rijkswaterstaat.nl/"),
    "rce": ("Rijksdienst voor het Cultureel Erfgoed", "https://www.cultureelerfgoed.nl/"),
    "rvo": ("Rijksdienst voor Ondernemend Nederland", "https://www.rvo.nl/"),
    "tudelft": ("TU Delft — 3D Geoinformation Research Group", "https://3d.bk.tudelft.nl/"),
    "cbs": ("Centraal Bureau voor de Statistiek", "https://www.cbs.nl/"),
    "vro": ("Ministerie van Volkshuisvesting en Ruimtelijke Ordening", "https://www.rijksoverheid.nl/"),
    "beeldmateriaal": ("Beeldmateriaal Nederland", "https://www.beeldmateriaal.nl/"),
}
HOST = {"name": "Source Cooperative", "roles": ["host"],
        "url": "https://source.coop/cholmes/portolan-nl"}
```

Verify each URL returns 200 before committing:
```bash
for u in https://www.kadaster.nl/ https://www.rijkswaterstaat.nl/ https://www.cultureelerfgoed.nl/ \
         https://www.rvo.nl/ https://3d.bk.tudelft.nl/ https://www.cbs.nl/ \
         https://www.rijksoverheid.nl/ https://www.beeldmateriaal.nl/; do
  printf '%s ' "$(curl -s -o /dev/null -w '%{http_code}' -L "$u")"; echo "$u"
done
```
Any non-200 is a wrong URL — find the right one rather than shipping a dead link.

- [ ] **Step 2: Write the fix**

```python
@fix("PTL-PRV-001", "add providers: the institution as producer, Source Cooperative as host")
def _providers(doc, path):
    if doc.get("type") != "Collection" or doc.get("providers"):
        return False
    inst = path.relative_to(CATALOG).parts[0]
    if inst not in PRODUCERS:
        return False
    name, url = PRODUCERS[inst]
    # host last: PTL-PRV-002 wants exactly one host, and the convention is that
    # it is the final entry.
    doc["providers"] = [{"name": name, "roles": ["producer", "licensor"], "url": url},
                        dict(HOST)]
    return True
```

- [ ] **Step 3: Apply, verify, commit**

```bash
cd ~/repos/portolan-nl-catalog
python3 tools/catalog/conform.py PTL-PRV-001 --confirm
$RASHID check catalog --no-data --json > /tmp/r.json || true
python3 -c "
import json; from collections import Counter
d=json.load(open('/tmp/r.json'))
c=Counter(f['rule_id'] for f in d['findings'])
print('PRV-001:', c.get('PTL-PRV-001', 0), 'PRV-002:', c.get('PTL-PRV-002', 0))
"
python3 tests/test_generators.py
git add -A && git commit -m "Add providers to all 32 collections lacking them"
```
Expected: both counts 0. If `PTL-PRV-002` is still non-zero, some collection has two `host` roles — find and fix it.

---

### Task 8: Visualization rules — `PTL-VIZ-001/002/003` and the #97 default role

The heaviest task: 32 collections have no thumbnail, and thumbnails require the working directory, matplotlib and network basemap tiles.

- [ ] **Step 1: List what is missing**

```bash
cd ~/repos/portolan-nl-catalog
python3 -c "
import json
d = json.load(open('/tmp/r.json'))
for r in ['PTL-VIZ-001','PTL-VIZ-002','PTL-VIZ-003','PTL-VIZ-006']:
    ps = sorted({f['path'] for f in d['findings'] if f['rule_id']==r})
    print(f'--- {r} ({len(ps)})')
    for p in ps: print('   ', p)
"
```

- [ ] **Step 2: `PTL-VIZ-003` — add `pmtiles:layers` to `rel:pmtiles` links (37)**

The layer name is already in the collection, as `pmtiles:layers` at the top level or as the data asset's stem.

```python
@fix("PTL-VIZ-003", "name the default-visible layers on rel:pmtiles links")
def _pmtiles_layers(doc, path):
    layers = doc.get("pmtiles:layers")
    if not layers:
        for k, a in (doc.get("assets") or {}).items():
            if isinstance(a, dict) and str(a.get("type")) == "application/vnd.pmtiles":
                layers = [Path(str(a.get("href", ""))).stem]
                break
    if not layers:
        return False
    changed = False
    for l in doc.get("links") or []:
        if isinstance(l, dict) and l.get("rel") == "pmtiles" and "pmtiles:layers" not in l:
            l["pmtiles:layers"] = layers
            changed = True
    return changed
```

Verify a sample against the actual PMTiles metadata — a wrong layer name renders an empty map:
```bash
python3 -c "
import json
d = json.load(open('catalog/vro/wandonderzoek/collection.json'))
print(d.get('pmtiles:layers'))
print([l for l in d['links'] if l['rel']=='pmtiles'])
"
```

- [ ] **Step 3: `PTL-VIZ-006` / spec #97 — mark the default style**

Where a collection has more than one style asset, exactly one carries both `style` and `default`.

```python
@fix("PTL-VIZ-006", "the default style asset carries the 'default' role (spec PR #97)")
def _default_style(doc, path):
    styles = {k: a for k, a in (doc.get("assets") or {}).items()
              if isinstance(a, dict) and "style" in (a.get("roles") or [])}
    if len(styles) < 2:
        return False                      # #97 does not apply to single-style collections
    if any("default" in (a.get("roles") or []) for a in styles.values()):
        return False
    key = next((k for k in styles if k.endswith("/default")), None)
    if key is None:
        order = doc.get("portolan:styles") or []
        key = next((k for k in order if k in styles), None)
    if key is None:
        return False
    styles[key]["roles"] = [*styles[key]["roles"], "default"]
    return True
```

```bash
python3 tools/catalog/conform.py PTL-VIZ-006 --confirm
```
Expected: ~18 files, matching the spec's measured count.

- [ ] **Step 4: `PTL-VIZ-001` — 32 missing thumbnails**

These need real rendering. Use the phase-2 pipeline:

```bash
cd ~/repos/portolan-nl-catalog
export PORTOLAN_NL_WORKDIR=/Users/cholmes/geodata/portolan-nl
python3 tools/catalog/make_styles_thumbnails.py     # renders via lib/images.save_webp
python3 tests/test_thumbnails.py
```

Some of the 32 will not render — a collection whose data is not in the working directory, or which has no geometry to draw. **Do not fabricate a thumbnail for those.** For each one that fails, record the collection and the reason in `docs/phase3-baseline.md`, and leave the finding open. A missing thumbnail is a smaller problem than a misleading one.

- [ ] **Step 5: `PTL-VIZ-002` — 3 collections with a visualization but no style asset**

Three collections have PMTiles but no registered style. Check whether a style file already exists on disk and simply is not registered as an asset (register it), or whether none exists (generate one with `make_extra_styles.py`, or leave it and record why).

- [ ] **Step 6: Full suite, re-measure, commit**

```bash
cd ~/repos/portolan-nl-catalog
for t in publish links git_ext thumbnails generators stac_valid; do
  echo "=== $t ==="; python3 tests/test_$t.py || echo "FAILED: $t"
done
git add -A && git commit -m "Close the Portolan visualization findings

pmtiles:layers on every rel:pmtiles link, the 'default' role on the default
style of every multi-style collection (spec PR #97), and thumbnails for the
collections that lacked them. Collections that could not be rendered are
recorded in docs/phase3-baseline.md with the reason."
```

---

### Task 9: `PTL-AST-003` / spec #116 — `file:size` — 2 224 findings, now warnings

Under #116 these are `SHOULD`. Fill `file:size` cheaply and leave `file:checksum` off — **a declared checksum that does not match the bytes is worse than an absent one**, and the data is ~50 GB of remote objects.

- [ ] **Step 1: Get the sizes from S3, not from disk**

The repo has no data files, but the published objects have sizes and the listing is one call:

```bash
cd ~/repos/portolan-nl-catalog
AWS_PROFILE=default aws s3 ls s3://us-west-2.opendata.source.coop/cholmes/portolan-nl/ \
  --recursive > /tmp/s3sizes.txt
wc -l /tmp/s3sizes.txt
```

- [ ] **Step 2: Write the fix**

```python
S3_SIZES: dict[str, int] = {}


def _load_sizes(listing="/tmp/s3sizes.txt", prefix="cholmes/portolan-nl/"):
    for line in Path(listing).read_text().splitlines():
        parts = line.split(maxsplit=3)
        if len(parts) == 4 and parts[3].startswith(prefix):
            S3_SIZES[parts[3][len(prefix):]] = int(parts[2])


@fix("PTL-AST-003", "add file:size from the published object (spec PR #116)")
def _file_size(doc, path):
    if not S3_SIZES:
        _load_sizes()
    base = path.parent.relative_to(CATALOG).as_posix()
    changed = False
    for a in (doc.get("assets") or {}).values():
        if not isinstance(a, dict) or "file:size" in a:
            continue
        href = str(a.get("href", ""))
        if href.startswith("http") or not href:
            continue
        key = f"{base}/{href.lstrip('./')}" if base != "." else href.lstrip("./")
        if key in S3_SIZES:
            a["file:size"] = S3_SIZES[key]
            changed = True
    if changed:
        ext = doc.setdefault("stac_extensions", [])
        uri = "https://stac-extensions.github.io/file/v2.1.0/schema.json"
        if uri not in ext:
            ext.append(uri)
    return changed
```

- [ ] **Step 3: Apply and sanity-check one value**

```bash
cd ~/repos/portolan-nl-catalog
python3 tools/catalog/conform.py PTL-AST-003 --confirm
python3 -c "
import json
d = json.load(open('catalog/rce/rijksmonumenten/collection.json'))
for k, a in d['assets'].items():
    print(k, a.get('file:size'))
"
AWS_PROFILE=default aws s3 ls \
  s3://us-west-2.opendata.source.coop/cholmes/portolan-nl/rce/rijksmonumenten/
```
The printed sizes must match the listing exactly. A wrong `file:size` is a lie in the metadata; verify before committing.

- [ ] **Step 4: Confirm the file extension is valid, then commit**

```bash
cd ~/repos/portolan-nl-catalog
python3 tests/test_stac_valid.py 2>&1 | tail -3
python3 tests/test_generators.py
git add -A && git commit -m "Add file:size from the published objects (spec PR #116)

Sizes read from the S3 listing, so they describe the bytes actually served.
file:checksum is deliberately left absent: #116 makes it a SHOULD, and a
declared checksum that does not match is worse than none."
```

---

### Task 10: The remaining singletons — 14 findings

`PTL-LNK-002` (4), `PTL-VIZ-002` leftovers, `PTL-MIR-002` (2), `PTL-AST-005` (2), `PTL-PRO-001/002/003`, `PTL-TTL-001`, `PTL-COL-003`.

- [ ] **Step 1: Read each finding and fix it individually**

```bash
cd ~/repos/portolan-nl-catalog
$RASHID check catalog --no-data --json > /tmp/r.json || true
python3 -c "
import json
d = json.load(open('/tmp/r.json'))
for f in d['findings']:
    if f['rule_id'] in ('PTL-LNK-002','PTL-MIR-002','PTL-AST-005','PTL-PRO-001',
                        'PTL-PRO-002','PTL-PRO-003','PTL-TTL-001','PTL-COL-003'):
        print(f\"{f['rule_id']}  {f['path']}  {f['message']}\")
        print(f\"    fix: {f.get('fix_hint','')}\")
"
```

These are one-offs; each gets a hand edit or a tiny fix function, whichever is clearer. Two need judgment:

- **`PTL-COL-003`** — collection id `3dbag` is flagged as not matching the naming convention. It is a **warning**, and `3dbag` is the collection's real, published name. Renaming it would break every existing link and every published href. **Leave it and record the decision.**
- **`PTL-AST-005`** — two catalogs declare assets. Moving a data asset off a catalog onto a collection changes what a client fetches. Check what those assets are first; if they are thumbnails rather than data, raise it upstream rather than restructuring the catalog around a rule that may not have meant thumbnails.

- [ ] **Step 2: Full suite and commit**

```bash
cd ~/repos/portolan-nl-catalog
for t in publish links git_ext thumbnails generators stac_valid; do
  echo "=== $t ==="; python3 tests/test_$t.py || echo "FAILED: $t"
done
git add -A && git commit -m "Close the remaining single-instance Portolan findings

3dbag's id is left alone deliberately: it is a warning, and the id is the
collection's published name."
```

---

### Task 11: `tests/test_portolan_conformance.py` and CI

- [ ] **Step 1: Write the test**

```python
"""Portolan conformance via rashid.

Targets Portolan 0.1 plus two in-flight spec PRs, so it needs a rashid built
from tools/portolan/build_rashid.sh rather than a released one:

  portolan-spec#97  / rashid#63 -- the default style carries a `default` role
  portolan-spec#116 / rashid#90 -- file:size and file:checksum are SHOULD

SKIPs (exit 0) when that rashid is not on PATH, so the local suite stays
zero-setup like the other five. Point $RASHID at the built binary, or set
$PORTOLAN_STRICT=1 to make a missing rashid a failure.

--no-data is deliberate: the data pass reads every asset's bytes, and this repo
holds no data files. Byte-level checks belong to a publish-time check against
S3, not to CI.

Run: RASHID=~/.local/share/portolan-nl/rashid-venv/bin/rashid \\
     python3 tests/test_portolan_conformance.py
"""
import json, os, shutil, subprocess, sys
from pathlib import Path
from collections import Counter

CATALOG = Path(__file__).resolve().parents[1] / "catalog"
RASHID = os.environ.get("RASHID") or shutil.which("rashid")

# Findings knowingly left open, with the reason. Each must be justified in
# docs/phase3-baseline.md; this is not a place to park inconvenient failures.
ACCEPTED = {
    "PTL-COL-003": "collection id '3dbag' is its published name; renaming breaks live hrefs",
}


def main() -> int:
    if not RASHID:
        if os.environ.get("PORTOLAN_STRICT"):
            print("FAIL: rashid not found and PORTOLAN_STRICT is set")
            return 1
        print("SKIP: rashid not found; build it with tools/portolan/build_rashid.sh")
        return 0

    r = subprocess.run([RASHID, "check", str(CATALOG), "--no-data", "--json"],
                       capture_output=True, text=True)
    try:
        report = json.loads(r.stdout)
    except json.JSONDecodeError:
        print(f"FAIL: rashid produced no JSON (exit {r.returncode})")
        print(r.stderr[-2000:])
        return 1

    errors = [f for f in report["findings"]
              if f["severity"] == "error" and f["rule_id"] not in ACCEPTED]
    counts = Counter(f["rule_id"] for f in errors)
    for rule, n in counts.most_common():
        example = next(f for f in errors if f["rule_id"] == rule)
        print(f"FAIL {rule} x{n}: {example['message'][:100]}")
        print(f"       e.g. {example['path']}")
    if errors:
        print(f"\n{len(errors)} Portolan conformance error(s) across "
              f"{report['files_checked']} files")
        return 1

    accepted = sum(1 for f in report["findings"] if f["rule_id"] in ACCEPTED)
    extra = f", {accepted} accepted" if accepted else ""
    print(f"OK: {report['files_checked']} objects conform to Portolan 0.1 "
          f"(+ spec PRs #97, #116){extra}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Run it**

```bash
cd ~/repos/portolan-nl-catalog
RASHID=$RASHID python3 tests/test_portolan_conformance.py
```
Expected: `OK:`. Any remaining error is either a real finding to fix or one that belongs in `ACCEPTED` **with a written justification** — never added just to get green.

- [ ] **Step 3: Add to CI**

The released rashid is the wrong one, so CI must build it:

```yaml
      - name: Build rashid with spec PRs #97 and #116
        run: bash tools/portolan/build_rashid.sh "$HOME/rashid-venv"

      - name: Portolan conformance
        env:
          RASHID: /home/runner/rashid-venv/bin/rashid
          PORTOLAN_STRICT: "1"
        run: python3 tests/test_portolan_conformance.py
```

`PORTOLAN_STRICT=1` means a build failure fails CI instead of silently skipping. Note in the workflow that this step tracks unmerged upstream branches and can break when they move — that is the accepted cost of bleeding edge.

- [ ] **Step 4: Commit and push**

```bash
cd ~/repos/portolan-nl-catalog
git add tests/test_portolan_conformance.py .github/workflows/ci.yml
git commit -m "Gate CI on Portolan conformance

Builds rashid from the two companion PR branches, since no release contains
them yet. SKIPs locally when that rashid is absent; strict in CI."
git push
gh run watch --repo cholmes/portolan-nl-catalog
```

---

### Task 12: Publish and close out phase 3

- [ ] **Step 1: Review the whole diff before it goes live**

```bash
cd ~/repos/portolan-nl-catalog
git diff --stat <phase-2-final-sha>..HEAD -- catalog/ | tail -3
```
This phase touches nearly every file in the catalog. Read the summary and confirm the counts match the tasks above.

- [ ] **Step 2: Drift, dry run, publish, verify**

```bash
cd ~/repos/portolan-nl-catalog
python3 tools/catalog/diff_workdir.py --summary
AWS_PROFILE=default python3 tools/catalog/publish.py | tail -3
AWS_PROFILE=default python3 tools/catalog/publish.py --confirm | tail -3
AWS_PROFILE=default python3 tools/catalog/publish.py | tail -1
curl -s https://data.source.coop/cholmes/portolan-nl/catalog.json | python3 -m json.tool | head -20
```
Expected: the final dry run reports `0 to upload`, and the live root catalog shows the Portolan schema URI in `stac_extensions`.

- [ ] **Step 3: Update the docs**

In `CLAUDE.md`: add `test_portolan_conformance.py` to the test list, document `tools/portolan/build_rashid.sh` and why a custom rashid is needed, and replace the Roadmap section — phases 2 and 3 are done. In `README.md`, note that the catalog targets Portolan 0.1 plus PRs #97 and #116.

- [ ] **Step 4: Record what upstream still owes**

Add a short section to `docs/phase3-baseline.md`: which of the four PRs were still open at completion, the exact rashid commit built against, and every `ACCEPTED` finding with its justification. When the PRs merge, this is what tells the next person what to re-check.

```bash
cd ~/repos/portolan-nl-catalog
git add -A && git commit -m "Document the Portolan 0.1 upgrade" && git push
```

---

## Phase 3 completion checklist

- [ ] `rashid` builds from `tools/portolan/build_rashid.sh` with both companion PRs merged
- [ ] `PTL-AST-003` is a warning and `PTL-VIZ-006` exists — proving #90 and #63 took effect
- [ ] `tests/test_portolan_conformance.py` passes, and every `ACCEPTED` entry is justified in `docs/phase3-baseline.md`
- [ ] CI builds rashid and runs the conformance gate with `PORTOLAN_STRICT=1`
- [ ] All seven tests green locally and in CI
- [ ] Every metadata change is also made in the generator that emits it — `test_generators.py` proves it
- [ ] `publish.py` dry run reports zero changes; the live catalog declares the Portolan schema
- [ ] Collections that could not get a thumbnail are recorded with the reason, not silently skipped

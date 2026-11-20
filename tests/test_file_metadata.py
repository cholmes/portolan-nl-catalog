"""Every committed file:size and file:checksum matches the file in the repo.

Assets whose file the repo itself publishes (thumbnails, styles, READMEs)
carry file:size and file:checksum (PTL-AST-003). A hand edit to one of those
files without refreshing the metadata would publish a wrong size or hash,
which is worse than publishing none. This gate recomputes both for every
asset whose href resolves inside catalog/ and fails on any mismatch.

Assets whose href points at S3 are checked for presence of file:size only
when absent locally; their values come from the published objects and cannot
be recomputed here.

Run: python3 tests/test_file_metadata.py
"""
import hashlib
import json
import sys
from pathlib import Path

CATALOG = Path(__file__).resolve().parents[1] / "catalog"


def stac_files():
    for p in sorted(CATALOG.rglob("*.json")):
        if ".portolan" in p.parts or "styles" in p.parts or p.name == "versions.json":
            continue
        try:
            d = json.loads(p.read_text())
        except json.JSONDecodeError:
            continue
        if isinstance(d, dict) and d.get("type") in ("Catalog", "Collection", "Feature"):
            yield p, d


def main() -> int:
    bad = []
    checked = 0
    for p, d in stac_files():
        for key, a in (d.get("assets") or {}).items():
            if not isinstance(a, dict):
                continue
            href = str(a.get("href") or "")
            if not href.startswith("./"):
                continue
            target = (p.parent / href).resolve()
            if not target.is_file() or target == p.resolve():
                continue
            size = a.get("file:size")
            checksum = a.get("file:checksum")
            if size is None and checksum is None:
                continue
            rel = p.relative_to(CATALOG)
            data = target.read_bytes()
            if size is not None and size != len(data):
                bad.append(f"{rel} asset '{key}': file:size {size} != {len(data)}")
            if checksum is not None:
                want = "1220" + hashlib.sha256(data).hexdigest()
                if checksum != want:
                    bad.append(f"{rel} asset '{key}': file:checksum does not match the file")
            checked += 1
    if bad:
        print("\n".join(f"FAIL {b}" for b in bad))
        print(f"\n{len(bad)} stale file:size/file:checksum value(s); "
              "re-run tools/catalog/conform.py or the owning generator")
        return 1
    print(f"OK: {checked} in-repo asset file metadata entries match their files")
    return 0


if __name__ == "__main__":
    sys.exit(main())

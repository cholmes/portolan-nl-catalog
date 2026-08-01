"""Portolan conformance via rashid.

Targets Portolan 0.1 plus two in-flight spec PRs, so it needs a rashid built
from tools/portolan/build_rashid.sh rather than a released one:

  portolan-spec#97  / rashid#63 -- the default style carries a `default` role
  portolan-spec#116 / rashid#90 -- file:size and file:checksum are SHOULD

SKIPs (exit 0) when that rashid is not on PATH, so the local suite stays
zero-setup like the others. Point $RASHID at the built binary, or set
$PORTOLAN_STRICT=1 to make a missing rashid a failure (CI does).

--no-data is deliberate: the data pass reads every asset's bytes, and this repo
holds no data files. Byte-level checks belong to a publish-time check against
S3, not to CI.

Run: RASHID=~/.local/share/portolan-nl/rashid-venv/bin/rashid \\
     python3 tests/test_portolan_conformance.py
"""
import json
import os
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path

CATALOG = Path(__file__).resolve().parents[1] / "catalog"
RASHID = os.environ.get("RASHID") or shutil.which("rashid")

# Findings knowingly left open, each with its reason. Every entry here is
# justified at length in docs/phase3-baseline.md. This is not a place to park
# inconvenient failures: three of these would require the catalog to assert
# something false, and the fourth is unwritten content, not a metadata defect.
ACCEPTED = {
    "PTL-VIZ-001": "thumbnails are WebP by design; rashid allows only PNG/JPEG",
    "PTL-PRO-001": "rel:via points at WFS/Atom service endpoints, which are not text/html",
    "PTL-VIZ-002": "three collections have no MapLibre style written yet",
    "PTL-COL-003": "collection id '3dbag' is its published name; renaming breaks live hrefs",
}


def main() -> int:
    if not RASHID:
        if os.environ.get("PORTOLAN_STRICT"):
            print("FAIL: rashid not found and PORTOLAN_STRICT is set. "
                  "Build it with tools/portolan/build_rashid.sh")
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
    for rule, n in Counter(f["rule_id"] for f in errors).most_common():
        example = next(f for f in errors if f["rule_id"] == rule)
        print(f"FAIL {rule} x{n}: {example['message'][:100]}")
        print(f"       e.g. {example['path']}")
    if errors:
        print(f"\n{len(errors)} Portolan conformance error(s) across "
              f"{report['files_checked']} files")
        return 1

    accepted = Counter(f["rule_id"] for f in report["findings"]
                       if f["rule_id"] in ACCEPTED and f["severity"] == "error")
    for rule, n in accepted.most_common():
        print(f"ACCEPTED {rule} x{n}: {ACCEPTED[rule]}")
    total = sum(accepted.values())
    extra = f", {total} accepted (see docs/phase3-baseline.md)" if total else ""
    print(f"OK: {report['files_checked']} objects conform to Portolan 0.1 "
          f"(+ spec PRs #97, #116){extra}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

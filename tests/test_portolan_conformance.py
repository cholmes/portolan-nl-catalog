"""Portolan conformance via rashid.

Targets Portolan v0.3.0, which released rashid >= 0.4.0 implements, so the
purpose-built rashid from tools/portolan/build_rashid.sh is no longer needed.
All three spec PRs this catalog once tracked ahead of release (#97, #116,
#120) are part of the released specification.

SKIPs (exit 0) when rashid is not on PATH, so the local suite stays
zero-setup like the others. Point $RASHID at a specific binary, or set
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

# Findings knowingly left open, each with its reason, and each justified in
# docs/phase3-baseline.md. This is not a place to park inconvenient failures.
# The v0.3 upgrade closed both former entries: every mirror now carries a
# text/html via link beside its service links (PORTO-CORE-084 allows the
# service links their real media types), and PTL-COL-003 is a warning under
# v0.3, which this gate does not fail on.
ACCEPTED: dict[str, str] = {}


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
    print(f"OK: {report['files_checked']} objects conform to Portolan v0.3.0{extra}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Offline pattern scan of Git-tracked files; never prints suspected values."""

import json
import subprocess
import sys


def main() -> int:
    result = subprocess.run(
        [
            "detect-secrets",
            "scan",
            "--no-verify",
            "--disable-plugin",
            "HexHighEntropyString",
            "--disable-plugin",
            "Base64HighEntropyString",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    findings = json.loads(result.stdout)["results"]
    for path, entries in sorted(findings.items()):
        print(f"FAIL {path}: {len(entries)} suspected credential pattern(s)")
    if findings:
        return 1
    print(
        "PASS tracked-file credential pattern scan (offline; entropy checks excluded)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

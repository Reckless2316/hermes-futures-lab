"""Local specification tools. Financial evaluation starts in P1."""

import argparse
import hashlib
import json
from pathlib import Path
from typing import Sequence

from futures_lab import __version__


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", action="version", version=__version__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("status", help="Show implementation and review status")
    fingerprint = commands.add_parser("fingerprint", help="Hash exact local artifact bytes")
    fingerprint.add_argument("path", type=Path)
    args = parser.parse_args(argv)

    result: dict[str, object]
    if args.command == "status":
        result = {
            "schema_version": 1,
            "package_version": __version__,
            "phase": "P0",
            "implementation": "specification_only",
            "evaluation_available": False,
            "acceptance": "pending_external_review_and_human_scope_approval",
        }
    else:
        try:
            with args.path.open("rb") as stream:
                digest = hashlib.file_digest(stream, "sha256").hexdigest()
        except OSError as error:
            parser.exit(2, f"futures-lab: cannot read artifact: {error.strerror}\n")
        result = {"schema_version": 1, "algorithm": "sha256", "sha256": digest}
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0

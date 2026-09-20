"""Local deterministic lab evaluation; never actual-account certification."""

import argparse
import hashlib
import json
from pathlib import Path
from typing import Sequence

from futures_lab import __version__
from futures_lab.data.input import load_document
from futures_lab.domain.values import DataError
from futures_lab.engine import evaluate_document
from futures_lab.reporting import code_version
from futures_lab.rules.manifest import load_rules


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", action="version", version=__version__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("status", help="Show implementation and review status")
    fingerprint = commands.add_parser(
        "fingerprint", help="Hash exact local artifact bytes"
    )
    fingerprint.add_argument("path", type=Path)
    evaluation = commands.add_parser(
        "evaluate", help="Evaluate normalized recorded events in candidate.3 lab mode"
    )
    evaluation.add_argument("path", type=Path)
    evaluation.add_argument(
        "--rules",
        type=Path,
        help="Exact candidate.3 bytes; defaults to packaged manifest",
    )
    evaluation.add_argument("--run-id", default="lab-run")
    evaluation.add_argument("--include-checkpoints", action="store_true")
    args = parser.parse_args(argv)

    result: dict[str, object]
    if args.command == "status":
        result = {
            "schema_version": 1,
            "package_version": __version__,
            "phase": "P1",
            "implementation": "deterministic_financial_engine",
            "evaluation_available": True,
            "acceptance": "p1_pending_independent_review_and_human_acceptance",
        }
    elif args.command == "evaluate":
        try:
            rules = load_rules(args.rules)
            document, digest = load_document(args.path)
            evaluation_result = evaluate_document(
                document,
                rules,
                input_sha256=digest,
                code_version=code_version(),
                run_id=args.run_id,
                include_checkpoints=args.include_checkpoints,
            )
            result = (
                evaluation_result
                if args.include_checkpoints
                else evaluation_result["report"]
            )
        except DataError as error:
            parser.exit(2, f"futures-lab: {error.reason}\n")
    else:
        try:
            with args.path.open("rb") as stream:
                digest = hashlib.file_digest(stream, "sha256").hexdigest()
        except OSError as error:
            parser.exit(2, f"futures-lab: cannot read artifact: {error.strerror}\n")
        result = {"schema_version": 1, "algorithm": "sha256", "sha256": digest}
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0

"""Checkpoint integrity checks only; these do not evaluate financial rules."""

import hashlib
import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
PAIRS = [
    ("rules/ftmo_futures_growth_evaluation_50k_2026-09-17.yaml", "rules/schema.json"),
    ("tests/fixtures/round_trip.json", "tests/fixtures/trace.schema.json"),
    ("tests/fixtures/growth_50k_reference.json", "tests/fixtures/reference.schema.json"),
]


def read_json(path: str) -> object:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def main() -> None:
    for artifact, schema_file in PAIRS:
        schema = read_json(schema_file)
        Draft202012Validator.check_schema(schema)
        data = (
            yaml.safe_load((ROOT / artifact).read_text(encoding="utf-8"))
            if artifact.endswith(".yaml")
            else read_json(artifact)
        )
        Draft202012Validator(schema, format_checker=FormatChecker()).validate(data)
        print("PASS schema:", artifact)

    inventory = read_json("tests/fixtures/artifacts.sha256.json")
    for path, expected in inventory.items():
        if hashlib.sha256((ROOT / path).read_bytes()).hexdigest() != expected:
            raise ValueError(f"Artifact hash mismatch: {path}")
    print("PASS exact-byte hashes:", len(inventory), "artifacts")

    trace = read_json("tests/fixtures/round_trip.json")
    events = trace["events"]
    if len({event["event_id"] for event in events}) != len(events):
        raise ValueError("Duplicate event IDs")
    if [event["sequence"] for event in events] != list(range(1, len(events) + 1)):
        raise ValueError("Unexpected trace sequence")
    selection = next(
        event["payload"] for event in events if event["event_type"] == "RulesetSelected"
    )
    if selection["ruleset_sha256"] != inventory[PAIRS[0][0]]:
        raise ValueError("Trace rules hash mismatch")
    if trace["provenance"]["input_sha256"] != inventory[trace["provenance"]["input_path"]]:
        raise ValueError("Trace recipe hash mismatch")
    print("PASS trace IDs, sequence, rules and recipe hash linkage")


if __name__ == "__main__":
    main()

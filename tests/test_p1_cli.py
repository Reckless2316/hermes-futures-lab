import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRACE = ROOT / "tests/fixtures/round_trip.json"


class P1CliTests(unittest.TestCase):
    def cli(self, *args):
        return subprocess.run(
            [sys.executable, "-m", "futures_lab", *map(str, args)],
            capture_output=True,
            text=True,
            timeout=20,
        )

    def test_packaged_manifest_default_evaluation_and_provenance(self):
        a = self.cli("evaluate", TRACE, "--run-id", "cli-test")
        b = self.cli("evaluate", TRACE, "--run-id", "cli-test")
        self.assertEqual(a.returncode, 0, a.stderr)
        self.assertEqual(a.stdout, b.stdout)
        r = json.loads(a.stdout)
        self.assertEqual(r["balance"], "50095.00")
        self.assertEqual(
            r["ruleset_sha256"],
            "a1dcf3f3ac04abb7c5334bd6e65e9374fc36d67c3422a4b590c3ed3ae8eeeda6",
        )
        self.assertEqual(r["evaluation_mode"], "candidate_3_lab_estimate")
        self.assertFalse(r["official_account_certification"])
        self.assertEqual(r["net_of_fees_label"], "lab_convention_pending_verification")
        self.assertIn("+sha256:", r["code_version"])
        self.assertEqual(len(r["input_sha256"]), 64)
        self.assertEqual(len(r["calendar_sha256"]), 64)

    def test_checkpoints_and_unknown_input_status(self):
        a = self.cli("evaluate", TRACE, "--include-checkpoints")
        self.assertEqual(len(json.loads(a.stdout)["checkpoints"]), 13)
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "bad.json"
            path.write_text("{}")
            r = self.cli("evaluate", path)
            self.assertEqual(r.returncode, 0)
            self.assertEqual(json.loads(r.stdout)["state"], "data_unavailable")
            path.write_text('{"x":1,"x":2}')
            r = self.cli("evaluate", path)
            self.assertEqual(r.returncode, 2)
            self.assertNotIn("Traceback", r.stderr)

    def test_cannot_evaluate_a_historical_or_modified_manifest(self):
        r = self.cli(
            "evaluate",
            TRACE,
            "--rules",
            ROOT / "rules/ftmo_futures_growth_evaluation_50k_2026-09-17.yaml",
        )
        self.assertEqual(r.returncode, 2)
        self.assertIn("unapproved_rules_bytes", r.stderr)

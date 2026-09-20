"""Install the built wheel outside the checkout and exercise its public CLI."""

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def run(*args: str, cwd: Path) -> str:
    result = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    if result.returncode:
        raise SystemExit(result.stderr or f"command failed: {args[0]}")
    return result.stdout


def main() -> None:
    wheels = list((ROOT / "dist").glob("*.whl"))
    if len(wheels) != 1:
        raise SystemExit(
            "Build exactly one wheel in dist before running this smoke test"
        )
    with tempfile.TemporaryDirectory(prefix="futures-lab-wheel-") as directory:
        isolated = Path(directory)
        environment = isolated / "venv"
        run("uv", "venv", "--python", "3.11.16", str(environment), cwd=isolated)
        python = str(environment / "bin/python")
        run("uv", "pip", "install", "--python", python, str(wheels[0]), cwd=isolated)
        trace = isolated / "round_trip.json"
        shutil.copyfile(ROOT / "tests/fixtures/round_trip.json", trace)
        status = json.loads(
            run(python, "-I", "-m", "futures_lab", "status", cwd=isolated)
        )
        assert (
            status["acceptance"] == "p1_pending_independent_review_and_human_acceptance"
        )
        output = run(
            python, "-I", "-m", "futures_lab", "evaluate", str(trace), cwd=isolated
        )
        assert output == run(
            python, "-I", "-m", "futures_lab", "evaluate", str(trace), cwd=isolated
        )
        report = json.loads(output)
        assert report["balance"] == report["equity"] == "50095.00"
        assert (
            report["ruleset_sha256"]
            == "a1dcf3f3ac04abb7c5334bd6e65e9374fc36d67c3422a4b590c3ed3ae8eeeda6"
        )
        assert report["evaluation_mode"] == "candidate_3_lab_estimate"
        assert not report["official_account_certification"]
        assert report["input_sha256"] == hashlib.sha256(trace.read_bytes()).hexdigest()
        run(
            python,
            "-I",
            "-c",
            "from importlib.metadata import metadata; m=metadata('hermes-futures-lab'); assert m['License-Expression']=='MIT'; assert m.get_all('Requires-Dist')==['pyyaml==6.0.3']",
            cwd=isolated,
        )
        print(
            "PASS isolated installed-wheel import, MIT metadata, pinned runtime dependency, packaged candidate and deterministic evaluation"
        )


if __name__ == "__main__":
    main()

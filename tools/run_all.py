from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

try:
    from .common import ROOT
except ImportError:  # direct script execution
    from common import ROOT

TOOLS = Path(__file__).resolve().parent
ATTEMPTS = ROOT / "artifacts" / "attempts"


def next_attempt() -> Path:
    ATTEMPTS.mkdir(parents=True, exist_ok=True)
    existing = [int(path.name.split("-")[-1]) for path in ATTEMPTS.glob("attempt-*") if path.name.split("-")[-1].isdigit()]
    path = ATTEMPTS / f"attempt-{(max(existing, default=0) + 1):03d}"
    path.mkdir()
    return path


def main() -> None:
    attempt = next_attempt()
    commands = [
        [sys.executable, "-B", str(TOOLS / "source_fingerprint.py")],
        [sys.executable, "-B", str(TOOLS / "validate_contract.py")],
        [sys.executable, "-B", str(TOOLS / "build_adapters.py"), "--mode", "normal", "--output-root", "artifacts/build-normal"],
        [sys.executable, "-B", str(TOOLS / "build_adapters.py"), "--mode", "candidate-sandbox", "--output-root", "artifacts/build"],
        [sys.executable, "-B", str(TOOLS / "validate_packages.py")],
        [sys.executable, "-B", str(TOOLS / "verify_determinism.py")],
        [sys.executable, "-B", str(TOOLS / "validate_runtime_fixtures.py")],
        [sys.executable, "-B", str(TOOLS / "run_evals.py")],
    ]
    results = []
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    for index, command in enumerate(commands, start=1):
        completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, env=env, check=False)
        record = {
            "index": index,
            "command": [Path(command[2]).name, *command[3:]],
            "exit_code": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }
        results.append(record)
        (attempt / f"{index:02d}.log").write_text(
            f"COMMAND: {' '.join(record['command'])}\nEXIT: {completed.returncode}\nSTDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}",
            encoding="utf-8",
            newline="\n",
        )
        if completed.returncode != 0:
            break
    status = "PASS" if len(results) == len(commands) and all(item["exit_code"] == 0 for item in results) else "FAIL"
    summary = {"schema_version": 1, "status": status, "attempt": attempt.name, "commands": results}
    (attempt / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8", newline="\n")
    latest = ROOT / "artifacts" / "validation" / "run-all-latest.json"
    latest.parent.mkdir(parents=True, exist_ok=True)
    latest.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"offline gate {status}: {len(results)}/{len(commands)} commands; evidence {attempt.relative_to(ROOT)}")
    if status != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()

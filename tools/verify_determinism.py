from __future__ import annotations

from pathlib import Path

try:
    from .build_adapters import build
except ImportError:  # direct script execution
    from build_adapters import build
try:
    from .common import ROOT, write_json
except ImportError:  # direct script execution
    from common import ROOT, write_json


def verify(output: Path | None = None) -> dict:
    run_a = build("candidate-sandbox", ROOT / "artifacts" / "determinism" / "run-a")
    run_b = build("candidate-sandbox", ROOT / "artifacts" / "determinism" / "run-b")
    comparisons = {}
    errors = []
    for surface in ("claude-code", "codex"):
        a = run_a["packages"][surface]
        b = run_b["packages"][surface]
        same_tree = a["tree_sha256"] == b["tree_sha256"]
        same_zip = a["zip_sha256"] == b["zip_sha256"]
        comparisons[surface] = {
            "run_a_tree_sha256": a["tree_sha256"],
            "run_b_tree_sha256": b["tree_sha256"],
            "tree_identical": same_tree,
            "run_a_zip_sha256": a["zip_sha256"],
            "run_b_zip_sha256": b["zip_sha256"],
            "zip_identical": same_zip,
        }
        if not (same_tree and same_zip):
            errors.append(surface)
    payload = {"schema_version": 1, "status": "PASS" if not errors else "FAIL", "comparisons": comparisons, "errors": errors}
    target = output or ROOT / "artifacts" / "validation" / "determinism.json"
    write_json(target, payload)
    if errors:
        raise SystemExit(f"determinism failed for {errors}; see {target}")
    return payload


if __name__ == "__main__":
    result = verify()
    print(f"determinism passed: {len(result['comparisons'])} surface packages")

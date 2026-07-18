from __future__ import annotations

import hashlib
from typing import Any

try:
    from .common import ROOT, load_json, sha256_file, write_json
except ImportError:  # direct script execution
    from common import ROOT, load_json, sha256_file, write_json

RUNTIME = ROOT / "evals" / "runtime"
OUTPUT = ROOT / "artifacts" / "runtime-evals" / "fixture-manifest.json"
EXPECTED_TASKS = {
    "create-simple-skill", "improve-bloated-skill", "resolve-trigger-collision",
    "migrate-claude-only-to-codex", "create-dual-surface-plugin", "reject-unsafe-plugin",
}
EXPECTED_CONDITIONS = {
    "claude-current-authoring-skills", "claude-rigwright",
    "codex-openai-skill-creator", "codex-rigwright",
}


def validate() -> dict[str, Any]:
    failures: list[str] = []
    protocol = load_json(RUNTIME / "protocol.json")
    tasks = load_json(RUNTIME / "tasks.json")
    result_schema = load_json(RUNTIME / "result.schema.json")
    condition_ids = {item.get("id") for item in protocol.get("conditions", [])}
    if condition_ids != EXPECTED_CONDITIONS:
        failures.append(f"condition ids differ: {sorted(condition_ids)}")
    if protocol.get("replicates_per_condition", 0) < 3:
        failures.append("at least three replicates are required for variance")
    if "no expected answer" not in " ".join(protocol.get("paired_controls", [])).lower():
        failures.append("non-leakage control is missing")
    task_ids = {item.get("id") for item in tasks.get("tasks", [])}
    if task_ids != EXPECTED_TASKS:
        failures.append(f"task ids differ: {sorted(task_ids)}")
    inputs: dict[str, dict[str, Any]] = {}
    for task in tasks.get("tasks", []):
        for key in ("id", "leaf", "public_prompt", "candidate_invocation", "baseline_invocation", "rubric"):
            if not task.get(key):
                failures.append(f"{task.get('id', '<unknown>')}: missing {key}")
        rubric = task.get("rubric", [])
        if len(rubric) < 4:
            failures.append(f"{task['id']}: fewer than four rubric items")
        if not any(item.get("critical") for item in rubric):
            failures.append(f"{task['id']}: no critical rubric item")
        if sum(int(item.get("weight", 0)) for item in rubric) <= 0:
            failures.append(f"{task['id']}: invalid rubric weights")
        for rel in task.get("input_files", []):
            path = ROOT / rel
            if not path.is_file():
                failures.append(f"{task['id']}: missing input {rel}")
                continue
            inputs[rel] = {"bytes": path.stat().st_size, "sha256": sha256_file(path)}
    required_result_keys = set(result_schema.get("required", []))
    if required_result_keys != {"decision", "summary", "files", "risks", "assumptions"}:
        failures.append("result schema required keys differ from response contract")
    fixture_paths = [RUNTIME / "protocol.json", RUNTIME / "tasks.json", RUNTIME / "result.schema.json"]
    fixture_paths.extend(ROOT / rel for rel in inputs)
    file_rows = []
    for path in sorted(set(fixture_paths), key=lambda item: item.as_posix().lower()):
        rel = path.relative_to(ROOT).as_posix()
        file_rows.append({"path": rel, "bytes": path.stat().st_size, "sha256": sha256_file(path)})
    aggregate_rows = "\n".join(f"{item['path']}|{item['bytes']}|{item['sha256']}" for item in file_rows)
    payload = {
        "schema_version": 1,
        "status": "PASS" if not failures else "FAIL",
        "task_count": len(task_ids),
        "condition_count": len(condition_ids),
        "replicates_per_condition": protocol.get("replicates_per_condition"),
        "input_files": inputs,
        "fixture_file_count": len(file_rows),
        "fixture_sha256": hashlib.sha256(aggregate_rows.encode("utf-8")).hexdigest(),
        "files": file_rows,
        "failures": failures,
    }
    write_json(OUTPUT, payload)
    if failures:
        raise SystemExit(f"runtime fixture validation failed with {len(failures)} failure(s)")
    return payload


if __name__ == "__main__":
    result = validate()
    print(
        "runtime fixtures passed: "
        f"{result['task_count']} tasks, {result['condition_count']} conditions, "
        f"{result['replicates_per_condition']} replicates, {result['fixture_sha256']}"
    )

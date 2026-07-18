from __future__ import annotations

import re
from pathlib import Path
from typing import Any

try:
    from .common import ROOT, ensure_unique, load_json, write_json
except ImportError:  # direct script execution
    from common import ROOT, ensure_unique, load_json, write_json


INITIAL_LEAVES = {
    "rigwright-route",
    "rigwright-author-skill",
    "rigwright-author-plugin",
    "rigwright-evaluate",
    "rigwright-migrate",
    "rigwright-prioritize",
    "rigwright-archive",
}
FUTURE_LEAVES = {
    "rigwright-author-mcp",
    "rigwright-author-agent",
    "rigwright-author-hook",
    "rigwright-author-command",
    "rigwright-author-app",
}
LIFECYCLE_STATES = {
    "current-authorized",
    "candidate-sandbox",
    "compatibility-alias",
    "archived-retained",
    "quarantined-untrusted",
    "rejected",
}
REQUIRED_SKILL_KEYS = {
    "schema_version", "id", "display_name", "description", "intent_owner", "intent", "outcome",
    "non_goals", "inputs", "outputs", "permissions", "triggers", "lifecycle", "instructions",
    "eval_path", "provenance",
}
REQUIRED_LIFECYCLE_KEYS = {
    "state", "canonical_owner", "intent_key", "scope", "surfaces", "routing_priority",
    "specificity", "supersedes", "evidence_date", "promotion_gate",
}


def validate_all(output: Path | None = None) -> dict[str, Any]:
    errors: list[str] = []
    checks = 0
    skill_root = ROOT / "src" / "skills"
    directories = {path.name for path in skill_root.iterdir() if path.is_dir()}
    checks += 1
    if directories != INITIAL_LEAVES:
        errors.append(f"initial leaf set mismatch: expected {sorted(INITIAL_LEAVES)}, got {sorted(directories)}")
    forbidden = directories & FUTURE_LEAVES
    checks += 1
    if forbidden:
        errors.append(f"future leaves implemented before gate: {sorted(forbidden)}")

    intent_keys: list[str] = []
    records: list[dict[str, Any]] = []
    eval_case_count = 0
    for leaf in sorted(directories):
        path = skill_root / leaf / "skill.json"
        try:
            record = load_json(path)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{leaf}: invalid skill.json: {exc}")
            continue
        records.append(record)
        checks += 1
        missing = REQUIRED_SKILL_KEYS - set(record)
        extra = set(record) - REQUIRED_SKILL_KEYS
        if missing or extra:
            errors.append(f"{leaf}: key mismatch missing={sorted(missing)} extra={sorted(extra)}")
        checks += 1
        if record.get("schema_version") != 1 or record.get("id") != leaf or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", leaf) or len(leaf) > 64:
            errors.append(f"{leaf}: invalid schema version or identifier")
        checks += 1
        description = record.get("description", "")
        if not isinstance(description, str) or not description or len(description) > 1024 or "<" in description or ">" in description:
            errors.append(f"{leaf}: invalid description")
        checks += 1
        if not isinstance(record.get("outcome"), str) or not record["outcome"].strip():
            errors.append(f"{leaf}: exactly one non-empty outcome string is required")
        checks += 1
        if not isinstance(record.get("non_goals"), list) or not record["non_goals"]:
            errors.append(f"{leaf}: explicit non-goals required")
        checks += 1
        triggers = record.get("triggers", {})
        if len(triggers.get("positive", [])) < 3 or len(triggers.get("negative", [])) < 1:
            errors.append(f"{leaf}: need >=3 positive triggers and >=1 negative trigger")
        checks += 1
        lifecycle = record.get("lifecycle", {})
        if set(lifecycle) != REQUIRED_LIFECYCLE_KEYS or lifecycle.get("state") not in LIFECYCLE_STATES:
            errors.append(f"{leaf}: invalid lifecycle record")
        else:
            intent_keys.append(lifecycle["intent_key"])
        checks += 1
        if lifecycle.get("state") != "candidate-sandbox" or lifecycle.get("routing_priority") != 400:
            errors.append(f"{leaf}: initial proposal leaves must be candidate-sandbox priority 400")
        checks += 1
        if record.get("eval_path") != "evals/evals.json":
            errors.append(f"{leaf}: eval_path must be evals/evals.json")
        eval_path = skill_root / leaf / "evals" / "evals.json"
        try:
            evals = load_json(eval_path)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{leaf}: invalid evals: {exc}")
            continue
        cases = evals.get("cases", [])
        eval_case_count += len(cases)
        checks += 1
        if evals.get("schema_version") != 1 or evals.get("skill_name") != leaf or len(cases) < 4:
            errors.append(f"{leaf}: eval schema/name/case count invalid")
        checks += 1
        positives = [case for case in cases if case.get("should_trigger") is True]
        negatives = [case for case in cases if case.get("should_trigger") is False]
        if len(positives) < 3 or len(negatives) < 1:
            errors.append(f"{leaf}: each workflow needs >=3 positives and >=1 near miss")
        checks += 1
        try:
            ensure_unique((case["id"] for case in cases), f"eval ids in {leaf}")
        except Exception as exc:  # noqa: BLE001
            errors.append(str(exc))
        for case in cases:
            checks += 1
            if not case.get("prompt") or not isinstance(case.get("expected_behavior"), list) or not case["expected_behavior"]:
                errors.append(f"{leaf}:{case.get('id')}: prompt and expected_behavior required")

    checks += 1
    try:
        ensure_unique(intent_keys, "intent keys")
    except Exception as exc:  # noqa: BLE001
        errors.append(str(exc))

    route = next((record for record in records if record.get("id") == "rigwright-route"), {})
    route_text = " ".join(route.get("instructions", [])).lower()
    forbidden_procedure_phrases = ["write frontmatter", "create .codex-plugin", "copy every source file", "run three model"]
    for phrase in forbidden_procedure_phrases:
        checks += 1
        if phrase in route_text:
            errors.append(f"router duplicates leaf procedure: {phrase}")

    for schema_path in sorted((ROOT / "contracts").glob("*.schema.json")):
        checks += 1
        try:
            schema = load_json(schema_path)
            if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
                errors.append(f"{schema_path.name}: unsupported $schema")
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{schema_path.name}: invalid JSON: {exc}")

    payload = {
        "schema_version": 1,
        "status": "PASS" if not errors else "FAIL",
        "checks": checks,
        "leaf_count": len(records),
        "eval_case_count": eval_case_count,
        "errors": errors,
    }
    target = output or ROOT / "artifacts" / "validation" / "contract-validation.json"
    write_json(target, payload)
    if errors:
        raise SystemExit(f"contract validation failed with {len(errors)} error(s); see {target}")
    return payload


if __name__ == "__main__":
    result = validate_all()
    print(f"contract validation passed: {result['checks']} checks, {result['leaf_count']} leaves, {result['eval_case_count']} eval cases")

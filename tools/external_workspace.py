"""Scaffold and validate neutral skills in an external Rigwright workspace."""
from __future__ import annotations

import argparse
import re
from datetime import date
from pathlib import Path
from typing import Any

try:
    from .common import load_json, write_json
    from .validate_contract import LIFECYCLE_STATES, REQUIRED_LIFECYCLE_KEYS, REQUIRED_SKILL_KEYS
except ImportError:  # direct script execution
    from common import load_json, write_json
    from validate_contract import LIFECYCLE_STATES, REQUIRED_LIFECYCLE_KEYS, REQUIRED_SKILL_KEYS


MARKER_NAME = "rigwright-workspace.json"
MARKER = {
    "schema_version": 1,
    "kind": "rigwright-skill-workspace",
    "skills_root": "src/skills",
}
SURFACES = {"neutral", "claude-code", "codex"}
SIDE_EFFECT_CLASSES = {"read-only", "proposal-write", "live-write"}
SAFETY_DECISIONS = {
    "proceed-proposal-only",
    "owner-confirmation-required",
    "blocked",
    "not-applicable",
}
ID_PATTERN = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")


def _title(skill_id: str) -> str:
    return " ".join(part.capitalize() for part in skill_id.split("-"))


def _non_empty_strings(value: Any, *, minimum: int = 1) -> bool:
    return (
        isinstance(value, list)
        and len(value) >= minimum
        and all(isinstance(item, str) and item.strip() for item in value)
    )


def _unique(value: Any) -> bool:
    if not isinstance(value, list):
        return False
    try:
        return len(value) == len(set(value))
    except TypeError:
        return False


def scaffold(
    workspace: Path,
    skill_id: str,
    description: str,
    outcome: str,
    evidence_date: str,
) -> Path:
    """Create one valid candidate skill without overwriting existing work."""
    workspace = workspace.resolve()
    if workspace.exists() and not workspace.is_dir():
        raise ValueError(f"workspace is not a directory: {workspace}")
    if not ID_PATTERN.fullmatch(skill_id) or len(skill_id) > 64:
        raise ValueError("skill id must be <=64 lowercase kebab-case characters")
    if not description.strip() or len(description) > 1024 or "<" in description or ">" in description:
        raise ValueError("description must be 1-1024 characters and contain no angle brackets")
    if not outcome.strip():
        raise ValueError("outcome must be a non-empty string")
    try:
        date.fromisoformat(evidence_date)
    except ValueError as exc:
        raise ValueError("evidence date must use YYYY-MM-DD") from exc

    marker_path = workspace / MARKER_NAME
    if marker_path.exists():
        try:
            existing_marker = load_json(marker_path)
        except Exception as exc:  # noqa: BLE001
            raise ValueError(f"invalid workspace marker at {marker_path}: {exc}") from exc
        if existing_marker != MARKER:
            raise ValueError(f"unsupported workspace marker at {marker_path}")

    skill_dir = workspace / "src" / "skills" / skill_id
    if skill_dir.exists():
        raise ValueError(f"refusing to overwrite existing skill directory: {skill_dir}")

    display_name = _title(skill_id)
    record = {
        "schema_version": 1,
        "id": skill_id,
        "display_name": display_name,
        "description": description.strip(),
        "intent_owner": f"{display_name} workflow",
        "intent": description.strip(),
        "outcome": outcome.strip(),
        "non_goals": [
            f"Install or activate {skill_id}",
            "Perform adjacent workflows with independently testable outcomes",
        ],
        "inputs": ["A bounded request and the material it is allowed to inspect"],
        "outputs": [outcome.strip()],
        "permissions": {
            "side_effect_class": "proposal-write",
            "allowed_scope": "Owner-selected external workspace only",
            "owner_gates": ["Installation", "Activation", "Promotion"],
        },
        "triggers": {
            "positive": [
                f"Use {skill_id} for this bounded request.",
                f"Run the {display_name} workflow on this input.",
                f"Apply {skill_id} and return its reviewable result.",
            ],
            "negative": [f"Install and activate {skill_id} globally."],
        },
        "lifecycle": {
            "state": "candidate-sandbox",
            "canonical_owner": skill_id,
            "intent_key": f"{skill_id}.workflow",
            "scope": "external-workspace",
            "surfaces": ["neutral"],
            "routing_priority": 400,
            "specificity": 50,
            "supersedes": [],
            "evidence_date": evidence_date,
            "promotion_gate": "Owner-reviewed eval evidence and explicit promotion approval",
        },
        "instructions": [
            "Confirm the request is bounded to this skill's single outcome.",
            "Inspect only the owner-selected input and produce the declared outcome.",
            "Return reviewable evidence without installing, activating, or promoting the skill.",
        ],
        "eval_path": "evals/evals.json",
        "provenance": ["rigwright-init-skill"],
    }
    cases = []
    for index, prompt in enumerate(record["triggers"]["positive"], start=1):
        cases.append(
            {
                "id": f"positive-{index}",
                "prompt": prompt,
                "should_trigger": True,
                "expected_leaf": skill_id,
                "expected_behavior": [outcome.strip()],
                "safety_decision": "proceed-proposal-only",
            }
        )
    cases.append(
        {
            "id": "near-miss-install",
            "prompt": record["triggers"]["negative"][0],
            "should_trigger": False,
            "expected_leaf": None,
            "expected_behavior": ["Leave installation and activation to the owner"],
            "safety_decision": "owner-confirmation-required",
        }
    )
    evals = {
        "schema_version": 1,
        "skill_name": skill_id,
        "workflow": description.strip(),
        "cases": cases,
    }

    write_json(marker_path, MARKER)
    write_json(skill_dir / "skill.json", record)
    write_json(skill_dir / "evals" / "evals.json", evals)
    return skill_dir / "skill.json"


def validate(workspace: Path) -> dict[str, Any]:
    """Validate arbitrary external skills without applying vendor leaf policy."""
    workspace = workspace.resolve()
    errors: list[str] = []
    checks = 0
    eval_case_count = 0
    intent_keys: list[str] = []

    marker_path = workspace / MARKER_NAME
    checks += 1
    try:
        marker = load_json(marker_path)
        if marker != MARKER:
            errors.append(f"{MARKER_NAME}: unsupported marker")
    except Exception as exc:  # noqa: BLE001
        errors.append(f"{MARKER_NAME}: invalid or missing: {exc}")

    skill_root = workspace / "src" / "skills"
    directories = sorted(path for path in skill_root.iterdir() if path.is_dir()) if skill_root.is_dir() else []
    checks += 1
    if not directories:
        errors.append("src/skills: at least one skill directory is required")

    for skill_dir in directories:
        leaf = skill_dir.name
        record_path = skill_dir / "skill.json"
        try:
            record = load_json(record_path)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{leaf}: invalid skill.json: {exc}")
            continue
        if not isinstance(record, dict):
            errors.append(f"{leaf}: skill.json must contain an object")
            continue

        checks += 1
        missing = REQUIRED_SKILL_KEYS - set(record)
        extra = set(record) - REQUIRED_SKILL_KEYS
        if missing or extra:
            errors.append(f"{leaf}: key mismatch missing={sorted(missing)} extra={sorted(extra)}")
        checks += 1
        if record.get("schema_version") != 1 or record.get("id") != leaf or not ID_PATTERN.fullmatch(leaf) or len(leaf) > 64:
            errors.append(f"{leaf}: invalid schema version or identifier")

        for field in ("display_name", "description", "intent_owner", "intent", "outcome"):
            checks += 1
            value = record.get(field)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{leaf}: {field} must be a non-empty string")
        description = record.get("description")
        if isinstance(description, str) and (len(description) > 1024 or "<" in description or ">" in description):
            errors.append(f"{leaf}: description exceeds the portable metadata boundary")

        for field in ("non_goals", "inputs", "outputs", "instructions", "provenance"):
            checks += 1
            value = record.get(field)
            if not _non_empty_strings(value) or not _unique(value):
                errors.append(f"{leaf}: {field} must contain unique non-empty strings")

        permissions = record.get("permissions")
        checks += 1
        if not isinstance(permissions, dict) or set(permissions) != {"side_effect_class", "allowed_scope", "owner_gates"}:
            errors.append(f"{leaf}: invalid permissions record")
        elif (
            permissions.get("side_effect_class") not in SIDE_EFFECT_CLASSES
            or not isinstance(permissions.get("allowed_scope"), str)
            or not permissions["allowed_scope"].strip()
            or not isinstance(permissions.get("owner_gates"), list)
            or not all(isinstance(item, str) for item in permissions["owner_gates"])
        ):
            errors.append(f"{leaf}: invalid permissions values")

        triggers = record.get("triggers")
        checks += 1
        if not isinstance(triggers, dict) or set(triggers) != {"positive", "negative"}:
            errors.append(f"{leaf}: invalid triggers record")
        elif (
            not _non_empty_strings(triggers.get("positive"), minimum=3)
            or not _unique(triggers["positive"])
            or not _non_empty_strings(triggers.get("negative"))
            or not _unique(triggers["negative"])
        ):
            errors.append(f"{leaf}: need unique non-empty >=3 positive and >=1 negative triggers")

        lifecycle = record.get("lifecycle")
        checks += 1
        if not isinstance(lifecycle, dict) or set(lifecycle) != REQUIRED_LIFECYCLE_KEYS:
            errors.append(f"{leaf}: invalid lifecycle record")
        else:
            if lifecycle.get("state") not in LIFECYCLE_STATES:
                errors.append(f"{leaf}: invalid lifecycle state")
            for field in ("canonical_owner", "intent_key", "scope", "promotion_gate"):
                if not isinstance(lifecycle.get(field), str) or not lifecycle[field].strip():
                    errors.append(f"{leaf}: lifecycle {field} must be a non-empty string")
            surfaces = lifecycle.get("surfaces")
            if not _non_empty_strings(surfaces) or not _unique(surfaces) or not set(surfaces) <= SURFACES:
                errors.append(f"{leaf}: lifecycle surfaces are invalid")
            routing_priority = lifecycle.get("routing_priority")
            specificity = lifecycle.get("specificity")
            if isinstance(routing_priority, bool) or not isinstance(routing_priority, int) or not 0 <= routing_priority <= 9999:
                errors.append(f"{leaf}: routing_priority must be an integer from 0 to 9999")
            if isinstance(specificity, bool) or not isinstance(specificity, int) or not 0 <= specificity <= 100:
                errors.append(f"{leaf}: specificity must be an integer from 0 to 100")
            if not isinstance(lifecycle.get("supersedes"), list) or not _unique(lifecycle["supersedes"]):
                errors.append(f"{leaf}: supersedes must be a unique list")
            try:
                date.fromisoformat(lifecycle.get("evidence_date", ""))
            except (TypeError, ValueError):
                errors.append(f"{leaf}: evidence_date must use YYYY-MM-DD")
            intent_key = lifecycle.get("intent_key")
            if isinstance(intent_key, str):
                intent_keys.append(intent_key)

        checks += 1
        if record.get("eval_path") != "evals/evals.json":
            errors.append(f"{leaf}: eval_path must be evals/evals.json")

        eval_path = skill_dir / "evals" / "evals.json"
        try:
            evals = load_json(eval_path)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{leaf}: invalid evals/evals.json: {exc}")
            continue
        if not isinstance(evals, dict):
            errors.append(f"{leaf}: evals/evals.json must contain an object")
            continue
        checks += 1
        if set(evals) != {"schema_version", "skill_name", "workflow", "cases"}:
            errors.append(f"{leaf}: eval key mismatch")
        cases = evals.get("cases", [])
        if evals.get("schema_version") != 1 or evals.get("skill_name") != leaf or not isinstance(evals.get("workflow"), str) or not evals["workflow"].strip() or not isinstance(cases, list) or len(cases) < 4:
            errors.append(f"{leaf}: eval schema/name/workflow/case count invalid")
            cases = cases if isinstance(cases, list) else []
        eval_case_count += len(cases)
        case_ids: list[str] = []
        positives = negatives = 0
        for case in cases:
            checks += 1
            if not isinstance(case, dict):
                errors.append(f"{leaf}: eval case must be an object")
                continue
            allowed = {"id", "prompt", "should_trigger", "expected_leaf", "expected_behavior", "safety_decision"}
            required = {"id", "prompt", "should_trigger", "expected_behavior"}
            if not required <= set(case) or not set(case) <= allowed:
                errors.append(f"{leaf}: eval case key mismatch")
            case_id = case.get("id")
            if not isinstance(case_id, str) or not case_id.strip():
                errors.append(f"{leaf}: eval case id must be non-empty")
            else:
                case_ids.append(case_id)
            if not isinstance(case.get("prompt"), str) or not case["prompt"].strip():
                errors.append(f"{leaf}:{case_id}: prompt must be non-empty")
            if not isinstance(case.get("should_trigger"), bool):
                errors.append(f"{leaf}:{case_id}: should_trigger must be boolean")
            elif case["should_trigger"]:
                positives += 1
                if case.get("expected_leaf") != leaf:
                    errors.append(f"{leaf}:{case_id}: positive case must select its own skill")
            else:
                negatives += 1
                if case.get("expected_leaf") == leaf:
                    errors.append(f"{leaf}:{case_id}: near miss must not select its own skill")
            if not _non_empty_strings(case.get("expected_behavior")):
                errors.append(f"{leaf}:{case_id}: expected_behavior must be non-empty")
            if "expected_leaf" in case and case["expected_leaf"] is not None and not isinstance(case["expected_leaf"], str):
                errors.append(f"{leaf}:{case_id}: expected_leaf must be a string or null")
            if "safety_decision" in case and case["safety_decision"] not in SAFETY_DECISIONS:
                errors.append(f"{leaf}:{case_id}: invalid safety_decision")
        if len(case_ids) != len(set(case_ids)):
            errors.append(f"{leaf}: eval case ids must be unique")
        if positives < 3 or negatives < 1:
            errors.append(f"{leaf}: evals need >=3 positive cases and >=1 near miss")

    checks += 1
    if len(intent_keys) != len(set(intent_keys)):
        errors.append("workspace lifecycle intent keys must be unique")

    return {
        "schema_version": 1,
        "status": "PASS" if not errors else "FAIL",
        "workspace": str(workspace),
        "checks": checks,
        "skill_count": len(directories),
        "eval_case_count": eval_case_count,
        "errors": errors,
    }


def init_main() -> None:
    parser = argparse.ArgumentParser(description="Create one neutral skill in an external workspace.")
    parser.add_argument("--workspace", required=True, type=Path)
    parser.add_argument("--id", required=True, dest="skill_id")
    parser.add_argument("--description", required=True)
    parser.add_argument("--outcome", required=True)
    parser.add_argument("--evidence-date", default=date.today().isoformat())
    args = parser.parse_args()
    try:
        path = scaffold(args.workspace, args.skill_id, args.description, args.outcome, args.evidence_date)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    print(f"skill scaffold written: {path.resolve()}")


def validate_main() -> None:
    parser = argparse.ArgumentParser(description="Validate all neutral skills in an external workspace.")
    parser.add_argument("--workspace", required=True, type=Path)
    args = parser.parse_args()
    result = validate(args.workspace)
    if result["status"] != "PASS":
        details = "\n".join(f"- {error}" for error in result["errors"])
        raise SystemExit(f"workspace validation failed: {len(result['errors'])} error(s)\n{details}")
    print(
        "workspace validation passed: "
        f"{result['skill_count']} skill(s), {result['eval_case_count']} eval case(s); "
        f"workspace {result['workspace']}"
    )

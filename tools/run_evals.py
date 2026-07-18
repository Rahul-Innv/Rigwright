from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    from .common import ROOT, load_json, write_json
except ImportError:  # direct script execution
    from common import ROOT, load_json, write_json
try:
    from .priority import select_owner
except ImportError:  # direct script execution
    from priority import select_owner


def route_prompt(prompt: str) -> str | None:
    text = prompt.lower()
    if any(term in text for term in ("pretooluse hook", "mcp server", "author an agent", "create a command", "create an app")):
        return None
    if any(term in text for term in ("archive", "restore", "checksummed")):
        return "rigwright-archive"
    if any(term in text for term in ("migrate", "port ", "migration", "legacy alias")):
        return "rigwright-migrate"
    if any(term in text for term in ("compare", "baseline", "variance", "benchmark")):
        return "rigwright-evaluate"
    if any(term in text for term in ("canonical", "overlapping", "priority", "routing collision")):
        return "rigwright-prioritize"
    if "plugin" in text:
        return "rigwright-author-plugin"
    if "skill" in text:
        return "rigwright-author-skill"
    return None


def run(output: Path | None = None) -> dict[str, Any]:
    failures: list[dict[str, Any]] = []
    assertions = 0
    near_misses = 0
    leaf_results = []
    eval_index: dict[tuple[str, str], dict[str, Any]] = {}
    for eval_path in sorted((ROOT / "src" / "skills").glob("*/evals/evals.json")):
        data = load_json(eval_path)
        leaf = data["skill_name"]
        positive = negative = 0
        for case in data["cases"]:
            eval_index[(leaf, case["id"])] = case
            assertions += 1
            if case["should_trigger"]:
                positive += 1
                if leaf != "rigwright-route" and case.get("expected_leaf") != leaf:
                    failures.append({"case": case["id"], "reason": f"positive case does not own {leaf}"})
            else:
                negative += 1
                near_misses += 1
                if case.get("expected_leaf") == leaf:
                    failures.append({"case": case["id"], "reason": "near miss still selects its leaf"})
            if leaf == "rigwright-route":
                actual = route_prompt(case["prompt"])
                if actual != case.get("expected_leaf"):
                    failures.append({"case": case["id"], "expected": case.get("expected_leaf"), "actual": actual})
        leaf_results.append({"leaf": leaf, "positive_cases": positive, "near_misses": negative, "status": "PASS" if positive >= 3 and negative >= 1 else "FAIL"})

    fixed = load_json(ROOT / "evals" / "fixed-tasks" / "tasks.json")
    for task in fixed["tasks"]:
        assertions += 1
        if (task["leaf"], task["source_case"]) not in eval_index:
            failures.append({"task": task["id"], "reason": "missing fixed-task source case"})

    baseline_data = load_json(ROOT / "evals" / "baselines" / "static-practice-baselines.json")
    required = set(baseline_data["required_practices"])
    baseline_results = []
    for baseline in baseline_data["baselines"]:
        supported = set(baseline["supports"])
        assertions += 1
        if not supported <= required:
            failures.append({"baseline": baseline["id"], "reason": "unknown practice in supports"})
        baseline_results.append({"id": baseline["id"], "supported": len(supported), "required": len(required), "coverage": round(len(supported) / len(required), 4)})
    rigwright = next(item for item in baseline_data["baselines"] if item["id"] == "rigwright-candidate")
    assertions += 1
    if set(rigwright["supports"]) != required:
        failures.append({"baseline": "rigwright-candidate", "reason": "candidate static contract misses required practices"})

    priority_data = load_json(ROOT / "evals" / "lifecycle-priority" / "cases.json")
    base = {record["id"]: record for record in priority_data["base_records"]}
    priority_results = []
    for case in priority_data["cases"]:
        pool = dict(base)
        for record in case.get("extra_records", []):
            pool[record["id"]] = record
        records = [pool[record_id] for record_id in case["records"]]
        actual = select_owner(records, case["context"])
        passed = actual["status"] == case["expected_status"] and actual.get("selected") == case.get("expected_selected")
        assertions += 1
        if not passed:
            failures.append({"priority_case": case["id"], "expected": {"status": case["expected_status"], "selected": case.get("expected_selected")}, "actual": actual})
        priority_results.append({"id": case["id"], "status": "PASS" if passed else "FAIL", "actual": actual})

    normal_build = load_json(ROOT / "artifacts" / "build-normal" / "build-report.json")
    assertions += 1
    if normal_build["included"] or len(normal_build["excluded"]) != 7:
        failures.append({"build": "normal", "reason": "candidate records appeared in normal adapter build"})
    candidate_build = load_json(ROOT / "artifacts" / "build" / "build-report.json")
    assertions += 1
    if len(candidate_build["included"]) != 7:
        failures.append({"build": "candidate-sandbox", "reason": "explicit sandbox build missing leaves"})

    for restore_report in sorted((ROOT / "artifacts" / "archive-proposals").glob("*/restore-test/report.json")):
        restore = load_json(restore_report)
        assertions += 1
        if restore.get("status") != "PASS":
            failures.append({"archive_restore": restore})

    runtime_summary_path = ROOT / "artifacts" / "runtime-evals" / "runtime-summary.json"
    if runtime_summary_path.is_file():
        runtime_summary = load_json(runtime_summary_path)
        runtime_forward_tests = {
            "status": "EXECUTED_WITH_LIMITATIONS_NOT_PROMOTED",
            "approval": runtime_summary.get("owner_approval"),
            "fresh_agents_used": True,
            "owner_human_review_complete": runtime_summary.get("owner_human_review_complete", False),
            "promotion_authorized": runtime_summary.get("promotion_authorized", False),
            "report": runtime_summary_path.relative_to(ROOT).as_posix(),
        }
    else:
        runtime_forward_tests = {
            "status": "BLOCKED_OWNER_GATE",
            "reason": "Provider execution requires separate owner approval and a completed runtime-summary artifact.",
            "fresh_agents_used": False,
        }

    payload = {
        "schema_version": 1,
        "status": "PASS" if not failures else "FAIL",
        "assertions": assertions,
        "leaf_results": leaf_results,
        "near_miss_cases": near_misses,
        "fixed_task_count": len(fixed["tasks"]),
        "static_baselines": baseline_results,
        "static_baseline_limitation": baseline_data["measurement"],
        "priority_results": priority_results,
        "runtime_forward_tests": runtime_forward_tests,
        "failures": failures,
    }
    target = output or ROOT / "artifacts" / "validation" / "offline-evals.json"
    write_json(target, payload)
    if failures:
        raise SystemExit(f"offline evals failed with {len(failures)} failure(s); see {target}")
    return payload


if __name__ == "__main__":
    result = run()
    print(f"offline evals passed: {result['assertions']} assertions, {result['near_miss_cases']} near misses, {result['fixed_task_count']} fixed tasks")

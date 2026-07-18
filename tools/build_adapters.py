from __future__ import annotations

import argparse
import shutil
from pathlib import Path
from typing import Any

try:
    from .common import ROOT, deterministic_zip, file_manifest, iter_files, load_json, safe_clear, write_json, yaml_quote
except ImportError:  # direct script execution
    from common import ROOT, deterministic_zip, file_manifest, iter_files, load_json, safe_clear, write_json, yaml_quote


def render_skill(record: dict[str, Any], surface: str) -> str:
    frontmatter = ["---", f"name: {record['id']}", f"description: {yaml_quote(record['description'])}", "---", ""]
    body = [
        f"# {record['display_name']}",
        "",
        record["intent"],
        "",
        "## Outcome",
        "",
        record["outcome"],
        "",
        "## Permission boundary",
        "",
        f"Side-effect class: `{record['permissions']['side_effect_class']}`.",
        f"Allowed scope: {record['permissions']['allowed_scope']}.",
    ]
    if record["permissions"]["owner_gates"]:
        body.extend(["", "Owner approval remains required for:"] + [f"- {item}" for item in record["permissions"]["owner_gates"]])
    body.extend(["", "## Procedure", ""])
    body.extend([f"{index}. {instruction}" for index, instruction in enumerate(record["instructions"], start=1)])
    body.extend(["", "## Non-goals", ""] + [f"- {item}" for item in record["non_goals"]])
    body.extend([
        "",
        "## Evaluation",
        "",
        "Read `evals/evals.json` for this leaf's positive cases, near misses, expected behavior, and safety decisions.",
        "",
        f"This is a generated `{surface}` adapter. Edit the neutral `src/skills/{record['id']}/skill.json` source instead of this file.",
        "",
    ])
    return "\n".join(frontmatter + body)


def render_openai_yaml(record: dict[str, Any]) -> str:
    short = record["display_name"]
    if len(short) < 25:
        short = f"Use {short} workflow"
    short = short[:64]
    default_prompt = f"Use ${record['id']} for this bounded proposal task."
    return "\n".join([
        "interface:",
        f"  display_name: {yaml_quote(record['display_name'])}",
        f"  short_description: {yaml_quote(short)}",
        f"  default_prompt: {yaml_quote(default_prompt)}",
        "policy:",
        "  allow_implicit_invocation: false",
        "",
    ])


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def eligible(record: dict[str, Any], mode: str) -> bool:
    state = record["lifecycle"]["state"]
    if mode == "normal":
        return state == "current-authorized"
    return state in {"current-authorized", "candidate-sandbox"}


def build(mode: str, output_root: Path) -> dict[str, Any]:
    if mode not in {"normal", "candidate-sandbox"}:
        raise ValueError(f"unsupported build mode: {mode}")
    output_root = output_root.resolve()
    safe_clear(output_root, ROOT / "artifacts")
    output_root.mkdir(parents=True, exist_ok=True)
    release = load_json(ROOT / "config" / "release.json")
    version = release["version"]
    author = release["author"]
    records = [load_json(path) for path in sorted((ROOT / "src" / "skills").glob("*/skill.json"))]
    included = [record for record in records if eligible(record, mode)]
    excluded = [{"id": record["id"], "state": record["lifecycle"]["state"]} for record in records if record not in included]
    report: dict[str, Any] = {
        "schema_version": 1,
        "mode": mode,
        "release": {
            "version": version,
            "release_state": release["release_state"],
            "author": author,
            "license": release["license"],
        },
        "included": [record["id"] for record in included],
        "excluded": excluded,
        "packages": {},
    }
    if not included:
        write_json(output_root / "build-report.json", report)
        return report

    notice = (
        "# Candidate sandbox package\n\n"
        f"Rigwright {version} is a pre-release candidate. "
        "This generated package contains candidate-sandbox records for offline evaluation only. "
        "It is not authorized for installation, activation, marketplace publication, or normal discovery.\n"
    )
    for surface in ("claude-code", "codex"):
        plugin_root = output_root / surface / "rigwright"
        write_text(plugin_root / "CANDIDATE-NOTICE.md", notice)
        shutil.copyfile(ROOT / "LICENSE", plugin_root / "LICENSE")
        if surface == "claude-code":
            write_json(plugin_root / ".claude-plugin" / "plugin.json", {
                "name": "rigwright",
                "version": version,
                "description": "Candidate-sandbox Rigwright atomic authoring workflows.",
                "author": {"name": author},
            })
        else:
            write_json(plugin_root / ".codex-plugin" / "plugin.json", {
                "name": "rigwright",
                "version": version,
                "description": "Candidate-sandbox Rigwright atomic authoring workflows.",
                "author": {"name": author},
                "skills": "./skills/",
                "interface": {
                    "displayName": "Rigwright",
                    "shortDescription": "Atomic cross-surface authoring workflows",
                    "longDescription": "Creates, evaluates, migrates, prioritizes, and archive-qualifies atomic skill and plugin proposals.",
                    "developerName": author,
                    "category": "Productivity",
                    "capabilities": [],
                    "defaultPrompt": ["Route this authoring task to one atomic Rigwright leaf."]
                }
            })
        for record in included:
            skill_root = plugin_root / "skills" / record["id"]
            write_text(skill_root / "SKILL.md", render_skill(record, surface))
            (skill_root / "evals").mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / "src" / "skills" / record["id"] / "evals" / "evals.json", skill_root / "evals" / "evals.json")
            if surface == "codex":
                write_text(skill_root / "agents" / "openai.yaml", render_openai_yaml(record))
        _, tree_sha, total_bytes = file_manifest(plugin_root)
        zip_path = output_root / "packages" / f"rigwright-{surface}.zip"
        zip_sha = deterministic_zip(plugin_root, zip_path)
        report["packages"][surface] = {
            "root": plugin_root.relative_to(output_root).as_posix(),
            "file_count": len(iter_files(plugin_root)),
            "total_bytes": total_bytes,
            "tree_sha256": tree_sha,
            "zip": zip_path.relative_to(output_root).as_posix(),
            "zip_sha256": zip_sha,
        }
    write_json(output_root / "build-report.json", report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", required=True, choices=["normal", "candidate-sandbox"])
    parser.add_argument("--output-root", type=Path, default=ROOT / "artifacts" / "build")
    args = parser.parse_args()
    report = build(args.mode, args.output_root)
    print(f"adapter build {args.mode}: {len(report['included'])} included, {len(report['excluded'])} excluded")


if __name__ == "__main__":
    main()

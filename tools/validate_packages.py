from __future__ import annotations

import json
import re
import zipfile
from pathlib import Path
from typing import Any

try:
    from .common import ROOT, iter_files, load_json, write_json
except ImportError:  # direct script execution
    from common import ROOT, iter_files, load_json, write_json


def parse_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        raise ValueError(f"missing frontmatter: {path}")
    result: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, raw = line.split(":", 1)
        raw = raw.strip()
        if raw.startswith('"'):
            result[key] = json.loads(raw)
        else:
            result[key] = raw
    return result


def validate(build_root: Path | None = None, output: Path | None = None) -> dict[str, Any]:
    root = (build_root or ROOT / "artifacts" / "build").resolve()
    errors: list[str] = []
    checks = 0
    release = load_json(ROOT / "config" / "release.json")
    expected_release = {
        "schema_version": 1,
        "product": "Rigwright",
        "version": "0.2.0",
        "release_state": "pre-release",
        "author": "Rahul Krishna",
        "copyright_holder": "Rahul Krishna",
        "license": "MIT",
        "canonical_host_url": "https://gitlab.com/krahul02004/Rigwright",
        "public_security_reporting_channel": None,
        "outward_actions_authorized": False,
    }
    checks += 1
    if release != expected_release:
        errors.append("release metadata does not match the approved 0.2.0 source candidate")
    checks += 1
    if (ROOT / "VERSION").read_text(encoding="utf-8").strip() != release.get("version"):
        errors.append("VERSION does not match config/release.json")
    license_bytes = (ROOT / "LICENSE").read_bytes()
    checks += 1
    if b"MIT License" not in license_bytes or b"Copyright (c) 2026 Rahul Krishna" not in license_bytes:
        errors.append("root MIT license metadata mismatch")
    version = release.get("version")
    author = release.get("author")
    expected = sorted(path.name for path in (ROOT / "src" / "skills").iterdir() if path.is_dir())
    for surface in ("claude-code", "codex"):
        plugin = root / surface / "rigwright"
        checks += 1
        if not (plugin / "CANDIDATE-NOTICE.md").is_file():
            errors.append(f"{surface}: missing candidate notice")
        manifest_path = plugin / (".claude-plugin/plugin.json" if surface == "claude-code" else ".codex-plugin/plugin.json")
        checks += 1
        try:
            manifest = load_json(manifest_path)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{surface}: invalid manifest: {exc}")
            continue
        checks += 1
        if manifest.get("name") != "rigwright":
            errors.append(f"{surface}: manifest name mismatch")
        checks += 1
        if manifest.get("version") != version:
            errors.append(f"{surface}: manifest version must match config/release.json")
        checks += 1
        if manifest.get("author") != {"name": author}:
            errors.append(f"{surface}: manifest author mismatch")
        if surface == "claude-code":
            pass
        else:
            checks += 1
            if not re.fullmatch(r"\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?", manifest.get("version", "")):
                errors.append("codex: strict semver required")
            checks += 1
            unsupported = set(manifest) & {"hooks", "commands", "agents"}
            if unsupported:
                errors.append(f"codex: unsupported future fields present: {sorted(unsupported)}")
            required_interface = {"displayName", "shortDescription", "longDescription", "developerName", "category", "capabilities", "defaultPrompt"}
            checks += 1
            if not required_interface.issubset(manifest.get("interface", {})):
                errors.append("codex: required interface metadata missing")
            checks += 1
            if manifest.get("interface", {}).get("developerName") != author:
                errors.append("codex: developerName mismatch")
        checks += 1
        if not (plugin / "LICENSE").is_file() or (plugin / "LICENSE").read_bytes() != license_bytes:
            errors.append(f"{surface}: packaged LICENSE must exactly match the root LICENSE")
        skill_dirs = sorted(path.name for path in (plugin / "skills").iterdir() if path.is_dir())
        checks += 1
        if skill_dirs != expected:
            errors.append(f"{surface}: skill set mismatch")
        for skill_id in skill_dirs:
            skill_root = plugin / "skills" / skill_id
            try:
                fm = parse_frontmatter(skill_root / "SKILL.md")
            except Exception as exc:  # noqa: BLE001
                errors.append(str(exc))
                continue
            checks += 1
            if set(fm) != {"name", "description"} or fm.get("name") != skill_id or not fm.get("description"):
                errors.append(f"{surface}:{skill_id}: frontmatter must contain only name and description")
            checks += 1
            evals = load_json(skill_root / "evals" / "evals.json")
            if evals.get("skill_name") != skill_id:
                errors.append(f"{surface}:{skill_id}: eval copy mismatch")
            if surface == "codex":
                checks += 1
                agent_text = (skill_root / "agents" / "openai.yaml").read_text(encoding="utf-8")
                if f"Use ${skill_id}" not in agent_text or "allow_implicit_invocation: false" not in agent_text:
                    errors.append(f"codex:{skill_id}: candidate UI/invocation metadata invalid")
        allowed_fixed = {
            "CANDIDATE-NOTICE.md",
            "LICENSE",
            ".claude-plugin/plugin.json" if surface == "claude-code" else ".codex-plugin/plugin.json",
        }
        package_files = iter_files(plugin)
        for package_file in package_files:
            relative = package_file.relative_to(plugin).as_posix()
            allowed_leaf = re.fullmatch(
                r"skills/[^/]+/(?:SKILL\.md|evals/evals\.json|agents/openai\.yaml)",
                relative,
            )
            checks += 1
            if relative not in allowed_fixed and not allowed_leaf:
                errors.append(f"{surface}: forbidden public-package member: {relative}")
            if surface == "claude-code" and relative.endswith("/agents/openai.yaml"):
                errors.append(f"{surface}: Codex-only agent metadata leaked into package: {relative}")
            payload = package_file.read_bytes()
            checks += 2
            if re.search(rb"(?i)[A-Z]:[\\/]Users[\\/][^\\/\s]+", payload):
                errors.append(f"{surface}: Windows home path in public-package candidate: {relative}")
            if re.search(rb"/Users/[^/\s]+", payload):
                errors.append(f"{surface}: macOS home path in public-package candidate: {relative}")
        zip_path = root / "packages" / f"rigwright-{surface}.zip"
        checks += 1
        if not zip_path.is_file():
            errors.append(f"{surface}: package ZIP missing")
        else:
            with zipfile.ZipFile(zip_path) as archive:
                names = archive.namelist()
                expected_names = [path.relative_to(plugin).as_posix() for path in package_files]
                checks += 1
                if names != expected_names:
                    errors.append(f"{surface}: ZIP member order or membership differs from the approved package tree")
                for package_file, name in zip(package_files, names, strict=False):
                    checks += 1
                    if archive.read(name) != package_file.read_bytes():
                        errors.append(f"{surface}: ZIP member bytes differ from package tree: {name}")
    payload = {"schema_version": 1, "status": "PASS" if not errors else "FAIL", "checks": checks, "errors": errors}
    target = output or ROOT / "artifacts" / "validation" / "package-validation.json"
    write_json(target, payload)
    if errors:
        raise SystemExit(f"package validation failed with {len(errors)} error(s); see {target}")
    return payload


if __name__ == "__main__":
    result = validate()
    print(f"package validation passed: {result['checks']} checks")

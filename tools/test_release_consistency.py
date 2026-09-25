"""Keep source release language aligned without claiming artifact provenance."""
from __future__ import annotations

import json
import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ReleaseConsistencyTests(unittest.TestCase):
    def test_0_2_0_release_and_candidate_skills_are_consistent(self) -> None:
        project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
        release = json.loads((ROOT / "config" / "release.json").read_text(encoding="utf-8"))
        version_file = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        status = (ROOT / "STATUS.md").read_text(encoding="utf-8")
        changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        readiness = (ROOT / "docs" / "public" / "release-readiness.md").read_text(encoding="utf-8")
        package_init = (ROOT / "tools" / "__init__.py").read_text(encoding="utf-8")
        adapter_policies = "\n".join(
            (ROOT / "adapters" / surface / "adapter.json").read_text(encoding="utf-8")
            for surface in ("claude-code", "codex")
        )
        builder = (ROOT / "tools" / "build_adapters.py").read_text(encoding="utf-8")

        self.assertEqual("0.2.0", project["version"])
        self.assertEqual(project["version"], release["version"])
        self.assertEqual(project["version"], version_file)
        self.assertIn('__version__ = "0.2.0"', package_init)
        self.assertEqual(
            release["canonical_host_url"],
            "https://gitlab.com/krahul02004/Rigwright",
        )
        self.assertEqual(project["urls"]["Repository"], release["canonical_host_url"])
        self.assertIn(f"version `{project['version']}`", status)
        self.assertIn(f"[`rigwright` {project['version']}]", status)
        self.assertIn("## [Unreleased]\n\n## [0.2.0] - 2026-07-19", changelog)
        self.assertIn("## [0.1.0] - 2026-07-18", changelog)
        self.assertNotIn("compare/v0.1.0", changelog)
        self.assertNotIn("no public semantic release yet", changelog.lower())
        self.assertIn("PyPI publishes the offline CLI at `0.2.0`", readiness)
        self.assertIn("candidate-sandbox proposals", readiness)
        self.assertIn("Never create a retroactive `v0.1.0` tag or Release", readiness)
        self.assertNotIn("PyPI still carries", readiness)
        self.assertEqual(2, adapter_policies.count("derive the selected source version from config/release.json"))
        self.assertIn('version = release["version"]', builder)


if __name__ == "__main__":
    unittest.main()

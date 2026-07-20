"""Keep source release language aligned without claiming artifact provenance."""
from __future__ import annotations

import json
import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ReleaseConsistencyTests(unittest.TestCase):
    def test_published_cli_state_is_consistent_and_provenance_limited(self) -> None:
        project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
        release = json.loads((ROOT / "config" / "release.json").read_text(encoding="utf-8"))
        version_file = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        status = (ROOT / "STATUS.md").read_text(encoding="utf-8")
        changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        readiness = (ROOT / "docs" / "public" / "release-readiness.md").read_text(encoding="utf-8")

        self.assertEqual(project["version"], release["version"])
        self.assertEqual(project["version"], version_file)
        self.assertEqual(
            release["canonical_host_url"],
            "https://gitlab.com/krahul02004/Rigwright",
        )
        self.assertEqual(project["urls"]["Repository"], release["canonical_host_url"])
        self.assertIn(f"version `{project['version']}`", status)
        self.assertIn("published to PyPI", status)
        self.assertIn("## [Unreleased]", changelog)
        self.assertIn("## [0.1.0] - 2026-07-18", changelog)
        self.assertIn("No matching git tag or GitLab Release exists", changelog)
        self.assertIn("artifact-to-commit provenance has not been established", changelog)
        self.assertNotIn("no public semantic release yet", changelog.lower())
        self.assertNotIn("`0.1.0` remains untagged and unreleased", changelog)
        self.assertIn("offline CLI `0.1.0` has been uploaded to PyPI", readiness)
        self.assertIn("no matching tag or GitLab Release exists", readiness)
        self.assertNotIn("no registry upload has been performed", readiness.lower())
        self.assertNotIn("no canonical host owner", readiness.lower())
        self.assertNotIn("first push", readiness.lower())


if __name__ == "__main__":
    unittest.main()

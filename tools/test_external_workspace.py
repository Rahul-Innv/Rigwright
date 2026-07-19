"""Safety regressions for the external workspace write path."""
from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import external_workspace


DESCRIPTION = "Check one input for a required marker."
OUTCOME = "Report whether the required marker exists."
EVIDENCE_DATE = "2026-07-19"


class ExternalWorkspaceTests(unittest.TestCase):
    def _make_directory_indirection(self, link: Path, target: Path) -> None:
        if os.name == "nt":
            completed = subprocess.run(
                ["cmd.exe", "/d", "/c", "mklink", "/J", str(link), str(target)],
                capture_output=True,
                text=True,
                check=False,
            )
            if completed.returncode != 0:
                self.skipTest(
                    "host cannot create a Windows junction: "
                    f"exit {completed.returncode}: {completed.stderr.strip()}"
                )
        else:
            try:
                link.symlink_to(target, target_is_directory=True)
            except OSError as exc:
                self.skipTest(f"host cannot create a directory symlink: {exc}")

    def test_marker_is_created_once_and_skill_overwrite_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary) / "workspace"
            external_workspace.scaffold(workspace, "marker-check", DESCRIPTION, OUTCOME, EVIDENCE_DATE)
            marker = workspace / external_workspace.MARKER_NAME

            with patch.object(external_workspace, "write_json", wraps=external_workspace.write_json) as writer:
                external_workspace.scaffold(workspace, "header-check", DESCRIPTION, OUTCOME, EVIDENCE_DATE)
            written_paths = [call.args[0] for call in writer.call_args_list]
            self.assertNotIn(marker.resolve(), [path.resolve() for path in written_paths])

            with self.assertRaisesRegex(ValueError, "refusing to overwrite"):
                external_workspace.scaffold(workspace, "marker-check", DESCRIPTION, OUTCOME, EVIDENCE_DATE)

    def test_symlink_or_junction_escape_is_refused_without_external_writes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            workspace = root / "workspace"
            outside = root / "outside"
            workspace.mkdir()
            outside.mkdir()
            indirect = workspace / "src"
            self._make_directory_indirection(indirect, outside)

            with self.assertRaisesRegex(ValueError, "indirect workspace path"):
                external_workspace.scaffold(workspace, "escape-check", DESCRIPTION, OUTCOME, EVIDENCE_DATE)
            self.assertEqual(list(outside.iterdir()), [])

    def test_nonexistent_workspace_below_indirect_ancestor_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            safe = root / "safe"
            outside = root / "outside"
            safe.mkdir()
            outside.mkdir()
            indirect_parent = safe / "link-to-outside"
            self._make_directory_indirection(indirect_parent, outside)
            requested = indirect_parent / "new-workspace"

            with self.assertRaisesRegex(ValueError, "indirect workspace ancestor"):
                external_workspace.scaffold(requested, "escape-check", DESCRIPTION, OUTCOME, EVIDENCE_DATE)
            self.assertFalse((outside / "new-workspace").exists())

            result = external_workspace.validate(requested)
            self.assertEqual(result["status"], "FAIL")
            self.assertTrue(any("indirect workspace ancestor" in error for error in result["errors"]))
            self.assertFalse((outside / "new-workspace").exists())

    def test_malformed_workspace_is_rejected_without_crashing(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary) / "workspace"
            external_workspace.write_json(workspace / external_workspace.MARKER_NAME, external_workspace.MARKER)
            external_workspace.write_json(workspace / "src" / "skills" / "broken-skill" / "skill.json", [])

            result = external_workspace.validate(workspace)

            self.assertEqual(result["status"], "FAIL")
            self.assertTrue(any("skill.json must contain an object" in error for error in result["errors"]))


if __name__ == "__main__":
    unittest.main()

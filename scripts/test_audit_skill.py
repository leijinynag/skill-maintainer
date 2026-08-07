#!/usr/bin/env python3
"""Tests for the deterministic skill audit."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import audit_skill


class AuditSkillTests(unittest.TestCase):
    def make_skill(self, body: str, name: str = "demo-skill") -> Path:
        root = Path(self.tempdir.name) / name
        root.mkdir(parents=True)
        (root / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: A test skill.\n---\n\n{body}\n",
            encoding="utf-8",
        )
        return root

    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_valid_skill_has_required_report_shape(self) -> None:
        root = self.make_skill("# Demo\n\nUse [the guide](references/guide.md).\n")
        (root / "references").mkdir()
        (root / "references/guide.md").write_text("# Guide\n", encoding="utf-8")
        report = audit_skill.build_report(root, "remove duplicate prose", None)
        self.assertEqual(report["validation"]["errors"], 0)
        self.assertEqual(report["change_ledger"]["delete"], [])
        self.assertIn("risk", report)

    def test_missing_skill_file_is_error(self) -> None:
        root = Path(self.tempdir.name) / "demo-skill"
        root.mkdir()
        report = audit_skill.build_report(root, "", None)
        self.assertIn("target.skill_missing", {item["id"] for item in report["findings"]})

    def test_name_mismatch_is_error(self) -> None:
        root = self.make_skill("# Demo\n", name="other-name")
        (root / "SKILL.md").write_text(
            "---\nname: wrong-name\ndescription: A test skill.\n---\n\n# Demo\n",
            encoding="utf-8",
        )
        report = audit_skill.build_report(root, "", None)
        self.assertIn("frontmatter.name_mismatch", {item["id"] for item in report["findings"]})

    def test_missing_frontmatter_is_error(self) -> None:
        root = Path(self.tempdir.name) / "demo-skill"
        root.mkdir()
        (root / "SKILL.md").write_text("# Demo\n", encoding="utf-8")
        report = audit_skill.build_report(root, "", None)
        ids = {item["id"] for item in report["findings"]}
        self.assertIn("frontmatter.missing", ids)

    def test_multiline_frontmatter_description_is_parsed(self) -> None:
        root = Path(self.tempdir.name) / "demo-skill"
        root.mkdir()
        (root / "SKILL.md").write_text(
            "---\n"
            "name: demo-skill\n"
            "description: >\n"
            "  A multiline description that should be accepted.\n"
            "  It continues on the next line.\n"
            "---\n\n"
            "# Demo\n",
            encoding="utf-8",
        )
        fields, findings = audit_skill.parse_frontmatter(root / "SKILL.md")
        self.assertIn("multiline description", fields["description"])
        self.assertNotIn("frontmatter.unparsed", {item["id"] for item in findings})

    def test_prose_tokens_and_context_files_are_not_broken_references(self) -> None:
        root = self.make_skill(
            "Use `MUST` only for contracts. Read `AGENTS.md` when it exists.\n"
            "Use `scripts/audit_skill.py` for deterministic checks.\n"
        )
        (root / "scripts").mkdir()
        (root / "scripts/audit_skill.py").write_text("# test fixture\n", encoding="utf-8")
        report = audit_skill.build_report(root, "", None)
        self.assertNotIn("references.broken", {item["id"] for item in report["findings"]})

    def test_broken_reference_is_reported(self) -> None:
        root = self.make_skill("Read [missing](references/missing.md).\n")
        report = audit_skill.build_report(root, "", None)
        self.assertIn("references.broken", {item["id"] for item in report["findings"]})

    def test_duplicate_rule_and_conflict_are_reported(self) -> None:
        root = self.make_skill(
            "- The agent MUST preserve the original output contract.\n"
            "- The agent MUST preserve the original output contract.\n"
            "- The agent MUST preserve the original output contract.\n"
            "- The agent MUST NOT preserve the original output contract.\n"
        )
        report = audit_skill.build_report(root, "", None)
        ids = {item["id"] for item in report["findings"]}
        self.assertIn("content.duplicate_rule", ids)
        self.assertIn("content.possible_conflict", ids)

    def test_append_only_diff_is_reported(self) -> None:
        root = self.make_skill("# Demo\n")
        subprocess.run(["git", "-C", str(root), "init", "-q"], check=True)
        subprocess.run(["git", "-C", str(root), "config", "user.email", "test@example.com"], check=True)
        subprocess.run(["git", "-C", str(root), "config", "user.name", "Test"], check=True)
        subprocess.run(["git", "-C", str(root), "add", "."], check=True)
        subprocess.run(["git", "-C", str(root), "commit", "-qm", "initial"], check=True)
        (root / "SKILL.md").write_text(
            (root / "SKILL.md").read_text(encoding="utf-8") + "\n" + "\n".join(f"- New rule {i}" for i in range(50)) + "\n",
            encoding="utf-8",
        )
        diff = subprocess.check_output(
            ["git", "-C", str(root), "diff", "--numstat", "HEAD", "--"],
            text=True,
        )
        self.assertTrue(diff.strip(), diff)
        report = audit_skill.build_report(root, "add a rule", "HEAD")
        self.assertIn("complexity.append_only", {item["id"] for item in report["findings"]})

    def test_behavior_request_is_medium_or_high_risk(self) -> None:
        root = self.make_skill("# Demo\n")
        report = audit_skill.build_report(root, "change the output fallback behavior", None)
        self.assertEqual(report["risk"]["level"], "medium")

    def test_safety_request_is_high_risk(self) -> None:
        root = self.make_skill("# Demo\n")
        report = audit_skill.build_report(root, "change the write confirmation rule", None)
        self.assertEqual(report["risk"]["level"], "high")

    def test_cli_writes_json_report(self) -> None:
        root = self.make_skill("# Demo\n")
        output = Path(self.tempdir.name) / ".skill-maintainer/report.json"
        result = subprocess.run(
            [sys.executable, str(Path(audit_skill.__file__)), str(root), "--json-out", str(output)],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0)
        data = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(data["report_version"], "0.1.0")
        self.assertEqual(data["target"]["name"], "demo-skill")

    def test_cli_default_report_path(self) -> None:
        root = self.make_skill("# Demo\n")
        result = subprocess.run(
            [sys.executable, str(Path(audit_skill.__file__)), str(root)],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0)
        report_path = root / ".skill-maintainer/audit-report.json"
        self.assertTrue(report_path.exists())
        self.assertIn(str(report_path), result.stdout)

    def test_invalid_target_returns_exit_code_two(self) -> None:
        root = Path(self.tempdir.name) / "missing"
        result = subprocess.run(
            [sys.executable, str(Path(audit_skill.__file__)), str(root)],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 2)

    def test_invalid_git_ref_returns_exit_code_two(self) -> None:
        root = self.make_skill("# Demo\n")
        result = subprocess.run(
            [
                sys.executable,
                str(Path(audit_skill.__file__)),
                str(root),
                "--git-ref",
                "does-not-exist",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 2)


if __name__ == "__main__":
    unittest.main()

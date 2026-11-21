"""Regression tests for calculator permissions and first-run guidance.

A skill's `allowed-tools` setting did not grant calculator permission when
tested, and widening permissions is never the fix. These tests keep the
guidance consistent and keep every skill and agent from widening access.
Standard library only.
"""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CALCULATOR_SKILLS = [
    "unit-economics", "scenario-comparison", "pricing-analysis", "go-to-market",
]


def read(relative):
    return (ROOT / relative).read_text(encoding="utf-8")


class TestCalculatorPermissionGuidance(unittest.TestCase):

    def test_each_calculator_skill_explains_the_permission_request(self):
        for name in CALCULATOR_SKILLS:
            text = read(f"skills/{name}/SKILL.md")
            self.assertIn("### Permission to run the calculator", text, name)
            self.assertIn("Show the exact command you will run.", text, name)
            self.assertIn("one at a time", text, name)
            self.assertIn("a refused command cancels any command started "
                          "alongside it", text, name)
            self.assertIn("Never ask the user to allow `python3` or `Bash` "
                          "in general", text, name)

    def test_each_calculator_skill_forbids_working_around_a_refusal(self):
        for name in CALCULATOR_SKILLS:
            text = read(f"skills/{name}/SKILL.md")
            self.assertIn("do not run the arithmetic another way", text, name)
            self.assertIn("manual calculation, not engine-validated", text,
                          name)
            self.assertIn("Never describe a figure as engine-validated", text,
                          name)

    def test_permission_guidance_is_identical_across_skills(self):
        blocks = set()
        for name in CALCULATOR_SKILLS:
            text = read(f"skills/{name}/SKILL.md")
            match = re.search(
                r"### Permission to run the calculator\n.*?\n\n(?=When )",
                text, re.S)
            self.assertIsNotNone(match, name)
            blocks.add(match.group(0))
        self.assertEqual(len(blocks), 1)


class TestNoPermissionWidening(unittest.TestCase):

    def test_no_skill_or_agent_sets_allowed_tools(self):
        for path in sorted((ROOT / "skills").glob("*/SKILL.md")) + sorted(
                (ROOT / "agents").glob("*.md")):
            head = path.read_text(encoding="utf-8").split("\n---\n", 1)[0]
            self.assertNotRegex(head, r"(?m)^allowed-tools\s*:", path.name)

    def test_no_document_tells_users_to_allow_bash_or_python_broadly(self):
        pattern = re.compile(
            r"Bash\(\s*(python3?)?\s*(:\s*)?\*?\s*\)|Bash\(\*\)|"
            r"Bash\(python3?:\*\)")
        for path in list((ROOT / "skills").glob("*/SKILL.md")) + [
                ROOT / "README.md"] + list((ROOT / "docs").glob("*.md")):
            self.assertIsNone(pattern.search(
                path.read_text(encoding="utf-8")), path.name)

    def test_readme_gives_the_scoped_allow_rule(self):
        text = read("README.md")
        self.assertIn(
            'Bash(python3 "/path/to/venturine/scripts/calculate.py" *)', text)
        self.assertIn(
            'Bash(python3 "/path/to/venturine/scripts/forecast.py" *)', text)
        self.assertIn("Do not allow `python3` or `Bash` in general", text)
        self.assertIn("manual calculation, not engine-validated", text)


class TestReadmeFirstRunGuidance(unittest.TestCase):

    def setUp(self):
        self.text = read("README.md")

    def test_readme_states_audience_and_workflow(self):
        self.assertIn("## Who it is for", self.text)
        self.assertIn("## A complete analysis, step by step", self.text)
        for skill in ("venture-intake", "business-report", "report-editor"):
            self.assertIn(f"`{skill}`", self.text)

    def test_readme_points_to_issue_forms_and_private_security_reports(self):
        self.assertIn("## Help, bugs and feature requests", self.text)
        for form in ("bug_report.yml", "feature_request.yml",
                     "evidence_or_calculation_issue.yml"):
            self.assertIn(f"template={form}", self.text)
            self.assertTrue(
                (ROOT / ".github" / "ISSUE_TEMPLATE" / form).is_file(), form)
        self.assertIn("do not use a public issue", self.text.lower())


class TestIntakeDoesNotEndMultiStepRequests(unittest.TestCase):
    """A multi-step request stopped after venture-intake in two native runs."""

    def test_intake_continues_when_later_steps_were_requested(self):
        text = read("skills/venture-intake/SKILL.md")
        self.assertIn("do not end your turn after the intake", text)
        self.assertIn("carry straight on with the next step they named", text)
        self.assertIn("Stop and ask only when a missing fact makes that step "
                      "impossible", text)


if __name__ == "__main__":
    unittest.main()

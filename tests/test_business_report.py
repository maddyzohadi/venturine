"""Tests for the Phase 4 components: the business-report skill and the
report-editor agent. Standard library only. The shared inventory, handoff
and untrusted-content rules are enforced in the other test modules; these
cover what is specific to Phase 4."""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = (ROOT / "skills/business-report/SKILL.md").read_text(encoding="utf-8")
AGENT = (ROOT / "agents/report-editor.md").read_text(encoding="utf-8")


def tools(text):
    block = text.split("tools:", 1)[1].split("---", 1)[0]
    return re.findall(r"^\s+- (\S+)", block, re.M)


class TestReportEditorAgent(unittest.TestCase):

    def test_it_is_read_only_with_no_web_and_no_shell(self):
        self.assertEqual(tools(AGENT), ["Read", "Glob", "Grep"])

    def test_it_covers_every_review_area(self):
        for needle in ("calculation receipt", "contradictions",
                       "unsupported conclusions", "evidence labels",
                       "NOT CHECKED"):
            self.assertIn(needle, AGENT, needle)

    def test_it_does_not_invent_or_repair(self):
        self.assertIn("Do not invent facts", AGENT)
        self.assertIn("Do not repair a figure", AGENT)

    def test_a_clean_verdict_is_not_an_audit(self):
        self.assertIn("does not make the report AUDITED", AGENT)


class TestBusinessReportSkill(unittest.TestCase):

    def test_it_adds_nothing_and_recomputes_nothing(self):
        self.assertIn("You do not research, you do not calculate", SKILL)
        self.assertIn("Do not recompute", SKILL)
        self.assertIn("Do not upgrade a label", SKILL)
        self.assertIn("manual calculation, not engine-validated", SKILL)

    def test_it_ties_status_to_the_auditor_not_the_editor(self):
        self.assertIn("Mark the report AUDITED only when the "
                      "`evidence-auditor` actually ran", SKILL)
        self.assertIn("The report-editor does not make a report AUDITED",
                      SKILL)

    def test_it_names_the_components_it_integrates(self):
        for name in ("idea-validator", "market-intelligence",
                     "competitor-intelligence", "unit-economics",
                     "customer-discovery", "go-to-market", "report-editor",
                     "evidence-audit"):
            self.assertIn(name, SKILL, name)

    def test_it_has_no_pre_approved_tools(self):
        self.assertNotIn("allowed-tools", SKILL)


class TestCitationReferences(unittest.TestCase):
    """A native run cited a contribution-margin figure to C2 instead of C1,
    and the editor missed it. Both components must now check ids."""

    def test_the_skill_cites_each_figure_to_its_own_calculation(self):
        self.assertIn("never as another calculation", SKILL)
        self.assertIn("re-check every `E` and `C` reference", SKILL)

    def test_the_editor_checks_citation_references(self):
        self.assertIn("### Citation References", AGENT)
        self.assertIn("must not be cited to a different calculation", AGENT)
        self.assertIn("wrong, missing or dangling reference", AGENT)
        self.assertIn("claim by claim, not id by id", AGENT)


if __name__ == "__main__":
    unittest.main()

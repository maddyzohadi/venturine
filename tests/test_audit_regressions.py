"""Deterministic regression tests for the audit follow-up (M1-M9).

Standard library only. No network access. Git is used only to confirm that
.gitignore does not hide tracked files.
"""

import json
import re
import subprocess
import sys
import unittest
from decimal import Decimal
from pathlib import Path

from scripts.calculator import (
    break_even_units,
    break_even_units_with_acquisition,
    cash_runway,
    customer_acquisition_cost,
    operating_profit,
    subscription_ltv,
)

ROOT = Path(__file__).resolve().parents[1]

LABELS = [
    "VERIFIED", "PARTIALLY_SUPPORTED", "UNVERIFIED", "CONTRADICTED",
    "FOUNDER_PROVIDED", "DERIVED", "ASSUMPTION", "UNKNOWN",
]
SKILLS = sorted((ROOT / "skills").glob("*/SKILL.md"))
AGENTS = sorted((ROOT / "agents").glob("*.md"))


def read(path):
    return Path(path).read_text(encoding="utf-8")


class TestEvidenceTerminology(unittest.TestCase):

    def test_reference_document_defines_every_label(self):
        text = read(ROOT / "docs" / "evidence-terminology.md")
        for label in LABELS + ["NOT_APPLICABLE"]:
            self.assertIn(f"`{label}`", text, label)

    def test_every_skill_and_classifying_agent_uses_the_full_label_set(self):
        classifying = [
            p for p in SKILLS + AGENTS if p.stem != "research-lead"
        ]
        # 6 skills, plus every agent except research-lead (3).
        self.assertEqual(len(classifying), 9)
        for path in classifying:
            text = read(path)
            for label in LABELS:
                self.assertRegex(
                    text, rf"(?m)^- {label}:", f"{path.name} lacks {label}"
                )
            self.assertIn("docs/evidence-terminology.md", text, path.name)

    def test_research_lead_uses_uppercase_labels(self):
        text = read(ROOT / "agents" / "research-lead.md")
        self.assertIn("VERIFIED, PARTIALLY_SUPPORTED, UNVERIFIED", text)
        self.assertNotIn("verified, partially supported, or unverified", text)

    def test_readme_does_not_overclaim_verification(self):
        text = read(ROOT / "README.md")
        self.assertNotIn("every claim and every number traceable", text)
        self.assertNotIn("independently reviews claims", text)
        self.assertIn("not a human audit", text)
        for label in LABELS:
            self.assertIn(label, text, label)


class TestUntrustedContentSafeguards(unittest.TestCase):

    def test_every_skill_and_agent_treats_content_as_data(self):
        for path in SKILLS + AGENTS:
            text = read(path)
            self.assertIn("## Untrusted Content", text, path.name)
            self.assertRegex(text, r"data,\s+not\s+instructions", path.name)
            self.assertRegex(text, r"[Ii]gnore it", path.name)

    def test_skill_sections_are_consistent(self):
        sections = set()
        for path in SKILLS:
            text = read(path)
            sections.add(text.split("## Untrusted Content", 1)[1].strip())
        self.assertEqual(len(sections), 1, "skills must share one wording")


class TestFinancialAnalystMatchesEngine(unittest.TestCase):

    def setUp(self):
        self.text = read(ROOT / "agents" / "financial-analyst.md")

    def test_stale_operating_profit_formula_is_gone(self):
        self.assertNotIn("Revenue - Operating Expenses - Cost of Goods Sold",
                         self.text)

    def test_current_formulas_present(self):
        for needle in (
            "Operating Profit = Revenue - COGS - Variable Operating Costs"
            " - Acquisition Costs - Fixed Operating Costs",
            "Loaded Contribution per Unit = Selling Price - Variable Cost"
            " per Unit - CAC per Customer",
            "CAC = Eligible Acquisition Spend / New Customers",
            "LTV = Monthly Contribution per Customer / Monthly Churn Rate",
            "Fixed Costs excluding acquisition",
        ):
            self.assertIn(needle, self.text)

    def test_double_counting_rule_and_no_execution_claim(self):
        self.assertIn("never both", self.text)
        self.assertIn("This agent cannot run commands", self.text)
        self.assertIn("not engine-validated", self.text)


class TestEngineConsistency(unittest.TestCase):
    """The formulas documented for the financial analyst, checked by hand."""

    def test_loaded_break_even_is_the_first_profitable_unit_count(self):
        fixed, price, var, cac = "1500", "149", "19.37", "60"
        loaded = break_even_units_with_acquisition(fixed, price, var, cac)
        units = loaded["break_even_units"]
        self.assertEqual(units, 22)

        def profit(n):
            return operating_profit(
                Decimal(price) * n,
                Decimal(var) * n,
                0,
                Decimal(cac) * n,
                fixed,
            )["operating_profit"]

        self.assertGreaterEqual(profit(units), 0)
        self.assertLess(profit(units - 1), 0)

    def test_fixed_budget_and_per_customer_cac_agree_when_counted_once(self):
        budget_as_fixed = break_even_units_with_acquisition(
            "2000", "100", "20", "0"
        )["break_even_units"]
        # 2000 / 80 = 25 units. Converting that budget to a per-customer
        # CAC at 25 customers gives 80 each; counted once, profit is zero.
        self.assertEqual(budget_as_fixed, 25)
        self.assertEqual(
            operating_profit(2500, 500, 0, 2000, 0)["operating_profit"],
            Decimal("0"),
        )
        self.assertEqual(
            customer_acquisition_cost("2000", "25"), Decimal("80"))

    def test_double_counting_changes_the_answer(self):
        once = break_even_units_with_acquisition("2000", "100", "20", "0")
        twice = break_even_units_with_acquisition("2000", "100", "20", "10")
        self.assertGreater(twice["break_even_units"],
                           once["break_even_units"])

    def test_plain_break_even_is_never_above_loaded(self):
        plain = break_even_units("1000", "75", "25")
        loaded = break_even_units_with_acquisition(
            "1000", "75", "25", "10")["break_even_units"]
        self.assertEqual((plain, loaded), (20, 25))

    def test_ltv_accepts_churn_of_exactly_one(self):
        self.assertEqual(subscription_ltv("40", "1"), Decimal("40"))

    def test_ltv_rejects_churn_just_above_one(self):
        with self.assertRaises(ValueError):
            subscription_ltv("40", "1.000001")

    def test_ltv_rejects_zero_churn(self):
        with self.assertRaises(ValueError):
            subscription_ltv("40", "0")

    def test_runway_with_zero_cash_is_zero_months(self):
        self.assertEqual(cash_runway("0", "1000"), Decimal("0"))

    def test_cac_is_exact_decimal_division(self):
        self.assertEqual(customer_acquisition_cost("100", "8"),
                         Decimal("12.5"))


class TestGitignore(unittest.TestCase):

    def test_gitignore_exists_and_covers_common_noise_and_secrets(self):
        text = read(ROOT / ".gitignore")
        for pattern in ("__pycache__/", ".env", ".DS_Store", "node_modules/"):
            self.assertIn(pattern, text, pattern)

    def test_required_assets_are_not_ignored(self):
        required = [
            ".claude-plugin/plugin.json", ".claude-plugin/marketplace.json",
            "assets/logo.svg", "assets/social-preview.png",
            "skills/idea-validator/SKILL.md", "agents/research-lead.md",
            "scripts/calculator.py", "tests/test_calculator.py",
            ".github/workflows/test-calculator.yml", "LICENSE", "NOTICE",
        ]
        for rel in required:
            self.assertTrue((ROOT / rel).is_file(), rel)
        try:
            result = subprocess.run(
                ["git", "check-ignore", "--no-index", "-v", *required],
                cwd=ROOT, capture_output=True, text=True, timeout=20,
            )
        except (OSError, subprocess.TimeoutExpired):
            self.skipTest("git is not available")
        if result.returncode == 128:
            self.skipTest("not a git checkout")
        self.assertEqual(result.stdout, "", f"ignored: {result.stdout}")

    def test_noise_and_secrets_are_ignored(self):
        try:
            result = subprocess.run(
                ["git", "check-ignore", "--no-index",
                 "scripts/__pycache__/x.pyc", ".env", ".env.local",
                 ".DS_Store"],
                cwd=ROOT, capture_output=True, text=True, timeout=20,
            )
        except (OSError, subprocess.TimeoutExpired):
            self.skipTest("git is not available")
        if result.returncode == 128:
            self.skipTest("not a git checkout")
        self.assertEqual(len(result.stdout.split()), 4, result.stdout)


class TestReleaseProcess(unittest.TestCase):

    def setUp(self):
        self.plugin = json.loads(
            read(ROOT / ".claude-plugin" / "plugin.json"))
        self.version = self.plugin["version"]
        self.changelog = read(ROOT / "CHANGELOG.md")

    def test_every_changelog_version_has_a_link_reference(self):
        headings = re.findall(r"^## \[(\d+\.\d+\.\d+)\]", self.changelog,
                              re.M)
        self.assertIn(self.version, headings)
        for version in headings:
            self.assertRegex(self.changelog, rf"(?m)^\[{re.escape(version)}\]: ",
                             f"no link reference for {version}")
        self.assertRegex(self.changelog, r"(?m)^\[Unreleased\]: ")

    def test_release_notes_exist_for_current_version(self):
        notes = ROOT / "docs" / "release-notes" / f"v{self.version}.md"
        self.assertTrue(notes.is_file())
        self.assertIn(f"v{self.version}", read(notes))

    def test_release_workflow_validates_but_never_publishes(self):
        text = read(ROOT / ".github" / "workflows" / "release-check.yml")
        self.assertIn('"v[0-9]+.[0-9]+.[0-9]+"', text)
        self.assertIn("claude plugin validate . --strict", text)
        self.assertIn("unittest discover", text)
        for forbidden in ("contents: write", "gh release", "action-gh-release",
                          "upload-artifact", "git push", "pull_request_target"):
            self.assertNotIn(forbidden, text, forbidden)

    def test_release_docs_say_nothing_is_published_automatically(self):
        text = read(ROOT / "docs" / "releasing.md")
        self.assertIn("Nothing here publishes a release", text)
        self.assertIn("git tag -a", text)
        self.assertNotIn("--force", text)


class TestDocsHonesty(unittest.TestCase):

    def test_competitive_landscape_names_founder_skills_with_dates(self):
        text = read(ROOT / "docs" / "competitive-landscape.md")
        self.assertIn("https://github.com/lool-ventures/founder-skills", text)
        self.assertRegex(text, r"re-verified: \d{4}-\d{2}-\d{2}")
        self.assertIn("no Founder Skills code, prompts", text)

    def test_competitive_landscape_makes_no_superiority_claims(self):
        text = read(ROOT / "docs" / "competitive-landscape.md").lower()
        for phrase in ("better than", "outperforms", "superior to",
                       "the best ", "beats "):
            self.assertNotIn(phrase, text, phrase)

    def test_commit_metadata_doc_does_not_repeat_the_personal_address(self):
        for path in (ROOT / "docs").rglob("*.md"):
            self.assertNotRegex(read(path), r"[\w.+-]+@gmail\.com",
                                f"{path.name} contains a Gmail address")

    def test_repository_settings_doc_states_limits(self):
        text = read(ROOT / "docs" / "repository-settings.md")
        for needle in ("Branch protection", "HTTP 403",
                       "Private vulnerability reporting"):
            self.assertIn(needle, text)

    def test_license_and_copyright_are_preserved(self):
        self.assertIn("Apache License", read(ROOT / "LICENSE"))
        self.assertIn("Mahdokht Zohadi", read(ROOT / "NOTICE"))


class TestCliDeterminism(unittest.TestCase):

    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, "-B", str(ROOT / "scripts" / "calculate.py"),
             *args],
            capture_output=True, text=True, timeout=20,
        )

    def test_identical_inputs_give_identical_output(self):
        a = self.run_cli("break-even-loaded", "1500", "149", "19.37", "60")
        b = self.run_cli("break-even-loaded", "1500", "149", "19.37", "60")
        self.assertEqual(a.returncode, 0)
        self.assertEqual(a.stdout, b.stdout)
        self.assertEqual(json.loads(a.stdout)["result"]["break_even_units"], 22)


if __name__ == "__main__":
    unittest.main()

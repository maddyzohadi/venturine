"""Regression tests for the low-severity audit findings (L1-L7).

Standard library only. No network access. Each test class names the finding
it guards. A seeded random oracle checks the engine's displayed results
against exact rational arithmetic.
"""

import ast
import json
import math
import random
import re
import subprocess
import sys
import unittest
from decimal import Decimal
from fractions import Fraction
from pathlib import Path

from scripts import calculate
from scripts.calculator import (
    break_even_units,
    break_even_units_with_acquisition,
    customer_acquisition_cost,
    number,
)

ROOT = Path(__file__).resolve().parents[1]
SKILLS = sorted((ROOT / "skills").glob("*/SKILL.md"))
AGENTS = sorted((ROOT / "agents").glob("*.md"))
LABELS = [
    "VERIFIED", "PARTIALLY_SUPPORTED", "UNVERIFIED", "CONTRADICTED",
    "FOUNDER_PROVIDED", "DERIVED", "ASSUMPTION", "UNKNOWN",
]


def read(path):
    return Path(path).read_text(encoding="utf-8")


def run_cli(*args):
    return subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "calculate.py"), *args],
        capture_output=True, text=True, timeout=10, check=False,
    )


def cli_json(*args):
    result = run_cli(*args)
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def round_half_up_cents(value):
    """
    Independent model of the display rule, in exact arithmetic: 2 decimal
    places at magnitude 1 or more, 4 significant digits below 1, half away
    from zero.
    """
    value = Fraction(value)
    if value == 0:
        return "0.00"
    magnitude = abs(value)
    sign = "-" if value < 0 else ""
    if magnitude < 1:
        exponent = 0
        while magnitude * 10 ** (exponent + 1) < 1:
            exponent += 1  # magnitude is in [10**-(exponent+1), 10**-exponent)
        places = exponent + 4  # first significant digit sits at 10**-(e+1)
        scaled = math.floor(magnitude * 10 ** places + Fraction(1, 2))
        if scaled < 10 ** places:  # still below 1 after rounding
            digits = str(scaled).rjust(places, "0")
            return sign + "0." + digits.rstrip("0")
    scaled = math.floor(magnitude * 100 + Fraction(1, 2))
    return f"{sign}{scaled // 100}.{scaled % 100:02d}"


class TestInputSyntaxIsAsciiOnly(unittest.TestCase):
    """L3: Unicode digits and underscores were accepted as numbers."""

    def test_non_ascii_digits_are_rejected(self):
        for text in ("٣", "١٢٣", "1٣", "１２"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                number(text)

    def test_underscores_and_whitespace_are_rejected(self):
        for text in ("1_000", "1_0.5", " 5", "5 ", "5\n", "", "+", "."):
            with self.subTest(text=repr(text)), self.assertRaises(ValueError):
                number(text)

    def test_hex_and_other_syntax_are_rejected(self):
        for text in ("0x10", "1e", "e5", "1,000", "$5", "5%", "--5"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                number(text)

    def test_plain_numbers_are_still_accepted(self):
        for text, expected in (
            ("5", Decimal("5")), ("5.", Decimal("5")),
            (".5", Decimal("0.5")), ("-0", Decimal("0")),
            ("+2.50", Decimal("2.5")), ("1e3", Decimal("1000")),
            ("1E+3", Decimal("1000")), ("0.000000001", Decimal("1E-9")),
        ):
            with self.subTest(text=text):
                self.assertEqual(number(text), expected)

    def test_python_numbers_are_still_accepted(self):
        self.assertEqual(number(10), Decimal(10))
        self.assertEqual(number(1.5), Decimal("1.5"))
        self.assertEqual(number(Decimal("1E+3")), Decimal(1000))

    def test_nan_and_infinity_keep_their_specific_message(self):
        for text in ("NaN", "Infinity", "-inf", "sNaN"):
            with self.subTest(text=text):
                with self.assertRaisesRegex(ValueError, "finite"):
                    number(text)

    def test_cli_rejects_them_cleanly(self):
        for text in ("٣", "1_000", " 5"):
            with self.subTest(text=repr(text)):
                result = run_cli("revenue", text, "2")
                self.assertEqual(result.returncode, 2)
                self.assertIn("error:", result.stderr)
                self.assertNotIn("Traceback", result.stderr)


class TestOutputFormatting(unittest.TestCase):
    """L1 and L2: exponent output, negative zero and false precision."""

    def results(self, data):
        """Every serialized Decimal string in a result."""
        result = data["result"]
        if isinstance(result, dict):
            return [v for v in result.values() if isinstance(v, str)
                    and re.fullmatch(r"-?[0-9.]+", v)]
        return [result] if isinstance(result, str) else []

    def test_integers_never_print_in_exponent_form(self):
        commands = [
            ("subscription-ltv", "30", "0.05"),
            ("revenue", "5.", "1e1"),
            ("revenue", "1e3", "1e3"),
            ("cac", "1e6", "1"),
            ("runway", "1e12", "1"),
            ("contribution-margin", "1e12", "0"),
            ("gross-margin", "1e3", "0"),
        ]
        for command in commands:
            with self.subTest(command=command):
                for text in self.results(cli_json(*command)):
                    self.assertNotRegex(text, r"[eE]", text)

    def test_the_audit_examples_print_plainly(self):
        self.assertEqual(
            cli_json("subscription-ltv", "30", "0.05")["result"], "600.00")
        self.assertEqual(cli_json("revenue", "5.", "1e1")["result"], "50.00")

    def test_negative_zero_is_normalized(self):
        for command in (
            ("revenue", "-0", "5"),
            ("revenue", "5", "-0"),
            ("contribution-margin", "5", "5"),
            ("gross-margin", "1", "-0"),
        ):
            with self.subTest(command=command):
                for text in self.results(cli_json(*command)):
                    self.assertNotIn("-", text, text)
        self.assertEqual(calculate.format_decimal(Decimal("-0")), "0.00")
        self.assertEqual(calculate.format_decimal(Decimal("0E+5")), "0.00")

    def test_long_repeating_results_are_bounded(self):
        self.assertEqual(cli_json("cac", "100", "3")["result"], "33.33")
        self.assertEqual(cli_json("runway", "1", "3")["result"], "0.3333")
        margin = cli_json(
            "operating-profit", "14900", "0", "1937", "6000", "1500"
        )["result"]["operating_margin_percent"]
        self.assertEqual(margin, "36.66")

    def test_displayed_digits_are_bounded(self):
        for command in (
            ("cac", "100", "7"), ("gross-margin", "1000", "333"),
            ("subscription-ltv", "10", "0.07"), ("runway", "10", "7"),
        ):
            with self.subTest(command=command):
                for text in self.results(cli_json(*command)):
                    self.assertRegex(text, r"^-?[0-9]+\.[0-9]{2}$", text)

    def test_rounding_is_half_up_away_from_zero(self):
        for value, expected in (
            ("1.125", "1.13"), ("2.675", "2.68"), ("10.015", "10.02"),
            ("-1.125", "-1.13"), ("1.005", "1.01"), ("1.004", "1.00"),
            ("999.995", "1000.00"),
        ):
            with self.subTest(value=value):
                self.assertEqual(
                    calculate.format_decimal(Decimal(value)), expected)

    def test_tiny_nonzero_results_do_not_display_as_zero(self):
        self.assertEqual(cli_json("revenue", "0.000001", "3")["result"],
                         "0.000003")
        self.assertEqual(
            calculate.format_decimal(Decimal("0.00333333")), "0.003333")
        for text in ("0.000000001", "1E-9", "0.0099999"):
            with self.subTest(text=text):
                shown = calculate.format_decimal(Decimal(text))
                self.assertNotEqual(Decimal(shown), 0)
                self.assertNotRegex(shown, r"[eE]")

    def test_values_below_one_keep_four_significant_digits(self):
        # Two decimal places would turn 0.0149 into 0.01, a 33% error.
        for text, expected in (
            ("0.0149", "0.0149"), ("0.0999", "0.0999"),
            ("0.3333333", "0.3333"), ("0.5", "0.5"),
            ("0.12345", "0.1235"), ("-0.0149", "-0.0149"),
            ("0.00149", "0.00149"), ("0.30004", "0.3"),
            ("0.1000", "0.1"), ("0.99996", "1.00"),
        ):
            with self.subTest(text=text):
                self.assertEqual(
                    calculate.format_decimal(Decimal(text)), expected)

    def test_rounding_up_to_one_does_not_show_extra_digits(self):
        self.assertEqual(
            calculate.format_decimal(Decimal("0.999996")), "1.00")

    def test_relative_display_error_is_always_small(self):
        rng = random.Random(11)
        for _ in range(2000):
            exponent = rng.randint(-8, 11)
            value = Decimal(rng.randint(1, 10 ** 6)) * Decimal(10) ** exponent
            shown = Decimal(calculate.format_decimal(value))
            error = abs(shown - value) / value
            # 2 decimals at magnitude 1+ is at most 0.5%; below 1, 0.05%.
            self.assertLess(error, Decimal("0.005"), (value, shown))
            if value < 1:
                self.assertLess(error, Decimal("0.0006"), (value, shown))

    def test_large_values_use_plain_notation(self):
        for text in ("1E+24", "123456789012345678901234", "1E+21"):
            with self.subTest(text=text):
                shown = calculate.format_decimal(Decimal(text))
                self.assertNotRegex(shown, r"[eE]")
                self.assertEqual(Decimal(shown), Decimal(text))
        self.assertEqual(
            cli_json("revenue", "1e12", "1e12")["result"],
            "1000000000000000000000000.00",
        )

    def test_rounding_note_appears_only_with_decimal_results(self):
        self.assertIn("display_rounding", cli_json("cac", "100", "3"))
        self.assertIn("display_rounding", cli_json(
            "operating-profit", "1", "0", "0", "0", "0"))
        self.assertIn("display_rounding", cli_json(
            "break-even-loaded", "1500", "149", "19.37", "60"))
        self.assertNotIn("display_rounding",
                         cli_json("break-even", "1500", "149", "19.37"))

    def test_whole_unit_results_stay_exact_integers(self):
        self.assertIsInstance(
            cli_json("break-even", "1500", "149", "19.37")["result"], int)
        loaded = cli_json("break-even-loaded", "1500", "149", "19.37", "60")
        self.assertIsInstance(loaded["result"]["break_even_units"], int)
        self.assertEqual(loaded["result"]["break_even_units"], 22)

    def test_inputs_are_echoed_exactly_as_given(self):
        data = cli_json("revenue", "5.", "1e1")
        self.assertEqual(data["inputs"], ["5.", "1e1"])

    def test_engine_arithmetic_is_still_exact(self):
        # Rounding is display only: the library keeps full precision.
        exact = customer_acquisition_cost("100", "3")
        self.assertEqual(exact, Decimal(100) / Decimal(3))
        self.assertGreater(len(str(exact)), 20)

    def test_formatting_does_not_change_break_even_decisions(self):
        # Display rounding must never feed back into the calculation.
        self.assertEqual(break_even_units("1", "3", "2.999999"), 1000000)
        self.assertEqual(
            cli_json("break-even", "1", "3", "2.999999")["result"], 1000000)


class TestRoundingNeverChangesTheCalculation(unittest.TestCase):
    """Display rounding must not feed back into any financial result."""

    CHAIN = ("4607", "38", "166", "27", "12966")  # spend, n, price, vc, fixed

    def chained_answers(self):
        spend, customers, price, cost, fixed = self.CHAIN
        exact_cac = customer_acquisition_cost(spend, customers)
        exact = break_even_units_with_acquisition(
            fixed, price, cost, exact_cac)["break_even_units"]
        data = cli_json("cac", spend, customers)
        shown = break_even_units_with_acquisition(
            fixed, price, cost, data["result"])["break_even_units"]
        unrounded = break_even_units_with_acquisition(
            fixed, price, cost, data["unrounded_result"])["break_even_units"]
        return exact, shown, unrounded

    def test_chaining_the_displayed_value_can_change_the_answer(self):
        # This is why unrounded_result exists: 121.24 is not 121.2368...
        exact, shown, _ = self.chained_answers()
        self.assertNotEqual(exact, shown)

    def test_chaining_the_unrounded_value_matches_the_exact_answer(self):
        exact, _, unrounded = self.chained_answers()
        self.assertEqual(exact, unrounded)

    def test_unrounded_result_appears_only_when_rounding_changed_something(
            self):
        data = cli_json("cac", "4607", "38")
        self.assertEqual(data["result"], "121.24")
        self.assertTrue(data["unrounded_result"].startswith("121.2368421"))
        self.assertIn("unrounded_result", data["display_rounding"])
        self.assertNotIn("unrounded_result", cli_json("cac", "1200", "30"))
        self.assertNotIn("unrounded_result", cli_json(
            "break-even", "1500", "149", "19.37"))

    def test_unrounded_values_are_plain_exact_decimals(self):
        data = cli_json("operating-profit", "14900", "0", "1937", "6000",
                        "1500")
        for key, text in data["unrounded_result"].items():
            self.assertRegex(text, r"^-?[0-9]+(\.[0-9]+)?$", key)
            self.assertNotRegex(text, r"[eE]")
        self.assertEqual(
            Fraction(data["unrounded_result"]["operating_profit"]), 5463)

    def test_unrounded_result_equals_the_engine_value_exactly(self):
        for spend, customers in (("100", "3"), ("1", "7"), ("999.99", "13")):
            with self.subTest(spend=spend):
                data = cli_json("cac", spend, customers)
                self.assertEqual(
                    Decimal(data["unrounded_result"]),
                    customer_acquisition_cost(spend, customers))

    def test_break_even_does_not_depend_on_the_display_formatter(self):
        from unittest import mock
        args = ("1500", "149", "19.37", "60")
        baseline = break_even_units_with_acquisition(*args)
        for formatter in (lambda v: "X", lambda v: "0.00"):
            with mock.patch.object(calculate, "format_decimal", formatter):
                again = break_even_units_with_acquisition(*args)
            self.assertEqual(again["break_even_units"],
                             baseline["break_even_units"])
        # And the library never returns rounded values.
        self.assertEqual(
            baseline["loaded_contribution_per_unit"], Decimal("69.63"))
        self.assertEqual(
            customer_acquisition_cost("100", "3"), Decimal(100) / Decimal(3))

    def test_library_results_are_identical_before_and_after_serialization(
            self):
        for operation, args in (
            ("cac", ("100", "3")), ("runway", ("1", "7")),
            ("gross-margin", ("1000", "333")),
            ("subscription-ltv", ("10", "0.07")),
        ):
            function, _ = calculate.OPERATIONS[operation]
            before = function(*args)
            calculate.serialize(before)
            self.assertEqual(function(*args), before)


class TestOracleAgreement(unittest.TestCase):
    """Exact rational arithmetic as an independent oracle (seeded)."""

    COUNT = 150

    def setUp(self):
        self.rng = random.Random(20261118)

    def amount(self, low=0, high=10000, places=2):
        scale = 10 ** places
        return Fraction(self.rng.randint(low * scale, high * scale), scale)

    def text(self, fraction, places=2):
        return f"{float(fraction):.{places}f}"

    def displayed(self, operation, args):
        function, _ = calculate.OPERATIONS[operation]
        return calculate.serialize(function(*args))

    def test_two_input_operations_match_the_oracle(self):
        for _ in range(self.COUNT):
            a = self.amount(1, 100000)
            b = self.amount(1, 100000)
            ta, tb = self.text(a), self.text(b)
            a, b = Fraction(ta), Fraction(tb)
            cases = {
                "revenue": a * b,
                "contribution-margin": a - b if a >= b else None,
                "cac": a / b,
                "runway": a / b,
            }
            for operation, expected in cases.items():
                if expected is None:
                    continue
                with self.subTest(operation=operation, a=ta, b=tb):
                    shown = self.displayed(operation, (ta, tb))
                    self.assertEqual(shown, round_half_up_cents(expected))

    def test_gross_margin_matches_the_oracle(self):
        for _ in range(self.COUNT):
            revenue = self.text(self.amount(1, 100000))
            cogs = self.text(self.amount(0, 100000))
            r, c = Fraction(revenue), Fraction(cogs)
            with self.subTest(revenue=revenue, cogs=cogs):
                shown = self.displayed("gross-margin", (revenue, cogs))
                self.assertEqual(
                    shown["gross_profit"], round_half_up_cents(r - c))
                self.assertEqual(
                    shown["gross_margin_percent"],
                    round_half_up_cents((r - c) / r * 100))

    def test_operating_profit_matches_the_oracle(self):
        for _ in range(self.COUNT):
            values = [self.text(self.amount(0, 50000)) for _ in range(5)]
            f = [Fraction(v) for v in values]
            costs = sum(f[1:], Fraction(0))
            profit = f[0] - costs
            with self.subTest(values=values):
                shown = self.displayed("operating-profit", values)
                self.assertEqual(shown["total_costs"],
                                 round_half_up_cents(costs))
                self.assertEqual(shown["operating_profit"],
                                 round_half_up_cents(profit))
                if f[0] > 0:
                    self.assertEqual(
                        shown["operating_margin_percent"],
                        round_half_up_cents(profit / f[0] * 100))
                else:
                    self.assertIsNone(shown["operating_margin_percent"])

    def test_subscription_ltv_matches_the_oracle(self):
        for _ in range(self.COUNT):
            contribution = self.text(self.amount(0, 5000))
            churn = self.text(self.amount(0, 1, 3) or Fraction(1, 1000), 3)
            if Fraction(churn) == 0:
                continue
            with self.subTest(contribution=contribution, churn=churn):
                shown = self.displayed(
                    "subscription-ltv", (contribution, churn))
                self.assertEqual(
                    shown,
                    round_half_up_cents(
                        Fraction(contribution) / Fraction(churn)))

    def test_break_even_matches_the_oracle_exactly(self):
        for _ in range(self.COUNT):
            fixed = self.text(self.amount(0, 100000))
            cost = self.text(self.amount(0, 500))
            margin = self.text(self.amount(0, 500) + Fraction(1, 100))
            price = self.text(Fraction(cost) + Fraction(margin))
            expected = math.ceil(Fraction(fixed) / Fraction(margin))
            with self.subTest(fixed=fixed, price=price, cost=cost):
                self.assertEqual(
                    break_even_units(fixed, price, cost), expected)

    def test_loaded_break_even_matches_the_oracle_exactly(self):
        for _ in range(self.COUNT):
            fixed = self.text(self.amount(0, 100000))
            cost = self.text(self.amount(0, 300))
            cac = self.text(self.amount(0, 200))
            loaded = self.text(self.amount(0, 300) + Fraction(1, 100))
            price = self.text(Fraction(cost) + Fraction(cac) + Fraction(loaded))
            expected = math.ceil(Fraction(fixed) / Fraction(loaded))
            with self.subTest(fixed=fixed, price=price, cost=cost, cac=cac):
                result = break_even_units_with_acquisition(
                    fixed, price, cost, cac)
                self.assertEqual(result["break_even_units"], expected)
                self.assertEqual(
                    Fraction(result["loaded_contribution_per_unit"]),
                    Fraction(loaded))


class TestBreakEvenBoundaries(unittest.TestCase):
    """Boundary cases proposed in the audit."""

    def test_exact_multiple_does_not_round_up(self):
        self.assertEqual(break_even_units("500", "50", "25"), 20)
        self.assertEqual(break_even_units("500.01", "50", "25"), 21)

    def test_zero_fixed_costs_break_even_at_zero_units(self):
        self.assertEqual(break_even_units("0", "50", "25"), 0)
        self.assertEqual(
            break_even_units_with_acquisition(
                "0", "50", "20", "5")["break_even_units"], 0)

    def test_cac_just_below_margin_is_accepted_and_equal_is_rejected(self):
        ok = break_even_units_with_acquisition("100", "50", "20", "29.99")
        self.assertEqual(ok["break_even_units"], 10000)
        with self.assertRaises(ValueError):
            break_even_units_with_acquisition("100", "50", "20", "30")

    def test_loaded_with_zero_cac_equals_plain(self):
        for fixed, price, cost in (("1500", "149", "19.37"), ("7", "3", "2")):
            self.assertEqual(
                break_even_units_with_acquisition(
                    fixed, price, cost, "0")["break_even_units"],
                break_even_units(fixed, price, cost))


class TestPythonSupportIsDeclaredAndTested(unittest.TestCase):
    """L4: no minimum Python was declared and CI tested only 3.13."""

    def test_documentation_states_the_minimum(self):
        for name in ("README.md", "CONTRIBUTING.md"):
            self.assertIn("3.9", read(ROOT / name), name)

    def test_ci_tests_the_minimum_and_newer_versions(self):
        text = read(ROOT / ".github" / "workflows" / "test-calculator.yml")
        self.assertIn("matrix:", text)
        self.assertIn("${{ matrix.python-version }}", text)
        versions = re.search(r"python-version:\s*\[([^\]]*)\]", text)
        self.assertIsNotNone(versions)
        listed = [v.strip(' "\'') for v in versions.group(1).split(",")]
        self.assertIn("3.9", listed)
        self.assertGreaterEqual(len(listed), 3)
        self.assertNotIn('python-version: "3.13"', text)

    def test_matrix_runs_on_an_image_that_has_the_minimum_python(self):
        # ubuntu-latest moved to 26.04, which has no prebuilt Python 3.9.
        text = read(ROOT / ".github" / "workflows" / "test-calculator.yml")
        self.assertRegex(text, r"runs-on:\s*ubuntu-(22|24)\.04\b")
        self.assertNotIn("runs-on: ubuntu-latest", text)

    def test_sources_use_only_python_3_9_syntax(self):
        for folder in ("scripts", "tests"):
            for path in sorted((ROOT / folder).glob("*.py")):
                with self.subTest(path=path.name):
                    ast.parse(read(path), filename=str(path),
                              feature_version=(3, 9))

    def test_no_python_3_10_plus_library_features_in_scripts(self):
        # str | None unions and match statements are 3.10+.
        for path in (ROOT / "scripts").glob("*.py"):
            tree = ast.parse(read(path))
            for node in ast.walk(tree):
                # ast.Match only exists on 3.10+; getattr keeps 3.9 working.
                match_node = getattr(ast, "Match", None)
                if match_node is not None:
                    self.assertNotIsInstance(node, match_node, path.name)
                if isinstance(node, ast.BinOp) and isinstance(
                        node.op, ast.BitOr):
                    self.fail(f"{path.name}: possible X | Y type union")


class TestMarketplaceMetadata(unittest.TestCase):
    """L5: overclaiming marketplace description, non-person owner."""

    def setUp(self):
        self.marketplace = json.loads(
            read(ROOT / ".claude-plugin" / "marketplace.json"))
        self.plugin = json.loads(
            read(ROOT / ".claude-plugin" / "plugin.json"))

    def test_marketplace_does_not_call_itself_official(self):
        self.assertNotRegex(
            self.marketplace["description"], r"(?i)\bofficial\b")

    def test_owner_is_a_named_person_matching_the_plugin_author(self):
        owner = self.marketplace["owner"]["name"]
        self.assertNotEqual(owner.lower(), "venturine")
        self.assertEqual(owner, self.plugin["author"]["name"])

    def test_plugin_has_a_homepage_on_the_repository(self):
        self.assertTrue(self.plugin["homepage"].startswith("https://"))
        self.assertEqual(self.plugin["homepage"], self.plugin["repository"])

    def test_marketplace_lists_exactly_the_plugin(self):
        entries = self.marketplace["plugins"]
        self.assertEqual([e["name"] for e in entries], [self.plugin["name"]])


class TestCliToolingIntegrity(unittest.TestCase):
    """L6: CI installed an unlocked CLI with no integrity check."""

    CI = ROOT / ".github" / "ci" / "claude-code"

    def setUp(self):
        self.package = json.loads(read(self.CI / "package.json"))
        self.lock = json.loads(read(self.CI / "package-lock.json"))

    def workflows(self):
        return sorted((ROOT / ".github" / "workflows").glob("*.yml"))

    def test_package_json_pins_an_exact_version(self):
        version = self.package["dependencies"]["@anthropic-ai/claude-code"]
        self.assertRegex(version, r"^\d+\.\d+\.\d+$")
        self.assertTrue(self.package["private"])

    def test_lockfile_matches_the_pin(self):
        pin = self.package["dependencies"]["@anthropic-ai/claude-code"]
        entry = self.lock["packages"]["node_modules/@anthropic-ai/claude-code"]
        self.assertEqual(entry["version"], pin)
        self.assertGreaterEqual(self.lock["lockfileVersion"], 2)

    def test_every_locked_package_has_an_integrity_hash_and_registry_url(self):
        packages = {k: v for k, v in self.lock["packages"].items() if k}
        self.assertTrue(packages)
        for name, entry in packages.items():
            with self.subTest(package=name):
                self.assertRegex(entry["integrity"], r"^sha512-")
                self.assertTrue(
                    entry["resolved"].startswith(
                        "https://registry.npmjs.org/"), entry["resolved"])

    def test_workflows_never_install_the_cli_without_the_lockfile(self):
        for path in self.workflows():
            text = read(path)
            with self.subTest(workflow=path.name):
                self.assertNotRegex(
                    text,
                    r"npm\s+(install|i)\b[^\n]*claude-code",
                    "unlocked CLI install",
                )
                self.assertNotRegex(text, r"npx\s+[^\n]*claude-code")

    def test_validating_workflows_use_npm_ci_in_the_pinned_directory(self):
        for name in ("validate-plugin.yml", "release-check.yml"):
            text = read(ROOT / ".github" / "workflows" / name)
            with self.subTest(workflow=name):
                self.assertIn("working-directory: .github/ci/claude-code",
                              text)
                self.assertIn("npm ci", text)
                # The CLI links a native binary in a postinstall step.
                self.assertNotIn("--ignore-scripts", text)
                self.assertIn(
                    ".github/ci/claude-code/node_modules/.bin/claude "
                    "plugin validate . --strict", text)

    def test_ci_tooling_changes_retrigger_validation(self):
        text = read(ROOT / ".github" / "workflows" / "validate-plugin.yml")
        self.assertIn('".github/ci/**"', text)

    def test_required_validation_runs_on_every_pull_request(self):
        # "Validate Plugin and Marketplace" is a required status check, so a
        # path filter on pull_request would block documentation-only PRs.
        text = read(ROOT / ".github" / "workflows" / "validate-plugin.yml")
        pull_request = text.split("  pull_request:\n", 1)[1].split(
            "  workflow_dispatch:", 1)[0]
        self.assertNotIn("paths:", pull_request)
        self.assertIn("name: Validate Plugin and Marketplace", text)

    def test_lockfile_is_not_ignored_by_git(self):
        result = subprocess.run(
            ["git", "check-ignore", "-q",
             ".github/ci/claude-code/package-lock.json"],
            cwd=ROOT, capture_output=True, check=False)
        self.assertEqual(result.returncode, 1, "lockfile must be tracked")


class TestSharedWordingDoesNotDrift(unittest.TestCase):
    """L7: repeated vocabulary and safety text drifted between files."""

    CLASSIFYING = [p for p in SKILLS + AGENTS if p.stem != "research-lead"]

    def label_lines(self, path):
        lines = {}
        for label in LABELS:
            match = re.search(rf"(?m)^- {label}: (.*)$", read(path))
            self.assertIsNotNone(match, f"{path.name} lacks {label}")
            lines[label] = match.group(1).strip()
        return lines

    def test_label_definitions_are_identical_everywhere(self):
        reference = self.label_lines(self.CLASSIFYING[0])
        for path in self.CLASSIFYING[1:]:
            with self.subTest(file=path.name):
                self.assertEqual(self.label_lines(path), reference)

    def test_untrusted_content_wording_is_identical_in_skills_and_analyst(self):
        sections = {}
        for path in SKILLS + [ROOT / "agents" / "financial-analyst.md"]:
            sections[path.name] = read(path).split(
                "## Untrusted Content", 1)[1].strip()
        self.assertEqual(len(set(sections.values())), 1, sections.keys())

    def test_web_agents_state_the_core_rules(self):
        for name in ("research-lead.md", "evidence-auditor.md"):
            text = read(ROOT / "agents" / name)
            with self.subTest(agent=name):
                self.assertRegex(text, r"data,\s+not\s+instructions")
                self.assertRegex(text, r"[Ii]gnore")


class TestCostCategoriesAgreeAcrossDocuments(unittest.TestCase):
    """Duplicated cost assumptions must name the same categories."""

    def test_skill_and_agent_name_the_same_categories(self):
        skill = read(ROOT / "skills" / "unit-economics" / "SKILL.md")
        agent = read(ROOT / "agents" / "financial-analyst.md")
        for text, name in ((skill, "unit-economics"), (agent, "analyst")):
            lowered = text.lower()
            for term in ("cogs", "variable operating", "acquisition",
                         "fixed operating"):
                self.assertIn(term, lowered, f"{name} lacks {term}")

    def test_skill_and_agent_both_forbid_double_counting(self):
        skill = read(ROOT / "skills" / "unit-economics" / "SKILL.md").lower()
        agent = read(ROOT / "agents" / "financial-analyst.md").lower()
        for text in (skill, agent):
            self.assertRegex(text, r"never both|exactly once|double.count")

    def test_documented_ltv_and_runway_formulas_agree(self):
        skill = read(ROOT / "skills" / "unit-economics" / "SKILL.md")
        agent = read(ROOT / "agents" / "financial-analyst.md")
        for text in (skill, agent):
            self.assertRegex(text, r"(?i)churn")
            self.assertRegex(text, r"(?i)runway")


class TestInjectionReportingDoesNotReproducePayloads(unittest.TestCase):
    """The reporting rule must not require repeating the malicious text."""

    FILES = SKILLS + AGENTS

    def test_every_skill_and_agent_forbids_repeating_injected_text(self):
        for path in self.FILES:
            text = read(path)
            with self.subTest(file=path.name):
                self.assertRegex(text, r"in your own words")
                self.assertRegex(
                    text, r"Do not repeat the instruction text")
                self.assertRegex(text, r"links")

    def test_old_wording_that_invited_quoting_is_gone(self):
        for path in self.FILES:
            self.assertNotIn(
                "note it briefly (source and what it tried to do)",
                read(path), path.name)

    def test_reporting_is_still_required(self):
        for path in self.FILES:
            text = read(path)
            with self.subTest(file=path.name):
                self.assertRegex(
                    text, r"(?i)report the attempt|Report the attempt")


class TestIdeaValidatorAuditConditions(unittest.TestCase):
    """The auditor is required for final high-confidence decisions only."""

    def setUp(self):
        self.skill = read(ROOT / "skills" / "idea-validator" / "SKILL.md")
        self.doc = read(ROOT / "docs" / "evidence-terminology.md")

    def test_unconditional_audit_request_is_gone(self):
        self.assertNotIn(
            "- Request an independent evidence audit when available.",
            self.skill)

    def test_audit_is_required_for_final_high_confidence_decisions(self):
        section = self.skill.split(
            "Independent audit before a high-confidence recommendation", 1
        )[1].split("### 8.", 1)[0]
        self.assertIn("PROCEED TO VALIDATION", section)
        self.assertIn("NOT VIABLE UNDER STATED CONSTRAINTS", section)
        self.assertRegex(section, r"(?i)final or high-confidence")
        self.assertIn("evidence-auditor", section)

    def test_audit_is_not_automatic_for_preliminary_questions(self):
        section = self.skill.split(
            "Do not run the auditor automatically for:", 1)[1].split(
            "If the conditions apply", 1)[0]
        for needle in ("simple or preliminary", "quick sanity check",
                       "INSUFFICIENT EVIDENCE", "REVISE THE CONCEPT",
                       "declines"):
            self.assertIn(needle, section)

    def test_unavailable_auditor_caps_the_confidence(self):
        self.assertIn("PRELIMINARY", self.skill)
        self.assertIn("AUDITED", self.skill)
        self.assertRegex(
            self.skill, r"no independent review took place")
        self.assertRegex(self.skill, r"do not call it high-confidence")

    def test_preliminary_means_no_review_ran_even_when_exempt(self):
        self.assertRegex(
            self.skill,
            r"PRELIMINARY whenever no independent review ran")
        self.assertRegex(self.skill, r"AUDITED only when the auditor actually ran")
        self.assertIn("whenever no review ran", self.doc)

    def test_skill_tells_the_model_to_check_key_claims_with_web_tools(self):
        self.assertRegex(
            self.skill,
            r"use them to check the claims the decision depends on")
        self.assertRegex(self.skill, r"match the stakes")
        self.assertRegex(self.skill, r"If you did not research")

    def test_output_marks_the_recommendation(self):
        self.assertRegex(
            self.skill,
            r"(?m)^9\. Recommendation, marked AUDITED .* or PRELIMINARY")

    def test_conditions_are_documented_in_the_reference_page(self):
        self.assertIn("When the idea-validator requires an independent "
                      "review", self.doc)
        for needle in ("PROCEED TO VALIDATION", "simple or preliminary",
                       "PRELIMINARY", "AUDITED", "not a human audit"):
            self.assertIn(needle, self.doc)

    def test_other_skills_do_not_auto_invoke_the_auditor_for_everything(
            self):
        # Only idea-validator defines the high-confidence audit gate.
        for name in ("market-intelligence", "competitor-intelligence",
                     "unit-economics"):
            text = read(ROOT / "skills" / name / "SKILL.md")
            self.assertNotIn("Independent audit before a high-confidence",
                             text, name)


class TestVendorPublishedPriceClassification(unittest.TestCase):
    """A vendor's observed list price is separate from claims about it."""

    FILES = [
        ROOT / "skills" / "competitor-intelligence" / "SKILL.md",
        ROOT / "skills" / "idea-validator" / "SKILL.md",
        ROOT / "skills" / "market-intelligence" / "SKILL.md",
        ROOT / "agents" / "research-lead.md",
        ROOT / "agents" / "evidence-auditor.md",
    ]

    def setUp(self):
        self.doc = read(ROOT / "docs" / "evidence-terminology.md")
        self.section = self.doc.split("## Vendor-published prices", 1)[
            1].split("## When the idea-validator", 1)[0]

    def table_rows(self):
        rows = {}
        for line in self.section.splitlines():
            match = re.match(r"\|\s*([^|]+?)\s*\|\s*`?([A-Z_]+)`?", line)
            if match and match.group(2) in LABELS:
                rows[match.group(1)] = match.group(2)
        return rows

    def test_reference_section_exists_and_uses_only_defined_labels(self):
        rows = self.table_rows()
        self.assertEqual(len(rows), 4, rows)
        for label in rows.values():
            self.assertIn(label, LABELS)

    def label_for(self, prefix):
        matches = [v for k, v in self.table_rows().items()
                   if k.startswith(prefix)]
        self.assertEqual(len(matches), 1, prefix)
        return matches[0]

    def test_each_source_type_gets_one_specific_label(self):
        self.assertEqual(self.label_for("The vendor's own page"), "VERIFIED")
        self.assertEqual(
            self.label_for("A search snippet"), "PARTIALLY_SUPPORTED")
        self.assertEqual(self.label_for("Text"), "FOUNDER_PROVIDED")
        self.assertEqual(self.label_for("No price found"), "UNKNOWN")

    def test_observed_price_is_scoped_and_requires_provenance(self):
        for needle in ("that the vendor published this list price on that "
                       "date", "billing period", "URL", "date you accessed"):
            self.assertIn(needle, self.section)

    def test_claims_about_the_price_are_separate_and_unverified(self):
        for needle in ("Claims about the price are separate claims",
                       "cheapest or the market rate", "actually pay",
                       "equivalent in scope", "still current",
                       "trusted by thousands", "separate ledger rows"):
            self.assertIn(needle, self.section)
        self.assertRegex(self.section, r"`UNVERIFIED` without it")

    def test_hostile_page_lowers_confidence_without_calling_price_false(self):
        self.assertRegex(self.section, r"lower your confidence")
        self.assertRegex(self.section, r"do not call its price false")

    def test_blanket_marketing_page_rule_no_longer_contradicts_it(self):
        self.assertNotIn("a competitor's own marketing page, or",
                         self.doc)
        self.assertIn("does not verify what the vendor says about itself",
                      self.doc)

    def test_vendor_price_wording_is_the_same_in_every_file_that_uses_it(
            self):
        for path in self.FILES:
            text = read(path)
            with self.subTest(file=path.name):
                self.assertIn("vendor-published list price", text)
                self.assertIn("only when you examined the vendor's own page",
                              text)
                self.assertIn('"Vendor-published prices"', text)
                self.assertIn("separate ledger rows", text)


class TestScenarioFindings(unittest.TestCase):
    """Defects found by running each skill and agent on hypothetical
    scenarios (see docs/scenario-testing.md)."""

    def test_no_markdown_file_has_a_doubled_bullet_marker(self):
        files = (
            SKILLS + AGENTS + sorted((ROOT / "docs").rglob("*.md"))
            + [ROOT / "README.md", ROOT / "CONTRIBUTING.md"]
        )
        for path in files:
            with self.subTest(file=path.name):
                self.assertNotRegex(read(path), r"(?m)^\s*- - ")

    def test_break_even_output_states_its_rounding_mode(self):
        for command in (
            ("break-even", "1500", "149", "19.37"),
            ("break-even-loaded", "1500", "149", "19.37", "60"),
        ):
            with self.subTest(command=command[0]):
                note = cli_json(*command)["units_rounding"]
                self.assertIn("up", note)
                self.assertIn("whole units", note)

    def test_research_skills_say_read_only_research_needs_no_extra_approval(
            self):
        for name in ("idea-validator", "market-intelligence",
                     "competitor-intelligence"):
            text = read(ROOT / "skills" / name / "SKILL.md")
            with self.subTest(skill=name):
                self.assertRegex(
                    text, r"(?i)read-only public (web )?research")
                self.assertRegex(text, r"(?i)needs no separate approval")
                self.assertRegex(text, r"(?i)confidential")

    def test_loaded_break_even_guidance_is_the_same_in_skill_and_agent(self):
        skill = read(ROOT / "skills" / "unit-economics" / "SKILL.md")
        agent = read(ROOT / "agents" / "financial-analyst.md")
        for text, name in ((skill, "skill"), (agent, "agent")):
            with self.subTest(file=name):
                self.assertRegex(
                    text, r"not reachable on single purchases")
                self.assertRegex(text, r"(?i)do not invent")
                self.assertRegex(text, r"(?i)same money")
                self.assertRegex(text, r"(?i)which framing|framing each")

    def test_auditor_defines_internal_contradictions_and_url_fetching(self):
        text = read(ROOT / "agents" / "evidence-auditor.md")
        self.assertRegex(text, r"contradicts another claim in the same")
        self.assertIn("evidence is internal", text)
        self.assertRegex(text, r"(?i)fetching public URLs cited")
        self.assertIn("in the Audit Summary", text)

    def test_scenario_testing_record_exists_and_states_its_limits(self):
        text = read(ROOT / "docs" / "scenario-testing.md")
        for needle in ("hypothetical", "not native plugin loading",
                       "Limitations"):
            self.assertIn(needle, text)


if __name__ == "__main__":
    unittest.main()

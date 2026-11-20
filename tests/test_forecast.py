"""Tests for the forecasting calculator and the Phase 2 skills.

Standard library only. No network access. Expected values are worked out by
hand or with exact rational arithmetic, not copied from the code's output.
"""

import ast
import hashlib
import json
import random
import re
import subprocess
import sys
import tempfile
import unittest
from decimal import Decimal
from fractions import Fraction
from pathlib import Path

from scripts import forecast as fc
from scripts import validate_handoff as vh
from scripts.calculate import OPERATIONS
from scripts.calculator import ENGINE_VERSION

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "forecast.py"
EXAMPLE = ROOT / "docs" / "forecast-handoff.example.json"
SKILLS = ("scenario-comparison", "pricing-analysis")


def read(relative):
    return (ROOT / relative).read_text(encoding="utf-8")


def run_cli(*args, cwd=None):
    return subprocess.run(
        [sys.executable, "-B", str(SCRIPT), *args],
        capture_output=True, text=True, timeout=20, cwd=cwd, check=False,
    )


def cli_json(*args):
    result = run_cli(*args)
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


# Base case used by hand calculations: 100 units at $24 with $9.50 variable
# cost earn 2,400 - 950 = 1,450 a month, less 1,500 fixed and 600
# acquisition, so operating profit is -650 a month.
FLAT = ["5000", "3", "100", "0", "24", "9.50", "1500", "600"]


def forecast_of(values):
    return fc.run_forecast(fc.parse_parameters(values))


class TestMonthlyModel(unittest.TestCase):

    def test_flat_case_matches_the_hand_calculation(self):
        result = forecast_of(FLAT)
        profits = [row["operating_profit"] for row in result["months"]]
        cash = [row["ending_cash"] for row in result["months"]]
        self.assertEqual(profits, [Decimal(-650)] * 3)
        self.assertEqual(cash, [Decimal(4350), Decimal(3700), Decimal(3050)])
        summary = result["summary"]
        self.assertEqual(summary["total_revenue"], Decimal(7200))
        self.assertEqual(summary["total_operating_profit"], Decimal(-1950))
        self.assertEqual(summary["ending_cash"], Decimal(3050))
        self.assertEqual(summary["minimum_cash"], Decimal(3050))
        self.assertEqual(summary["minimum_cash_month"], 3)
        self.assertIsNone(summary["cash_out_month"])
        self.assertIsNone(summary["runway_months"])
        self.assertIsNone(summary["break_even_month"])

    def test_every_row_follows_the_stated_formulas(self):
        values = ["2000", "6", "50", "0.1", "10", "4", "100", "30"]
        rows = forecast_of(values)["months"]
        units = Fraction(50)
        cash = Fraction(2000)
        for row in rows:
            if row["month"] > 1:
                units *= Fraction(11, 10)
            profit = units * 10 - units * 4 - 30 - 100
            cash += profit
            self.assertAlmostEqual(float(row["units"]), float(units),
                                   places=9)
            self.assertAlmostEqual(float(row["operating_profit"]),
                                   float(profit), places=8)
            self.assertAlmostEqual(float(row["ending_cash"]), float(cash),
                                   places=8)

    def test_runway_is_whole_months_plus_the_share_of_the_last(self):
        # 1,000 of cash and a 650 monthly loss: 350 left after month 1, so
        # month 2 ends at -300 and the cash lasts 1 + 350/650 months.
        values = ["1000", "6", "100", "0", "24", "9.50", "1500", "600"]
        summary = forecast_of(values)["summary"]
        self.assertEqual(summary["cash_out_month"], 2)
        expected = 1 + Fraction(350, 650)
        self.assertAlmostEqual(float(summary["runway_months"]),
                               float(expected), places=12)

    def test_cash_is_allowed_to_go_negative_and_the_gap_is_visible(self):
        values = ["1000", "6", "100", "0", "24", "9.50", "1500", "600"]
        summary = forecast_of(values)["summary"]
        self.assertEqual(summary["ending_cash"], Decimal(1000 - 6 * 650))
        self.assertEqual(summary["minimum_cash"], summary["ending_cash"])

    def test_starting_with_no_cash_and_a_loss_gives_zero_runway(self):
        values = ["0", "3", "100", "0", "24", "9.50", "1500", "600"]
        summary = forecast_of(values)["summary"]
        self.assertEqual(summary["cash_out_month"], 1)
        self.assertEqual(summary["runway_months"], Decimal(0))

    def test_break_even_month_is_the_first_non_negative_profit(self):
        # Profit per month = 10 * units - 1000; units 50, 100, 200...
        values = ["5000", "5", "50", "1", "20", "10", "1000", "0"]
        summary = forecast_of(values)["summary"]
        self.assertEqual(summary["break_even_month"], 2)  # 100 * 10 = 1000
        first = forecast_of(values)["months"][1]
        self.assertEqual(first["operating_profit"], Decimal(0))

    def test_shrinking_and_zero_unit_businesses_work(self):
        values = ["1000", "4", "100", "-0.5", "10", "2", "0", "0"]
        units = [r["units"] for r in forecast_of(values)["months"]]
        self.assertEqual(units, [Decimal(100), Decimal(50), Decimal(25),
                                 Decimal("12.5")])
        zero = forecast_of(["1000", "2", "0", "0.5", "10", "2", "10", "0"])
        self.assertEqual(zero["summary"]["ending_cash"], Decimal(980))

    def test_a_single_month_horizon(self):
        summary = forecast_of(["100", "1", "10", "0.5", "5", "1", "10", "0"]
                              )["summary"]
        self.assertEqual(summary["months"], 1)
        self.assertEqual(summary["ending_cash"], Decimal(130))

    def test_the_longest_horizon_runs(self):
        values = ["1000", "120", "10", "0.01", "5", "1", "10", "0"]
        self.assertEqual(len(forecast_of(values)["months"]), 120)

    def test_acquisition_is_charged_once_per_month(self):
        low = forecast_of(["0", "1", "10", "0", "10", "0", "0", "0"])
        high = forecast_of(["0", "1", "10", "0", "10", "0", "0", "30"])
        difference = (low["summary"]["ending_cash"]
                      - high["summary"]["ending_cash"])
        self.assertEqual(difference, Decimal(30))

    def test_invariants_hold_for_random_valid_inputs(self):
        rng = random.Random(20261121)
        for _ in range(300):
            values = [
                str(rng.randint(0, 100000)), str(rng.randint(1, 60)),
                str(rng.randint(0, 5000)),
                str(Fraction(rng.randint(-50, 100), 100).__float__()),
                str(rng.randint(0, 500)), str(rng.randint(0, 300)),
                str(rng.randint(0, 20000)), str(rng.randint(0, 5000)),
            ]
            result = forecast_of(values)
            rows = result["months"]
            self.assertEqual(len(rows), int(values[1]))
            total = sum(r["operating_profit"] for r in rows)
            # Both sides round at 28 digits, so compare within a tiny margin.
            gap = abs(result["summary"]["ending_cash"]
                      - (Decimal(values[0]) + total))
            self.assertLess(gap, Decimal("0.000001"))
            for before, after in zip(rows, rows[1:]):
                self.assertEqual(after["opening_cash"],
                                 before["ending_cash"])
            lowest = min(r["ending_cash"] for r in rows)
            self.assertEqual(result["summary"]["minimum_cash"], lowest)


class TestInputValidation(unittest.TestCase):

    def rejects(self, values, fragment):
        with self.assertRaisesRegex(ValueError, fragment):
            fc.parse_parameters(values)

    def test_months_must_be_a_whole_number_in_range(self):
        self.rejects(FLAT[:1] + ["0"] + FLAT[2:], "from 1 to 120")
        self.rejects(FLAT[:1] + ["121"] + FLAT[2:], "from 1 to 120")
        self.rejects(FLAT[:1] + ["12.5"] + FLAT[2:], "whole number")
        self.rejects(FLAT[:1] + ["-3"] + FLAT[2:], "from 1 to 120")

    def test_growth_must_be_a_sensible_fraction(self):
        for bad in ("1.01", "-0.991", "5", "-1"):
            self.rejects(FLAT[:3] + [bad] + FLAT[4:], "Monthly unit growth")
        for good in ("-0.99", "1", "0", "0.03"):
            fc.parse_parameters(FLAT[:3] + [good] + FLAT[4:])

    def test_money_and_units_cannot_be_negative(self):
        for index in (0, 2, 4, 5, 6, 7):
            values = list(FLAT)
            values[index] = "-1"
            self.rejects(values, "cannot be negative")

    def test_calculator_input_rules_apply(self):
        for bad in ("1_000", "٣", " 5", "NaN", "1e999999999", "1" * 70,
                    "1000000000001", "0.0000000001"):
            values = list(FLAT)
            values[4] = bad
            with self.assertRaises(ValueError):
                fc.parse_parameters(values)

    def test_the_wrong_number_of_inputs_is_rejected(self):
        self.rejects(FLAT[:7], "Expected 8 inputs")

    def test_absurd_results_are_rejected_not_printed(self):
        values = ["0", "120", "1000000000000", "1", "1000000000000", "0",
                  "0", "0"]
        with self.assertRaisesRegex(ValueError, "supported range"):
            forecast_of(values)


class TestScenarioComparison(unittest.TestCase):

    CONSERVATIVE = ["5000", "12", "80", "0.01", "24", "9.50", "1500", "600"]
    BASE = ["5000", "12", "100", "0.03", "24", "9.50", "1500", "600"]

    def compare(self, *scenarios):
        return fc.scenario_compare(list(scenarios))[0]

    def test_it_reports_exactly_which_inputs_differ(self):
        result = self.compare(("conservative", self.CONSERVATIVE),
                              ("base", self.BASE))
        self.assertEqual(result["varied_inputs"],
                         ["starting_units", "monthly_unit_growth"])

    def test_each_scenario_matches_its_own_forecast(self):
        result = self.compare(("conservative", self.CONSERVATIVE),
                              ("base", self.BASE))
        for scenario, values in zip(result["scenarios"],
                                    (self.CONSERVATIVE, self.BASE)):
            self.assertEqual(scenario["summary"],
                             forecast_of(values)["summary"])

    def test_differences_are_measured_from_the_first_scenario(self):
        result = self.compare(("conservative", self.CONSERVATIVE),
                              ("base", self.BASE))
        low = result["scenarios"][0]["summary"]["ending_cash"]
        high = result["scenarios"][1]["summary"]["ending_cash"]
        self.assertEqual(
            result["differences_from_first"][0]["ending_cash_difference"],
            high - low)

    def test_ordering_is_by_ending_cash_with_name_as_the_tie_break(self):
        result = self.compare(("zeta", self.BASE), ("alpha", self.BASE),
                              ("low", self.CONSERVATIVE))
        self.assertEqual(result["ordering_by_ending_cash"],
                         ["alpha", "zeta", "low"])

    def test_no_scenario_is_labeled_likely_and_no_probability_appears(self):
        text = json.dumps(self.compare(("a", self.BASE),
                                       ("b", self.CONSERVATIVE)), default=str)
        for word in ("expected", "likely", "probab", "forecasted"):
            self.assertNotIn(word, text.lower())

    def test_scenarios_must_share_the_horizon(self):
        other = list(self.BASE)
        other[1] = "24"
        with self.assertRaisesRegex(ValueError, "same number of months"):
            self.compare(("a", self.BASE), ("b", other))

    def test_scenario_count_and_names_are_checked(self):
        with self.assertRaisesRegex(ValueError, "2 to 5"):
            self.compare(("only", self.BASE))
        six = [(f"s{i}", self.BASE) for i in range(6)]
        with self.assertRaisesRegex(ValueError, "2 to 5"):
            self.compare(*six)
        for bad in ("Base", "1base", "a b", "a" * 31, "", "a;b"):
            with self.assertRaisesRegex(ValueError, "names"):
                self.compare((bad, self.BASE), ("ok", self.BASE))
        with self.assertRaisesRegex(ValueError, "unique"):
            self.compare(("a", self.BASE), ("a", self.CONSERVATIVE))

    def test_identical_scenarios_report_no_variation(self):
        result = self.compare(("a", self.BASE), ("b", self.BASE))
        self.assertEqual(result["varied_inputs"], [])


class TestSensitivity(unittest.TestCase):

    BASE = ["5000", "12", "100", "0.03", "24", "9.50", "1500", "600"]

    def run_sensitivity(self, deltas=("10",), vary=None):
        return fc.sensitivity(self.BASE, list(deltas), vary)[0]

    def test_each_row_changes_exactly_one_input(self):
        result = self.run_sensitivity(("10",), ["price"])
        base = forecast_of(self.BASE)["summary"]["ending_cash"]
        by_sign = {r["change_percent"]: r for r in result["rows"]}
        self.assertEqual(set(by_sign), {"-10", "+10"})
        for text, factor in (("-10", Decimal("0.9")),
                             ("+10", Decimal("1.1"))):
            changed = list(self.BASE)
            changed[4] = str(Decimal("24") * factor)
            expected = forecast_of(changed)["summary"]["ending_cash"]
            self.assertEqual(by_sign[text]["ending_cash"], expected)
            self.assertEqual(by_sign[text]["ending_cash_change"],
                             expected - base)

    def test_the_base_summary_is_the_unchanged_forecast(self):
        result = self.run_sensitivity()
        self.assertEqual(result["base_summary"],
                         forecast_of(self.BASE)["summary"])

    def test_rows_cover_every_varied_input_delta_and_direction(self):
        result = self.run_sensitivity(("10", "20"))
        self.assertEqual(len(result["rows"]),
                         len(fc.VARIABLE_PARAMETERS) * 2 * 2)

    def test_ranking_orders_inputs_by_their_largest_effect(self):
        ranking = self.run_sensitivity(("10", "20"))[
            "ranking_by_ending_cash_change"]
        swings = [r["largest_ending_cash_change"] for r in ranking]
        self.assertEqual(swings, sorted(swings, reverse=True))
        self.assertEqual(sorted(r["parameter"] for r in ranking),
                         sorted(fc.VARIABLE_PARAMETERS))

    def test_a_zero_base_value_is_reported_not_silently_ignored(self):
        values = list(self.BASE)
        values[7] = "0"
        result = fc.sensitivity(values, ["10"], ["acquisition_spend"])[0]
        self.assertTrue(any("acquisition_spend" in n and "0" in n
                            for n in result["notes"]))
        self.assertEqual({r["ending_cash_change"] for r in result["rows"]},
                         {Decimal(0)})

    def test_the_horizon_cannot_be_varied(self):
        with self.assertRaisesRegex(ValueError, "Cannot vary"):
            self.run_sensitivity(("10",), ["months"])

    def test_deltas_are_checked(self):
        for bad in (["0"], ["-5"], ["101"], ["10", "10"],
                    [str(i) for i in range(1, 7)]):
            with self.assertRaises(ValueError):
                fc.sensitivity(self.BASE, bad)

    def test_a_change_that_makes_an_input_invalid_is_an_error_naming_it(self):
        with self.assertRaisesRegex(ValueError, "monthly_unit_growth"):
            fc.sensitivity(self.BASE[:3] + ["0.6"] + self.BASE[4:], ["100"],
                           ["monthly_unit_growth"])


class TestPriceComparison(unittest.TestCase):

    # variable 9.50, fixed 1,500, CAC 12, 100 units, prices 24, 29, 34.
    def rows(self, *extra):
        values = ["9.50", "1500", "12", "100", "24", "29", "34", *extra]
        return fc.price_compare(values)[0]["prices"]

    def test_values_match_the_hand_calculation(self):
        first, second, third = self.rows()
        # Contribution 14.50, loaded 2.50, break-even 1500/14.5 -> 104 and
        # 1500/2.5 -> 600, profit at 100 units 100 * 2.5 - 1500 = -1250.
        self.assertEqual(first["contribution_per_unit"], Decimal("14.50"))
        self.assertEqual(first["loaded_contribution_per_unit"],
                         Decimal("2.50"))
        self.assertEqual(first["break_even_units_excluding_acquisition"],
                         104)
        self.assertEqual(first["break_even_units_including_acquisition"],
                         600)
        self.assertEqual(first["operating_profit_at_expected_units"],
                         Decimal(-1250))
        self.assertEqual(first["revenue_at_expected_units"], Decimal(2400))
        self.assertEqual(second["loaded_contribution_per_unit"],
                         Decimal("7.50"))
        self.assertEqual(second["break_even_units_including_acquisition"],
                         200)
        self.assertEqual(third["operating_profit_at_expected_units"],
                         Decimal(-250))

    def test_units_needed_to_match_the_first_price_profit(self):
        first, second, third = self.rows()
        # Contribution to match at the first price: 100 * 2.5 = 250.
        self.assertEqual(first["units_needed_to_match_first_price_profit"],
                         100)
        self.assertEqual(second["units_needed_to_match_first_price_profit"],
                         34)  # ceil(250 / 7.5)
        self.assertEqual(third["units_needed_to_match_first_price_profit"],
                         20)  # 250 / 12.5

    def test_a_price_that_cannot_cover_cost_has_no_break_even(self):
        result = fc.price_compare(["9.50", "1500", "12", "100", "9", "20"]
                                  )[0]["prices"]
        self.assertIsNone(result[0]["break_even_units_excluding_acquisition"])
        self.assertIsNone(result[0]["break_even_units_including_acquisition"])
        self.assertIsNone(
            result[0]["units_needed_to_match_first_price_profit"])
        self.assertEqual(result[0]["contribution_per_unit"], Decimal("-0.5"))

    def test_the_constant_volume_assumption_is_stated_in_the_result(self):
        result, _ = fc.price_compare(["9.50", "1500", "12", "100", "24"])
        self.assertIs(result["assumes_constant_volume"], True)
        self.assertIs(result["assumes_one_purchase_per_customer"], True)
        self.assertIs(result["fixed_costs_exclude_acquisition"], True)

    def test_a_zero_price_has_no_margin_percent(self):
        result = fc.price_compare(["0", "100", "0", "10", "0"])[0]["prices"]
        self.assertIsNone(result[0]["contribution_margin_percent"])

    def test_the_number_of_prices_is_limited(self):
        with self.assertRaisesRegex(ValueError, "from 1 to 8"):
            fc.price_compare(["1", "1", "0", "1"])
        with self.assertRaisesRegex(ValueError, "from 1 to 8"):
            fc.price_compare(["1", "1", "0", "1"] + ["5"] * 9)


class TestReceipts(unittest.TestCase):

    def test_the_fingerprint_is_deterministic(self):
        first = cli_json("monthly-forecast", *FLAT)
        second = cli_json("monthly-forecast", *FLAT)
        self.assertEqual(first, second)
        self.assertEqual(first["receipt"]["fingerprint"],
                         second["receipt"]["fingerprint"])

    def test_any_input_change_changes_the_fingerprint(self):
        base = cli_json("monthly-forecast", *FLAT)["receipt"]["fingerprint"]
        for index in range(8):
            values = list(FLAT)
            values[index] = str(Decimal(values[index]) + 1)
            changed = cli_json("monthly-forecast", *values)
            self.assertNotEqual(changed["receipt"]["fingerprint"], base,
                                index)

    def test_the_fingerprint_can_be_recomputed_from_the_receipt(self):
        receipt = cli_json("monthly-forecast", *FLAT)["receipt"]
        payload = {
            "operation": receipt["operation"], "model": receipt["model"],
            "engine_version": receipt["engine_version"],
            "inputs": [[i["name"], i["value"]] for i in receipt["inputs"]],
        }
        canonical = json.dumps(payload, sort_keys=True,
                               separators=(",", ":"))
        digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        self.assertEqual(receipt["fingerprint"], f"sha256:{digest}")

    def test_the_receipt_records_inputs_assumptions_and_exclusions(self):
        output = cli_json("monthly-forecast", *FLAT)
        receipt = output["receipt"]
        self.assertEqual([i["name"] for i in receipt["inputs"]],
                         list(fc.PARAMETERS))
        self.assertEqual([i["value"] for i in receipt["inputs"]], FLAT)
        self.assertEqual(receipt["engine_version"], ENGINE_VERSION)
        self.assertEqual(receipt["model"], fc.MODEL)
        self.assertTrue(any("counted once" in a
                            for a in receipt["assumptions"]))
        self.assertTrue(any("go below zero" in a
                            for a in receipt["assumptions"]))
        for item in ("taxes", "capital expenditures",
                     "working capital and payment timing", "seasonality"):
            self.assertIn(item, receipt["exclusions"])
        self.assertEqual(output["version"], ENGINE_VERSION)

    def test_the_price_receipt_states_the_demand_assumption(self):
        receipt = cli_json("price-compare", "9.50", "1500", "12", "100",
                           "24", "29")["receipt"]
        self.assertTrue(any("Demand does not respond to price" in a
                            for a in receipt["assumptions"]))

    def test_every_operation_has_a_distinct_fingerprint_namespace(self):
        a = fc.make_receipt("monthly-forecast", [("x", "1")])
        b = fc.make_receipt("sensitivity", [("x", "1")])
        self.assertNotEqual(a["fingerprint"], b["fingerprint"])


class TestCommandLine(unittest.TestCase):

    def test_each_operation_runs_by_path_with_the_documented_shape(self):
        base = ["5000", "12", "100", "0.03", "24", "9.50", "1500", "600"]
        outputs = {
            "monthly-forecast": cli_json("monthly-forecast", *base),
            "scenario-compare": cli_json(
                "scenario-compare", "--scenario", "a", *base,
                "--scenario", "b", *base),
            "sensitivity": cli_json("sensitivity", *base, "--delta", "10"),
            "price-compare": cli_json("price-compare", "9.5", "1500", "12",
                                      "100", "24", "29"),
        }
        for operation, output in outputs.items():
            self.assertEqual(output["operation"], operation)
            self.assertEqual(output["engine"], "venturine")
            self.assertEqual(output["status"], "calculated")
            self.assertIn("fingerprint", output["receipt"])
            self.assertIn("display_rounding", output)

    def test_runs_from_an_unrelated_directory_and_ignores_a_decoy(self):
        with tempfile.TemporaryDirectory() as other:
            package = Path(other) / "scripts"
            package.mkdir()
            for name in ("__init__.py", "calculator.py", "calculate.py"):
                (package / name).write_text("raise SystemExit(99)\n")
            result = run_cli("monthly-forecast", *FLAT, cwd=other)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_bad_input_exits_two_with_no_traceback(self):
        cases = [
            ["monthly-forecast", *FLAT[:7]],
            ["monthly-forecast"],
            ["sensitivity", *FLAT[:7], "--delta", "10"],
            ["monthly-forecast", "5000", "0", *FLAT[2:]],
            ["monthly-forecast", *FLAT[:3], "9", *FLAT[4:]],
            ["monthly-forecast", *FLAT[:4], "1_000", *FLAT[5:]],
            ["scenario-compare", "--scenario", "a", *FLAT],
            ["sensitivity", *FLAT, "--delta", "0"],
            ["sensitivity", *FLAT, "--delta", "10", "--vary", "months"],
            ["price-compare", "1", "1"],
            ["nonsense"], [],
        ]
        for args in cases:
            result = run_cli(*args)
            self.assertEqual(result.returncode, 2, args)
            self.assertNotIn("Traceback", result.stderr, args)

    def test_output_never_uses_exponent_notation_or_negative_zero(self):
        values = ["0", "1", "1000000000000", "0", "1000000000000", "0",
                  "0", "0"]
        text = run_cli("monthly-forecast", *values).stdout
        result = json.dumps(json.loads(text)["result"])
        self.assertIn("1000000000000000000000000.00", result)
        self.assertNotRegex(result, r"\d[eE][+-]?\d")
        self.assertNotIn('"-0', result)

    def test_help_documents_the_operations(self):
        result = run_cli("--help")
        self.assertEqual(result.returncode, 0)
        for name in ("monthly-forecast", "scenario-compare", "sensitivity",
                     "price-compare"):
            self.assertIn(name, result.stdout)
        self.assertIn("Count acquisition exactly once", result.stdout)

    def test_the_original_calculator_is_unchanged(self):
        self.assertEqual(
            set(OPERATIONS),
            {"revenue", "gross-margin", "contribution-margin", "break-even",
             "break-even-loaded", "operating-profit", "cac", "runway",
             "subscription-ltv"})
        self.assertEqual(ENGINE_VERSION, "0.2.1")


class TestForecastHasNoSideEffects(unittest.TestCase):

    def setUp(self):
        self.source = read("scripts/forecast.py")
        self.tree = ast.parse(self.source)

    def test_imports_are_limited(self):
        imported = set()
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Import):
                imported.update(a.name.split(".")[0] for a in node.names)
            elif isinstance(node, ast.ImportFrom):
                imported.add((node.module or "").split(".")[0])
        self.assertEqual(
            imported,
            {"argparse", "hashlib", "json", "re", "decimal", "calculator",
             "calculate"})

    def test_no_file_access_network_or_dynamic_execution(self):
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                self.assertNotIn(
                    node.func.id,
                    {"open", "exec", "eval", "compile", "__import__",
                     "input", "getattr", "setattr"})
        for pattern in (r"\.write\(", r"\.read\(", r"\bos\.", r"subprocess",
                        r"\bsocket\b", r"urllib", r"\brandom\b",
                        r"\btime\.[a-z]", r"\bdatetime\b"):
            self.assertNotRegex(self.source, pattern)


class TestHandoffIntegration(unittest.TestCase):

    def example(self):
        return json.loads(EXAMPLE.read_text(encoding="utf-8"))

    def test_the_example_handoff_is_valid(self):
        result = vh.validate(self.example())
        self.assertTrue(result["valid"], result["errors"])
        self.assertEqual(result["warnings"], [])

    def test_its_receipt_is_the_one_a_fresh_run_prints(self):
        document = self.example()
        calc = document["calculations"][0]
        values = [item["value"] for item in calc["inputs"]]
        output = cli_json("monthly-forecast", *values)
        self.assertEqual(calc["receipt"], output["receipt"]["fingerprint"])
        self.assertEqual(calc["engine_version"], output["version"])
        summary = output["result"]["summary"]
        self.assertEqual(calc["result"], summary)

    def test_every_input_is_labeled_and_guesses_are_assumptions(self):
        document = self.example()
        labels = {e["id"]: e["label"] for e in document["evidence_ledger"]}
        calc = document["calculations"][0]
        self.assertEqual([i["name"] for i in calc["inputs"]],
                         list(fc.PARAMETERS))
        for item in calc["inputs"]:
            self.assertIn(labels[item["evidence"]],
                          {"FOUNDER_PROVIDED", "ASSUMPTION", "VERIFIED"})
        self.assertEqual(labels["E9"], "DERIVED")
        self.assertIs(calc["acquisition_counted_once"], True)

    def test_the_validator_and_the_calculator_agree_on_the_operations(self):
        self.assertEqual(
            set(vh.FORECAST_OPERATIONS),
            {"monthly-forecast", "scenario-compare", "sensitivity",
             "price-compare", "channel-compare"})
        self.assertEqual(vh.FORECAST_OPERATIONS["monthly-forecast"],
                         (len(fc.PARAMETERS), len(fc.PARAMETERS)))
        low, high = vh.FORECAST_OPERATIONS["scenario-compare"]
        self.assertEqual(low, fc.MIN_SCENARIOS * len(fc.PARAMETERS))
        self.assertEqual(high, fc.MAX_SCENARIOS * len(fc.PARAMETERS))
        low, high = vh.FORECAST_OPERATIONS["sensitivity"]
        self.assertEqual((low, high),
                         (len(fc.PARAMETERS) + 1,
                          len(fc.PARAMETERS) + fc.MAX_DELTAS))
        self.assertEqual(vh.FORECAST_OPERATIONS["price-compare"],
                         (5, 4 + fc.MAX_PRICES))
        self.assertEqual(vh.FORECAST_OPERATIONS["channel-compare"],
                         (4, 2 + 2 * fc.MAX_CHANNELS))

    def test_an_engine_validated_forecast_needs_its_receipt(self):
        document = self.example()
        del document["calculations"][0]["receipt"]
        result = vh.validate(document)
        self.assertTrue(any("needs the receipt" in e
                            for e in result["errors"]))

    def test_a_receipt_is_refused_on_a_result_that_was_not_validated(self):
        document = self.example()
        calc = document["calculations"][0]
        calc["engine_validated"] = False
        del calc["engine_version"]
        calc["method"] = "By hand"
        result = vh.validate(document)
        self.assertTrue(any("only an engine-validated" in e
                            for e in result["errors"]))

    def test_a_malformed_receipt_is_rejected(self):
        for bad in ("abc", "sha256:xyz", "sha256:" + "A" * 64,
                    "sha256:" + "a" * 63, "md5:" + "a" * 32):
            document = self.example()
            document["calculations"][0]["receipt"] = bad
            self.assertFalse(vh.validate(document)["valid"], bad)

    def test_acquisition_must_be_counted_once_for_forecasts(self):
        document = self.example()
        document["calculations"][0]["acquisition_counted_once"] = False
        result = vh.validate(document)
        self.assertTrue(any("exactly once" in e for e in result["errors"]))

    def test_the_input_count_is_checked_for_forecast_operations(self):
        document = self.example()
        document["calculations"][0]["inputs"].pop()
        self.assertTrue(any("takes from 8 to 8 inputs" in e
                            for e in vh.validate(document)["errors"]))

    def test_older_handoffs_remain_valid(self):
        old = json.loads(read("docs/handoff-v1.example.json"))
        self.assertTrue(vh.validate(old)["valid"])
        self.assertNotIn("receipt", old["calculations"][0])


class TestPhase2Skills(unittest.TestCase):

    def text(self, name):
        return read(f"skills/{name}/SKILL.md")

    def test_the_skills_exist_with_complete_frontmatter(self):
        for name in SKILLS:
            text = self.text(name)
            match = re.match(r"^---\nname: ([^\n]+)\ndescription: ([^\n]+)\n"
                             r"---\n", text)
            self.assertTrue(match, name)
            self.assertEqual(match.group(1), name)
            self.assertGreater(len(match.group(2)), 80)
            self.assertLess(len(match.group(2)), 500)

    def test_documented_commands_use_the_path_form_and_really_run(self):
        pattern = re.compile(
            r'python3 "\$\{CLAUDE_PLUGIN_ROOT\}/scripts/'
            r'(forecast|calculate)\.py" ([^`\n]+)')
        for name in SKILLS:
            commands = pattern.findall(self.text(name))
            self.assertTrue(commands, name)
            for script, args in commands:
                result = subprocess.run(
                    [sys.executable, "-B",
                     str(ROOT / "scripts" / f"{script}.py"),
                     *args.split()],
                    capture_output=True, text=True, timeout=20, cwd=ROOT,
                    check=False)
                self.assertEqual(result.returncode, 0,
                                 f"{name}: {script} {args}: {result.stderr}")
            self.assertNotIn("python3 -m scripts", self.text(name))

    def test_both_skills_cover_every_forecast_operation_between_them(self):
        combined = (self.text("scenario-comparison")
                    + self.text("pricing-analysis")
                    + self.text("go-to-market"))
        for operation in vh.FORECAST_OPERATIONS:
            self.assertIn(f"forecast.py\" {operation} ", combined)

    def test_the_skills_never_predict_or_invent(self):
        scenario = self.text("scenario-comparison")
        self.assertIn("A scenario is a set of assumptions, not a prediction",
                      scenario)
        self.assertIn("never invent a financial figure", scenario)
        self.assertIn("Do not assign probabilities to scenarios", scenario)
        self.assertIn("Do not make up conservative or optimistic values",
                      scenario)
        self.assertIn("A value that differs between scenarios is an "
                      "ASSUMPTION", scenario)
        pricing = self.text("pricing-analysis")
        self.assertIn("does not predict how many customers will buy at "
                      "each price", pricing)
        self.assertIn("Do not state or imply a demand response without "
                      "evidence", pricing)
        self.assertIn("Never invent a financial figure, a competitor "
                      "price, or a willingness to pay", pricing)

    def test_failure_handling_never_fabricates_output_or_receipts(self):
        for name in SKILLS:
            text = self.text(name)
            self.assertIn("Do not fabricate JSON output", text)
            self.assertIn("receipt", text.split("Do not fabricate JSON "
                                                "output", 1)[1][:120])
            self.assertIn("manual calculation, not engine-validated", text)

    def test_acquisition_is_counted_once_in_both_skills(self):
        for name in SKILLS:
            self.assertIn("exactly once", self.text(name))

    def test_script_execution_is_limited_to_the_calculators(self):
        for name in SKILLS:
            text = self.text(name)
            self.assertIn("The documented Venturine calculators "
                          "(`calculate.py` and `forecast.py`) are the only "
                          "permitted script exception", text)
            self.assertIn("explicit user authorization", text)
            self.assertIn("Do not chain commands with pipes, redirection or "
                          "command substitution", text)
            self.assertIn("Never pass secrets, credentials or personal data "
                          "as arguments", text)

    def test_the_vendor_price_rule_is_in_the_pricing_skill(self):
        text = self.text("pricing-analysis")
        self.assertIn("vendor-published list price", text)
        self.assertIn("only when you examined the vendor's own page", text)
        self.assertIn('"Vendor-published prices"', text)

    def test_the_handoff_guidance_matches_the_validator_rules(self):
        for name in SKILLS:
            text = self.text(name)
            self.assertIn("## Handoff Calculations", text)
            self.assertIn("copy `engine_version` and the `receipt` "
                          "fingerprint exactly as printed", text)
            self.assertIn("set `acquisition_counted_once` to true", text)
            self.assertIn("`engine_validated` to true only if the "
                          "calculator actually ran", text)

    def test_the_new_skills_are_named_in_the_readme_and_intake(self):
        readme = read("README.md")
        intake = self.text("venture-intake")
        for name in SKILLS:
            self.assertIn(f"`{name}`", readme)
            self.assertIn(f"`{name}`", intake)
        self.assertIn("scenario-comparison", self.text("unit-economics"))

    def test_the_forecasting_documentation_is_complete(self):
        text = read("docs/forecasting.md")
        for needle in ("Deterministic", "calculation receipt",
                       "does not predict", "enters exactly once",
                       "does not predict how demand responds to price",
                       "Cash is allowed to go below zero",
                       "Repeat purchases and customer lifetime value are "
                       "not modeled"):
            self.assertIn(needle, text.replace("Calculation receipts",
                                               "calculation receipt"))
        for name in ("monthly-forecast", "scenario-compare", "sensitivity",
                     "price-compare"):
            self.assertIn(name, text)

    def test_documented_forecast_commands_in_the_docs_run(self):
        pattern = re.compile(r"^python3 scripts/forecast\.py (.+)$", re.M)
        for relative in ("docs/forecasting.md", "docs/examples.md"):
            commands = pattern.findall(read(relative))
            self.assertTrue(commands, relative)
            for args in commands:
                result = run_cli(*args.split(), cwd=ROOT)
                self.assertEqual(result.returncode, 0,
                                 f"{relative}: {args}: {result.stderr}")

    def test_numbers_quoted_in_the_examples_match_the_calculator(self):
        text = read("docs/examples.md")
        result = cli_json(
            "scenario-compare", "--scenario", "conservative", "5000", "12",
            "80", "0.01", "24", "9.50", "1500", "600", "--scenario", "base",
            "5000", "12", "100", "0.03", "24", "9.50", "1500", "600")
        summaries = {s["name"]: s["summary"] for s in result["result"][
            "scenarios"]}
        self.assertIn(f"${summaries['base']['ending_cash']}", text)
        self.assertIn(f"month {summaries['conservative']['cash_out_month']}",
                      text)


if __name__ == "__main__":
    unittest.main()

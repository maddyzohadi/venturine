
import contextlib
import decimal
import io
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "calculate.py"


class TestCalculatorCLI(unittest.TestCase):

    def run_calculator(self, *args):
        return subprocess.run(
            [
                sys.executable,
                "-m",
                "scripts.calculate",
                *args,
            ],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )

    def test_revenue(self):
        result = self.run_calculator(
            "revenue", "100", "29.99"
        )
        self.assertEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        self.assertEqual(data["result"], "2999.00")
        self.assertEqual(data["status"], "calculated")
        self.assertEqual(data["version"], "0.2.1")

    def test_gross_margin(self):
        result = self.run_calculator(
            "gross-margin", "10000", "4000"
        )
        self.assertEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        self.assertEqual(
            data["result"]["gross_profit"], "6000"
        )
        self.assertEqual(
            data["result"]["gross_margin_percent"], "60.0"
        )

    def test_contribution_margin(self):
        result = self.run_calculator(
            "contribution-margin", "75", "25"
        )
        self.assertEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        self.assertEqual(data["result"], "50")

    def test_break_even(self):
        result = self.run_calculator(
            "break-even", "101", "50", "20"
        )
        self.assertEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        self.assertEqual(data["result"], 4)

    def test_cac(self):
        result = self.run_calculator(
            "cac", "1200", "30"
        )
        self.assertEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        self.assertEqual(data["result"], "40")

    def test_runway(self):
        result = self.run_calculator(
            "runway", "15000", "3000"
        )
        self.assertEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        self.assertEqual(data["result"], "5")

    def test_subscription_ltv(self):
        result = self.run_calculator(
            "subscription-ltv", "30", "0.05"
        )
        self.assertEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        self.assertEqual(
            data["result"], "6E+2"
        )

    def test_invalid_operation(self):
        result = self.run_calculator("unknown", "10", "20")
        self.assertNotEqual(result.returncode, 0)

    def test_missing_inputs(self):
        result = self.run_calculator("revenue", "100")
        self.assertNotEqual(result.returncode, 0)

    def test_invalid_number(self):
        result = self.run_calculator(
            "revenue", "invalid", "20"
        )
        self.assertNotEqual(result.returncode, 0)

    def test_zero_customers(self):
        result = self.run_calculator("cac", "1200", "0")
        self.assertNotEqual(result.returncode, 0)

    def test_break_even_legacy_flags_acquisition_excluded(self):
        result = self.run_calculator(
            "break-even", "1500", "149", "19.37"
        )
        self.assertEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        self.assertEqual(data["result"], 12)
        self.assertFalse(data["acquisition_included"])
        self.assertIn("break-even-loaded", data["warning"])

    def test_break_even_loaded(self):
        result = self.run_calculator(
            "break-even-loaded", "1500", "149", "19.37", "60"
        )
        self.assertEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        self.assertEqual(data["operation"], "break-even-loaded")
        self.assertEqual(data["result"]["break_even_units"], 22)
        self.assertEqual(
            data["result"]["loaded_contribution_per_unit"], "69.63"
        )
        self.assertTrue(data["result"]["acquisition_included"])

    def test_break_even_loaded_cac_too_high(self):
        result = self.run_calculator(
            "break-even-loaded", "1000", "100", "20", "80"
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("acquisition", result.stderr)

    def test_break_even_loaded_wrong_arg_count(self):
        result = self.run_calculator(
            "break-even-loaded", "1500", "149", "19.37"
        )
        self.assertNotEqual(result.returncode, 0)

    def test_operating_profit(self):
        result = self.run_calculator(
            "operating-profit", "14900", "0", "1937", "6000", "1500"
        )
        self.assertEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        self.assertEqual(
            data["result"]["operating_profit"], "5463"
        )
        self.assertEqual(data["result"]["acquisition"], "6000")
        self.assertEqual(data["result"]["total_costs"], "9437")

    def test_operating_profit_zero_revenue_margin_null(self):
        result = self.run_calculator(
            "operating-profit", "0", "0", "0", "0", "1500"
        )
        self.assertEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        self.assertIsNone(data["result"]["operating_margin_percent"])

    def test_operating_profit_requires_all_categories(self):
        result = self.run_calculator(
            "operating-profit", "1000", "0", "0", "100"
        )
        self.assertNotEqual(result.returncode, 0)

    def test_operating_profit_negative_rejected(self):
        result = self.run_calculator(
            "operating-profit", "1000", "0", "-5", "0", "0"
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("cannot be negative", result.stderr)

    def test_huge_exponent_rejected_quickly(self):
        result = self.run_calculator(
            "break-even", "1E999999999", "50", "20"
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("exceed", result.stderr)

    def test_shell_metacharacters_rejected_as_numbers(self):
        result = self.run_calculator("revenue", "1;ls", "5")
        self.assertNotEqual(result.returncode, 0)

    def test_all_original_operations_still_listed(self):
        for operation in (
            "revenue", "gross-margin", "contribution-margin",
            "break-even", "cac", "runway", "subscription-ltv",
        ):
            result = self.run_calculator(operation, "--help")
            self.assertEqual(result.returncode, 0, operation)


class TestRunByScriptPath(unittest.TestCase):
    """Regression tests for the audit finding on working-directory
    shadowing (H1). The documented command is run by file path, so a
    "scripts" package in the caller's directory must never be used."""

    def run_script(self, *args, cwd=None, extra_env=None):
        env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
        env.update(extra_env or {})
        return subprocess.run(
            [sys.executable, "-B", str(SCRIPT), *args],
            capture_output=True, text=True, timeout=20,
            cwd=cwd, env=env, check=False,
        )

    def test_runs_by_path_from_repo_root(self):
        result = self.run_script("revenue", "100", "29.99", cwd=ROOT)
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data["result"], "2999.00")
        self.assertEqual(data["engine"], "venturine")

    def test_runs_by_path_from_unrelated_directory(self):
        with tempfile.TemporaryDirectory() as other:
            result = self.run_script("revenue", "2", "5", cwd=other)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["result"], "10")

    def test_decoy_scripts_package_in_cwd_is_ignored(self):
        with tempfile.TemporaryDirectory() as decoy:
            package = Path(decoy) / "scripts"
            package.mkdir()
            marker = "SHADOWED-BY-DECOY"
            for name in ("calculate.py", "calculator.py", "__init__.py"):
                (package / name).write_text(f'print("{marker}")\n')
            (Path(decoy) / "calculator.py").write_text(
                f'print("{marker}")\n'
            )
            result = self.run_script("revenue", "1", "2", cwd=decoy)
        self.assertNotIn(marker, result.stdout + result.stderr)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["engine"], "venturine")

    def test_decoy_does_not_win_even_with_pythonpath_set_to_cwd(self):
        with tempfile.TemporaryDirectory() as decoy:
            (Path(decoy) / "calculator.py").write_text(
                'print("SHADOWED-BY-DECOY")\n'
            )
            result = self.run_script(
                "revenue", "1", "2", cwd=decoy,
                extra_env={"PYTHONPATH": decoy},
            )
        self.assertNotIn("SHADOWED-BY-DECOY", result.stdout)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_script_and_module_forms_agree(self):
        by_path = self.run_script("break-even-loaded", "1500", "149",
                                  "19.37", "60", cwd=ROOT)
        by_module = subprocess.run(
            [sys.executable, "-B", "-m", "scripts.calculate",
             "break-even-loaded", "1500", "149", "19.37", "60"],
            capture_output=True, text=True, timeout=20, cwd=ROOT,
            check=False,
        )
        self.assertEqual(by_path.returncode, 0)
        self.assertEqual(by_path.stdout, by_module.stdout)


class TestNoTracebacks(unittest.TestCase):
    """Regression tests for the audit finding on uncaught exceptions and
    runaway CPU use (H2). Every failure must be a clean argparse error."""

    FUZZ = [
        ("runway", "15000", "1E-999999"),
        ("runway", "15000", "1E-999990"),
        ("runway", "15000", "1E-10"),
        ("cac", "1", "1E-999990"),
        ("cac", "1", "1E-999999999999"),
        ("subscription-ltv", "30", "1E-999990"),
        ("subscription-ltv", "30", "1E-999999999"),
        ("break-even", "1", "1E-999990", "0"),
        ("break-even", "1", "1E-999900", "0"),
        ("break-even", "1", "1E-99990", "0"),
        ("break-even", "1E12", "1.000000001", "1"),
        ("break-even", "1", "1.0000000000000000000000000002", "1"),
        ("break-even-loaded", "1", "1E-999990", "0", "0"),
        ("break-even-loaded", "1E12", "1", "0", "0.999999999"),
        ("revenue", "1E999999999", "2"),
        ("revenue", "1E-999999999999999999999", "2"),
        ("gross-margin", "1E-999999", "0"),
        ("operating-profit", "1E-999999", "0", "0", "0", "0"),
        ("operating-profit", "1E12", "1E12", "1E12", "1E12", "1E12"),
    ]

    def test_fuzz_cases_never_traceback_and_finish_quickly(self):
        for case in self.FUZZ:
            start = time.monotonic()
            result = subprocess.run(
                [sys.executable, "-B", "-m", "scripts.calculate", *case],
                capture_output=True, text=True, timeout=20, cwd=ROOT,
                check=False,
            )
            elapsed = time.monotonic() - start
            self.assertNotIn("Traceback", result.stderr, case)
            self.assertLess(elapsed, 5, f"{case} took {elapsed:.1f}s")
            self.assertIn(result.returncode, (0, 2), case)

    def test_tiny_divisors_are_clean_errors(self):
        for case in (("runway", "15000", "1E-999999"),
                     ("break-even", "1", "1E-999990", "0")):
            result = subprocess.run(
                [sys.executable, "-B", "-m", "scripts.calculate", *case],
                capture_output=True, text=True, timeout=20, cwd=ROOT,
                check=False,
            )
            self.assertEqual(result.returncode, 2, case)
            self.assertIn("error:", result.stderr)

    def run_main_with_failure(self, exception):
        from scripts import calculate

        broken = mock.Mock(side_effect=exception)
        patched = dict(calculate.OPERATIONS, revenue=(broken, 2))
        stderr = io.StringIO()
        with mock.patch.object(calculate, "OPERATIONS", patched), \
                mock.patch.object(sys, "argv",
                                  ["calculate", "revenue", "1", "2"]), \
                contextlib.redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as raised:
                calculate.main()
        return raised.exception.code, stderr.getvalue()

    def test_arithmetic_errors_are_reported_cleanly(self):
        for exception in (decimal.Overflow(), decimal.InvalidOperation(),
                          decimal.DivisionByZero(), ZeroDivisionError()):
            code, message = self.run_main_with_failure(exception)
            self.assertEqual(code, 2, exception)
            self.assertIn("error:", message)
            self.assertNotIn("Traceback", message)

    def test_serialization_errors_are_reported_cleanly(self):
        # json.dumps cannot render integers above 4300 digits.
        huge = 10 ** 5000
        from scripts import calculate

        patched = dict(calculate.OPERATIONS, revenue=(lambda a, b: huge, 2))
        stderr = io.StringIO()
        with mock.patch.object(calculate, "OPERATIONS", patched), \
                mock.patch.object(sys, "argv",
                                  ["calculate", "revenue", "1", "2"]), \
                contextlib.redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as raised:
                calculate.main()
        self.assertEqual(raised.exception.code, 2)
        self.assertIn("error:", stderr.getvalue())

    def test_minimum_magnitude_message_is_clear(self):
        result = subprocess.run(
            [sys.executable, "-B", "-m", "scripts.calculate",
             "runway", "15000", "0.0000000001"],
            capture_output=True, text=True, timeout=20, cwd=ROOT,
            check=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("cannot be smaller than", result.stderr)


if __name__ == "__main__":
    unittest.main()

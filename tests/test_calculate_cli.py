
import json
import subprocess
import sys
import unittest


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
        self.assertEqual(data["version"], "0.2.0")

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


if __name__ == "__main__":
    unittest.main()

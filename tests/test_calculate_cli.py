
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
        self.assertEqual(data["version"], "0.1.0")

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


if __name__ == "__main__":
    unittest.main()

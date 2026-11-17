
import unittest
from decimal import Decimal

from scripts.calculator import (
    ENGINE_VERSION,
    number,
    revenue,
    gross_margin,
    contribution_margin,
    break_even_units,
    customer_acquisition_cost,
    cash_runway,
    subscription_ltv,
)


class TestFinancialCalculator(unittest.TestCase):

    def test_engine_version(self):
        self.assertEqual(ENGINE_VERSION, "0.1.0")

    def test_revenue(self):
        self.assertEqual(revenue(100, "29.99"), Decimal("2999.00"))

    def test_zero_revenue(self):
        self.assertEqual(revenue(0, 50), Decimal("0"))

    def test_gross_margin(self):
        result = gross_margin(10000, 4000)
        self.assertEqual(result["gross_profit"], Decimal("6000"))
        self.assertEqual(
            result["gross_margin_percent"], Decimal("60")
        )

    def test_negative_gross_profit(self):
        result = gross_margin(100, 150)
        self.assertEqual(result["gross_profit"], Decimal("-50"))
        self.assertEqual(
            result["gross_margin_percent"], Decimal("-50")
        )

    def test_contribution_margin(self):
        self.assertEqual(
            contribution_margin(75, 25), Decimal("50")
        )

    def test_negative_contribution_margin(self):
        self.assertEqual(
            contribution_margin(20, 30), Decimal("-10")
        )

    def test_break_even_units(self):
        self.assertEqual(break_even_units(1000, 75, 25), 20)

    def test_break_even_rounding(self):
        self.assertEqual(break_even_units(101, 50, 20), 4)

    def test_zero_contribution_margin(self):
        with self.assertRaises(ValueError):
            break_even_units(1000, 50, 50)

    def test_customer_acquisition_cost(self):
        self.assertEqual(
            customer_acquisition_cost(1200, 30),
            Decimal("40"),
        )

    def test_zero_customers(self):
        with self.assertRaises(ValueError):
            customer_acquisition_cost(1200, 0)

    def test_cash_runway(self):
        self.assertEqual(
            cash_runway(15000, 3000), Decimal("5")
        )

    def test_zero_burn(self):
        with self.assertRaises(ValueError):
            cash_runway(15000, 0)

    def test_subscription_ltv(self):
        self.assertEqual(
            subscription_ltv(30, "0.05"), Decimal("6E+2")
        )

    def test_invalid_churn(self):
        with self.assertRaises(ValueError):
            subscription_ltv(30, "1.5")

    def test_negative_input(self):
        with self.assertRaises(ValueError):
            revenue(-10, 50)

    def test_invalid_number(self):
        with self.assertRaises(ValueError):
            number("not-a-number")

    def test_nan_rejected(self):
        with self.assertRaises(ValueError):
            number("NaN")

    def test_infinity_rejected(self):
        with self.assertRaises(ValueError):
            number("Infinity")

    def test_boolean_rejected(self):
        with self.assertRaises(ValueError):
            number(True)


if __name__ == "__main__":
    unittest.main()

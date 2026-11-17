
import unittest
from decimal import Decimal

from scripts.calculator import (
    ENGINE_VERSION,
    number,
    revenue,
    gross_margin,
    contribution_margin,
    break_even_units,
    break_even_units_with_acquisition,
    operating_profit,
    customer_acquisition_cost,
    cash_runway,
    subscription_ltv,
)


class TestFinancialCalculator(unittest.TestCase):

    def test_engine_version(self):
        self.assertEqual(ENGINE_VERSION, "0.2.1")

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


class TestOperatingProfit(unittest.TestCase):

    def test_operating_profit(self):
        result = operating_profit(14900, 0, "1937", 6000, 1500)
        self.assertEqual(result["total_costs"], Decimal("9437"))
        self.assertEqual(result["operating_profit"], Decimal("5463"))

    def test_categories_reported_separately(self):
        result = operating_profit(1000, 100, 50, 200, 300)
        self.assertEqual(result["cogs"], Decimal("100"))
        self.assertEqual(result["variable_operating"], Decimal("50"))
        self.assertEqual(result["acquisition"], Decimal("200"))
        self.assertEqual(result["fixed_operating"], Decimal("300"))
        self.assertEqual(result["operating_profit"], Decimal("350"))
        self.assertEqual(
            result["operating_margin_percent"], Decimal("35")
        )

    def test_operating_loss(self):
        result = operating_profit(100, 50, 50, 50, 50)
        self.assertEqual(result["operating_profit"], Decimal("-100"))

    def test_zero_revenue_has_no_margin(self):
        result = operating_profit(0, 0, 0, 0, 1500)
        self.assertEqual(result["operating_profit"], Decimal("-1500"))
        self.assertIsNone(result["operating_margin_percent"])

    def test_exclusions_documented(self):
        result = operating_profit(100, 0, 0, 0, 0)
        self.assertIn("taxes", result["excluded"])

    def test_negative_category_rejected(self):
        with self.assertRaises(ValueError):
            operating_profit(100, 10, -1, 0, 0)

    def test_negative_revenue_rejected(self):
        with self.assertRaises(ValueError):
            operating_profit(-1, 0, 0, 0, 0)


class TestBreakEvenWithAcquisition(unittest.TestCase):

    def test_loaded_exceeds_unloaded(self):
        # Contribution 149 - 19.37 = 129.63 -> 1500/129.63 -> 12 units.
        self.assertEqual(break_even_units(1500, 149, "19.37"), 12)
        # Loaded: 129.63 - 60 = 69.63 -> 1500/69.63 -> 22 units.
        result = break_even_units_with_acquisition(
            1500, 149, "19.37", 60
        )
        self.assertEqual(result["break_even_units"], 22)
        self.assertEqual(
            result["loaded_contribution_per_unit"], Decimal("69.63")
        )

    def test_zero_cac_matches_unloaded(self):
        result = break_even_units_with_acquisition(1500, 149, "19.37", 0)
        self.assertEqual(
            result["break_even_units"],
            break_even_units(1500, 149, "19.37"),
        )

    def test_assumptions_reported(self):
        result = break_even_units_with_acquisition(1000, 75, 25, 10)
        self.assertTrue(result["acquisition_included"])
        self.assertTrue(result["assumes_one_purchase_per_customer"])
        self.assertTrue(result["fixed_costs_exclude_acquisition"])

    def test_no_double_counting_with_fixed_budget(self):
        # A $600 fixed ad budget modeled as fixed cost with CAC 0 ...
        as_fixed = break_even_units_with_acquisition(
            1500 + 600, 149, "19.37", 0
        )
        # ... is the caller's choice; adding the same $600 as CAC too
        # would be a double count and must give a strictly worse answer,
        # which is why the documented contract forbids doing both.
        double = break_even_units_with_acquisition(
            1500 + 600, 149, "19.37", 60
        )
        self.assertLess(
            as_fixed["break_even_units"], double["break_even_units"]
        )

    def test_cac_consumes_margin_rejected(self):
        with self.assertRaises(ValueError):
            break_even_units_with_acquisition(1000, 100, 20, 80)
        with self.assertRaises(ValueError):
            break_even_units_with_acquisition(1000, 100, 20, 90)

    def test_negative_cac_rejected(self):
        with self.assertRaises(ValueError):
            break_even_units_with_acquisition(1000, 100, 20, -5)


class TestMinimumMagnitude(unittest.TestCase):
    """Regression tests for the audit finding on tiny divisors (H2)."""

    def test_zero_is_allowed(self):
        self.assertEqual(number("0"), Decimal("0"))
        self.assertEqual(number("0.000"), Decimal("0.000"))

    def test_smallest_allowed_nonzero(self):
        self.assertEqual(number("0.000000001"), Decimal("1E-9"))

    def test_below_minimum_rejected(self):
        for text in ("0.0000000001", "1E-10", "1E-999990", "1E-999999",
                     "0.0000000000000000000000000001"):
            with self.assertRaises(ValueError, msg=text):
                number(text)

    def test_tiny_divisors_raise_valueerror_not_overflow(self):
        with self.assertRaises(ValueError):
            cash_runway(15000, "1E-999999")
        with self.assertRaises(ValueError):
            customer_acquisition_cost(1, "1E-999990")
        with self.assertRaises(ValueError):
            subscription_ltv(30, "1E-999990")

    def test_break_even_with_tiny_margin_fails_fast(self):
        with self.assertRaises(ValueError):
            break_even_units(1, "1E-999990", 0)
        with self.assertRaises(ValueError):
            break_even_units_with_acquisition(1, "1E-999990", 0, 0)

    def test_break_even_result_cap(self):
        # 1e12 / 1e-9 = 1e21 units, above the 1e18 cap.
        with self.assertRaises(ValueError):
            break_even_units("1E12", "1.000000001", 1)
        with self.assertRaises(ValueError):
            break_even_units_with_acquisition(
                "1E12", "1.000000001", 0, "0.999999999"
            )

    def test_break_even_at_cap_boundary_is_allowed(self):
        self.assertEqual(
            break_even_units("1E9", "0.000000002", "0.000000001"),
            1000000000 * 1000000000,
        )

    def test_nearly_equal_price_and_cost_is_bounded(self):
        # Subtraction can still produce a tiny margin from valid inputs.
        with self.assertRaises(ValueError):
            break_even_units(1, "1.0000000000000000000000000002", 1)


class TestInputBounds(unittest.TestCase):

    def test_max_value_accepted(self):
        self.assertEqual(number("1000000000000"), Decimal("1E+12"))

    def test_above_max_rejected(self):
        with self.assertRaises(ValueError):
            number("1000000000001")

    def test_negative_above_max_rejected(self):
        with self.assertRaises(ValueError):
            number("-1000000000001")

    def test_huge_exponent_rejected(self):
        with self.assertRaises(ValueError):
            number("1E999999999")

    def test_overlong_input_rejected(self):
        with self.assertRaises(ValueError):
            number("1" * 65)

    def test_bound_applies_to_operations(self):
        with self.assertRaises(ValueError):
            break_even_units("1E30", 50, 20)


if __name__ == "__main__":
    unittest.main()

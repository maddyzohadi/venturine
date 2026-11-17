
"""
Venturine Financial Calculator
Version: 0.1.0

Pure financial calculation functions.
No network access, file writes, or automatic execution.
Requires only the Python standard library.
"""

from decimal import Decimal, InvalidOperation, ROUND_CEILING


ENGINE_VERSION = "0.1.0"


def number(value):
    """Convert a numeric input into a finite Decimal."""
    if isinstance(value, bool):
        raise ValueError("Boolean values are not valid financial inputs.")

    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        raise ValueError("A valid numeric input is required.")

    if not result.is_finite():
        raise ValueError("Inputs must be finite numbers.")

    return result


def require_nonnegative(value, name):
    result = number(value)
    if result < 0:
        raise ValueError(f"{name} cannot be negative.")
    return result


def require_positive(value, name):
    result = number(value)
    if result <= 0:
        raise ValueError(f"{name} must be greater than zero.")
    return result


def revenue(units, price_per_unit):
    """Calculate total revenue."""
    units = require_nonnegative(units, "Units")
    price = require_nonnegative(price_per_unit, "Price")
    return units * price


def gross_margin(total_revenue, cost_of_goods_sold):
    """Return gross profit and gross margin percentage."""
    total_revenue = require_positive(total_revenue, "Revenue")
    cogs = require_nonnegative(cost_of_goods_sold, "COGS")

    profit = total_revenue - cogs
    percentage = (profit / total_revenue) * 100

    return {
        "gross_profit": profit,
        "gross_margin_percent": percentage,
    }


def contribution_margin(unit_price, variable_cost):
    """Calculate contribution margin per unit."""
    price = require_nonnegative(unit_price, "Unit price")
    cost = require_nonnegative(variable_cost, "Variable cost")

    return price - cost


def break_even_units(fixed_costs, unit_price, variable_cost):
    """Calculate whole units required to break even."""
    fixed = require_nonnegative(fixed_costs, "Fixed costs")
    margin = contribution_margin(unit_price, variable_cost)

    if margin <= 0:
        raise ValueError(
            "Break-even requires positive contribution margin."
        )

    return int(
        (fixed / margin).to_integral_value(rounding=ROUND_CEILING)
    )


def customer_acquisition_cost(acquisition_spend, new_customers):
    """Calculate CAC from eligible acquisition costs."""
    spend = require_nonnegative(acquisition_spend, "Acquisition spend")
    customers = require_positive(new_customers, "New customers")

    return spend / customers


def cash_runway(available_cash, monthly_net_burn):
    """Calculate static cash runway in months."""
    cash = require_nonnegative(available_cash, "Available cash")
    burn = require_positive(monthly_net_burn, "Monthly net burn")

    return cash / burn


def subscription_ltv(monthly_contribution, monthly_churn_rate):
    """
    Simplified subscription LTV.

    Churn rate is a fraction, e.g. 0.05 for 5%.
    Assumes stable monthly contribution and churn.
    """
    contribution = require_nonnegative(
        monthly_contribution, "Monthly contribution"
    )
    churn = require_positive(monthly_churn_rate, "Churn rate")

    if churn > 1:
        raise ValueError("Churn rate cannot exceed 1.")

    return contribution / churn

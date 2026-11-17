
"""
Venturine Financial Calculator
Version: 0.2.1

Pure financial calculation functions.
No network access, file writes, or automatic execution.
Requires only the Python standard library.
"""

from decimal import Decimal, InvalidOperation, ROUND_CEILING


ENGINE_VERSION = "0.2.1"

# Input bounds. Prevent resource exhaustion from absurd magnitudes/exponents
# (e.g. "1E999999999") while allowing any realistic business figure.
MAX_INPUT_CHARS = 64
MAX_ABS_VALUE = Decimal("1000000000000")  # 1e12
# Nonzero inputs must be at least this large in absolute value. Without a
# floor, a tiny divisor (e.g. "1E-999990") makes a quotient with a million
# digits, which costs tens of seconds of CPU or overflows the Decimal context.
MIN_NONZERO_ABS_VALUE = Decimal("0.000000001")  # 1e-9
# Break-even results above this many units are rejected as implausible.
MAX_BREAK_EVEN_UNITS = Decimal("1000000000000000000")  # 1e18


def number(value):
    """Convert a numeric input into a finite Decimal."""
    if isinstance(value, bool):
        raise ValueError("Boolean values are not valid financial inputs.")

    text = str(value)
    if len(text) > MAX_INPUT_CHARS:
        raise ValueError(
            f"Inputs cannot exceed {MAX_INPUT_CHARS} characters."
        )

    try:
        result = Decimal(text)
    except (InvalidOperation, ValueError, TypeError):
        raise ValueError("A valid numeric input is required.")

    if not result.is_finite():
        raise ValueError("Inputs must be finite numbers.")

    # copy_abs() avoids context-rounding Overflow on huge exponents.
    magnitude = result.copy_abs()
    if magnitude > MAX_ABS_VALUE:
        raise ValueError(
            f"Inputs cannot exceed {MAX_ABS_VALUE:,} in absolute value."
        )

    if magnitude != 0 and magnitude < MIN_NONZERO_ABS_VALUE:
        raise ValueError(
            "Nonzero inputs cannot be smaller than "
            f"{MIN_NONZERO_ABS_VALUE:f} in absolute value."
        )

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


def _ceil_units(fixed, margin):
    """Round fixed / margin up to whole units, rejecting absurd results."""
    quotient = fixed / margin

    if quotient > MAX_BREAK_EVEN_UNITS:
        raise ValueError(
            "Break-even exceeds 1,000,000,000,000,000,000 units; "
            "check the inputs."
        )

    return int(quotient.to_integral_value(rounding=ROUND_CEILING))


def break_even_units(fixed_costs, unit_price, variable_cost):
    """Calculate whole units required to break even."""
    fixed = require_nonnegative(fixed_costs, "Fixed costs")
    margin = contribution_margin(unit_price, variable_cost)

    if margin <= 0:
        raise ValueError(
            "Break-even requires positive contribution margin."
        )

    return _ceil_units(fixed, margin)


def break_even_units_with_acquisition(
    fixed_costs_excluding_acquisition,
    unit_price,
    variable_cost,
    cac_per_customer,
):
    """
    Whole units required to break even, including customer acquisition.

    Assumptions (also returned in the result):
    - Each customer buys exactly one unit (no repeat purchases).
    - CAC is charged per customer, so loaded contribution per unit is
      unit_price - variable_cost - cac_per_customer.
    - fixed_costs_excluding_acquisition must NOT include acquisition
      spending. A fixed acquisition budget (e.g. a monthly ad budget) is
      either added to the fixed costs here OR converted to a per-customer
      CAC, never both; counting it in both places double-counts it.
    """
    fixed = require_nonnegative(
        fixed_costs_excluding_acquisition,
        "Fixed costs excluding acquisition",
    )
    cac = require_nonnegative(cac_per_customer, "CAC per customer")
    margin = contribution_margin(unit_price, variable_cost) - cac

    if margin <= 0:
        raise ValueError(
            "Break-even requires positive contribution margin after "
            "customer acquisition cost."
        )

    return {
        "break_even_units": _ceil_units(fixed, margin),
        "loaded_contribution_per_unit": margin,
        "acquisition_included": True,
        "assumes_one_purchase_per_customer": True,
        "fixed_costs_exclude_acquisition": True,
    }


def operating_profit(
    total_revenue,
    cogs,
    variable_operating,
    acquisition,
    fixed_operating,
):
    """
    Operating profit for one period with mutually exclusive cost categories.

    Each cost belongs in exactly one category:
    - cogs: direct cost of goods/services sold.
    - variable_operating: other costs that scale with volume
      (payment fees, support, fulfilment) not already in cogs.
    - acquisition: TOTAL customer acquisition spend for the period,
      whether budgeted or CAC x new customers. Enter it once; do not
      also include it in fixed_operating.
    - fixed_operating: recurring costs that do not scale with volume,
      excluding acquisition.

    Operating profit = revenue - all four categories. Excludes taxes,
    interest, capital expenditures, and owner compensation unless the
    caller includes the latter in fixed_operating.
    """
    rev = require_nonnegative(total_revenue, "Revenue")
    categories = {
        "cogs": require_nonnegative(cogs, "COGS"),
        "variable_operating": require_nonnegative(
            variable_operating, "Variable operating costs"
        ),
        "acquisition": require_nonnegative(
            acquisition, "Acquisition costs"
        ),
        "fixed_operating": require_nonnegative(
            fixed_operating, "Fixed operating costs"
        ),
    }
    total_costs = sum(categories.values(), Decimal(0))
    profit = rev - total_costs

    return {
        "revenue": rev,
        **categories,
        "total_costs": total_costs,
        "operating_profit": profit,
        "operating_margin_percent": (
            (profit / rev) * 100 if rev > 0 else None
        ),
        "excluded": [
            "taxes",
            "interest",
            "capital expenditures",
            "owner compensation unless included in fixed_operating",
        ],
    }


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

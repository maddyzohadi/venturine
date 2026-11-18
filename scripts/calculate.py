
"""
Venturine calculation interface, v0.2.1.

Usage (run by file path):
python3 scripts/calculate.py revenue 100 29.99

Always run this file by its path. Running it as "python -m scripts.calculate"
puts the current directory first on the module path, so a "scripts" package
in an unrelated project would run instead of this one.

Accepts only explicitly supported financial operations.
No network access, file writes, or automatic execution.
"""

import argparse
import json
from decimal import Context, Decimal, InvalidOperation, ROUND_HALF_UP

if __package__:
    # Imported as part of the "scripts" package (tests, "python -m").
    from .calculator import (
        ENGINE_VERSION,
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
else:
    # Run by file path: Python puts this file's own directory first on the
    # module path, ahead of the current directory, so this cannot be shadowed.
    from calculator import (
        ENGINE_VERSION,
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


OPERATIONS = {
    "revenue": (revenue, 2),
    "gross-margin": (gross_margin, 2),
    "contribution-margin": (contribution_margin, 2),
    "break-even": (break_even_units, 3),
    "break-even-loaded": (break_even_units_with_acquisition, 4),
    "operating-profit": (operating_profit, 5),
    "cac": (customer_acquisition_cost, 2),
    "runway": (cash_runway, 2),
    "subscription-ltv": (subscription_ltv, 2),
}


# Extra, non-breaking fields merged into the JSON output of an operation.
UNITS_ROUNDING_NOTE = "Rounded up to whole units."

OPERATION_NOTES = {
    "break-even-loaded": {"units_rounding": UNITS_ROUNDING_NOTE},
    "break-even": {
        "units_rounding": UNITS_ROUNDING_NOTE,
        "acquisition_included": False,
        "warning": (
            "Operating break-even only. Customer acquisition costs are "
            "not included; use break-even-loaded when acquisition "
            "spending is relevant."
        ),
    },
}

# Positional input order, for documentation in --help.
USAGE_NOTES = """\
input order:
  revenue            UNITS PRICE
  gross-margin       REVENUE COGS
  contribution-margin PRICE VARIABLE_COST
  break-even         FIXED PRICE VARIABLE_COST   (excludes acquisition)
  break-even-loaded  FIXED_EXCL_ACQUISITION PRICE VARIABLE_COST CAC_PER_CUSTOMER
                     (one purchase per customer; do not count acquisition
                      in both FIXED and CAC)
  operating-profit   REVENUE COGS VARIABLE_OPERATING ACQUISITION FIXED_OPERATING
                     (categories are mutually exclusive; enter 0 explicitly)
  cac                SPEND NEW_CUSTOMERS
  runway             CASH MONTHLY_NET_BURN
  subscription-ltv   MONTHLY_CONTRIBUTION MONTHLY_CHURN_FRACTION
"""


CENT = Decimal("0.01")
SMALL_VALUE_CONTEXT = Context(prec=4, rounding=ROUND_HALF_UP)

DISPLAY_ROUNDING_NOTE = (
    "Decimal results are displayed in plain notation, rounded half-up to 2 "
    "decimal places (4 significant digits when the magnitude is below "
    "0.01). Calculations use exact decimal arithmetic; whole-unit results "
    "are exact integers."
)


def format_decimal(value):
    """
    Render a Decimal for display: plain notation (no exponent), no negative
    zero, and a bounded number of digits so results do not imply precision
    the inputs never had.
    """
    if value.is_zero():
        return "0.00"

    try:
        if abs(value) >= CENT:
            rounded = value.quantize(CENT, rounding=ROUND_HALF_UP)
        else:
            rounded = SMALL_VALUE_CONTEXT.create_decimal(value)
    except InvalidOperation:
        rounded = value

    return format(rounded, "f")


def serialize(value):
    if isinstance(value, Decimal):
        return format_decimal(value)

    if isinstance(value, dict):
        return {
            key: serialize(item)
            for key, item in value.items()
        }

    return value


def contains_decimal(value):
    if isinstance(value, Decimal):
        return True

    if isinstance(value, dict):
        return any(contains_decimal(item) for item in value.values())

    return False


def main():
    parser = argparse.ArgumentParser(
        description="Venturine financial calculator",
        epilog=USAGE_NOTES,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "operation",
        choices=sorted(OPERATIONS),
    )

    parser.add_argument(
        "values",
        nargs="*",
        help="Numeric inputs for the selected operation",
    )

    args = parser.parse_args()

    function, expected_count = OPERATIONS[args.operation]

    if len(args.values) != expected_count:
        parser.error(
            f"{args.operation} requires "
            f"{expected_count} numeric inputs."
        )

    try:
        result = function(*args.values)
        output = {
            "engine": "venturine",
            "version": ENGINE_VERSION,
            "operation": args.operation,
            "inputs": args.values,
            "result": serialize(result),
            "status": "calculated",
        }
        output.update(OPERATION_NOTES.get(args.operation, {}))
        if contains_decimal(result):
            output["display_rounding"] = DISPLAY_ROUNDING_NOTE
        text = json.dumps(output, indent=2)
    except (ValueError, TypeError, ArithmeticError) as error:
        # ArithmeticError covers decimal.Overflow and InvalidOperation, which
        # are not ValueErrors and previously escaped as tracebacks.
        parser.error(str(error) or error.__class__.__name__)

    print(text)


if __name__ == "__main__":
    main()

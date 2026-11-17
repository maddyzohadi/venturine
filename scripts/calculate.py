
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
from decimal import Decimal

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
OPERATION_NOTES = {
    "break-even": {
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


def serialize(value):
    if isinstance(value, Decimal):
        return str(value)

    if isinstance(value, dict):
        return {
            key: serialize(item)
            for key, item in value.items()
        }

    return value


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
        text = json.dumps(output, indent=2)
    except (ValueError, TypeError, ArithmeticError) as error:
        # ArithmeticError covers decimal.Overflow and InvalidOperation, which
        # are not ValueErrors and previously escaped as tracebacks.
        parser.error(str(error) or error.__class__.__name__)

    print(text)


if __name__ == "__main__":
    main()

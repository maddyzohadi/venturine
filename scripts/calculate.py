
"""
Venturine calculation interface, v0.1.0.

Usage:
python -m scripts.calculate revenue 100 29.99

Accepts only explicitly supported financial operations.
No network access, file writes, or automatic execution.
"""

import argparse
import json
from decimal import Decimal

from scripts.calculator import (
    ENGINE_VERSION,
    revenue,
    gross_margin,
    contribution_margin,
    break_even_units,
    customer_acquisition_cost,
    cash_runway,
    subscription_ltv,
)


OPERATIONS = {
    "revenue": (revenue, 2),
    "gross-margin": (gross_margin, 2),
    "contribution-margin": (contribution_margin, 2),
    "break-even": (break_even_units, 3),
    "cac": (customer_acquisition_cost, 2),
    "runway": (cash_runway, 2),
    "subscription-ltv": (subscription_ltv, 2),
}


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
        description="Venturine financial calculator"
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
    except (ValueError, TypeError) as error:
        parser.error(str(error))

    output = {
        "engine": "venturine",
        "version": ENGINE_VERSION,
        "operation": args.operation,
        "inputs": args.values,
        "result": serialize(result),
        "status": "calculated",
    }

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()

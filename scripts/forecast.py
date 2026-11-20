"""
Venturine forecasting calculator.

Usage (run by file path):
python3 scripts/forecast.py monthly-forecast 5000 12 100 0.03 24 9.50 1500 600

Operations: monthly-forecast, scenario-compare, sensitivity, price-compare.
Every result carries a calculation receipt: the exact inputs, the model
assumptions and exclusions, the engine version, and a SHA-256 fingerprint,
so a result can be reproduced and checked.

Deterministic: the same inputs always give the same output. Uses exact
decimal arithmetic and the same input validation as the calculator.
No network access, file reads or writes, or automatic execution.
Requires only the Python standard library.
"""

import argparse
import hashlib
import json
import re
from decimal import Decimal

if __package__:
    # Imported as part of the "scripts" package (tests, "python -m").
    from .calculator import (
        ENGINE_VERSION,
        _ceil_units,
        number,
        require_nonnegative,
    )
    from .calculate import DISPLAY_ROUNDING_NOTE, format_decimal
else:
    # Run by file path: this file's own directory comes first on the module
    # path, so a "scripts" package elsewhere cannot shadow these imports.
    from calculator import (
        ENGINE_VERSION,
        _ceil_units,
        number,
        require_nonnegative,
    )
    from calculate import DISPLAY_ROUNDING_NOTE, format_decimal


MODEL = "venturine-forecast/v1"

# Inputs of a monthly forecast, in command-line order.
PARAMETERS = (
    "starting_cash",
    "months",
    "starting_units",
    "monthly_unit_growth",
    "price",
    "variable_cost",
    "fixed_costs",
    "acquisition_spend",
)
# Inputs a sensitivity analysis may vary. The horizon is fixed.
VARIABLE_PARAMETERS = tuple(p for p in PARAMETERS if p != "months")

MAX_MONTHS = 120
MIN_GROWTH = Decimal("-0.99")
MAX_GROWTH = Decimal("1")
MAX_RESULT = Decimal("1000000000000000000000000")  # 1e24
MAX_SCENARIOS = 5
MIN_SCENARIOS = 2
MAX_DELTAS = 5
MAX_PRICES = 8
SCENARIO_NAME = re.compile(r"^[a-z][a-z0-9_-]{0,29}$")

ASSUMPTIONS = (
    "Revenue is received as cash in the month it is earned.",
    "Units sold in month 1 equal starting_units and then change by "
    "monthly_unit_growth each month. Growth is an input, not a result of "
    "acquisition spending.",
    "Price, variable cost per unit, fixed costs and acquisition spending "
    "are the same every month.",
    "acquisition_spend is the total acquisition spending for the month. "
    "It is counted once, so fixed_costs must exclude it.",
    "Net cash flow in a month equals operating profit: revenue minus "
    "variable costs, acquisition spending and fixed costs.",
    "Cash is allowed to go below zero so the size of a funding gap is "
    "visible. No new funding is assumed.",
)
EXCLUSIONS = (
    "taxes",
    "interest and other financing flows",
    "capital expenditures",
    "working capital and payment timing",
    "seasonality",
    "refunds and chargebacks",
    "owner pay, unless it is included in fixed_costs",
)
PRICE_ASSUMPTIONS = (
    "Expected units per month are the same at every candidate price. Demand "
    "does not respond to price in this model.",
    "Each customer buys exactly one unit, so CAC is charged once per unit.",
    "fixed_costs exclude acquisition spending, which is counted once as CAC "
    "per customer.",
)

DISPLAY_NOTE = (
    DISPLAY_ROUNDING_NOTE
    + " Do not feed displayed forecast values back in as inputs; re-run "
    "with the original inputs."
)

USAGE_NOTES = """\
operations and input order:
  monthly-forecast  STARTING_CASH MONTHS STARTING_UNITS MONTHLY_UNIT_GROWTH
                    PRICE VARIABLE_COST FIXED_COSTS ACQUISITION_SPEND
  scenario-compare  --scenario NAME <the 8 monthly-forecast inputs> ...
                    (2 to 5 scenarios, all with the same MONTHS)
  sensitivity       <the 8 monthly-forecast inputs> --delta PERCENT [...]
                    [--vary PARAMETER ...]
  price-compare     VARIABLE_COST FIXED_COSTS CAC_PER_CUSTOMER
                    EXPECTED_UNITS PRICE [PRICE ...]   (up to 8 prices)

MONTHLY_UNIT_GROWTH is a fraction, for example 0.03 for 3 percent.
FIXED_COSTS must exclude acquisition; ACQUISITION_SPEND is the total
acquisition spending per month. Count acquisition exactly once.
"""


# ---------------------------------------------------------------- inputs


def validate_parameters(params):
    """Check a dictionary of Decimal inputs. Raises ValueError."""
    for key, label in (
        ("starting_cash", "Starting cash"),
        ("starting_units", "Starting units"),
        ("price", "Price"),
        ("variable_cost", "Variable cost"),
        ("fixed_costs", "Fixed costs"),
        ("acquisition_spend", "Acquisition spend"),
    ):
        if params[key] < 0:
            raise ValueError(f"{label} cannot be negative.")

    months = params["months"]
    if months != months.to_integral_value():
        raise ValueError("Months must be a whole number.")
    if not 1 <= months <= MAX_MONTHS:
        raise ValueError(f"Months must be from 1 to {MAX_MONTHS}.")

    growth = params["monthly_unit_growth"]
    if not MIN_GROWTH <= growth <= MAX_GROWTH:
        raise ValueError(
            "Monthly unit growth must be a fraction from -0.99 to 1, for "
            "example 0.03 for 3 percent."
        )
    return params


def parse_parameters(values):
    """Turn the eight command-line inputs into validated Decimals."""
    if len(values) != len(PARAMETERS):
        raise ValueError(
            f"Expected {len(PARAMETERS)} inputs: " + ", ".join(PARAMETERS)
        )
    return validate_parameters(
        {name: number(value) for name, value in zip(PARAMETERS, values)}
    )


# ---------------------------------------------------------------- the model


def _guard(*values):
    for value in values:
        if abs(value) > MAX_RESULT:
            raise ValueError(
                "A result exceeds the supported range of 1,000,000,000,000,"
                "000,000,000,000,000; check the inputs."
            )


def run_forecast(params):
    """
    Monthly forecast from validated inputs.

    Returns {"summary": ..., "months": [...]} using Decimal values.
    """
    months = int(params["months"])
    growth_factor = 1 + params["monthly_unit_growth"]
    units = params["starting_units"]
    cash = params["starting_cash"]

    rows = []
    for month in range(1, months + 1):
        if month > 1:
            units = units * growth_factor
        revenue = units * params["price"]
        variable = units * params["variable_cost"]
        profit = (
            revenue - variable - params["acquisition_spend"]
            - params["fixed_costs"]
        )
        opening = cash
        cash = opening + profit
        _guard(units, revenue, variable, profit, cash)
        rows.append({
            "month": month,
            "units": units,
            "revenue": revenue,
            "variable_costs": variable,
            "acquisition_spend": params["acquisition_spend"],
            "fixed_costs": params["fixed_costs"],
            "operating_profit": profit,
            "opening_cash": opening,
            "ending_cash": cash,
        })

    cash_out_month = None
    runway = None
    for row in rows:
        if row["ending_cash"] < 0:
            cash_out_month = row["month"]
            # The month's outflow exceeds its opening balance, so the share
            # of the month that the cash lasts is opening / outflow.
            runway = (row["month"] - 1) + (
                row["opening_cash"] / -row["operating_profit"]
            )
            break

    lowest = min(rows, key=lambda r: r["ending_cash"])
    break_even_month = next(
        (r["month"] for r in rows if r["operating_profit"] >= 0), None
    )
    summary = {
        "months": months,
        "total_revenue": sum((r["revenue"] for r in rows), Decimal(0)),
        "total_operating_profit": sum(
            (r["operating_profit"] for r in rows), Decimal(0)
        ),
        "ending_cash": rows[-1]["ending_cash"],
        "minimum_cash": lowest["ending_cash"],
        "minimum_cash_month": lowest["month"],
        "cash_out_month": cash_out_month,
        "runway_months": runway,
        "break_even_month": break_even_month,
    }
    return {"summary": summary, "months": rows}


# ---------------------------------------------------------------- receipts


def make_receipt(operation, named_inputs, assumptions=ASSUMPTIONS):
    """
    A calculation receipt. The fingerprint is the SHA-256 of the operation,
    model, engine version and the inputs exactly as given, so the same
    inputs always give the same fingerprint and any change gives another.
    """
    pairs = [[name, str(value)] for name, value in named_inputs]
    payload = {
        "operation": operation,
        "model": MODEL,
        "engine_version": ENGINE_VERSION,
        "inputs": pairs,
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return {
        "fingerprint": f"sha256:{digest}",
        "operation": operation,
        "model": MODEL,
        "engine_version": ENGINE_VERSION,
        "inputs": [{"name": n, "value": v} for n, v in pairs],
        "assumptions": list(assumptions),
        "exclusions": list(EXCLUSIONS),
    }


# ---------------------------------------------------------------- operations


def monthly_forecast(values):
    params = parse_parameters(values)
    result = run_forecast(params)
    return result, list(zip(PARAMETERS, values))


def scenario_compare(scenarios):
    """scenarios: a list of (name, eight input strings)."""
    if not MIN_SCENARIOS <= len(scenarios) <= MAX_SCENARIOS:
        raise ValueError(
            f"Compare from {MIN_SCENARIOS} to {MAX_SCENARIOS} scenarios."
        )
    names = [name for name, _ in scenarios]
    for name in names:
        if not SCENARIO_NAME.match(name):
            raise ValueError(
                "Scenario names must be lowercase letters, digits, hyphens "
                "or underscores, start with a letter, and be at most 30 "
                "characters."
            )
    if len(set(names)) != len(names):
        raise ValueError("Scenario names must be unique.")

    parsed = [(name, parse_parameters(values)) for name, values in scenarios]
    horizon = parsed[0][1]["months"]
    for name, params in parsed:
        if params["months"] != horizon:
            raise ValueError(
                "All scenarios must use the same number of months so they "
                f"are comparable; '{name}' differs from '{parsed[0][0]}'."
            )

    forecasts = [(name, params, run_forecast(params))
                 for name, params in parsed]
    varied = [
        parameter for parameter in PARAMETERS
        if len({params[parameter] for _, params in parsed}) > 1
    ]
    base_summary = forecasts[0][2]["summary"]
    result = {
        "months": int(horizon),
        "varied_inputs": varied,
        "scenarios": [
            {
                "name": name,
                "inputs": {p: str(scenarios[i][1][PARAMETERS.index(p)])
                           for p in PARAMETERS},
                "summary": forecast["summary"],
            }
            for i, (name, _, forecast) in enumerate(forecasts)
        ],
        "differences_from_first": [
            {
                "name": name,
                "ending_cash_difference": (
                    forecast["summary"]["ending_cash"]
                    - base_summary["ending_cash"]
                ),
                "total_operating_profit_difference": (
                    forecast["summary"]["total_operating_profit"]
                    - base_summary["total_operating_profit"]
                ),
            }
            for name, _, forecast in forecasts[1:]
        ],
        "ordering_by_ending_cash": [
            name for name, _, forecast in sorted(
                forecasts,
                key=lambda item: (-item[2]["summary"]["ending_cash"],
                                  item[0]),
            )
        ],
    }
    named = [
        (f"{name}.{parameter}", value)
        for name, values in scenarios
        for parameter, value in zip(PARAMETERS, values)
    ]
    return result, named


SENSITIVITY_METRICS = (
    "ending_cash", "total_operating_profit", "minimum_cash",
    "cash_out_month", "runway_months", "break_even_month",
)


def sensitivity(values, deltas, vary=None):
    """
    One-at-a-time sensitivity. Each varied input is moved down and up by
    each percentage while every other input stays at its base value.
    """
    base_params = parse_parameters(values)
    parsed = []
    for text in deltas:
        delta = number(text)
        if not 0 < delta <= 100:
            raise ValueError(
                "Each delta must be a percentage greater than 0 and at "
                "most 100."
            )
        parsed.append((delta, text))
    if not 1 <= len(parsed) <= MAX_DELTAS:
        raise ValueError(f"Give from 1 to {MAX_DELTAS} deltas.")
    if len({delta for delta, _ in parsed}) != len(parsed):
        raise ValueError("Deltas must be different from each other.")
    parsed.sort(key=lambda item: item[0])

    chosen = list(vary) if vary else list(VARIABLE_PARAMETERS)
    for parameter in chosen:
        if parameter not in VARIABLE_PARAMETERS:
            raise ValueError(
                f"Cannot vary '{parameter}'. Choose from: "
                + ", ".join(VARIABLE_PARAMETERS)
            )
    chosen = [p for p in VARIABLE_PARAMETERS if p in set(chosen)]

    base = run_forecast(base_params)["summary"]
    rows, notes, swings = [], [], {}
    for parameter in chosen:
        if base_params[parameter] == 0:
            notes.append(
                f"{parameter}: the base value is 0, so a percentage change "
                "does not move it."
            )
        swings[parameter] = Decimal(0)
        for delta, text in parsed:
            for sign, label in ((-1, "-"), (1, "+")):
                changed = dict(base_params)
                changed[parameter] = base_params[parameter] * (
                    1 + sign * delta / 100
                )
                try:
                    validate_parameters(changed)
                    summary = run_forecast(changed)["summary"]
                except ValueError as error:
                    raise ValueError(
                        f"{parameter} {label}{text}%: {error}"
                    ) from None
                row = {
                    "parameter": parameter,
                    "change_percent": f"{label}{text.lstrip('+-')}",
                    "value": changed[parameter],
                }
                for metric in SENSITIVITY_METRICS:
                    row[metric] = summary[metric]
                row["ending_cash_change"] = (
                    summary["ending_cash"] - base["ending_cash"]
                )
                row["total_operating_profit_change"] = (
                    summary["total_operating_profit"]
                    - base["total_operating_profit"]
                )
                swings[parameter] = max(
                    swings[parameter], abs(row["ending_cash_change"])
                )
                rows.append(row)

    ranking = [
        {"parameter": parameter, "largest_ending_cash_change": swing}
        for parameter, swing in sorted(
            swings.items(), key=lambda item: (-item[1], item[0])
        )
    ]
    result = {
        "base_summary": base,
        "rows": rows,
        "ranking_by_ending_cash_change": ranking,
        "notes": notes,
    }
    named = list(zip(PARAMETERS, values))
    named += [(f"delta_percent.{i}", text)
              for i, (_, text) in enumerate(parsed, start=1)]
    named.append(("vary", ",".join(chosen)))
    return result, named


def price_compare(values):
    """
    values: VARIABLE_COST FIXED_COSTS CAC_PER_CUSTOMER EXPECTED_UNITS and
    then one or more candidate prices.
    """
    if not 5 <= len(values) <= 4 + MAX_PRICES:
        raise ValueError(
            "Give VARIABLE_COST, FIXED_COSTS, CAC_PER_CUSTOMER, "
            f"EXPECTED_UNITS and from 1 to {MAX_PRICES} prices."
        )
    variable = require_nonnegative(values[0], "Variable cost")
    fixed = require_nonnegative(values[1], "Fixed costs")
    cac = require_nonnegative(values[2], "CAC per customer")
    units = require_nonnegative(values[3], "Expected units")
    prices = [require_nonnegative(v, "Price") for v in values[4:]]

    def loaded_of(price):
        return price - variable - cac

    baseline_contribution = units * loaded_of(prices[0])
    rows = []
    for price in prices:
        contribution = price - variable
        loaded = loaded_of(price)
        try:
            operating_break_even = (
                _ceil_units(fixed, contribution) if contribution > 0 else None
            )
            loaded_break_even = (
                _ceil_units(fixed, loaded) if loaded > 0 else None
            )
            match = None
            if loaded > 0:
                target = max(Decimal(0), baseline_contribution)
                match = _ceil_units(target, loaded)
        except ValueError:
            operating_break_even = loaded_break_even = match = None
        _guard(units * price, units * loaded)
        rows.append({
            "price": price,
            "contribution_per_unit": contribution,
            "contribution_margin_percent": (
                contribution / price * 100 if price > 0 else None
            ),
            "loaded_contribution_per_unit": loaded,
            "break_even_units_excluding_acquisition": operating_break_even,
            "break_even_units_including_acquisition": loaded_break_even,
            "revenue_at_expected_units": units * price,
            "operating_profit_at_expected_units": units * loaded - fixed,
            "units_needed_to_match_first_price_profit": match,
        })
    result = {
        "expected_units": units,
        "assumes_constant_volume": True,
        "assumes_one_purchase_per_customer": True,
        "fixed_costs_exclude_acquisition": True,
        "prices": rows,
    }
    named = [
        ("variable_cost", values[0]), ("fixed_costs", values[1]),
        ("cac_per_customer", values[2]), ("expected_units", values[3]),
    ]
    named += [(f"price.{i}", v) for i, v in enumerate(values[4:], start=1)]
    return result, named


# ---------------------------------------------------------------- output


def display(value):
    """Convert a result to JSON-ready text, rounding only for display."""
    if isinstance(value, Decimal):
        return format_decimal(value)
    if isinstance(value, dict):
        return {key: display(item) for key, item in value.items()}
    if isinstance(value, list):
        return [display(item) for item in value]
    return value


def build_parser():
    parser = argparse.ArgumentParser(
        description="Venturine forecasting calculator",
        epilog=USAGE_NOTES,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="operation", required=True)

    # A plain metavar: older versions of argparse (3.9 to 3.12) raise a
    # TypeError, instead of a usage error, when a positional argument with a
    # tuple metavar is missing. The epilog lists the input order.
    forecast = sub.add_parser("monthly-forecast")
    forecast.add_argument("values", nargs=len(PARAMETERS), metavar="INPUT")

    scenarios = sub.add_parser("scenario-compare")
    scenarios.add_argument(
        "--scenario", nargs=len(PARAMETERS) + 1, action="append",
        required=True,
        metavar=("NAME",) + tuple(name.upper() for name in PARAMETERS),
    )

    sens = sub.add_parser("sensitivity")
    sens.add_argument("values", nargs=len(PARAMETERS), metavar="INPUT")
    sens.add_argument("--delta", action="append", required=True,
                      metavar="PERCENT")
    sens.add_argument("--vary", action="append", metavar="PARAMETER")

    price = sub.add_parser("price-compare")
    price.add_argument("values", nargs="+", metavar="VALUE")
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    try:
        if args.operation == "monthly-forecast":
            result, named = monthly_forecast(args.values)
        elif args.operation == "scenario-compare":
            result, named = scenario_compare(
                [(item[0], item[1:]) for item in args.scenario]
            )
        elif args.operation == "sensitivity":
            result, named = sensitivity(args.values, args.delta, args.vary)
        else:
            result, named = price_compare(args.values)

        assumptions = (
            PRICE_ASSUMPTIONS if args.operation == "price-compare"
            else ASSUMPTIONS
        )
        output = {
            "engine": "venturine",
            "version": ENGINE_VERSION,
            "operation": args.operation,
            "inputs": dict(named),
            "result": display(result),
            "receipt": make_receipt(args.operation, named, assumptions),
            "display_rounding": DISPLAY_NOTE,
            "status": "calculated",
        }
        text = json.dumps(output, indent=2)
    except (ValueError, TypeError, ArithmeticError) as error:
        parser.error(str(error) or error.__class__.__name__)

    print(text)


if __name__ == "__main__":
    main()

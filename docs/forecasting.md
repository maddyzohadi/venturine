# Forecasting, scenarios, sensitivity and pricing

This page describes the forecasting calculator, `scripts/forecast.py`. It sits beside the original calculator (`scripts/calculate.py`), which is unchanged, and it is used by the `scenario-comparison` and `pricing-analysis` skills.

A forecast shows what follows from the inputs you give it. It does not predict results and does not verify the inputs. Every figure comes from deterministic code, never from a model's arithmetic, and every result carries a receipt.

## What it guarantees

- **Deterministic.** The same inputs always give the same output, including the receipt fingerprint. It uses exact decimal arithmetic.
- **Validated inputs.** It uses the calculator's input rules: plain numbers written with ASCII digits, at most 64 characters, an absolute value of at most 1,000,000,000,000. Months must be a whole number from 1 to 120, and monthly unit growth must be from -0.99 to 1. Any result above 1,000,000,000,000,000,000,000,000 is rejected as implausible.
- **No side effects.** No network, no file reads or writes, no other programs. It uses only the Python standard library, and `hashlib` only to compute the receipt.
- **Run by file path**, like the calculator, so a `scripts` folder elsewhere cannot shadow it.

## The monthly model

The model has eight inputs, in this order:

| Input | Meaning |
|---|---|
| `starting_cash` | Cash at the start. Not negative. |
| `months` | How many months to forecast, 1 to 120. |
| `starting_units` | Units sold in month 1. |
| `monthly_unit_growth` | Change in units each month as a fraction, for example `0.03` for 3 percent. |
| `price` | Price per unit. |
| `variable_cost` | Variable cost per unit. |
| `fixed_costs` | Fixed costs per month, **excluding acquisition spending**. |
| `acquisition_spend` | Total acquisition spending per month. |

For each month: revenue is units times price, variable costs are units times variable cost, and operating profit is revenue minus variable costs, acquisition spending and fixed costs. Net cash flow equals operating profit. Ending cash is opening cash plus net cash flow.

The summary reports total revenue, total operating profit, ending cash, the lowest cash balance and its month, the month cash first goes below zero, runway in months, and the first month with a non-negative operating profit. Runway is the whole months before the month cash runs out plus the share of that month the cash lasts, which is that month's opening cash divided by its outflow. It is blank if cash does not run out within the horizon.

Acquisition spending enters exactly once. `fixed_costs` must not include it. Growth is an input, not a result of acquisition spending: the model does not link spend to growth.

## Assumptions and exclusions

Every receipt lists these assumptions:

- Revenue is received as cash in the month it is earned.
- Units start at `starting_units` and change by the growth rate each month.
- Price, variable cost, fixed costs and acquisition spending are the same every month.
- Cash is allowed to go below zero so the size of a funding gap is visible. No new funding is assumed.

It leaves out taxes, interest and other financing flows, capital expenditures, working capital and payment timing, seasonality, refunds and chargebacks, and owner pay unless it is in `fixed_costs`. If one of these matters for a business, the forecast is incomplete for that business.

## Operations

```bash
python3 scripts/forecast.py monthly-forecast 5000 12 100 0.03 24 9.50 1500 600
```

Prints the monthly table and the summary.

```bash
python3 scripts/forecast.py scenario-compare --scenario conservative 5000 12 80 0.01 24 9.50 1500 600 --scenario base 5000 12 100 0.03 24 9.50 1500 600
```

Compares 2 to 5 scenarios, each with the eight inputs. All scenarios must use the same number of months so they are comparable. The output lists which inputs differ (`varied_inputs`), each scenario's summary, the differences from the first scenario, and the scenarios ordered by ending cash. It does not label any scenario likely or expected, and no probabilities are assigned.

```bash
python3 scripts/forecast.py sensitivity 5000 12 100 0.03 24 9.50 1500 600 --delta 10 --delta 20
```

Moves one input at a time down and up by each percentage while the others stay at their base values, and reports the change in ending cash and total operating profit. Use `--vary` to choose inputs. It ranks inputs by the largest change in ending cash. An input whose base value is 0 cannot move by a percentage, and the output says so. A change that would make an input invalid, for example growth above 1, is an error.

```bash
python3 scripts/forecast.py price-compare 9.50 1500 12 100 24 29 34
```

Takes `VARIABLE_COST FIXED_COSTS CAC_PER_CUSTOMER EXPECTED_UNITS` and then 1 to 8 candidate prices. For each price it reports the contribution per unit and margin, break-even units with and without acquisition cost, revenue and operating profit at the expected volume, and the units needed to match the first price's profit. **Expected units are the same at every price. The model does not predict how demand responds to price.** Each customer is assumed to buy one unit, so CAC is charged once per unit.

## Calculation receipts

Every output has a `receipt`:

- `fingerprint`: `sha256:` followed by the SHA-256 of the operation, model, engine version and the inputs exactly as given.
- `model` and `engine_version`: what produced the result.
- `inputs`, `assumptions` and `exclusions`: what the result rests on.

The same inputs always give the same fingerprint and any change gives a different one. A receipt proves that a result is reproducible from stated inputs. It does not prove that the inputs are true.

## Display rounding

Values are printed in plain notation and rounded for display, as in the calculator. The arithmetic is exact. Do not feed a displayed value back in as an input. Run the command again with the original inputs.

## Using it in a handoff

A forecast result goes into a `venturine-handoff/v1` document as an entry in `calculations`, with the operation name, every input tied to a ledger entry that carries its label, `engine_validated: true`, the printed `engine_version`, the printed `receipt`, and `acquisition_counted_once: true`. The validator requires the receipt for an engine-validated forecast result and refuses one on a result that was not. See [handoff-v1.md](handoff-v1.md), and [forecast-handoff.example.json](forecast-handoff.example.json) for an example whose receipt is the one the calculator printed.

## Limitations

- A forecast is as reliable as its inputs. A guess entered as a number is still a guess, and the handoff keeps it labeled `ASSUMPTION`.
- Growth, price and costs are constant by assumption. Real businesses are not that smooth.
- Repeat purchases and customer lifetime value are not modeled here.

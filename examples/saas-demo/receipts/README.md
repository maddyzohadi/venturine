# Calculator receipts

These are the exact outputs of the calculators the demo run executed. All inputs are hypothetical founder inputs (see [../inputs.md](../inputs.md)). The calculators are deterministic: run the commands below from the root of a clone of this repository and you should get byte-for-byte the same JSON (`python3` 3.9 or newer, standard library only).

| File | Command | Result |
|---|---|---|
| [01-contribution-margin.json](01-contribution-margin.json) | `python3 scripts/calculate.py contribution-margin 49 9` | $40.00 per clinic per month |
| [02-gross-margin.json](02-gross-margin.json) | `python3 scripts/calculate.py gross-margin 49 9` | gross profit $40.00, 81.63% |
| [03-break-even.json](03-break-even.json) | `python3 scripts/calculate.py break-even 2100 49 9` | 53 clinics (operating break-even; the output says acquisition is not included) |
| [04-break-even-loaded-rejected.md](04-break-even-loaded-rejected.md) | `python3 scripts/calculate.py break-even-loaded 1200 49 9 150` | rejected: contribution after CAC would be negative |
| [05-subscription-ltv.json](05-subscription-ltv.json) | `python3 scripts/calculate.py subscription-ltv 40 0.04` | $1,000.00 |
| [06-cac.json](06-cac.json) | `python3 scripts/calculate.py cac 900 6` | $150.00 |
| [07-forecast-conservative.json](07-forecast-conservative.json) | `python3 scripts/forecast.py monthly-forecast 40000 24 6 0.08 49 9 1200 900` | ending cash $5,623.54; no break-even in 24 months |
| [08-forecast-base.json](08-forecast-base.json) | `python3 scripts/forecast.py monthly-forecast 40000 24 6 0.15 49 9 1200 900` | ending cash $33,800.28; break-even month 17 |
| [09-forecast-optimistic.json](09-forecast-optimistic.json) | `python3 scripts/forecast.py monthly-forecast 40000 24 6 0.22 49 9 1200 900` | ending cash $117,460.03; break-even month 12 |

The forecast files carry a `receipt` object: the exact inputs, the model assumptions and exclusions, and a SHA-256 fingerprint of them. Two runs with the same inputs give the same fingerprint, so a reader can tell whether a quoted figure came from these inputs.

The rejected command (04) is kept on purpose: the engine refuses a loaded break-even when the customer acquisition cost is larger than the margin per customer, instead of returning a meaningless number.

A calculator result shows that the arithmetic is right for the inputs. It does not show that the inputs are true.

> **Hypothetical example.** Verbatim output of the `scenario-comparison` skill from the demo run described in [../run-log.md](../run-log.md). Nothing here is real market data.

Running the three scenarios one at a time with forecast.py. Starting with conservative (8%/month).

Conservative receipt captured. Running base scenario (15%/month).

Base receipt captured. Running optimistic scenario (22%/month).

All three receipts captured. Compiling the scenario comparison.

---

## Scenario Comparison — SlotKeeper (Hypothetical)

> **HYPOTHETICAL TEACHING EXAMPLE.** All growth rates are ASSUMPTION. No figures have been externally verified. Calculator receipts are shown exactly as printed by the engine (venturine-forecast/v1, v0.2.1). This output is for illustrative purposes only and is not financial, legal, or investment advice.

---

### 1. Input Ledger

| ID | Input | Value | Label | Note |
|---|---|---|---|---|
| E1 | Price | $49/clinic/month | FOUNDER_PROVIDED | Same across all scenarios |
| E2 | Variable cost | $9/clinic/month | FOUNDER_PROVIDED | Same across all scenarios |
| E3 | Fixed costs (excl. acquisition) | $1,200/month | FOUNDER_PROVIDED | Same across all scenarios |
| E4 | Acquisition spend | $900/month | FOUNDER_PROVIDED | Same; counted once; excluded from E3 |
| E5 | Starting cash | $40,000 | FOUNDER_PROVIDED | Same across all scenarios |
| E6 | Forecast horizon | 24 months | FOUNDER_PROVIDED | Same across all scenarios |
| E7 | Month 1 paying clinics | 6 | FOUNDER_PROVIDED | Same starting point |
| E8 | Monthly growth rate — base | 15%/month | ASSUMPTION | Varied input |
| E9 | Monthly growth rate — conservative | 8%/month | ASSUMPTION | Varied input |
| E10 | Monthly growth rate — optimistic | 22%/month | ASSUMPTION | Varied input |
| E12 | Reachable clinics in region | 1,000 | ASSUMPTION | Market ceiling; not modelled by calculator |

**What differs between scenarios:** monthly unit growth rate only (E8/E9/E10).
**What is constant:** all other inputs (E1–E7).
**No probabilities assigned.** No scenario is called "expected."

---

### 2. Calculator Receipts

#### Scenario F1 — Conservative (8%/month) · engine v0.2.1
```
fingerprint: sha256:aef4f1d400108130d4dc2361fd395d9d856c8369afa9b210f13a0b52a6a5eee4
model: venturine-forecast/v1
inputs: starting_cash=40000, months=24, starting_units=6,
        monthly_unit_growth=0.08, price=49, variable_cost=9,
        fixed_costs=1200, acquisition_spend=900
acquisition_counted_once: true (acquisition_spend separate from fixed_costs)
```

#### Scenario F2 — Base (15%/month) · engine v0.2.1
```
fingerprint: sha256:1f2c6d14b65f353896d0b4e02765c3b801fed30efc4e026959ab957338d03bdb
model: venturine-forecast/v1
inputs: starting_cash=40000, months=24, starting_units=6,
        monthly_unit_growth=0.15, price=49, variable_cost=9,
        fixed_costs=1200, acquisition_spend=900
acquisition_counted_once: true
```

#### Scenario F3 — Optimistic (22%/month) · engine v0.2.1
```
fingerprint: sha256:bfaa054e7e0a45f047ceeafbce119823dc50af637a66c1a685f1eb373051f9ee
model: venturine-forecast/v1
inputs: starting_cash=40000, months=24, starting_units=6,
        monthly_unit_growth=0.22, price=49, variable_cost=9,
        fixed_costs=1200, acquisition_spend=900
acquisition_counted_once: true
```

---

### 3. Results Side by Side (all DERIVED)

| Metric | Conservative (8%) | Base (15%) | Optimistic (22%) |
|---|---|---|---|
| Growth rate label | ASSUMPTION | ASSUMPTION | ASSUMPTION |
| **Break-even month** | **Never (>24)** | **Month 17** | **Month 12** |
| Cash-out month | None | None | None |
| Runway (months) | N/A — never cash-negative | N/A | N/A |
| Minimum cash | $5,623.54 (Month 24) | $19,772.19 (Month 16) | $25,530.89 (Month 11) |
| Ending cash (Month 24) | $5,623.54 | $33,800.28 | $117,460.03 |
| Total operating profit (24 mo.) | −$34,376.46 | −$6,199.72 | +$77,460.03 |
| Total revenue (24 mo.) | $19,628.84 | $54,145.35 | $156,628.53 |
| Month 24 clinic count | 35.2 | 149.4 | 581.3 |
| Month 24 MRR | $1,726.21 | $7,318.09 | $28,485.47 |

---

### 4. Monthly Milestones — Key Months

| Month | Conservative clinics | Base clinics | Optimistic clinics |
|---|---|---|---|
| 1 | 6.0 | 6.0 | 6.0 |
| 6 | 8.8 | 12.1 | 16.2 |
| 12 | 14.0 | 27.9 | **53.5 (break-even)** |
| 17 | 20.6 | **56.2 (break-even)** | 144.5 |
| 18 | 22.2 | 64.6 | 176.3 |
| 24 | 35.2 | 149.4 | 581.3 |

> Break-even is 53 clinics (from unit-economics C3). Rows marked **bold** are break-even months.

---

### 5. Market Ceiling Note

The 1,000-clinic regional ceiling is an ASSUMPTION (E12). The model does not enforce it; the calculator grows units indefinitely.

- **Conservative:** Month 24 = 35 clinics — 3.5% of ceiling. No ceiling risk within the horizon.
- **Base:** Month 24 = 149 clinics — 14.9% of ceiling. No ceiling risk within the horizon.
- **Optimistic:** Month 24 = 581 clinics — 58.1% of ceiling. At 22%/month the model would reach 1,000 clinics at approximately **Month 27** (manual estimate: 6 × 1.22²⁶ ≈ 988). Growth would slow or stop near that point. The Month 24 figure is therefore **overstated** if the ceiling is real.

---

### 6. What Drives the Result

The growth rate is the dominant variable. All other inputs are shared:

- **Conservative at 8%:** Never reaches break-even within 24 months. Cash falls steadily from $40,000 to $5,624. The business survives but does not turn profitable — it exits the horizon still losing ~$691/month.
- **Base at 15%:** Reaches break-even at Month 17, minimum cash $19,772 at Month 16. Ends Month 24 with $33,800 and growing. This scenario is cash-safe for the full horizon.
- **Optimistic at 22%:** Reaches break-even at Month 12, minimum cash $25,531 at Month 11. Ends Month 24 at $117,460. The final months show very large profit figures that would require approaching or exceeding the 1,000-clinic ceiling — treat these as upper-bound only.

None of these scenarios produces a cash-out within 24 months given $40,000 starting cash, because the business starts with large cash reserves relative to the monthly burn.

---

### 7. Model Limits That Matter Here

The model assumes:
- Revenue is received as cash in the month earned (no payment lag)
- Growth rate is constant and does not respond to market saturation or competition
- Acquisition spend converts linearly to units at a fixed rate every month
- Price, variable cost, fixed costs, and acquisition spend are constant for 24 months

**Exclusions relevant to SlotKeeper:**
- **HIPAA compliance costs:** Not in the variable cost; if material, contribution margin and break-even both shift adversely
- **Founder salary:** Excluded from fixed costs by design; if the founder eventually takes salary, break-even rises
- **Churn:** The 4% monthly churn (ASSUMPTION) is not applied to the unit count in this model — the calculator grows units monotonically. In reality, clinics that leave reduce the active base, compressing revenue. This means all three forecasts **overstate** MRR and ending cash to the extent that net churn reduces the active base
- **Market saturation:** Not modelled; optimistic scenario approaches the 1,000-clinic ceiling at Month ~27

---

### 8. What to Measure Next

| Priority | Measurement | Why it reduces uncertainty |
|---|---|---|
| 1 | Actual new clinics acquired in first 2 months | Reveals true early growth rate; most consequential input |
| 2 | Actual churn after 3–6 months | Determines whether the monotonic growth assumption holds |
| 3 | HIPAA compliance cost | Corrects variable cost; shifts break-even and all forecasts |
| 4 | Channel conversion rate from $900/month spend | Validates or refutes the implied CAC of $150 |

---

### Handoff Block

```json
{
  "schema": "venturine-handoff/v1",
  "created": "2026-11-21",
  "producer": {
    "component": "scenario-comparison",
    "kind": "skill"
  },
  "venture": {
    "name": "SlotKeeper (fictional)",
    "hypothetical": true
  },
  "evidence_ledger": [
    {
      "id": "E1", "claim": "Price per clinic per month", "label": "FOUNDER_PROVIDED", "value": "49", "unit": "USD/clinic/month", "category": "pricing"
    },
    {
      "id": "E2", "claim": "Variable cost per clinic per month", "label": "FOUNDER_PROVIDED", "value": "9", "unit": "USD/clinic/month", "category": "cost"
    },
    {
      "id": "E3", "claim": "Fixed costs per month (excl. acquisition)", "label": "FOUNDER_PROVIDED", "value": "1200", "unit": "USD/month", "category": "cost"
    },
    {
      "id": "E4", "claim": "Monthly acquisition spend", "label": "FOUNDER_PROVIDED", "value": "900", "unit": "USD/month", "category": "cost"
    },
    {
      "id": "E5", "claim": "Starting cash", "label": "FOUNDER_PROVIDED", "value": "40000", "unit": "USD"
    },
    {
      "id": "E6", "claim": "Forecast horizon", "label": "FOUNDER_PROVIDED", "value": "24", "unit": "months"
    },
    {
      "id": "E7", "claim": "Paying clinics at Month 1", "label": "FOUNDER_PROVIDED", "value": "6", "unit": "clinics"
    },
    {
      "id": "E8", "claim": "Monthly growth rate — base", "label": "ASSUMPTION", "value": "15", "unit": "percent/month", "category": "customer"
    },
    {
      "id": "E9", "claim": "Monthly growth rate — conservative", "label": "ASSUMPTION", "value": "8", "unit": "percent/month", "category": "customer"
    },
    {
      "id": "E10", "claim": "Monthly growth rate — optimistic", "label": "ASSUMPTION", "value": "22", "unit": "percent/month", "category": "customer"
    },
    {
      "id": "E12", "claim": "Reachable clinics in region (market ceiling)", "label": "ASSUMPTION", "value": "1000", "unit": "clinics", "category": "market"
    },
    {
      "id": "E32", "claim": "Conservative scenario: break-even month", "label": "DERIVED", "value": "none within 24 months", "unit": "month", "calculation": "F1", "derived_from": ["E1","E2","E3","E4","E5","E6","E7","E9"]
    },
    {
      "id": "E33", "claim": "Base scenario: break-even month", "label": "DERIVED", "value": "17", "unit": "month", "calculation": "F2", "derived_from": ["E1","E2","E3","E4","E5","E6","E7","E8"]
    },
    {
      "id": "E34", "claim": "Optimistic scenario: break-even month", "label": "DERIVED", "value": "12", "unit": "month", "calculation": "F3", "derived_from": ["E1","E2","E3","E4","E5","E6","E7","E10"]
    },
    {
      "id": "E35", "claim": "Conservative scenario: Month 24 ending cash", "label": "DERIVED", "value": "5623.54", "unit": "USD", "calculation": "F1"
    },
    {
      "id": "E36", "claim": "Base scenario: Month 24 ending cash", "label": "DERIVED", "value": "33800.28", "unit": "USD", "calculation": "F2"
    },
    {
      "id": "E37", "claim": "Optimistic scenario: Month 24 ending cash", "label": "DERIVED", "value": "117460.03", "unit": "USD", "calculation": "F3", "limitations": "Approaches 1,000-clinic ceiling at ~Month 27; Month 24 figures may be overstated"
    }
  ],
  "calculations": [
    {
      "id": "F1",
      "operation": "monthly-forecast",
      "inputs": [
        {"name": "starting_cash", "value": "40000", "evidence": "E5"},
        {"name": "months", "value": "24", "evidence": "E6"},
        {"name": "starting_units", "value": "6", "evidence": "E7"},
        {"name": "monthly_unit_growth", "value": "0.08", "evidence": "E9"},
        {"name": "price", "value": "49", "evidence": "E1"},
        {"name": "variable_cost", "value": "9", "evidence": "E2"},
        {"name": "fixed_costs", "value": "1200", "evidence": "E3"},
        {"name": "acquisition_spend", "value": "900", "evidence": "E4"}
      ],
      "result": {"break_even_month": null, "ending_cash": "5623.54", "minimum_cash": "5623.54", "minimum_cash_month": 24, "cash_out_month": null},
      "receipt": "sha256:aef4f1d400108130d4dc2361fd395d9d856c8369afa9b210f13a0b52a6a5eee4",
      "engine_validated": true,
      "engine_version": "0.2.1",
      "acquisition_counted_once": true
    },
    {
      "id": "F2",
      "operation": "monthly-forecast",
      "inputs": [
        {"name": "starting_cash", "value": "40000", "evidence": "E5"},
        {"name": "months", "value": "24", "evidence": "E6"},
        {"name": "starting_units", "value": "6", "evidence": "E7"},
        {"name": "monthly_unit_growth", "value": "0.15", "evidence": "E8"},
        {"name": "price", "value": "49", "evidence": "E1"},
        {"name": "variable_cost", "value": "9", "evidence": "E2"},
        {"name": "fixed_costs", "value": "1200", "evidence": "E3"},
        {"name": "acquisition_spend", "value": "900", "evidence": "E4"}
      ],
      "result": {"break_even_month": 17, "ending_cash": "33800.28", "minimum_cash": "19772.19", "minimum_cash_month": 16, "cash_out_month": null},
      "receipt": "sha256:1f2c6d14b65f353896d0b4e02765c3b801fed30efc4e026959ab957338d03bdb",
      "engine_validated": true,
      "engine_version": "0.2.1",
      "acquisition_counted_once": true
    },
    {
      "id": "F3",
      "operation": "monthly-forecast",
      "inputs": [
        {"name": "starting_cash", "value": "40000", "evidence": "E5"},
        {"name": "months", "value": "24", "evidence": "E6"},
        {"name": "starting_units", "value": "6", "evidence": "E7"},
        {"name": "monthly_unit_growth", "value": "0.22", "evidence": "E10"},
        {"name": "price", "value": "49", "evidence": "E1"},
        {"name": "variable_cost", "value": "9", "evidence": "E2"},
        {"name": "fixed_costs", "value": "1200", "evidence": "E3"},
        {"name": "acquisition_spend", "value": "900", "evidence": "E4"}
      ],
      "result": {"break_even_month": 12, "ending_cash": "117460.03", "minimum_cash": "25530.89", "minimum_cash_month": 11, "cash_out_month": null},
      "receipt": "sha256:bfaa054e7e0a45f047ceeafbce119823dc50af637a66c1a685f1eb373051f9ee",
      "engine_validated": true,
      "engine_version": "0.2.1",
      "acquisition_counted_once": true
    }
  ],
  "open_questions": [
    "What is the actual monthly growth rate in the first 3 months of operation?",
    "Does 4% monthly churn materially reduce the active clinic base relative to the monotonic growth model?",
    "At what month does the optimistic scenario effectively slow due to approaching the 1,000-clinic ceiling?",
    "What HIPAA compliance cost should be added to variable cost?"
  ],
  "next_steps": [
    "Run assumption-ledger to rank and prioritise all open assumptions from all skills",
    "Run evidence-audit on the full ledger before treating any scenario as a planning basis",
    "Validate Month-1 and Month-2 growth actuals as soon as the product launches",
    "Re-run with net-churn-adjusted growth rate once real churn data is available"
  ]
}
```

Running assumption-ledger next.

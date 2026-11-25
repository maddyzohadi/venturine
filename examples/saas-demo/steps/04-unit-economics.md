> **Hypothetical example.** Verbatim output of the `unit-economics` skill from the demo run described in [../run-log.md](../run-log.md). Nothing here is real market data.

I'll run the calculate.py engine now, one command at a time. Starting with contribution margin.

**C1 — Contribution margin receipt:** `$40.00/clinic/month` (engine v0.2.1). Now running gross margin.

**C2 — Gross margin receipt:** 81.63%, gross profit $40.00. Now running break-even (Framing 1: acquisition budget included in fixed costs).

**C3 — Break-even receipt (Framing 1):** 53 clinics. Now running Framing 2 (loaded, CAC = $150 implied from $900 ÷ 6 Month-1 clinics).

**C4 — Loaded break-even:** Calculator rejected — `Break-even requires positive contribution margin after customer acquisition cost.` CAC ($150 implied) exceeds per-clinic contribution ($40), so loaded break-even is not reachable on a single-purchase basis. This is expected for a subscription model where viability depends on multi-month retention. Now running subscription LTV.

**C5 — LTV receipt:** $1,000.00. Now running implied CAC.

**C6 — CAC receipt:** $150.00. All five calculator runs complete. Compiling the full unit economics output.

---

## Unit Economics — SlotKeeper (Hypothetical)

> **HYPOTHETICAL TEACHING EXAMPLE.** All inputs are FOUNDER_PROVIDED or ASSUMPTION. No figures have been externally verified. Calculator receipts are shown exactly as printed by the engine. This output is for illustrative purposes only and is not financial, legal, or investment advice.

---

### Executive Financial Assessment

SlotKeeper's per-clinic economics are strong on paper: an 81.63% gross margin and $40/clinic/month contribution. The implied CAC of $150 is recovered in 3.75 months of contribution, and the LTV/CAC ratio of 6.67× (derived manually) is favourable for a SaaS business. The steady-state operating break-even is **53 clinics** when the $900/month acquisition budget is treated as a fixed cost — the product starts at 6 clinics in Month 1, so reaching break-even depends entirely on the ASSUMPTION-labelled growth rates. All inputs are unverified; HIPAA compliance costs are excluded and could reduce the contribution margin meaningfully.

---

### Input Ledger

| ID | Input | Value | Label | Note |
|---|---|---|---|---|
| E1 | Price | $49/clinic/month | FOUNDER_PROVIDED | |
| E2 | Variable cost | $9/clinic/month | FOUNDER_PROVIDED | Messaging + hosting |
| E3 | Fixed costs (excl. acquisition) | $1,200/month | FOUNDER_PROVIDED | |
| E4 | Acquisition spend | $900/month | FOUNDER_PROVIDED | Treated as separate fixed budget |
| E5 | Starting cash | $40,000 | FOUNDER_PROVIDED | |
| E7 | Month 1 clinics | 6 | FOUNDER_PROVIDED | Used to derive Month-1 implied CAC |
| E11 | Monthly churn | 4% | ASSUMPTION | For LTV only; unvalidated |

---

### Calculator Receipts (all engine v0.2.1)

#### C1 — Contribution Margin
```
Command: calculate.py contribution-margin 49 9
{
  "operation": "contribution-margin",
  "inputs": ["49", "9"],
  "result": "40.00",
  "status": "calculated"
}
```
**$40.00 per clinic per month** (DERIVED from E1, E2)

---

#### C2 — Gross Margin
```
Command: calculate.py gross-margin 49 9
{
  "operation": "gross-margin",
  "inputs": ["49", "9"],
  "result": {
    "gross_profit": "40.00",
    "gross_margin_percent": "81.63"
  },
  "status": "calculated"
}
```
**Gross margin 81.63%, gross profit $40.00** (DERIVED from E1, E2)

---

#### C3 — Break-Even (Framing 1: acquisition budget in fixed costs)
```
Command: calculate.py break-even 2100 49 9
{
  "operation": "break-even",
  "inputs": ["2100", "49", "9"],
  "result": 53,
  "units_rounding": "Rounded up to whole units.",
  "acquisition_included": false,
  "warning": "Operating break-even only. Customer acquisition costs are not included;
              use break-even-loaded when acquisition spending is relevant.",
  "status": "calculated"
}
```
**53 clinics** to reach operating break-even (DERIVED).

> **Framing note:** The $900/month acquisition budget is included in the $2,100 fixed-cost total here (Framing 1). This is the steady-state monthly break-even when the acquisition budget is a constant monthly spend, with CAC treated as $0 per customer. The calculator correctly notes `acquisition_included: false` because the per-customer CAC argument was not passed — the acquisition money entered via the fixed-cost total instead.

#### C4 — Break-Even Loaded (Framing 2: per-customer CAC = $150)
```
Command: calculate.py break-even-loaded 1200 49 9 150
ERROR: Break-even requires positive contribution margin after customer acquisition cost.
```
**Calculator rejected.** Loaded contribution = $49 − $9 − $150 = **−$110**. CAC ($150) exceeds contribution margin ($40) so single-purchase break-even is not reachable. This is structurally expected for a subscription model: viability depends on multi-month retention, not a single transaction. The LTV calculation (C5) addresses this.

> **Double-counting safeguard:** $900/month acquisition spend is the same money in both framings. It was entered in Framing 1 as part of fixed costs and in Framing 2 as a per-customer CAC. Only one framing applies at a time; both numbers are never counted simultaneously.

---

#### C5 — Subscription LTV
```
Command: calculate.py subscription-ltv 40 0.04
{
  "operation": "subscription-ltv",
  "inputs": ["40", "0.04"],
  "result": "1000.00",
  "status": "calculated"
}
```
**LTV = $1,000.00** (DERIVED from C1, E11)

Formula: monthly contribution ($40) ÷ monthly churn rate (0.04) = $1,000. This implies an average clinic tenure of 25 months. **The 4% churn rate is an ASSUMPTION with no empirical basis.**

---

#### C6 — Implied CAC
```
Command: calculate.py cac 900 6
{
  "operation": "cac",
  "inputs": ["900", "6"],
  "result": "150.00",
  "status": "calculated"
}
```
**Implied CAC = $150.00** (DERIVED from E4, E7)

> Month-1 new clinics (6) is FOUNDER_PROVIDED. The implied CAC is ASSUMPTION-dependent because: (a) the 6 clinics are a Month-1 target, not an observed result; (b) the $900 acquisition spend is a budget, not a measured result; (c) if fewer than 6 clinics are acquired, CAC rises proportionally.

---

### Derived Metrics (manual calculation, not engine-validated)

| Metric | Value | Formula | Label |
|---|---|---|---|
| LTV / CAC ratio | 6.67× | $1,000 ÷ $150 | DERIVED (manual) |
| CAC payback period | 3.75 months | $150 ÷ $40/month | DERIVED (manual) |
| Month 1 MRR | $294 | 6 × $49 | DERIVED (manual) |
| Month 1 net cash flow | −$1,806/month | $294 − $2,100 | DERIVED (manual) |

> LTV/CAC and CAC payback have no dedicated calculator command; these are manual arithmetic from the engine's outputs. Allowing the calculator and re-running would not change them, as there is no supported operation for these two metrics.

---

### Cost Structure

| Category | Amount | Label |
|---|---|---|
| Variable cost per clinic | $9/month | FOUNDER_PROVIDED |
| Fixed operating costs | $1,200/month | FOUNDER_PROVIDED |
| Acquisition spend | $900/month | FOUNDER_PROVIDED |
| **Total monthly fixed burden** | **$2,100/month** | DERIVED |
| HIPAA compliance costs | UNKNOWN | — |
| Founder salary | $0 | FOUNDER_PROVIDED |

---

### Break-Even Summary

| Framing | Break-even | Method |
|---|---|---|
| Framing 1 (acquisition as fixed monthly budget) | **53 clinics** | Engine-validated (C3) |
| Framing 2 (acquisition as per-customer CAC) | **Not reachable on single purchase** | Engine-rejected (C4) — subscription retention required |

Month 1 starts at 6 clinics — **47 short of break-even**. The pace at which break-even is reached depends on the ASSUMPTION-labelled growth rates and will be modelled in scenario-comparison.

---

### Risk Register

| Risk | Impact |
|---|---|
| 4% churn ASSUMPTION overstates LTV | LTV is highly sensitive: at 8% churn, LTV = $500; at 2% churn, LTV = $2,000 |
| HIPAA compliance cost excluded | Adding even $3/clinic/month in compliance variable cost reduces contribution to $37; break-even rises to 57 clinics |
| CAC rises if Month-1 target not met | At 3 new clinics in Month 1, implied CAC = $300; LTV/CAC falls to 3.3× |
| Growth rates are ASSUMPTION | Break-even timing is entirely unvalidated |
| $900 acquisition budget may not convert 6 clinics | No channel identified; actual CAC is unknown |

---

### Final Assessment

**ECONOMICALLY PROMISING UNDER STATED ASSUMPTIONS**

The unit economics are structurally sound: 81.63% gross margin, $40 contribution per clinic, $1,000 LTV against $150 CAC, and a 3.75-month payback. The 53-clinic break-even is reachable in theory within the 24-month horizon if growth assumptions hold. However, every input that determines whether this promise is real — churn, growth rate, actual CAC, HIPAA compliance cost — is either ASSUMPTION or UNKNOWN. The economics must be re-evaluated once those gaps are resolved.

---

### Handoff Block

```json
{
  "schema": "venturine-handoff/v1",
  "created": "2026-11-21",
  "producer": {
    "component": "unit-economics",
    "kind": "skill"
  },
  "venture": {
    "name": "SlotKeeper (fictional)",
    "hypothetical": true
  },
  "evidence_ledger": [
    {
      "id": "E1",
      "claim": "Price per clinic per month",
      "label": "FOUNDER_PROVIDED",
      "value": "49",
      "unit": "USD/clinic/month",
      "category": "pricing"
    },
    {
      "id": "E2",
      "claim": "Variable cost per clinic per month",
      "label": "FOUNDER_PROVIDED",
      "value": "9",
      "unit": "USD/clinic/month",
      "category": "cost"
    },
    {
      "id": "E3",
      "claim": "Fixed costs per month (excl. acquisition)",
      "label": "FOUNDER_PROVIDED",
      "value": "1200",
      "unit": "USD/month",
      "category": "cost"
    },
    {
      "id": "E4",
      "claim": "Monthly acquisition spend",
      "label": "FOUNDER_PROVIDED",
      "value": "900",
      "unit": "USD/month",
      "category": "cost"
    },
    {
      "id": "E5",
      "claim": "Starting cash",
      "label": "FOUNDER_PROVIDED",
      "value": "40000",
      "unit": "USD"
    },
    {
      "id": "E7",
      "claim": "Paying clinics at Month 1",
      "label": "FOUNDER_PROVIDED",
      "value": "6",
      "unit": "clinics"
    },
    {
      "id": "E8",
      "claim": "Monthly growth rate — base",
      "label": "ASSUMPTION",
      "value": "15",
      "unit": "percent/month",
      "category": "customer"
    },
    {
      "id": "E9",
      "claim": "Monthly growth rate — conservative",
      "label": "ASSUMPTION",
      "value": "8",
      "unit": "percent/month",
      "category": "customer"
    },
    {
      "id": "E10",
      "claim": "Monthly growth rate — optimistic",
      "label": "ASSUMPTION",
      "value": "22",
      "unit": "percent/month",
      "category": "customer"
    },
    {
      "id": "E11",
      "claim": "Monthly churn rate (LTV only)",
      "label": "ASSUMPTION",
      "value": "4",
      "unit": "percent/month",
      "category": "customer"
    },
    {
      "id": "E12",
      "claim": "Reachable clinics in launch region",
      "label": "ASSUMPTION",
      "value": "1000",
      "unit": "clinics",
      "category": "market"
    },
    {
      "id": "E25",
      "claim": "Contribution margin per clinic per month",
      "label": "DERIVED",
      "value": "40.00",
      "unit": "USD/clinic/month",
      "category": "cost",
      "calculation": "C1",
      "derived_from": ["E1", "E2"]
    },
    {
      "id": "E26",
      "claim": "Gross margin percentage",
      "label": "DERIVED",
      "value": "81.63",
      "unit": "percent",
      "category": "pricing",
      "calculation": "C2",
      "derived_from": ["E1", "E2"]
    },
    {
      "id": "E27",
      "claim": "Operating break-even (Framing 1: acquisition in fixed costs)",
      "label": "DERIVED",
      "value": "53",
      "unit": "clinics",
      "category": "cost",
      "calculation": "C3",
      "derived_from": ["E3", "E4", "E1", "E2"]
    },
    {
      "id": "E28",
      "claim": "Subscription LTV at 4% monthly churn",
      "label": "DERIVED",
      "value": "1000.00",
      "unit": "USD",
      "category": "customer",
      "calculation": "C5",
      "derived_from": ["E25", "E11"],
      "limitations": "Churn rate is ASSUMPTION; LTV is highly sensitive to this input"
    },
    {
      "id": "E29",
      "claim": "Implied CAC (Month 1: $900 spend / 6 new clinics)",
      "label": "DERIVED",
      "value": "150.00",
      "unit": "USD/clinic",
      "category": "cost",
      "calculation": "C6",
      "derived_from": ["E4", "E7"],
      "limitations": "Both inputs are FOUNDER_PROVIDED targets, not measured results; actual CAC unknown"
    },
    {
      "id": "E30",
      "claim": "LTV/CAC ratio",
      "label": "DERIVED",
      "value": "6.67",
      "unit": "ratio",
      "category": "customer",
      "derived_from": ["E28", "E29"],
      "limitations": "Manual calculation, not engine-validated; inherits all assumptions from E28 and E29"
    },
    {
      "id": "E31",
      "claim": "CAC payback period",
      "label": "DERIVED",
      "value": "3.75",
      "unit": "months",
      "category": "customer",
      "derived_from": ["E29", "E25"],
      "limitations": "Manual calculation, not engine-validated"
    }
  ],
  "calculations": [
    {
      "id": "C1",
      "operation": "contribution-margin",
      "inputs": [
        {"name": "price", "value": "49", "evidence": "E1"},
        {"name": "variable_cost", "value": "9", "evidence": "E2"}
      ],
      "result": "40.00",
      "engine_validated": true,
      "engine_version": "0.2.1"
    },
    {
      "id": "C2",
      "operation": "gross-margin",
      "inputs": [
        {"name": "revenue", "value": "49", "evidence": "E1"},
        {"name": "cogs", "value": "9", "evidence": "E2"}
      ],
      "result": {"gross_profit": "40.00", "gross_margin_percent": "81.63"},
      "engine_validated": true,
      "engine_version": "0.2.1"
    },
    {
      "id": "C3",
      "operation": "break-even",
      "inputs": [
        {"name": "fixed_costs", "value": "2100", "evidence": "E3"},
        {"name": "price", "value": "49", "evidence": "E1"},
        {"name": "variable_cost", "value": "9", "evidence": "E2"}
      ],
      "result": "53",
      "engine_validated": true,
      "engine_version": "0.2.1"
    },
    {
      "id": "C4",
      "operation": "break-even-loaded",
      "inputs": [
        {"name": "fixed_costs_excl_acquisition", "value": "1200", "evidence": "E3"},
        {"name": "price", "value": "49", "evidence": "E1"},
        {"name": "variable_cost", "value": "9", "evidence": "E2"},
        {"name": "cac", "value": "150", "evidence": "E29"}
      ],
      "result": "ERROR: negative loaded contribution — not reachable on single purchase",
      "engine_validated": false,
      "method": "Calculator rejected: CAC ($150) exceeds contribution margin ($40); subscription retention required for viability"
    },
    {
      "id": "C5",
      "operation": "subscription-ltv",
      "inputs": [
        {"name": "monthly_contribution", "value": "40", "evidence": "E25"},
        {"name": "monthly_churn", "value": "0.04", "evidence": "E11"}
      ],
      "result": "1000.00",
      "engine_validated": true,
      "engine_version": "0.2.1"
    },
    {
      "id": "C6",
      "operation": "cac",
      "inputs": [
        {"name": "total_acquisition_spend", "value": "900", "evidence": "E4"},
        {"name": "new_customers", "value": "6", "evidence": "E7"}
      ],
      "result": "150.00",
      "engine_validated": true,
      "engine_version": "0.2.1"
    }
  ],
  "open_questions": [
    "What is actual monthly churn at comparable SaaS products for small clinics?",
    "What HIPAA compliance costs are excluded from the $9/clinic variable cost?",
    "Will $900/month acquisition spend actually yield 6 new clinics in Month 1?",
    "At what clinic count does growth slow as the 1,000-clinic pool saturates?"
  ],
  "next_steps": [
    "Run scenario-comparison with the three growth scenarios (8%, 15%, 22%) using forecast.py",
    "Validate 4% churn assumption through customer interviews or comparable-product research",
    "Scope HIPAA compliance cost and re-run contribution margin with the corrected variable cost",
    "Run assumption-ledger to rank and prioritise all open assumptions"
  ]
}
```

Running scenario-comparison next with forecast.py for all three scenarios.

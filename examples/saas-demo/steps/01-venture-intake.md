> **Hypothetical example.** Verbatim output of the `venture-intake` skill from the demo run described in [../run-log.md](../run-log.md). Nothing here is real market data.

## Venture Intake — SlotKeeper (Hypothetical)

> **HYPOTHETICAL TEACHING EXAMPLE.** All inputs are fictional. No figures have been verified. This output is for illustrative purposes only and is not financial, legal, or investment advice.

---

### 1. Venture Profile

| Field | Value |
|---|---|
| Company | SlotKeeper (fictional) |
| Stage | Pre-revenue (no existing customers or pilots) |
| Product | SaaS subscription: automated appointment reminders + waitlist slot-filling |
| Target customer | Independent clinics, 1–5 practitioners |
| Customer problem | Missed appointments reduce clinic utilisation and revenue |
| Proposed solution | Software sends reminders and offers freed slots to a waitlist |
| Business model | Monthly subscription per clinic |
| Geography | One hypothetical US region |
| Founder salary | $0 |

---

### 2. Input Ledger

| ID | Input | Value as written | Label | Note |
|---|---|---|---|---|
| E1 | Price | $49 / clinic / month | FOUNDER_PROVIDED | |
| E2 | Variable cost | $9 / clinic / month | FOUNDER_PROVIDED | Described as messaging + hosting |
| E3 | Fixed costs (excl. acquisition) | $1,200 / month | FOUNDER_PROVIDED | Explicitly excludes acquisition spend |
| E4 | Acquisition spend | $900 / month | FOUNDER_PROVIDED | Treated as separate line from fixed costs |
| E5 | Starting cash | $40,000 | FOUNDER_PROVIDED | |
| E6 | Forecast horizon | 24 months | FOUNDER_PROVIDED | |
| E7 | Month 1 paying clinics | 6 | FOUNDER_PROVIDED | Stated alongside "no customers or pilots today" — see inconsistencies |
| E8 | Base growth rate | 15% / month (paying clinics) | ASSUMPTION | Founder-labelled assumption |
| E9 | Conservative growth rate | 8% / month | ASSUMPTION | Founder-labelled assumption |
| E10 | Optimistic growth rate | 22% / month | ASSUMPTION | Founder-labelled assumption |
| E11 | Monthly churn | 4% of active clinics / month | ASSUMPTION | Used for LTV only, per founder |
| E12 | Reachable clinics in region | 1,000 | ASSUMPTION | Founder explicitly flagged as not a statistic |
| E13 | Founder salary | $0 / month | FOUNDER_PROVIDED | No opportunity cost modelled |

---

### 3. Inconsistencies Found

**Minor tension — E7 vs. current stage.**
The founder states "no customers or pilots exist today" but sets Month 1 at 6 paying clinics. These can be reconciled if Month 1 sales happen during the first month of operation, but the intake cannot confirm that. The analysis should treat the 6 as a Month-1 target, not a starting baseline, and note the gap.

**No other inconsistencies detected.** Price ($49) exceeds variable cost ($9), giving a positive contribution per clinic. Acquisition spend is correctly ring-fenced from the fixed-cost figure. All three growth rates are plausible as independent scenarios.

---

### 4. Missing Information (Priority Order)

| Priority | Gap | Why It Matters |
|---|---|---|
| High | UNKNOWN — Customer acquisition cost per clinic (CAC) | Acquisition spend is $900/month but clinics acquired per dollar is not stated; needed for CAC calculation |
| High | UNKNOWN — How Month 1 reaches 6 clinics | No channel, outreach plan, or pilot evidence; this is the riskiest near-term assumption |
| High | UNKNOWN — HIPAA / health-data compliance obligations | Clinics handle patient appointment data; regulatory scope affects variable cost and legal risk |
| High | UNKNOWN — Current reminder workflow clinics use (status quo) | Needed to judge switching friction and competitive alternatives |
| Medium | UNKNOWN — Any customer or problem validation (interviews, surveys) | No pilots exist; willingness to pay at $49 is untested |
| Medium | UNKNOWN — Named competitive alternatives | Cannot assess differentiation without knowing what clinics use today |
| Medium | UNKNOWN — Billing cadence (monthly / annual) | Affects cash flow timing and churn mechanics |
| Low | UNKNOWN — Average no-show rate at target clinics | Would let the founder quantify the problem's dollar value to clinics |
| Low | UNKNOWN — Clinic average monthly revenue | Needed to size the ROI story for the sales pitch |

---

### 5. Readiness for Each Skill

| Skill | Ready? | What is missing |
|---|---|---|
| `idea-validator` | **Yes** | Idea, customer, problem, and geography are all present |
| `market-intelligence` | **Partial** | Market definition present; TAM/SAM/SOM will be UNKNOWN (no external data, only the 1,000-clinic ASSUMPTION) |
| `competitor-intelligence` | **Partial** | Product and customer present; no alternatives named |
| `unit-economics` | **Yes** | Price, variable cost, fixed costs, acquisition spend, and churn are all present |
| `scenario-comparison` | **Yes** | All required fields present (starting cash, horizon, Month-1 units, growth rates, price, variable cost, fixed costs, acquisition spend) |
| `pricing-analysis` | **Partial** | Missing per-clinic CAC and competitive price benchmarks |
| `customer-discovery` | **No** | No research done; no interviews or pilot data |
| `go-to-market` | **No** | No channel evidence, no acquisition test data, no competitive comparison |
| `assumption-ledger` | **Yes** | Intake provides sufficient inputs |

---

### 6. Recommended Next Step

**`idea-validator`** — the fastest way to surface structural problems (market size signal, problem severity, competitive risk) before committing to financial modelling. Run it offline; leave market-size figures UNKNOWN rather than sourcing them from outside data.

A founder committing money or time to any decision based on this intake should plan an **`evidence-audit`** before relying on the outputs.

---

### 7. Handoff Block

```json
{
  "schema": "venturine-handoff/v1",
  "created": "2026-11-21",
  "producer": {
    "component": "venture-intake",
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
      "claim": "Variable cost per clinic per month (messaging + hosting)",
      "label": "FOUNDER_PROVIDED",
      "value": "9",
      "unit": "USD/clinic/month",
      "category": "cost"
    },
    {
      "id": "E3",
      "claim": "Fixed costs per month, excluding acquisition spend",
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
      "id": "E6",
      "claim": "Forecast horizon",
      "label": "FOUNDER_PROVIDED",
      "value": "24",
      "unit": "months"
    },
    {
      "id": "E7",
      "claim": "Paying clinics at Month 1",
      "label": "FOUNDER_PROVIDED",
      "value": "6",
      "unit": "clinics",
      "limitations": "Stated alongside 'no customers or pilots today'; treated as a Month-1 sales target"
    },
    {
      "id": "E8",
      "claim": "Monthly clinic growth rate — base case",
      "label": "ASSUMPTION",
      "value": "15",
      "unit": "percent/month",
      "category": "customer"
    },
    {
      "id": "E9",
      "claim": "Monthly clinic growth rate — conservative case",
      "label": "ASSUMPTION",
      "value": "8",
      "unit": "percent/month",
      "category": "customer"
    },
    {
      "id": "E10",
      "claim": "Monthly clinic growth rate — optimistic case",
      "label": "ASSUMPTION",
      "value": "22",
      "unit": "percent/month",
      "category": "customer"
    },
    {
      "id": "E11",
      "claim": "Monthly churn rate (used for LTV only)",
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
      "category": "market",
      "limitations": "Founder explicitly noted this is not a verified statistic"
    },
    {
      "id": "E13",
      "claim": "Founder salary",
      "label": "FOUNDER_PROVIDED",
      "value": "0",
      "unit": "USD/month"
    },
    {
      "id": "E14",
      "claim": "Target customer segment",
      "label": "FOUNDER_PROVIDED",
      "category": "segment"
    },
    {
      "id": "E15",
      "claim": "Geography",
      "label": "FOUNDER_PROVIDED",
      "category": "market"
    },
    {
      "id": "E16",
      "claim": "Customer acquisition cost per clinic",
      "label": "UNKNOWN",
      "category": "cost",
      "priority": "high"
    },
    {
      "id": "E17",
      "claim": "HIPAA / health-data compliance obligations",
      "label": "UNKNOWN",
      "category": "regulatory",
      "priority": "high"
    },
    {
      "id": "E18",
      "claim": "Current reminder workflow used by target clinics (status quo)",
      "label": "UNKNOWN",
      "category": "competition",
      "priority": "high"
    },
    {
      "id": "E19",
      "claim": "Customer / problem validation evidence (interviews, surveys, pilots)",
      "label": "UNKNOWN",
      "category": "customer",
      "priority": "high"
    },
    {
      "id": "E20",
      "claim": "Named competitive alternatives",
      "label": "UNKNOWN",
      "category": "competition",
      "priority": "medium"
    },
    {
      "id": "E21",
      "claim": "Average no-show rate at target clinics",
      "label": "UNKNOWN",
      "category": "problem",
      "priority": "low"
    }
  ],
  "open_questions": [
    "How does the founder plan to acquire the 6 Month-1 clinics, given no existing customers or pilots?",
    "What is the per-clinic customer acquisition cost implied by the $900/month spend and expected new clinics per month?",
    "Are there HIPAA or state health-data regulations that apply to appointment reminder data?",
    "What do target clinics use today for appointment reminders (status quo and switching friction)?",
    "Has the founder spoken to any potential customers? If so, what was their reaction to $49/month?"
  ],
  "next_steps": [
    "Run idea-validator to surface structural risks before financial modelling",
    "Run market-intelligence offline; leave TAM/SAM/SOM UNKNOWN unless derivable solely from the 1,000-clinic assumption",
    "Run unit-economics and scenario-comparison once idea-validator is complete",
    "Plan an evidence-audit before relying on any output for real decisions"
  ]
}
```

Running idea-validator next.

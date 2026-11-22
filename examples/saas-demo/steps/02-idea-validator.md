> **Hypothetical example.** Verbatim output of the `idea-validator` skill from the demo run described in [../run-log.md](../run-log.md). Nothing here is real market data.

## Idea Validator — SlotKeeper (Hypothetical)

> **HYPOTHETICAL TEACHING EXAMPLE.** Web research is disabled. All market-size figures not derivable from founder inputs are UNKNOWN. No external sources were examined. This output is for illustrative purposes only and is not financial, legal, or investment advice.

---

### 1. Executive Assessment

SlotKeeper addresses a structurally plausible problem — missed appointments reduce clinic revenue — with a subscription model that has positive unit economics on paper. However, every assumption about demand, pricing acceptance, competition, and growth is unvalidated. The HIPAA compliance gap is a potentially material cost and legal risk that is entirely unresolved. No customer has been spoken to, no pilot has run, and the competitive landscape is completely unknown. The idea cannot be advanced to a high-confidence go/no-go without substantially more evidence.

**Recommendation: INSUFFICIENT EVIDENCE (PRELIMINARY — no independent review ran)**

---

### 2. Business Idea Summary

| Field | Detail |
|---|---|
| Product | SaaS: automated appointment reminders + waitlist slot-filling |
| Target customer | Independent clinics, 1–5 practitioners, one hypothetical US region |
| Problem | Missed appointments reduce utilisation and revenue |
| Solution | Software sends reminders; offers freed slots to a waitlist automatically |
| Business model | Monthly subscription, $49/clinic/month |
| Stage | Pre-revenue, no customers or pilots |

---

### 3. Customer Problem and Demand

| Claim | Label | Note |
|---|---|---|
| Missed appointments reduce clinic revenue | ASSUMPTION | Structurally plausible; no data examined |
| Target clinics actively experience this problem | UNKNOWN | No interviews or surveys conducted |
| Target clinics would pay $49/month for this solution | UNKNOWN | No pilots or willingness-to-pay tests run |
| Average no-show rate at target clinics | UNKNOWN | Not provided; needed to quantify problem severity |
| Clinics would switch away from their current workflow | UNKNOWN | Current workflow unknown; switching friction unassessed |
| Observable demand signals (search volume, forum complaints, etc.) | UNKNOWN | Web research disabled |

**Assessment:** The problem is directionally credible — no-shows are a known operational friction in clinical settings — but every demand-side claim is UNKNOWN. There is no evidence that the specific segment (1–5 practitioner independent clinics) considers this a high-priority, paying problem.

---

### 4. Competitive Landscape

| Claim | Label | Note |
|---|---|---|
| Named direct competitors | UNKNOWN | Founder named none; no research conducted |
| Larger EHR/PMS platforms offering built-in reminders | UNKNOWN | Cannot assess without research |
| Standalone reminder/scheduling tools in this segment | UNKNOWN | Cannot assess without research |
| SlotKeeper's differentiation from incumbents | UNKNOWN | Cannot assess without knowing what incumbents offer |
| Typical market price for appointment reminder software | UNKNOWN | Web research disabled |

**Assessment:** The competitive landscape is entirely unmapped. It is structurally likely that some form of appointment reminder functionality exists in the market (practice management systems, standalone tools, or generic messaging platforms). Whether $49/month is competitive, overpriced, or underpriced relative to alternatives is UNKNOWN. The waitlist slot-filling feature may be a differentiator — but without knowing what alternatives offer, this cannot be assessed.

---

### 5. Feasibility and Economics

#### Unit Economics (preliminary, derived from FOUNDER_PROVIDED inputs)

| Metric | Derived value | Basis |
|---|---|---|
| Contribution margin per clinic | $40/month | $49 − $9 (DERIVED) |
| Total monthly fixed burden | $2,100/month | $1,200 + $900 (DERIVED) |
| Break-even clinic count | ~53 clinics | $2,100 ÷ $40 (DERIVED) |
| Month 1 revenue | $294/month | 6 × $49 (DERIVED) |
| Month 1 net cash flow | −$1,806/month | $294 − $2,100 (DERIVED) |

*Note: These are rough preliminary figures. The unit-economics skill will produce validated calculations.*

**Starting cash of $40,000 against a ~$1,806/month Month-1 burn gives an estimated runway of roughly 20+ months before break-even — but only if growth assumptions hold.** That is an ASSUMPTION-dependent outcome, not a verified projection.

#### Technical Feasibility

| Factor | Assessment |
|---|---|
| Messaging infrastructure | Moderate complexity; standard SMS/email APIs exist |
| Scheduling integration | UNKNOWN — depends on whether SlotKeeper reads clinic calendars or operates standalone |
| HIPAA compliance | UNKNOWN — handling patient appointment data in the US almost certainly triggers HIPAA obligations; compliance adds development, legal, and operational costs that are not in the variable cost estimate |
| Waitlist management logic | Moderate complexity — matching freed slots to waitlisted patients in real time |

#### Regulatory Risk (High Priority)

HIPAA compliance status is **UNKNOWN** and is a material risk. If patient names and appointment times are processed, HIPAA's Security Rule, Privacy Rule, and Business Associate Agreement requirements apply. Compliance costs (legal, technical, audit) are not reflected in the $9/clinic/month variable cost. This could change the unit economics meaningfully.

---

### 6. Evidence and Uncertainties

| ID | Claim | Label |
|---|---|---|
| E1 | Price: $49/clinic/month | FOUNDER_PROVIDED |
| E2 | Variable cost: $9/clinic/month | FOUNDER_PROVIDED |
| E3 | Fixed costs: $1,200/month | FOUNDER_PROVIDED |
| E4 | Acquisition spend: $900/month | FOUNDER_PROVIDED |
| E5 | Starting cash: $40,000 | FOUNDER_PROVIDED |
| E7 | Month 1 clinics: 6 | FOUNDER_PROVIDED |
| E8–E10 | Growth rates: 8%, 15%, 22%/month | ASSUMPTION |
| E11 | Monthly churn: 4% | ASSUMPTION |
| E12 | Reachable clinics: 1,000 | ASSUMPTION |
| — | No-show rate at target clinics | UNKNOWN |
| — | Customer willingness to pay at $49/month | UNKNOWN |
| — | Named competitors and their pricing | UNKNOWN |
| — | HIPAA applicability and compliance cost | UNKNOWN |
| — | Clinic scheduling integration requirements | UNKNOWN |
| — | Switching friction from current workflow | UNKNOWN |
| — | TAM / SAM / SOM | UNKNOWN (web disabled; founder's 1,000-clinic figure is ASSUMPTION) |

---

### 7. Top Risks

| Rank | Risk | Why it matters |
|---|---|---|
| 1 | **No customer validation** | Zero evidence that target clinics will pay $49/month; entire revenue model rests on an untested hypothesis |
| 2 | **HIPAA compliance scope unknown** | Could materially increase variable costs and require legal/technical investment before launch |
| 3 | **Competitive displacement** | Existing EHR or scheduling tools may already offer reminders; clinics may not switch |
| 4 | **Month 1 acquisition path undefined** | 6 clinics from zero with $900/month spend and no identified channel; CAC is UNKNOWN |
| 5 | **Growth rates are pure assumption** | 8–22%/month compounding growth has no empirical basis; break-even and runway projections depend entirely on these figures |
| 6 | **Reachable market may be smaller than assumed** | 1,000 clinics is ASSUMPTION; if the actual addressable count is lower, saturation occurs faster and growth slows earlier |
| 7 | **4% churn assumption** | Unvalidated; small-clinic SaaS churn can be considerably higher; LTV is sensitive to this figure |

---

### 8. Validation Experiments (Priority Order)

| Priority | Experiment | What it tests | Cost signal |
|---|---|---|---|
| 1 | 15–20 customer discovery interviews with target clinic owners/managers | Willingness to pay, problem severity, current workflow | Low (time only) |
| 2 | HIPAA compliance scoping call with a healthcare attorney or compliance consultant | Whether the product is in-scope, minimum compliance cost | Low–moderate |
| 3 | Competitive audit (manual search): what do clinics already use for reminders? | Switching friction, incumbent pricing, differentiation | Low (time) |
| 4 | Landing-page pilot with $900 test spend | Actual click-through and signup conversion; implied CAC | Uses existing budget |
| 5 | 2–3 clinic pilot (free or discounted) | Activation, actual usage, retention signal, NPS | Moderate (dev time) |
| 6 | No-show rate survey or secondary data | Quantify problem severity to build ROI narrative | Low |

---

### 9. Recommendation

**INSUFFICIENT EVIDENCE (PRELIMINARY)**

The idea is structurally coherent: it targets a real operational problem, has a positive contribution margin, and uses a defensible SaaS model. However, the following conditions make a high-confidence go/no-go impossible at this stage:

- No customer has been interviewed or surveyed.
- HIPAA compliance scope is unknown and could change unit economics materially.
- The competitive landscape is entirely unmapped.
- All growth and churn figures are unvalidated assumptions.
- The 1,000-clinic market estimate is an ASSUMPTION, not a measurement.

The founder should run customer discovery and a HIPAA scoping exercise before committing further spend. Once those two gaps are resolved, re-running this validation with the new evidence will likely yield a more decisive recommendation.

*No independent evidence-audit ran (not triggered for INSUFFICIENT EVIDENCE; offer extended as a next step if the founder wants one before proceeding).*

---

### Handoff Block

```json
{
  "schema": "venturine-handoff/v1",
  "created": "2026-11-21",
  "producer": {
    "component": "idea-validator",
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
      "limitations": "No existing customers; treated as Month-1 sales target"
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
      "category": "market",
      "limitations": "Founder-stated assumption, not a verified statistic"
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
      "claim": "Customer willingness to pay $49/month",
      "label": "UNKNOWN",
      "category": "pricing",
      "priority": "high"
    },
    {
      "id": "E15",
      "claim": "HIPAA compliance applicability and cost",
      "label": "UNKNOWN",
      "category": "regulatory",
      "priority": "high"
    },
    {
      "id": "E16",
      "claim": "Named competitive alternatives",
      "label": "UNKNOWN",
      "category": "competition",
      "priority": "high"
    },
    {
      "id": "E17",
      "claim": "Average no-show rate at target clinics",
      "label": "UNKNOWN",
      "category": "problem",
      "priority": "medium"
    },
    {
      "id": "E18",
      "claim": "TAM / SAM / SOM for appointment reminder software in this region",
      "label": "UNKNOWN",
      "category": "market",
      "priority": "medium"
    },
    {
      "id": "E19",
      "claim": "Month 1 acquisition channel and expected CAC",
      "label": "UNKNOWN",
      "category": "channel",
      "priority": "high"
    }
  ],
  "open_questions": [
    "Will target clinic owners pay $49/month for appointment reminder + waitlist software?",
    "Is SlotKeeper in scope for HIPAA, and what does compliance cost?",
    "What reminder solutions do target clinics use today, and what would it take to switch?",
    "How will the founder acquire the 6 Month-1 clinics, and what is the implied CAC?",
    "What is the actual no-show rate at target clinics?"
  ],
  "next_steps": [
    "Run 15–20 customer discovery interviews before committing further spend",
    "Scope HIPAA compliance obligations with a legal or compliance professional",
    "Map competitive alternatives through manual research before the market-intelligence step",
    "Run market-intelligence (offline) to structure what is known vs unknown about the market",
    "Run unit-economics once HIPAA cost is known to get accurate contribution margin",
    "Consider an evidence-audit before treating any output as a basis for financial commitment"
  ]
}
```

Running market-intelligence next (offline, no web research).

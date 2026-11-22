> **Hypothetical example.** Verbatim output of the `assumption-ledger` skill from the demo run described in [../run-log.md](../run-log.md). Nothing here is real market data.

## Assumption Ledger — SlotKeeper (Hypothetical)

> **HYPOTHETICAL TEACHING EXAMPLE.** No assumption has been upgraded without new evidence. No new facts have been invented. This ledger records what the plan depends on, the evidence supporting each item, and what to validate first. It is for planning only and is not financial, legal, or investment advice.

---

### Priority Matrix Applied

| Impact if wrong | Evidence: Weak (ASSUMPTION / FOUNDER_PROVIDED / UNKNOWN) | Evidence: Partial | Evidence: Strong |
|---|---|---|---|
| **High** | **HIGH** | MEDIUM | LOW |
| **Medium** | **MEDIUM** | LOW | LOW |
| **Low** | **LOW** | LOW | LOW |

All items in this ledger carry weak evidence. No item has been VERIFIED or PARTIALLY_SUPPORTED.

---

### The Ledger

#### HIGH PRIORITY — Plan fails or a major decision changes if wrong

| ID | Assumption (testable sentence) | Category | Label | Impact if wrong | Validation |
|---|---|---|---|---|---|
| **E14** | Clinics in the target segment will pay $49/month for appointment reminder + waitlist software | pricing | UNKNOWN | Revenue model collapses; at $29/month contribution drops to $20, break-even doubles to 105 clinics | 15–20 price-anchored customer interviews; landing page test with $49 price point |
| **E15** | HIPAA compliance does not apply to SlotKeeper, or its cost is already included in $9/clinic variable cost | regulatory | UNKNOWN | If HIPAA adds $5/clinic/month, contribution drops to $35, break-even rises to 60 clinics; LTV falls to $875 | Healthcare compliance attorney scoping call before launch |
| **E19** | The $900/month acquisition budget will acquire 6 or more new clinics in Month 1 via an identified channel | channel | UNKNOWN | If only 3 clinics acquired, implied CAC doubles to $300; growth starting point halves; all scenario break-even months extend by 3–5 months | Identify and test one specific channel; track cost-per-lead and cost-per-signup |
| **E8** | Paying clinics grow at 15%/month compounding (base scenario) | customer | ASSUMPTION | Never reaches break-even within 24 months if real growth is ≤10%/month; conservative scenario ends at $5,624 cash | Measure actual Month 1 and Month 2 growth; recalibrate after first 90 days |
| **E11** | Monthly clinic churn is 4% | customer | ASSUMPTION | At 8% churn: LTV falls from $1,000 to $500; LTV/CAC drops from 6.67× to 3.33×. The forecast model does not apply churn to clinic count at all — real net growth = stated growth minus churn | Track cohort retention from first paying clinic; set trigger at 90 days |
| **E38** | The forecast model's growth rate represents net growth (acquisitions minus churn), so the 4% churn does not separately reduce the active clinic base | operations | ASSUMPTION *(inferred from plan)* | If churn is additive to losses rather than embedded in the growth rate, Month 24 base-case clinic count falls from ~149 to ~100; MRR and cash figures are materially overstated | Clarify with founder: is the growth rate gross or net of churn? |
| **E12** | 1,000 clinics (1–5 practitioners) operate in the target region and are reachable | market | ASSUMPTION | If actual reachable pool is 500, the optimistic scenario saturates at ~Month 22 rather than Month 27; growth caps earlier; TAM halves to $294K/year | Professional directory search or state licensing database count |
| **E2** | Variable cost is $9/clinic/month and does not increase with messaging volume or HIPAA compliance requirements | cost | FOUNDER_PROVIDED | HIPAA compliance and higher-volume messaging could raise variable cost by $3–10/clinic; break-even rises to 57–70 clinics; LTV falls to $750–925 | Get vendor quotes for HIPAA-compliant SMS/email infrastructure at target scale |
| **E7** | 6 paying clinics are signed up in Month 1 (starting point for all compounding growth) | customer | FOUNDER_PROVIDED | If Month 1 = 3 clinics, all scenario outputs shift: base break-even moves to Month 20; conservative never reaches break-even | Actual count on Day 30 of operation — no test required, only time |
| **E5** | Starting cash is $40,000 | other | FOUNDER_PROVIDED | Conservative scenario ends at $5,624 — a 20% reduction in starting cash ($32K) would leave less than $4K buffer; conservative scenario becomes risky | Verifiable by the founder from bank or cap table; confirm before launch |

---

#### MEDIUM PRIORITY — Results change materially but the plan survives

| ID | Assumption (testable sentence) | Category | Label | Impact if wrong | Validation |
|---|---|---|---|---|---|
| **E16** | No incumbent competitor dominates the 1–5 practitioner clinic segment with a comparable feature at comparable or lower price | competition | UNKNOWN | If dominant incumbent exists at $29/month, acquisition cost rises significantly and WTP at $49 may not hold | Manual competitor research: search for clinic scheduling + reminder tools; check EHR/PMS feature lists |
| **E1** | The $49/month price is set at a level the market will accept | pricing | FOUNDER_PROVIDED | Structural: if WTP is lower, contribution and all derived metrics shift; if higher, margin improves | Covered by E14 customer interviews — price sensitivity test |
| **E3** | Fixed operating costs are $1,200/month and are complete (no major omitted categories) | cost | FOUNDER_PROVIDED | Each $200/month omitted raises break-even by 5 clinics (at $40 contribution) | Full cost audit: enumerate every monthly subscription, tool, and service; include founder's minimal stipend scenario |
| **E4** | $900/month acquisition spend is sufficient to drive target growth and can be maintained for 24 months | cost | FOUNDER_PROVIDED | If spend must rise to $1,800/month to hit growth targets, monthly fixed burden rises to $3,000; break-even rises to 75 clinics | Test spend efficiency in first 60 days: cost per lead, cost per clinic |
| **E9** | Monthly clinic growth in the conservative case is 8%/month | customer | ASSUMPTION | Conservative scenario is already the worst-case; if actual growth is 5%/month, the scenario underestimates cash depletion | Same as E8 — measure Month 1–2 actual growth |
| **E10** | Monthly clinic growth in the optimistic case is 22%/month | customer | ASSUMPTION | Optimistic case is a planning upper bound; overshooting the ceiling at Month ~27 means the case is already constrained | Same as E8; also monitor market ceiling approach |
| **E39** | No significant one-time startup costs exist beyond the stated monthly fixed and variable costs (e.g., product build, legal, compliance) | cost | ASSUMPTION *(inferred from plan)* | Startup build cost could reduce starting cash meaningfully; $10K in one-time costs reduces conservative ending cash from $5,624 to ~−$4,376 | Enumerate all one-time costs before treating $40,000 as fully available operating cash |
| **E18** | The 1,000-clinic assumption is a reasonable proxy for the actual reachable market in the region | market | ASSUMPTION | If addressable market is 400–600, growth hits ceiling sooner and total revenue ceiling drops below $350K/year | Directory, licensing authority, or professional association count |

---

#### LOW PRIORITY — Effect is minor or the assumption is not load-bearing

| ID | Assumption (testable sentence) | Category | Label | Impact if wrong | Validation |
|---|---|---|---|---|---|
| **E17** | No-show rates at target clinics are high enough that reminder software provides meaningful ROI | problem | UNKNOWN | Does not affect financials; affects the value proposition's persuasiveness | Secondary research or 5 clinic interviews |
| **E6** | 24 months is a sufficient planning horizon | other | FOUNDER_PROVIDED | Low — the forecast model can be re-run at a different horizon at any time | Not required; adjust if fundraising or exit plans extend beyond 24 months |
| **E23** | National market data for appointment reminder SaaS is relevant to this single-region venture | market | UNKNOWN | Low — the 1,000-clinic regional assumption is the operative constraint, not national data | Not required at this stage |
| **E24** | The industry is growing (appointment reminder software market) | market | UNKNOWN | Low — the business plan does not depend on market growth, only on regional penetration | Not required at this stage |

---

### What Rests on What

```
E14 (WTP at $49) ──────────────────────────────► All revenue figures, E25–E37
E15 (HIPAA cost) ─────────────────────────────► E2, E25 (contribution margin), E27 (break-even), E28 (LTV), all forecasts F1–F3
E19 (Month 1 channel / actual CAC) ───────────► E7 (Month 1 = 6), E29 (implied CAC $150), E30 (LTV/CAC), E31 (payback)
E8  (15% growth) ─────────────────────────────► F2 (base forecast), E33 (break-even Month 17), E36 (ending cash $33,800)
E11 (4% churn) ───────────────────────────────► E28 (LTV $1,000), E30 (LTV/CAC 6.67×), E31 (payback 3.75 mo.)
E38 (net vs gross growth) ────────────────────► F1, F2, F3 (all scenario cash balances overstated if churn is additive)
E12 (1,000 clinic ceiling) ───────────────────► E20 (TAM $588K), E21 (SAM $588K); optimistic F3 hits ceiling ~Month 27
E2  (variable cost $9) ───────────────────────► E25 (CM $40), E26 (GM 81.63%), E27 (break-even 53), E28 (LTV $1,000), F1–F3
E7  (Month 1 = 6) ────────────────────────────► All compounding growth in F1, F2, F3
E5  (starting cash $40,000) ──────────────────► Ending cash in F1 ($5,624 — barely positive)
```

**Every DERIVED output (E25–E37) rests on at least one HIGH-priority ASSUMPTION or UNKNOWN.** A correct calculation does not validate its inputs.

---

### Validation Priorities (highest first)

| Rank | Item | Test | Evidence that changes label | Decision trigger |
|---|---|---|---|---|
| 1 | **E14** — WTP at $49 | 15–20 customer interviews with price-anchoring exercise | ≥12 of 20 express willingness to pay $49/month | If WTP is <$39, re-run contribution margin and break-even before spending acquisition budget |
| 2 | **E15** — HIPAA scope | Scoping call with healthcare compliance attorney | Attorney opinion on applicability | If HIPAA adds ≥$5/clinic, re-run unit economics before launch |
| 3 | **E19** — Channel and actual CAC | Run $900 test spend on one specific channel; count signups | Actual signed clinics / spend | If CAC >$300, reconsider growth assumptions and acquisition budget |
| 4 | **E38** — Net vs gross growth | Founder to confirm: are growth rates stated net or gross of churn? | Founder's answer (immediate, no cost) | If gross, all scenario MRR figures are overstated; re-run with net rate |
| 5 | **E8** — 15% base growth | Measure actual Month 1 and Month 2 clinic count | Actual compounding growth rate | If actual <10%/month by Month 3, switch planning to conservative scenario |
| 6 | **E11** — 4% churn | Track cohort from first 10 clinics at 30, 60, 90 days | Observed cancellation rate | If churn >8%, LTV/CAC falls below 3×; re-evaluate pricing and retention strategy |
| 7 | **E39** — One-time startup costs | Enumerate all build, legal, compliance one-time costs | Full cost list | If >$10K, reduce effective starting cash in model |
| 8 | **E12** — 1,000-clinic ceiling | Search state licensing authority or professional directory | Actual count with ±20% confidence | If <600, cap optimistic scenario growth earlier |
| 9 | **E2** — Variable cost completeness | Get HIPAA-compliant messaging vendor quotes at 50, 100, 500 clinic scale | Vendor price list | If >$15/clinic at scale, re-run all economics |

---

### Unresolved Risks

| Risk | Consequence | Status |
|---|---|---|
| Churn excluded from scenario growth (E38) | All three scenario MRR and cash figures overstated by an unknown but potentially material amount | Unresolved — requires founder clarification |
| HIPAA compliance cost unknown (E15) | Variable cost could be understated by $3–10/clinic; break-even and LTV both affected | Unresolved — requires legal scoping |
| No customer has been spoken to (E14) | The entire revenue model rests on an untested price hypothesis | Unresolved — requires customer interviews |
| Month 1 acquisition path undefined (E19) | 6 clinics in Month 1 from $900 spend with no channel identified is a high-risk assumption | Unresolved — requires channel test |
| Conservative scenario has only $5,624 buffer at Month 24 (E35) | A worse-than-conservative outcome (slower growth, higher churn, higher costs) produces cash-out | Partially mitigated by $40K starting cash; unresolved in outcome |

---

### Changes Since Previous Version

This is the first version of the assumption ledger for SlotKeeper. Two inferred assumptions were added that were not in prior skills:

- **E38** (inferred): The forecast's growth rate is assumed to be net of churn, not gross. This was surfaced from the scenario-comparison model limitation note. High priority; requires immediate founder clarification.
- **E39** (inferred): No one-time startup costs exist beyond stated monthly figures. Medium priority; should be enumerated before treating $40,000 as fully available.

---

### Handoff Block

```json
{
  "schema": "venturine-handoff/v1",
  "created": "2026-11-21",
  "producer": {
    "component": "assumption-ledger",
    "kind": "skill"
  },
  "venture": {
    "name": "SlotKeeper (fictional)",
    "hypothetical": true
  },
  "evidence_ledger": [
    {"id": "E1", "claim": "Price $49/clinic/month is accepted by the market", "label": "FOUNDER_PROVIDED", "value": "49", "unit": "USD/clinic/month", "category": "pricing", "priority": "medium", "risk": "If WTP is $29–39, contribution drops 20–50% and break-even doubles", "validation": "Customer interviews with price-anchoring"},
    {"id": "E2", "claim": "Variable cost is $9/clinic/month and is complete including compliance", "label": "FOUNDER_PROVIDED", "value": "9", "unit": "USD/clinic/month", "category": "cost", "priority": "high", "risk": "HIPAA or messaging cost increases reduce contribution margin and raise break-even", "validation": "Get HIPAA-compliant vendor quotes; legal scoping"},
    {"id": "E3", "claim": "Fixed costs are $1,200/month and no material categories are omitted", "label": "FOUNDER_PROVIDED", "value": "1200", "unit": "USD/month", "category": "cost", "priority": "medium", "risk": "Each $200/month omitted raises break-even by 5 clinics", "validation": "Full cost audit before launch"},
    {"id": "E4", "claim": "Acquisition spend of $900/month is sufficient to drive target growth", "label": "FOUNDER_PROVIDED", "value": "900", "unit": "USD/month", "category": "cost", "priority": "medium", "risk": "If spend must double, break-even rises to 75 clinics", "validation": "Track cost-per-clinic in first 60 days"},
    {"id": "E5", "claim": "Starting cash is $40,000", "label": "FOUNDER_PROVIDED", "value": "40000", "unit": "USD", "category": "other", "priority": "high", "risk": "Conservative scenario ends at $5,624; lower starting cash risks cash-out", "validation": "Verifiable by founder from bank balance"},
    {"id": "E7", "claim": "6 paying clinics are signed in Month 1", "label": "FOUNDER_PROVIDED", "value": "6", "unit": "clinics", "category": "customer", "priority": "high", "risk": "If Month 1 = 3, all scenario break-even months extend by 3–5 months", "validation": "Actual count on Day 30"},
    {"id": "E8", "claim": "Paying clinics grow at 15%/month compounding (base case)", "label": "ASSUMPTION", "value": "15", "unit": "percent/month", "category": "customer", "priority": "high", "risk": "At ≤10%/month real growth, never reaches break-even in 24 months", "validation": "Measure Month 1–2 actual growth; recalibrate at 90 days"},
    {"id": "E9", "claim": "Conservative case growth is 8%/month", "label": "ASSUMPTION", "value": "8", "unit": "percent/month", "category": "customer", "priority": "medium", "risk": "Already worst-case; if actual is 5%/month, cash falls further", "validation": "Same as E8"},
    {"id": "E10", "claim": "Optimistic case growth is 22%/month", "label": "ASSUMPTION", "value": "22", "unit": "percent/month", "category": "customer", "priority": "medium", "risk": "Hits 1,000-clinic ceiling at Month ~27; Month 24 figures overstated near ceiling", "validation": "Same as E8; monitor saturation"},
    {"id": "E11", "claim": "Monthly churn is 4%", "label": "ASSUMPTION", "value": "4", "unit": "percent/month", "category": "customer", "priority": "high", "risk": "At 8% churn: LTV halves to $500, LTV/CAC falls to 3.3×; churn not applied to scenario unit counts, so all MRR overstated", "validation": "Track cohort at 30/60/90 days from first clinic"},
    {"id": "E12", "claim": "1,000 clinics (1–5 practitioners) are reachable in the launch region", "label": "ASSUMPTION", "value": "1000", "unit": "clinics", "category": "market", "priority": "high", "risk": "TAM halves to $294K/year at 500; optimistic scenario saturates earlier", "validation": "State licensing database or professional directory count"},
    {"id": "E14", "claim": "Target clinics will pay $49/month for this product", "label": "UNKNOWN", "category": "pricing", "priority": "high", "risk": "Entire revenue model is untested; at $29 WTP, break-even doubles", "validation": "15–20 customer interviews with price anchor; landing page test"},
    {"id": "E15", "claim": "HIPAA compliance cost is zero or already captured in variable cost", "label": "UNKNOWN", "category": "regulatory", "priority": "high", "risk": "Compliance adds $3–10/clinic/month; contribution and LTV both fall materially", "validation": "Healthcare compliance attorney scoping call"},
    {"id": "E16", "claim": "No incumbent competitor dominates this segment at comparable or lower price", "label": "UNKNOWN", "category": "competition", "priority": "medium", "risk": "Incumbent at $29/month raises acquisition cost and undermines WTP", "validation": "Manual competitor search before acquisition spend"},
    {"id": "E17", "claim": "No-show rates at target clinics are high enough to make reminder software ROI-positive for clinics", "label": "UNKNOWN", "category": "problem", "priority": "low", "risk": "Low no-show rate weakens the sales narrative; does not affect unit economics directly", "validation": "5 clinic interviews; secondary search"},
    {"id": "E19", "claim": "The $900/month acquisition budget will acquire 6+ clinics in Month 1 via an identified channel", "label": "UNKNOWN", "category": "channel", "priority": "high", "risk": "If CAC is $300, Month 1 yields 3 clinics; all growth projections compress", "validation": "Identify channel; run $900 test spend; count signups"},
    {"id": "E38", "claim": "The stated growth rates are net of churn (the forecast model does not separately subtract lost clinics)", "label": "ASSUMPTION", "category": "operations", "priority": "high", "risk": "If growth is gross and churn is additive, Month 24 base clinic count is ~100 not 149; all MRR and cash figures overstated", "validation": "Founder to clarify immediately — no cost"},
    {"id": "E39", "claim": "No material one-time startup costs exist beyond stated monthly figures", "label": "ASSUMPTION", "category": "cost", "priority": "medium", "risk": "$10K in one-time costs reduces conservative ending cash from $5,624 to near zero", "validation": "Enumerate all build, legal, and compliance one-time costs before launch"}
  ],
  "open_questions": [
    "Are the stated growth rates (8%, 15%, 22%) net or gross of the 4% monthly churn?",
    "What one-time startup costs exist (product build, legal, HIPAA compliance setup)?",
    "Has the founder spoken to any potential clinic customers about the $49 price point?",
    "What channel will be used to acquire the first 6 clinics, and what is the evidence for a $150 CAC on that channel?"
  ],
  "next_steps": [
    "Run evidence-audit on this ledger before treating any output as a planning basis",
    "Founder to immediately clarify E38 (net vs gross growth) — zero cost, changes all scenario outputs",
    "Run customer interviews to resolve E14 (WTP) before committing acquisition budget",
    "Scope HIPAA compliance (E15) before finalising variable cost and unit economics",
    "Run business-report to consolidate all Venturine outputs into one document"
  ]
}
```

Running the evidence-auditor agent next (offline, no web).

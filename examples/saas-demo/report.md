# SlotKeeper — Business Analysis Report

**Date:** 2026-11-21  
**Status:** PRELIMINARY — evidence-auditor ran and returned REVISION REQUIRED; all seven corrections were incorporated. The report-editor subsequently returned REVISION REQUIRED (three material issues, corrected in this version). No second auditor pass has confirmed the corrections; the report remains PRELIMINARY until an independent re-audit is run.  
**Analyses combined:** venture-intake · idea-validator · market-intelligence · unit-economics · scenario-comparison · assumption-ledger · evidence-audit  
**Not analyzed:** competitor-intelligence · pricing-analysis · customer-discovery · go-to-market

---

> ⚠️ **HYPOTHETICAL TEACHING EXAMPLE**
> Every number in this report is fictional. SlotKeeper does not exist. All inputs
> are labelled FOUNDER_PROVIDED or ASSUMPTION. No figure has been verified against
> any external source. This report is for illustrative purposes only and is not
> financial, legal, or investment advice.

---

## Evidence-Label Legend

| Label | Meaning |
|---|---|
| VERIFIED | Fact from an examined, relevant source |
| PARTIALLY_SUPPORTED | Some evidence exists; scope or breadth is limited |
| FOUNDER_PROVIDED | Stated by the founder; not independently checked |
| ASSUMPTION | Planning hypothesis; no empirical basis |
| DERIVED | Calculated from documented inputs |
| UNKNOWN | Missing; not filled in |
| CONTRADICTED | Credible evidence conflicts with the claim |

---

## 1. Executive Summary

SlotKeeper is a fictional SaaS product that sends automated appointment reminders
and offers freed slots to a waitlist for independent clinics (1–5 practitioners)
in one hypothetical US region. The product targets a structurally plausible problem
at a price point that yields positive contribution margins on paper.

**What the analysis supports:** The unit economics are directionally sound under
stated assumptions — 81.63% gross margin [C2], $40/clinic/month contribution [C1],
and an LTV/CAC ratio of 6.67× [manual, DERIVED]. In the base and optimistic
scenarios the business reaches operating break-even before Month 24 and survives
on starting cash alone.

**What the analysis does not support:** Every figure rests on ASSUMPTION or
FOUNDER_PROVIDED inputs. No customer has been interviewed, no competitor has
been identified, no HIPAA compliance cost has been scoped, and no acquisition
channel has been tested. The idea-validator returned **INSUFFICIENT EVIDENCE**.

**Three largest risks:**
1. Customer willingness to pay $49/month is entirely untested [E14 — UNKNOWN].
2. HIPAA compliance cost is unknown and excluded from every margin figure [E15 — UNKNOWN].
3. The conservative scenario exhausts nearly all starting cash ($40,000 → $5,624)
   over 24 months without ever reaching break-even — a near-total cash exhaustion
   risk [F1 — DERIVED, **SOLVENCY RISK**].

---

## 2. Venture Profile

| Field | Value | Label |
|---|---|---|
| Product | SaaS: appointment reminders + waitlist slot-filling | FOUNDER_PROVIDED |
| Target customer | Independent clinics, 1–5 practitioners | FOUNDER_PROVIDED |
| Geography | One hypothetical US region | FOUNDER_PROVIDED |
| Stage | Pre-revenue; no customers or pilots | FOUNDER_PROVIDED |
| Founder salary | $0/month | FOUNDER_PROVIDED |

---

## 3. Market

**Regional TAM:** $588,000/year [E20 — DERIVED from ASSUMPTION]  
Formula: 1,000 clinics [E12 — ASSUMPTION] × $49/month [E1] × 12 = $588,000/year.  
This figure inherits the full uncertainty of E12. It is not an industry statistic.

**SAM/SOM:** UNKNOWN [E21/E22] — no data to narrow the addressable pool.  
**Industry market size, growth rate, competitors:** UNKNOWN [E16, E18, E23, E24].  
**No-show rate at target clinics (problem severity):** UNKNOWN [E17].

> Market-intelligence was run offline (web research disabled). All market-size
> figures are either DERIVED from the founder's ASSUMPTION or labelled UNKNOWN.
> No external data was examined.

---

## 4. Unit Economics

All calculations engine-validated by calculate.py v0.2.1. Receipts are referenced
by operation and inputs; full JSON receipts are in the unit-economics skill output.

> **HIPAA disclosure (auditor correction #5):** ALL figures below assume zero
> HIPAA compliance cost [E15 — UNKNOWN]. If HIPAA applies, variable cost (E2)
> is understated and every downstream figure is optimistic on the cost side.

| Metric | Value | Basis | Label |
|---|---|---|---|
| Price | $49/clinic/month | E1 | FOUNDER_PROVIDED |
| Variable cost | $9/clinic/month | E2 (HIPAA excluded) | FOUNDER_PROVIDED |
| Contribution margin | **$40.00/clinic/month** | C1: `contribution-margin 49 9` | DERIVED |
| Gross margin | **81.63%** | C2: `gross-margin 49 9` | DERIVED |
| Fixed costs (excl. acquisition) | $1,200/month | E3 | FOUNDER_PROVIDED |
| Acquisition spend | $900/month | E4 | FOUNDER_PROVIDED |
| Total monthly fixed burden | $2,100/month | E3 + E4 | DERIVED |
| **Break-even (total, incl. acquisition)** | **53 clinics** | C3: `break-even 2100 49 9` | DERIVED |
| Break-even-loaded | **Engine rejected** | C4: ENGINE ERROR — negative loaded contribution ($49−$9−$150 = −$110); CAC exceeds per-unit margin; subscription retention required | — |
| LTV (4% monthly churn) | **$1,000** | C5: `subscription-ltv 40 0.04` | DERIVED |
| Implied CAC | **$150** | C6: `cac 900 6` — PLANNING ESTIMATE, not observed | DERIVED |
| LTV / CAC | **6.67×** | Manual: $1,000 ÷ $150 | DERIVED (manual) |
| CAC payback | **3.75 months** | Manual: $150 ÷ $40 | DERIVED (manual) |

**Break-even note (auditor correction #1):** The 53-clinic figure uses $2,100
in fixed costs, which includes the $900 acquisition budget. This is total
operating break-even including acquisition spend. The engine emitted the flag
`acquisition_included: false` because acquisition was not passed as a separate
CAC argument — it was embedded in the fixed-cost total. The 53-clinic result is
correct for that framing; the flag does not indicate an error.

**Month 1 target (auditor correction #2):** 6 paying clinics in Month 1 is a
planning ASSUMPTION (target), not an observed figure [E7 — relabelled from
FOUNDER_PROVIDED per auditor finding].

**LTV / churn note (auditor correction #3 & #4):** LTV uses 4% monthly churn.
The scenario forecasts below use GROSS growth rates — churn is not deducted
from the active clinic count in those models. LTV [C5] and scenario cash figures
are therefore computed under incompatible churn assumptions and cannot be
directly reconciled.

---

## 5. Scenarios

All scenarios engine-validated by forecast.py v0.2.1. Growth rates are all
ASSUMPTION. Receipt fingerprints are abbreviated; full receipts are in the
scenario-comparison skill output.

> **Churn disclosure (auditor correction #3 & #4):** Scenario models apply GROSS
> growth rates (8%, 15%, 22%) to clinic counts. The 4% monthly churn [E11 —
> ASSUMPTION] is NOT deducted from the active clinic base. All scenario MRR
> and ending-cash figures are optimistic relative to what net-churn outcomes
> would produce. At 4% net churn, effective growth rates are approximately
> 4%, 11%, and 18% respectively — which would shift break-even and cash outcomes
> materially toward the conservative case.

| Metric | Conservative (8%) | Base (15%) | Optimistic (22%) |
|---|---|---|---|
| Growth rate label | ASSUMPTION | ASSUMPTION | ASSUMPTION |
| Break-even month | **Never (<24 mo.)** | **Month 17** | **Month 12** |
| Minimum cash | $5,623.54 (Mo. 24) | $19,772.19 (Mo. 16) | $25,530.89 (Mo. 11) |
| Ending cash (Mo. 24) | **$5,623.54** | $33,800.28 | $117,460.03 |
| Total cash change vs start [DERIVED (manual): ending cash − $40,000 E5] | −$34,376.46 | −$6,199.72 | +$77,460.03 |
| Month 24 clinics [DERIVED (manual): 6×(1+g)²⁴; not in engine output] | ~35 | ~149 | ~581 |
| Receipt fingerprint | sha256:aef4f1d… | sha256:1f2c6d1… | sha256:bfaa054… |

> Full receipt fingerprints: F1 sha256:aef4f1d400108130d4dc2361fd395d9d856c8369afa9b210f13a0b52a6a5eee4 · F2 sha256:1f2c6d14b65f353896d0b4e02765c3b801fed30efc4e026959ab957338d03bdb · F3 sha256:bfaa054e7e0a45f047ceeafbce119823dc50af637a66c1a685f1eb373051f9ee

**Conservative solvency risk (auditor correction #7):** Under the conservative
scenario (F1), cash falls from $40,000 to $5,624 over 24 months — approximately
86% depletion (manual: $34,376 ÷ $40,000; not engine-validated) — without ever
reaching break-even. This is a near-total cash exhaustion risk. Any outcome
worse than 8%/month growth (slower acquisition, higher churn, HIPAA costs)
would produce a cash-out within the horizon.

**Market ceiling note:** The 1,000-clinic assumption [E12 — ASSUMPTION] caps the
regional addressable market. The optimistic scenario reaches ~581 clinics at
Month 24 [DERIVED (manual) — not in engine output]. At 22%/month growth, the
1,000-clinic ceiling would be reached at approximately Month 27 [DERIVED (manual):
6 × 1.22²⁶ ≈ 988 clinics — not engine-validated]. The model does not enforce this
ceiling; the final months of F3 are overstated if saturation occurs.

---

## 6. Assumption Ledger (top 10 by priority)

| ID | Assumption | Label | Priority | Risk if wrong |
|---|---|---|---|---|
| E14 | Clinics will pay $49/month | UNKNOWN | HIGH | Revenue model untested; at $29 WTP, break-even doubles |
| E15 | HIPAA cost is zero or captured in $9 variable cost | UNKNOWN | HIGH | Affects all margins and break-even; unquantified |
| E19 | $900/month acquires 6+ clinics in Month 1 | UNKNOWN | HIGH | CAC doubles if 3 clinics; all growth projections compress |
| E8 | Base growth 15%/month | ASSUMPTION | HIGH | At ≤10%/month, never reaches break-even in 24 months |
| E11 | Monthly churn 4% | ASSUMPTION | HIGH | At 8% churn: LTV halves; scenario outputs further overstated |
| E38 | Growth rates are gross (churn not deducted in scenarios) | ASSUMPTION | HIGH | All scenario MRR overstated if net growth < gross growth |
| E7 | 6 clinics acquired in Month 1 (target) | ASSUMPTION | HIGH | Starting base for all compounding growth |
| E12 | 1,000 reachable clinics in region | ASSUMPTION | HIGH | TAM ceiling; saturation timing |
| E2 | Variable cost complete at $9 (HIPAA excluded) | FOUNDER_PROVIDED | HIGH | HIPAA adder could raise break-even to 57–70 clinics |
| E39 | No material one-time startup costs | ASSUMPTION (inferred) | MEDIUM | $10K one-time costs cut conservative ending cash to near zero |

---

## 7. Contradictions and Inconsistencies

The evidence-auditor (REVISION REQUIRED, 2026-11-21) identified seven issues.
All seven have been incorporated in this report:

1. **C3 break-even label** — corrected: 53 clinics is total operating break-even
   *including* acquisition spend at $2,100/month fixed base.
2. **E7 label** — corrected: Month 1 = 6 clinics is an ASSUMPTION (target), not
   FOUNDER_PROVIDED (observed fact).
3. **E11 / scenario churn** — disclosed: LTV [C5] and scenario models use incompatible
   churn assumptions; scenario cash figures are optimistic.
4. **E38 gross vs net growth** — resolved: growth rates are GROSS; churn not embedded.
5. **E2 / E15 HIPAA gap** — disclosed: all margin and cash-flow figures assume
   zero HIPAA cost.
6. **E20 TAM provenance** — corrected: $588,000/year is DERIVED from an ASSUMPTION,
   not from industry data.
7. **F1 solvency risk** — flagged: conservative scenario exhausts ~86% of starting
   cash without break-even.

**Remaining structural inconsistency:** LTV [C5] and scenario outputs (F1–F3)
still rest on incompatible churn assumptions (LTV deducts churn; scenarios do not).
Resolving this requires re-running scenarios with net-churn-adjusted growth rates,
which requires a validated churn figure [E11 — ASSUMPTION].

The report-editor (REVISION REQUIRED, 2026-11-21) identified three additional
material issues, now corrected:

- **Total cash change figures** relabelled from "total operating profit" to
  DERIVED (manual): ending cash minus starting cash ($40,000 E5). These are not
  engine-validated and are not accrual profit figures.
- **Month 24 clinic counts** (~35, ~149, ~581) relabelled DERIVED (manual):
  computed from 6 × (1+g)²⁴; not present in engine output.
- **Status** downgraded from AUDITED to PRELIMINARY: the report-editor found
  REVISION REQUIRED; no second auditor pass has confirmed the corrections.

---

## 8. Key Risks

| Rank | Risk | Evidence status |
|---|---|---|
| 1 | WTP at $49/month untested — entire revenue model unvalidated | UNKNOWN |
| 2 | HIPAA compliance cost unknown — all cost-side figures contingent | UNKNOWN |
| 3 | Conservative scenario: near-total cash exhaustion without break-even | DERIVED (from ASSUMPTION inputs) |
| 4 | No acquisition channel identified — Month 1 target of 6 clinics unsupported | UNKNOWN |
| 5 | Competitive landscape unknown — incumbents may already serve this segment | UNKNOWN |
| 6 | Scenario outputs overstated because churn not applied to clinic count | ASSUMPTION (structural model limitation) |
| 7 | Optimistic scenario approaches 1,000-clinic ceiling at ~Month 27 | DERIVED (manual) from ASSUMPTION |

---

## 9. What to Validate First

| Priority | Action | Resolves |
|---|---|---|
| 1 | 15–20 customer discovery interviews with price-anchoring | E14 — WTP $49 |
| 2 | HIPAA compliance scoping call with healthcare attorney | E15 — variable cost completeness |
| 3 | Identify one acquisition channel; run $900 test spend; count signups | E19 — actual CAC |
| 4 | Measure actual Month 1 and Month 2 clinic growth | E8 — base growth rate |
| 5 | Track 90-day cohort retention from first paying clinic | E11 — churn rate |
| 6 | Enumerate all one-time startup costs before treating $40K as fully available | E39 — startup cost gap |

---

## 10. What This Analysis Did Not Verify

- No customer interviews were conducted (willingness to pay, problem severity, status quo workflow).
- No competitor research was conducted (no alternatives named or priced).
- No HIPAA or regulatory assessment was performed.
- No external market data was examined (web research was disabled throughout all steps).
- All growth, churn, and market-size figures remain ASSUMPTION or UNKNOWN.
- No pilot clinics, trials, or letters of intent exist.
- Competitor-intelligence, pricing-analysis, customer-discovery, and go-to-market
  analyses were not run. Each would materially improve the evidence base.

---

## 11. Recommendation

The idea-validator returned **INSUFFICIENT EVIDENCE** (preliminary, no prior audit).
The evidence-auditor returned **REVISION REQUIRED**, with all corrections now applied.
The report-editor returned **REVISION REQUIRED**, with all material corrections now applied.

The analysis does not support a go/no-go decision. The unit economics are
structurally promising under stated assumptions, but every critical assumption —
willingness to pay, HIPAA cost, actual growth rate, acquisition channel, and churn —
is either ASSUMPTION or UNKNOWN. The conservative scenario risks total cash
exhaustion. No customer has been spoken to.

**The founder should run customer discovery interviews and a HIPAA scoping call
before committing any acquisition spend.** Once those two gaps are resolved,
re-running unit-economics and scenario-comparison with updated inputs will produce
a materially more reliable basis for a decision.

---

## 12. Evidence Index

| ID | Claim | Label | Source |
|---|---|---|---|
| E1 | Price $49/clinic/month | FOUNDER_PROVIDED | venture-intake |
| E2 | Variable cost $9/clinic/month (HIPAA excluded) | FOUNDER_PROVIDED | venture-intake |
| E3 | Fixed costs $1,200/month excl. acquisition | FOUNDER_PROVIDED | venture-intake |
| E4 | Acquisition spend $900/month | FOUNDER_PROVIDED | venture-intake |
| E5 | Starting cash $40,000 | FOUNDER_PROVIDED | venture-intake |
| E7 | Month 1 target: 6 paying clinics | ASSUMPTION | venture-intake / auditor correction |
| E8 | Base growth 15%/month | ASSUMPTION | venture-intake |
| E9 | Conservative growth 8%/month | ASSUMPTION | venture-intake |
| E10 | Optimistic growth 22%/month | ASSUMPTION | venture-intake |
| E11 | Monthly churn 4% (LTV only) | ASSUMPTION | venture-intake |
| E12 | Reachable clinics in region: 1,000 | ASSUMPTION | venture-intake |
| E14 | Customer WTP $49/month | UNKNOWN | idea-validator |
| E15 | HIPAA compliance cost | UNKNOWN | idea-validator |
| E16 | Named competitors | UNKNOWN | idea-validator |
| E19 | Acquisition channel and actual CAC | UNKNOWN | idea-validator |
| E20 | Regional TAM $588,000/year | DERIVED from ASSUMPTION | market-intelligence |
| C1 | Contribution margin $40.00 | DERIVED (engine, v0.2.1) | unit-economics |
| C2 | Gross margin 81.63% | DERIVED (engine, v0.2.1) | unit-economics |
| C3 | Break-even 53 clinics (total incl. acquisition) | DERIVED (engine, v0.2.1) | unit-economics |
| C5 | LTV $1,000 | DERIVED (engine, v0.2.1) | unit-economics |
| C6 | Implied CAC $150 (planning estimate) | DERIVED (engine, v0.2.1) | unit-economics |
| F1 | Conservative scenario outputs | DERIVED (engine, v0.2.1) | scenario-comparison |
| F2 | Base scenario outputs | DERIVED (engine, v0.2.1) | scenario-comparison |
| F3 | Optimistic scenario outputs | DERIVED (engine, v0.2.1) | scenario-comparison |

---

*Report assembled by Venturine · business-report skill · 2026-11-21*  
*Evidence-auditor: REVISION REQUIRED → corrections applied. Report-editor: REVISION REQUIRED → corrections applied.*  
*Status: PRELIMINARY — no confirmed second-pass audit.*  
*Calculator engine: venturine v0.2.1 (calculate.py + forecast.py)*  
*All figures are fictional and for teaching purposes only.*

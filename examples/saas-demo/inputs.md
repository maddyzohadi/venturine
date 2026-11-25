# Inputs: SlotKeeper (hypothetical)

> **Hypothetical teaching example.** SlotKeeper is a made-up company. Every number below is fictional founder input. None of it is real market data.

## The scenario

SlotKeeper is a subscription software product for independent clinics with 1 to 5 practitioners, in one hypothetical US region. It sends automated appointment reminders and offers freed-up slots to a waitlist, to reduce missed appointments. There are no customers and no pilots.

| Input | Value | Label |
|---|---|---|
| Price | $49 per clinic per month | FOUNDER_PROVIDED |
| Variable cost | $9 per clinic per month | FOUNDER_PROVIDED |
| Fixed costs (excluding acquisition) | $1,200 per month | FOUNDER_PROVIDED |
| Acquisition spend | $900 per month | FOUNDER_PROVIDED |
| Starting cash | $40,000 | FOUNDER_PROVIDED |
| Forecast horizon | 24 months | FOUNDER_PROVIDED |
| Month 1 | 6 paying clinics | FOUNDER_PROVIDED (the run re-labeled it ASSUMPTION, see the report) |
| Growth per month | 8% conservative, 15% base, 22% optimistic | ASSUMPTION |
| Monthly churn (lifetime value only) | 4% | ASSUMPTION |
| Reachable clinics in the region | 1,000 | ASSUMPTION |

Web search was **disabled** for the run, so nothing in the analysis depends on outside facts. Where a market fact would be needed (market size, competitors, how often appointments are missed), the run leaves it UNKNOWN.

## The exact prompt

This is the prompt given to Claude Code, with the Venturine plugin loaded. It is sent as one message, followed by the paragraph in the next section.

```text
This is a HYPOTHETICAL teaching example. Everything below is fictional founder input for a made-up company. Treat every number as FOUNDER_PROVIDED or ASSUMPTION, never VERIFIED. Do not do any web research and do not use any search or fetch tool: nothing here may rely on outside facts. If a market fact would be needed, label it UNKNOWN instead of supplying one. Do not invent sources, statistics or calculator output.

Company: SlotKeeper (fictional). A subscription software product for independent clinics with 1 to 5 practitioners, in one hypothetical US region. It sends automated appointment reminders and offers freed-up slots to a waitlist, to reduce missed appointments.

Founder inputs (all FOUNDER_PROVIDED, hypothetical):
- Price: $49 per clinic per month.
- Variable cost: $9 per clinic per month (messaging and hosting).
- Fixed costs: $1,200 per month, excluding acquisition spend.
- Acquisition spend: $900 per month.
- Starting cash: $40,000. Forecast horizon: 24 months.
- Month 1: 6 paying clinics. No customers or pilots exist today.
- Base case: paying clinics grow 15% a month. Conservative: 8% a month. Optimistic: 22% a month. All three growth rates are ASSUMPTIONS, not measurements.
- Monthly churn: 4% (ASSUMPTION), used only for lifetime value.
- Founder assumes 1,000 reachable clinics in the launch region (ASSUMPTION, not a statistic).
- No salary for the founder.

Run these Venturine steps in order, without asking me questions (label gaps UNKNOWN and continue): venture-intake, idea-validator, market-intelligence (offline: leave TAM/SAM/SOM UNKNOWN unless the only input is the founder's 1,000-clinic assumption, and label anything derived from it ASSUMPTION or DERIVED), unit-economics, scenario-comparison (conservative, base and optimistic with scenario-compare), assumption-ledger, evidence-audit using the evidence-auditor agent (offline, no web), business-report, then the report-editor agent on the finished report.
Use the Venturine calculators for every calculation: calculate.py for unit economics (contribution margin, gross margin, break-even, cac, subscription-ltv) and forecast.py for the scenarios. Run them one at a time. Show each calculator's receipt as the calculator printed it. If a command is refused, say so and label the figure "manual calculation, not engine-validated".
Keep the report concise: under about 250 lines, with an executive summary, a hypothetical-example banner, an evidence-label legend, an Assumption Ledger table, unit economics, scenarios, key risks, what the founder should validate first, and a short list of what this analysis did not verify. Write the final report to ./report.md in the current directory and write nothing else outside this directory. End by listing exactly which skills and agents you invoked, which calculator commands ran, and any command refused.
```

## The one extra instruction

In the first attempt, the session did the market step itself instead of calling the `market-intelligence` skill. The run in this folder added this paragraph to the prompt:

```text
Important: every named step must be run by calling the Skill tool with that skill (venturine:venture-intake, venturine:idea-validator, venturine:market-intelligence, venturine:unit-economics, venturine:scenario-comparison, venturine:assumption-ledger, venturine:business-report) and the named agents must be run with the Agent tool (venturine:evidence-auditor, venturine:report-editor). Do not do any step inline without invoking its skill or agent. The web is disabled; the market-intelligence skill must still be invoked and must work offline.
```

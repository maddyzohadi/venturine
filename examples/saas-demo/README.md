# Worked example: SlotKeeper (hypothetical)

> **Hypothetical teaching example.** SlotKeeper is a made-up company. Every input is fictional, and no market data, sources or statistics were used: web search was off for this run. The analysis below shows what Venturine does with weak evidence, not a real business.

This folder is a recorded run of the real Venturine skills, agents and calculators on one invented business. It shows three things a first-time visitor usually wants to see: evidence labels, an assumption ledger, and calculation receipts you can re-run.

## At a glance

Inputs: $49 a month per clinic, $9 variable cost, $1,200 fixed costs, $900 a month acquisition spend, $40,000 starting cash, 6 clinics in month 1 ([all inputs](inputs.md)).

| Calculator result | Value | Receipt |
|---|---|---|
| Contribution margin | $40.00 per clinic per month | [01](receipts/01-contribution-margin.json) |
| Gross margin | 81.63% | [02](receipts/02-gross-margin.json) |
| Break-even (fixed costs plus acquisition spend) | 53 clinics | [03](receipts/03-break-even.json) |
| Loaded break-even | rejected: acquisition cost per clinic is larger than the margin | [04](receipts/04-break-even-loaded-rejected.md) |
| Lifetime value at 4% monthly churn | $1,000.00 | [05](receipts/05-subscription-ltv.json) |
| Customer acquisition cost | $150.00 | [06](receipts/06-cac.json) |

| 24-month scenario (growth is an ASSUMPTION) | Conservative 8% | Base 15% | Optimistic 22% |
|---|---|---|---|
| Break-even month | none | 17 | 12 |
| Ending cash | $5,623.54 | $33,800.28 | $117,460.03 |
| Receipt | [07](receipts/07-forecast-conservative.json) | [08](receipts/08-forecast-base.json) | [09](receipts/09-forecast-optimistic.json) |

The point of the example is what surrounds those numbers:

- **Evidence labels.** Every input and claim is labeled FOUNDER_PROVIDED, ASSUMPTION, DERIVED or UNKNOWN. Market size, competitors and willingness to pay stay UNKNOWN because no source was examined. See the legend and evidence index in [report.md](report.md).
- **Assumption ledger.** The full ranked ledger, with what to test first, is in [steps/06-assumption-ledger.md](steps/06-assumption-ledger.md). The report carries the top ten.
- **Honest verdict.** The idea validator returned INSUFFICIENT EVIDENCE, and the report says it does not support a go or no-go decision.
- **Independent review.** The `evidence-auditor` and `report-editor` agents each returned REVISION REQUIRED. Their findings are in [steps/07-evidence-auditor.md](steps/07-evidence-auditor.md) and [steps/08-report-editor.md](steps/08-report-editor.md). The report stays PRELIMINARY because nothing re-audited it. These are AI review passes, not human audits.

## Read it in this order

1. [report.md](report.md): the finished business report.
2. [receipts/](receipts/README.md): the exact calculator outputs.
3. [steps/](steps/): the full output of every skill and agent, for the curious.
4. [run-log.md](run-log.md): which skills, agents and commands ran, and what the run needed.

## Reproduce it

**1. Install** (Claude Code with plugin support, and Python 3.9 or newer):

```text
/plugin marketplace add maddyzohadi/venturine
/plugin install venturine@venturine-marketplace
```

**2. Allow the calculators (optional).** Claude Code asks permission before running a calculator command. Approve each one, or choose the option that allows that exact command for the session. To allow them ahead of time, add rules for the two scripts using the path shown in the prompt, and never `python3` or `Bash` in general. See the [README](../../README.md#quick-start-about-five-minutes) for the form of the rule.

**3. Run the analysis.** Paste the prompt from [inputs.md](inputs.md) into Claude Code. Venturine's skills usually end with a recommended next step, so the session tends to stop after each one. When it does, type `continue`. The run recorded here needed eight such messages.

Claude's wording, labels and the findings of the review agents will differ from this run, because they are written by an AI model. Check that the skills named in [run-log.md](run-log.md) actually ran, since a session can do a step itself instead of calling its skill.

**4. Re-run the calculators.** These results do not vary. From a clone of this repository:

```bash
python3 scripts/calculate.py contribution-margin 49 9
python3 scripts/forecast.py monthly-forecast 40000 24 6 0.15 49 9 1200 900
```

Every command is listed in [receipts/README.md](receipts/README.md). The output should match the files there exactly, including the receipt fingerprint.

## Limits of this example

- **It is one run.** Another run will word things differently and may label an input differently.
- **Every input is invented,** and the growth rates, churn and market ceiling are assumptions. The calculators show the arithmetic is right for them, not that they are true.
- **No outside facts.** With web search off, the market analysis only has the founder's assumed 1,000 reachable clinics to work from, and its market size is derived from that assumption. A real analysis would add sourced research, which Venturine labels separately.
- **The forecast does not model churn.** Growth is applied as a gross rate, so the lifetime-value figure and the scenarios rest on different churn assumptions. The report says so itself.
- **Small slips in the generated report.** On review I found three, left as they were produced:
  1. The report says the month-24 clinic counts (about 35, 149 and 581) are not in the engine output. They are: the `units` column of each forecast gives 35.23, 149.35 and 581.34.
  2. It writes those counts as 6 × (1 + g)²⁴. The exponent should be 23, because month 1 is 6 clinics. The values are right.
  3. It estimates the optimistic case reaches the 1,000-clinic ceiling in month 27 and gives 6 × 1.22²⁶ ≈ 988. The product is about 1,056. Month 27 is still right.
- **Some model-written text has no label,** for example the idea validator's remark that missed appointments are a known problem in clinical settings. It is general knowledge, not a sourced statistic.
- **The report is longer than a summary** (about 320 lines). The tables above are the short version.

This example is not financial, legal or investment advice.

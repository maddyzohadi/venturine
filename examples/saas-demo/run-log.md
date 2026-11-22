# Run log

> **Hypothetical example.** This records what the demo run actually did, taken from the Claude Code session log. Nothing in it is edited.

| | |
|---|---|
| Date | 2026-11-21 |
| Plugin | Venturine at commit `221a9aa`: release v0.3.1 plus two later changes (a README line and CI, and a one-line wording change in each skill and agent). Calculators unchanged, engine 0.2.1. |
| Model | `claude-sonnet-4-6`, as recorded in the session log |
| Web access | Disabled (`WebSearch` and `WebFetch` were not allowed). 0 web calls were made. |
| Calculator permission | Two scoped allow rules, one for `scripts/calculate.py` and one for `scripts/forecast.py`. No general `Bash` permission. |

## Skills invoked, in order

Each was called through the `Skill` tool.

1. `venture-intake` ([output](steps/01-venture-intake.md))
2. `idea-validator` ([output](steps/02-idea-validator.md))
3. `market-intelligence`, offline ([output](steps/03-market-intelligence.md))
4. `unit-economics` ([output](steps/04-unit-economics.md))
5. `scenario-comparison` ([output](steps/05-scenario-comparison.md))
6. `assumption-ledger` ([output](steps/06-assumption-ledger.md))
7. `business-report`, which wrote [report.md](report.md)

## Agents invoked

- `evidence-auditor` ([output](steps/07-evidence-auditor.md)): verdict REVISION REQUIRED, seven findings.
- `report-editor` ([output](steps/08-report-editor.md)): verdict REVISION REQUIRED, three findings.

The `business-report` step incorporated the findings. No second audit followed, so the report is marked PRELIMINARY, which is what the plugin is meant to do.

## Not run

`competitor-intelligence`, `pricing-analysis`, `customer-discovery`, `go-to-market`, `evidence-audit` (the evidence-auditor agent was called directly instead of through the skill), `red-team-reviewer` and the `research-lead`, `financial-analyst` and `go-to-market-strategist` agents. The demo keeps to the four areas it set out to show, plus review.

## Calculator commands

Nine commands ran, one at a time. Eight returned results and one was rejected by the engine. See [receipts/](receipts/README.md). No command was refused by a permission prompt. Two figures in the report (LTV divided by CAC, and CAC payback) were worked out by hand by the session and are labeled "manual" in the report. They are not calculator output.

## What it took to get through the pipeline

The session paused after nearly every skill, because each ends with a recommended next step. The original message was followed by one longer "continue with the remaining steps" message and then seven messages that said only "continue". In an interactive session you would type "continue" yourself.

An earlier attempt with the same inputs finished in a single message but did the market step itself, without calling the `market-intelligence` skill. It was discarded and the run above replaced it.

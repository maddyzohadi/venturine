<p align="center">
  <img src="assets/logo.svg" alt="Venturine logo" width="96" />
</p>

# Venturine

Evidence-labeled startup analysis for Claude Code: validate an idea, size a market, study competitors, and test the economics, with claims labeled by how well they are supported and arithmetic done by a reproducible calculator.

Venturine is a Claude Code plugin made of skills and agents for founders and independent builders. It is built around two habits: label what you actually know versus what you assume, and compute numbers with a reproducible calculator instead of doing arithmetic in prose.

> **Status: private beta (v0.2.1).** The repository is private while the beta is prepared, so installation requires access to it. See the [roadmap](docs/roadmap.md) for what is shipped and what is planned.

## What you get today

| Area | What it does |
|---|---|
| **Idea validation** | `idea-validator` evaluates demand, feasibility, competition and risk, and ends in one of four labeled decisions. |
| **Market intelligence** | `market-intelligence` defines the market, segments customers, and sizes TAM, SAM and SOM only when sourced inputs exist. |
| **Competitor intelligence** | `competitor-intelligence` separates direct, indirect and substitute competitors and marks unverified claims as unverified. |
| **Unit economics** | `unit-economics` covers margins, CAC, LTV, payback, break-even and runway, using a calculator for the arithmetic. |
| **Research and review agents** | `research-lead` gathers evidence, `financial-analyst` models the economics, `evidence-auditor` runs a second AI review pass over claims and calculations. It is not a human audit and does not guarantee accuracy. |
| **Financial calculator** | A standard-library Python engine (v0.2.1) with nine operations and an automated test suite. |
| **Customer and growth** (unreleased) | `customer-discovery` structures segments, problems and interview findings from research you actually did, and never invents interviews or results. `go-to-market` builds a plan from the evidence: starting segment, positioning, channels, budget and experiments, with channel economics from the calculator. `assumption-ledger` ranks what a plan depends on and what to validate first. The `go-to-market-strategist` agent analyzes channels, positioning and growth options from the available evidence. |
| **Integrated reporting** (unreleased) | `business-report` combines the validation, market, competitor, financial, customer and go-to-market findings into one report. It keeps every evidence label, calculation receipt and contradiction, and adds no new facts. The `report-editor` agent checks the report against its source findings for accuracy, consistency, receipts, labels and unsupported conclusions. It has no web access and is not an audit. |
| **Forecasting and pricing** (unreleased) | `scenario-comparison` compares scenarios over a monthly forecast of cash flow and runway, and shows how sensitive the outcome is to each input. `pricing-analysis` compares candidate prices by margin, break-even and profit. A separate calculator does the arithmetic and gives each result a receipt. See [docs/forecasting.md](docs/forecasting.md). |
| **Intake and handoff** (unreleased) | `venture-intake` turns a rough description into a structured venture profile with labeled inputs and a list of what is missing. Skills can pass their results on in the [`venturine-handoff/v1`](docs/handoff-v1.md) format, which a standard-library validator checks. |
| **Independent review** (unreleased) | `evidence-audit` prepares an analysis for the `evidence-auditor` and reports what changed. `red-team-reviewer` argues the strongest case against a conclusion and looks for disconfirming evidence. Both are AI passes, not human audits. |

## Design principles

- **Evidence labels, not vibes.** Claims and inputs are labeled VERIFIED, PARTIALLY_SUPPORTED, UNVERIFIED, CONTRADICTED, FOUNDER_PROVIDED, DERIVED, ASSUMPTION or UNKNOWN, with the same meanings in every skill and agent ([definitions](docs/evidence-terminology.md)). Skills are instructed never to invent sources, statistics or citations. These are instructions to an AI model, so labels can still be wrong; check the sources behind anything that matters.
- **Reproducible numbers.** Calculations run through a deterministic engine that echoes its inputs, so a result can be re-run. See [Financial calculator](#financial-calculator).
- **Least privilege.** No agent has shell access. The only code that runs is the calculators and the handoff validator, in your main Claude Code session, with your permission. See [security and privacy](docs/security-and-privacy.md).
- **Honest limits.** A skill reports "insufficient evidence" instead of filling gaps, and states what it did not verify or audit.

Venturine does not claim to be better than other tools. If you are comparing options, the [competitive landscape](docs/competitive-landscape.md) lists similar projects with dated, sourced facts.

## Quick start (about five minutes)

> The five-minute target has not yet been timed with outside testers. If it takes you longer, please open an issue and say where you got stuck.

**1. Check prerequisites (1 minute).**

- Claude Code with plugin support
- Python 3.9 or newer: run `python3 --version` (macOS ships 3.9, which works)
- Access to this repository (it is private during the beta)

**2. Install (1 minute).** In Claude Code:

```text
/plugin marketplace add maddyzohadi/venturine
/plugin install venturine@venturine-marketplace
```

**3. Run your first analysis (2 minutes).** Describe a business idea and name the skill:

```text
Use the Venturine idea-validator skill to evaluate this hypothetical idea:
a US business selling niche AI automation workflow kits to small accounting
firms, with a $15,000 startup budget. State your assumptions.
```

You should get an executive assessment, assumptions, risks, validation experiments and one of four decisions (PROCEED TO VALIDATION, REVISE THE CONCEPT, INSUFFICIENT EVIDENCE or NOT VIABLE UNDER STATED CONSTRAINTS). Claims you did not supply should be labeled as assumptions or unverified.

**4. Run a calculation (1 minute).** Ask for numbers:

```text
Use the Venturine unit-economics skill and the calculator to find the break-even
sales volume for a $149 kit with $19.37 variable cost per sale, $1,500 monthly
fixed costs excluding marketing, and an assumed $60 customer acquisition cost.
```

Claude Code will ask permission before running the calculator. The command looks like this, and you can run it yourself to check:

```bash
python3 scripts/calculate.py break-even-loaded 1500 149 19.37 60
```

Expected result: 22 units, with `loaded_contribution_per_unit` of `69.63`. The plain `break-even` command gives 12 units because it leaves acquisition cost out, and its output says so. The difference is the reason both exist.

More prompts and full outputs are in [docs/examples.md](docs/examples.md).

## Examples

All examples use hypothetical businesses and illustrative numbers. They are not real results.

**Validate an idea**

```text
Use idea-validator on: a subscription meal-prep service for shift workers
in one US city, $15,000 budget. Ask me only for facts that change the answer.
```

**Check a market**

```text
Use market-intelligence to define the serviceable market for a bookkeeping
tool for US dental practices. Show formulas and mark every input as verified,
founder-provided, derived, assumption or unknown.
```

**Review competitors**

```text
Use competitor-intelligence to map direct, indirect and substitute options
for a niche workflow-template product. Mark anything you could not verify.
```

**Audit the findings**

```text
Ask the evidence-auditor agent for a second review pass over the claims and
calculations above and list what remains unverified.
```

**Start with an intake** (unreleased)

```text
Use venture-intake on this hypothetical idea: a weekend market stall selling
sourdough loaves. Ask me only what changes the analysis, label what I tell
you, and give me a handoff I can pass to the other skills.
```

**Audit before you commit money or time** (unreleased)

```text
Use evidence-audit on the analysis above before I decide. Run the
evidence-auditor, tell me what changed, and say whether the result is
AUDITED or PRELIMINARY.
```

**Compare scenarios** (unreleased)

```text
Use scenario-comparison on this hypothetical bakery: $5,000 cash, 12 months,
100 loaves in month 1, price $24, variable cost $9.50, fixed costs $1,500 a
month, advertising $600 a month. Conservative is 80 loaves growing 1% a month;
base is 100 growing 3%. Label every input and give me the receipts.
```

**Test a price** (unreleased)

```text
Use pricing-analysis to compare $24, $29 and $34 for that bakery: variable
cost $9.50, fixed costs $1,500, acquisition cost $12 per customer, 100 units a
month. Do not assume how demand changes with price.
```

**Organize customer research** (unreleased)

```text
Use customer-discovery on my notes from five conversations with hypothetical
bakery customers (pasted below). Report counts exactly as I gave them, do not
add anything I did not say, and tell me what I still do not know.
```

**Plan how to reach customers** (unreleased)

```text
Use go-to-market for that bakery. I spent $40 on flyers and got 4 customers,
and referrals cost nothing and brought 3. Contribution per customer is
$4.50 and I can spend $200 a month. Compare the channels and plan my next
experiments.
```

**Rank your assumptions** (unreleased)

```text
Use assumption-ledger on my plan and the handoff above. Show what each
result rests on, rank what to validate first, and track what changes as I
learn more.
```

**Assemble a report** (unreleased)

```text
Use business-report to combine my validation, market, competitor, financial,
customer and go-to-market findings into one report, then have the
report-editor check it against those findings.
```

**Challenge a conclusion** (unreleased)

```text
Ask the red-team-reviewer agent for the strongest case against this
recommendation, a premortem, and any evidence that contradicts it.
```

## Financial calculator

The calculator lives in `scripts/` and uses only the Python standard library. It does not use the network or write files. Run it by file path, as shown below, from any directory.

| Command | Inputs | Notes |
|---|---|---|
| `revenue` | `UNITS PRICE` | |
| `gross-margin` | `REVENUE COGS` | |
| `contribution-margin` | `PRICE VARIABLE_COST` | |
| `break-even` | `FIXED PRICE VARIABLE_COST` | Operating break-even. Excludes acquisition cost, and the output says so. |
| `break-even-loaded` | `FIXED_EXCL_ACQUISITION PRICE VARIABLE_COST CAC_PER_CUSTOMER` | Assumes one purchase per customer. |
| `operating-profit` | `REVENUE COGS VARIABLE_OPERATING ACQUISITION FIXED_OPERATING` | Four mutually exclusive cost categories. |
| `cac` | `SPEND NEW_CUSTOMERS` | |
| `runway` | `CASH MONTHLY_NET_BURN` | |
| `subscription-ltv` | `MONTHLY_CONTRIBUTION MONTHLY_CHURN_FRACTION` | |

Acquisition spending must be counted exactly once: either as a fixed cost with a CAC of 0, or as a per-customer CAC with the fixed costs excluding it, never both. Inputs are limited to 64 characters and an absolute value of 1,000,000,000,000. Nonzero values must be at least 0.000000001, and invalid values are rejected with clear errors.

Numbers must be written with ASCII digits and an optional sign, decimal point and exponent (`1500`, `19.37`, `1e3`). Thousands separators, underscores, spaces and non-ASCII digits are rejected.

Results are printed in plain notation (never `6E+2`), rounded half-up to 2 decimal places for display, or to 4 significant digits when the magnitude is below 1 (so `0.0149` is not shown as `0.01`). The arithmetic itself is exact, and whole-unit results such as break-even are exact integers. A `display_rounding` field in the output states this. Rounding can change a later answer if you feed a displayed value into another calculation, for example a rounded CAC into `break-even-loaded`, so when rounding changed a value the output also includes `unrounded_result` with full-precision values for that purpose. Report the rounded result, not the unrounded digits, and do not read extra precision into either.

A successful calculation shows the arithmetic is right for the inputs you gave. It does not verify that the inputs are true.

## Security and privacy

- No telemetry, and the plugin has no hooks and no bundled servers.
- Agents have no shell access. This is enforced by a test.
- The calculator cannot reach the network, read or write files, or run other programs.
- The forecasting calculator is deterministic, uses only the Python standard library, and cannot reach the network, read or write files, or run other programs.
- The handoff validator reads only the one `.json` file you name, never writes files or reaches the network, and never prints the file's contents.
- `research-lead`, `evidence-auditor`, `red-team-reviewer` and `go-to-market-strategist` can search and fetch web pages. Do not put confidential details into research requests. Skills and agents are instructed to treat fetched content as data, not instructions. This reduces prompt-injection risk but cannot eliminate it.

Read [docs/security-and-privacy.md](docs/security-and-privacy.md) for the full picture, and [SECURITY.md](SECURITY.md) to report a vulnerability.

## Repository layout

```text
.claude-plugin/   plugin and marketplace manifests
skills/           idea-validator, market-intelligence, competitor-intelligence, unit-economics, venture-intake, evidence-audit, scenario-comparison, pricing-analysis, customer-discovery, go-to-market, assumption-ledger, business-report
agents/           research-lead, financial-analyst, evidence-auditor, red-team-reviewer, go-to-market-strategist, report-editor
schemas/          JSON Schema for the handoff format
scripts/          calculator, forecasting calculator, handoff validator, and command-line interfaces
tests/            calculator and repository tests
docs/             security, evidence terminology, competitive landscape, examples, roadmap, release process and notes, repository settings, commit metadata
assets/           logo and social preview image
```

## Roadmap

The planned architecture is 12 skills and 6 agents, delivered in phases: shared evidence and handoff contracts, scenario comparison, go-to-market and customer discovery, and an integrated business report. Release v0.2.1 ships 4 skills and 3 agents. Phases 1 to 4 (8 more skills, 3 more agents, the handoff format, forecasting and pricing calculations, customer and growth analysis, and integrated business reporting) are built but not yet released. See [docs/roadmap.md](docs/roadmap.md).

## Contributing

Contributions are welcome. Read [CONTRIBUTING.md](CONTRIBUTING.md) and the [Code of Conduct](CODE_OF_CONDUCT.md). Run the tests with:

```bash
python3 -m unittest discover -s tests
```

## License and name

Released under the [Apache License 2.0](LICENSE). Copyright 2026 Mahdokht Zohadi (see [NOTICE](NOTICE)). Created by Maddy Zohadi.

The Apache License does not grant permission to use the Venturine name or logo as branding for independent products. See the [name and logo policy](TRADEMARK.md).

## Disclaimer

Venturine provides research and business-planning assistance. Its outputs are not personalized financial, investment, tax, accounting or legal advice, and they do not guarantee commercial success. Verify material facts and figures independently before making decisions.

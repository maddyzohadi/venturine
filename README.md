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

## Design principles

- **Evidence labels, not vibes.** Claims and inputs are labeled VERIFIED, PARTIALLY_SUPPORTED, UNVERIFIED, CONTRADICTED, FOUNDER_PROVIDED, DERIVED, ASSUMPTION or UNKNOWN, with the same meanings in every skill and agent ([definitions](docs/evidence-terminology.md)). Skills are instructed never to invent sources, statistics or citations. These are instructions to an AI model, so labels can still be wrong; check the sources behind anything that matters.
- **Reproducible numbers.** Calculations run through a deterministic engine that echoes its inputs, so a result can be re-run. See [Financial calculator](#financial-calculator).
- **Least privilege.** No agent has shell access. The only code that runs is the calculator, in your main Claude Code session, with your permission. See [security and privacy](docs/security-and-privacy.md).
- **Honest limits.** A skill reports "insufficient evidence" instead of filling gaps, and states what it did not verify or audit.

Venturine does not claim to be better than other tools. If you are comparing options, the [competitive landscape](docs/competitive-landscape.md) lists similar projects with dated, sourced facts.

## Quick start (about five minutes)

> The five-minute target has not yet been timed with outside testers. If it takes you longer, please open an issue and say where you got stuck.

**1. Check prerequisites (1 minute).**

- Claude Code with plugin support
- Python 3: run `python3 --version`
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

A successful calculation shows the arithmetic is right for the inputs you gave. It does not verify that the inputs are true.

## Security and privacy

- No telemetry, and the plugin has no hooks and no bundled servers.
- Agents have no shell access. This is enforced by a test.
- The calculator cannot reach the network, read or write files, or run other programs.
- `research-lead` and `evidence-auditor` can search and fetch web pages. Do not put confidential details into research requests. Skills and agents are instructed to treat fetched content as data, not instructions. This reduces prompt-injection risk but cannot eliminate it.

Read [docs/security-and-privacy.md](docs/security-and-privacy.md) for the full picture, and [SECURITY.md](SECURITY.md) to report a vulnerability.

## Repository layout

```text
.claude-plugin/   plugin and marketplace manifests
skills/           idea-validator, market-intelligence, competitor-intelligence, unit-economics
agents/           research-lead, financial-analyst, evidence-auditor
scripts/          calculator and command-line interface
tests/            calculator and repository tests
docs/             security, evidence terminology, competitive landscape, examples, roadmap, release process and notes, repository settings, commit metadata
assets/           logo and social preview image
```

## Roadmap

The planned architecture is 12 skills and 6 agents, delivered in phases: shared evidence and handoff contracts, scenario comparison, go-to-market and customer discovery, and an integrated business report. Today 4 skills and 3 agents are shipped. See [docs/roadmap.md](docs/roadmap.md).

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

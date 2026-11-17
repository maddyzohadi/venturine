
# Venturine

Open-source AI skills for startup validation, market intelligence, financial analysis, and evidence-backed business decisions.

Venturine helps founders, entrepreneurs, and independent business builders evaluate opportunities using structured research, transparent assumptions, and traceable financial calculations.

## Features

- Business idea validation
- Market intelligence and TAM/SAM/SOM analysis
- Competitor research and positioning
- Unit economics and profitability analysis
- Evidence auditing and source verification
- Python-based financial calculations

## Included Skills

- `idea-validator`
- `market-intelligence`
- `competitor-intelligence`
- `unit-economics`

## Included Agents

- `research-lead`
- `financial-analyst`
- `evidence-auditor`


## Installation

In Claude Code, first add the Venturine marketplace:

`/plugin marketplace add maddyzohadi/venturine`

Then install the plugin:

`/plugin install venturine@venturine-marketplace`

The GitHub repository must be accessible to the installing user.


## Financial Calculator

The Python calculator (engine v0.2.0) uses only the standard library, with no network access or file writes. It supports:

- `revenue`
- `gross-margin`
- `contribution-margin`
- `break-even` (operating break-even; excludes customer acquisition, and its output says so)
- `break-even-loaded` (includes per-customer acquisition cost; assumes one purchase per customer)
- `operating-profit` (four mutually exclusive cost categories: COGS, variable operating, acquisition, fixed operating)
- `cac`
- `runway`
- `subscription-ltv`

Acquisition spending must be counted exactly once: either as a fixed cost with a CAC of 0, or as a per-customer CAC with the fixed costs excluding it, never both. Inputs are bounded (at most 64 characters, absolute value at most 1,000,000,000,000) and invalid values are rejected with clear errors.

Run the tests with `python3 -m unittest discover -s tests`.

## Requirements

- Claude Code with plugin support
- Python 3 for financial calculator execution
- Appropriate permissions for approved calculator commands

## Development Status

Venturine v0.1 is under development and undergoing validation.

The financial calculator includes automated tests. Plugin compatibility, agent coordination, and end-to-end business analysis still require testing.

## Disclaimer

Venturine provides research and business planning assistance. Its outputs are not a substitute for professional financial, legal, tax, or investment advice.

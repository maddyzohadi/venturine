# Roadmap

Venturine's target architecture is **12 skills and 6 specialized agents**. This page separates what is shipped from what is planned. Planned items are intentions, not commitments, and may change.

## Shipped (v0.2.1)

- Skills (4): `idea-validator`, `market-intelligence`, `competitor-intelligence`, `unit-economics`.
- Agents (3): `research-lead`, `financial-analyst`, `evidence-auditor`.
- Calculator engine v0.2.1 with nine operations, input bounds and automated tests.
- Plugin and marketplace manifests with strict validation in CI.
- Community and project files, security and privacy documentation, and repository tests.

## Built, not yet released (Phases 1 and 2)

Phases 1 and 2 are implemented on the main branch. The plugin version is still 0.2.1 until a release is cut, and the roadmap versions below are planned, not assigned.

- Skills (2 added, 6 total): `venture-intake`, `evidence-audit`.
- Agent (1 added, 4 total): `red-team-reviewer`.
- The [`venturine-handoff/v1`](handoff-v1.md) format, with a JSON Schema and a standard-library validator.
- An optional handoff output on every existing skill and agent. Their default output is unchanged.
- No change to the original calculator, which stays at v0.2.1.

Phase 2 adds:

- Skills (2 added, 8 total): `scenario-comparison`, `pricing-analysis`.
- A forecasting calculator, `scripts/forecast.py`, with a monthly cash-flow and runway model, scenario comparison, one-at-a-time sensitivity analysis and price comparison. Each result carries a calculation receipt. See [forecasting.md](forecasting.md).
- Handoff support: the four new operations and receipts, added compatibly to `venturine-handoff/v1`.
- Not included: repeat-purchase customer lifetime value, which stays on the roadmap.

## Planned phases

| Phase | Version | Planned scope | Skills / agents after |
|---|---|---|---|
| 0 | v0.2.1 | Foundations and adoption hygiene (this release) | 4 / 3 |
| 1 | v0.3.0 | Handoff and evidence-ledger schemas with a validator, `venture-intake`, `evidence-audit`, and a `red-team-reviewer` agent (built, not yet released) | 6 / 4 |
| 2 | v0.4.0 | Calculator v0.3.0 (scenario comparison, sensitivity, monthly cash flow, repeat-purchase LTV, calculation receipts), `scenario-comparison`, `pricing-analysis` (all but repeat-purchase LTV built, not yet released) | 8 / 4 |
| 3 | v0.5.0 | `customer-discovery`, `go-to-market`, `assumption-ledger`, and a `go-to-market-strategist` agent | 11 / 5 |
| 4 | v0.6.0 | `business-report` and a `report-editor` agent for an integrated report | 12 / 6 |
| 5 | v1.0.0 | Compatibility checks, independent security review, semver and deprecation policy, release process | 12 / 6 |

## Principles for every phase

- Each phase lists acceptance criteria and automated tests before work starts.
- No agent receives shell access. Calculator execution stays in the main session.
- No claim of superiority, and no fabricated statistics or testimonials.
- Behavior of skills cannot be fully unit tested, so deterministic parts (calculator, schemas, lints) are tested automatically and the prose is reviewed against sample outputs.

## How progress will be measured

Adoption indicators are recorded after launch and targets are set by the maintainer once a baseline exists. No numeric targets are promised here.

- Repository stars and forks.
- Unique visitors and cloners, from the repository's traffic page.
- Issues and pull requests opened by people other than the maintainer.
- Time to first successful analysis, measured with outside testers following the quick start.
- CI pass rate and open-defect counts.

## Public beta

The repository stays private until the public beta is ready. The pre-public checklist lives in [security-and-privacy.md](security-and-privacy.md).

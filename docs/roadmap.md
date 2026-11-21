# Roadmap

Venturine's target architecture is **12 skills and 6 specialized agents**. This page separates what is shipped from what is planned. Planned items are intentions, not commitments, and may change.

## Shipped (v0.2.1)

- Skills (4): `idea-validator`, `market-intelligence`, `competitor-intelligence`, `unit-economics`.
- Agents (3): `research-lead`, `financial-analyst`, `evidence-auditor`.
- Calculator engine v0.2.1 with nine operations, input bounds and automated tests.
- Plugin and marketplace manifests with strict validation in CI.
- Community and project files, security and privacy documentation, and repository tests.

## Released in v0.3.0 (Phases 1 to 4)

Phases 1 to 4 ship together in v0.3.0. The calculator engine stays at 0.2.1.

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

Phase 3 adds:

- Skills (3 added, 11 total): `customer-discovery`, `go-to-market`, `assumption-ledger`.
- Agent (1 added, 5 total): `go-to-market-strategist`.
- A `channel-compare` operation in the forecasting calculator: CAC from a channel test, the customers a budget buys at that CAC, and whether a first purchase recovers it. It makes no recommendation. See [forecasting.md](forecasting.md).
- Compatible handoff additions: the ledger fields `category`, `priority`, `risk` and `sample`, and an `interview` source type that can never make a claim `VERIFIED`.

Phase 4 adds:

- Skill (1 added, 12 total): `business-report`.
- Agent (1 added, 6 total): `report-editor`, which has read-only file tools and no web access.
- No change to the handoff schema or to either calculator.

## Phases and versions

| Phase | Version | Planned scope | Skills / agents after |
|---|---|---|---|
| 0 | v0.2.1 | Foundations and adoption hygiene (v0.2.1) | 4 / 3 |
| 1 | v0.3.0 | Handoff and evidence-ledger schemas with a validator, `venture-intake`, `evidence-audit`, and a `red-team-reviewer` agent (released in v0.3.0) | 6 / 4 |
| 2 | v0.3.0 | A forecasting calculator (scenario comparison, sensitivity, monthly cash flow, calculation receipts; repeat-purchase LTV not built), `scenario-comparison`, `pricing-analysis` (released in v0.3.0) | 8 / 4 |
| 3 | v0.3.0 | `customer-discovery`, `go-to-market`, `assumption-ledger`, and a `go-to-market-strategist` agent (released in v0.3.0) | 11 / 5 |
| 4 | v0.3.0 | `business-report` and a `report-editor` agent for an integrated report (released in v0.3.0) | 12 / 6 |
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

The pre-public checklist lives in [security-and-privacy.md](security-and-privacy.md).

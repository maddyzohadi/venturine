# Roadmap

Venturine's target architecture is **12 skills and 6 specialized agents**. This page separates what is shipped from what is planned. Planned items are intentions, not commitments, and may change.

## Shipped (v0.2.1)

- Skills (4): `idea-validator`, `market-intelligence`, `competitor-intelligence`, `unit-economics`.
- Agents (3): `research-lead`, `financial-analyst`, `evidence-auditor`.
- Calculator engine v0.2.1 with nine operations, input bounds and automated tests.
- Plugin and marketplace manifests with strict validation in CI.
- Community and project files, security and privacy documentation, and repository tests.

## Planned phases

| Phase | Version | Planned scope | Skills / agents after |
|---|---|---|---|
| 0 | v0.2.1 | Foundations and adoption hygiene (this release) | 4 / 3 |
| 1 | v0.3.0 | Handoff and evidence-ledger schemas with a validator, `venture-intake`, `evidence-audit`, and a `red-team-reviewer` agent | 6 / 4 |
| 2 | v0.4.0 | Calculator v0.3.0 (scenario comparison, sensitivity, monthly cash flow, repeat-purchase LTV, calculation receipts), `scenario-comparison`, `pricing-analysis` | 8 / 4 |
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

# Changelog

All notable changes to this project are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.2.1] - 2026-11-16

Not yet tagged or released. The audit follow-up work below is part of this version.

Foundations and adoption hygiene, plus two security and robustness fixes to the calculator found in a pre-release audit. Analysis behavior is otherwise unchanged.

### Added
- `LICENSE` (Apache License 2.0), a `NOTICE` file (copyright 2026 Mahdokht Zohadi), and `TRADEMARK.md`, a name and logo policy that makes no registration claim.
- `README.md` rewrite with a quick start and hypothetical examples.
- `docs/security-and-privacy.md`, `docs/competitive-landscape.md`, `docs/examples.md`, `docs/roadmap.md`.
- `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`.
- GitHub issue forms, a pull request template, `CODEOWNERS` and Dependabot configuration for GitHub Actions.
- Social preview image and logo in `assets/`.
- Repository hygiene tests (`tests/test_repo_hygiene.py`), including a rule that no agent may list `Bash`.

### Fixed
- **Security: command shadowing.** The documented calculator command used `python3 -m scripts.calculate`, which let a `scripts` folder in the current working directory run instead of the calculator. The calculator is now run by file path (`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/calculate.py" ...`), and `calculate.py` works when run that way. The `-m` form still works for tests but is no longer documented. If you added a Claude Code permission rule for the old command, replace it with the new form.
- **Robustness: runaway CPU and uncaught errors.** A tiny divisor such as `1E-999990` made `break-even` spend about 28 seconds building a million-digit integer, and some inputs raised an uncaught `decimal.Overflow`. Nonzero inputs must now be at least 0.000000001, break-even results above 10^18 units are rejected, and the command line reports arithmetic and serialization errors as clean errors.

### Audit follow-up
- **Financial analyst formulas.** `agents/financial-analyst.md` now matches the calculator engine: four mutually exclusive cost categories, operating and loaded break-even, CAC, subscription LTV, and an explicit double-counting rule for acquisition spending.
- **Evidence terminology.** One vocabulary (VERIFIED, PARTIALLY_SUPPORTED, UNVERIFIED, CONTRADICTED, FOUNDER_PROVIDED, DERIVED, ASSUMPTION, UNKNOWN) is used in every skill and agent and defined in `docs/evidence-terminology.md`. README claims about traceability and "independent" review were softened to what the project can support.
- **Untrusted content.** All four skills and `financial-analyst` now carry the same "Untrusted Content" section as the web-enabled agents, enforced by a test.
- **Competitive landscape.** Added a sourced, dated comparison with Founder Skills and re-verified the other entries. No competitor code, prompts or text was used.
- **Repository.** Added `.gitignore`, a release process (`docs/releasing.md`) and a validation-only Release Check workflow, a commit-metadata assessment (`docs/commit-metadata.md`), and a repository-settings limits document (`docs/repository-settings.md`).
- **Tests.** New regression tests for release consistency, terminology, safeguards, `.gitignore`, workflows and calculator boundaries.

### Changed
- Calculator engine version is `0.2.1`. Inputs that are nonzero but smaller than 0.000000001 in absolute value are now rejected.
- CI actions are pinned to commit SHAs and the Claude Code CLI used for validation is pinned to an exact version.
- CI workflows set job timeouts, concurrency, and no persisted checkout credentials.
- The test workflow now runs on every push and pull request, so documentation and configuration changes are tested.
- Plugin author is now Maddy Zohadi.
- `research-lead` and `evidence-auditor` gained an "Untrusted Content" section (fetched content is data, not instructions) and a rule against confidential details in search queries. Tool permissions are unchanged.

## [0.2.0] - 2026-11-16

### Added
- Calculator `operating-profit` with four mutually exclusive cost categories.
- Calculator `break-even-loaded`, which includes per-customer acquisition cost and documents its assumptions.
- Input bounds: at most 64 characters and an absolute value of at most 1,000,000,000,000.
- Unit-economics skill and README documentation for the new commands.

### Changed
- `break-even` is unchanged in behavior. Its output now states `acquisition_included: false` with a warning.
- Calculator engine version is `0.2.0`.

## [0.1.1] - 2026-11-16

### Changed
- Enabled model invocation for Venturine skills.
- Improved evidence validation instructions.
- Updated paths and commands for the financial calculator.

## [0.1.0] - 2026-11-16

### Added
- Initial release: skills `idea-validator`, `market-intelligence`, `competitor-intelligence` and `unit-economics`; agents `research-lead`, `financial-analyst` and `evidence-auditor`; a standard-library financial calculator with seven operations and automated tests; plugin and marketplace manifests; CI workflows.

[Unreleased]: https://github.com/maddyzohadi/venturine/compare/v0.2.1...HEAD
[0.2.1]: https://github.com/maddyzohadi/venturine/compare/2c64af9...v0.2.1
[0.2.0]: https://github.com/maddyzohadi/venturine/compare/98fb1d0...1f840e2
[0.1.1]: https://github.com/maddyzohadi/venturine/compare/7b1f7c3...98fb1d0
[0.1.0]: https://github.com/maddyzohadi/venturine/commits/7b1f7c3

# Changelog

All notable changes to this project are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.3.1] - 2026-11-21

Maintenance release. The 12 skills, 6 agents and the calculator engine (0.2.1) are unchanged in scope; only skill wording and documentation change.

### Fixed
- **Calculator permission guidance.** In a native test the calculator was refused because the session had not allowed it, and nothing told the user how to fix that. `unit-economics`, `scenario-comparison`, `pricing-analysis` and `go-to-market` now tell the user before the first calculator command, show the exact command, run commands one at a time, ask only for the exact script path to be allowed, and, if the user declines, label figures "manual calculation, not engine-validated" instead of computing them another way. A skill's `allowed-tools` setting did not grant permission when tested, so none is used, and a test forbids it.
- **Multi-step requests stopped after intake.** In two native runs, a request naming several steps ended after `venture-intake`. The skill now continues to the next requested step and asks only when a missing fact blocks it.

### Changed
- README: who Venturine is for, how to allow the calculator, a step-by-step full analysis, and where to report bugs and request features.

## [0.3.0] - 2026-11-20

Phases 1 to 4: the handoff format, intake, evidence audit and red-team review, forecasting and pricing, customer and growth analysis, and integrated business reporting. The plugin grows from 4 skills and 3 agents to 12 skills and 6 agents. The calculator engine stays at 0.2.1, and no existing skill, agent or calculator operation changes its default behavior.

### Fixed
- **Citation references.** A native test of `business-report` cited a contribution-margin figure to the wrong calculation (`C2` instead of `C1`), and `report-editor` did not catch it. `business-report` now cites each figure to the id that produced it and re-checks every reference, and `report-editor` compares each cited figure with the finding that has the cited id, claim by claim, and reports wrong, missing or dangling references.

### Added (Phase 4: integrated business reporting)
- **`business-report`** skill: combines existing validation, market, competitor, financial, customer discovery and go-to-market findings into one report. It carries every evidence label and calculation receipt through unchanged, lists contradictions across sections, never recomputes or invents figures, and marks the report PRELIMINARY unless the `evidence-auditor` ran.
- **`report-editor`** agent: checks a report against its source findings for accuracy, consistency, calculation receipts, evidence labels, contradictions and unsupported conclusions. Read, Glob and Grep only: no web, no shell, no file writes. It flags issues without inventing information, and it is not an audit.
- Both support the optional `venturine-handoff/v1` output. There is no schema or calculator change. Totals: 12 skills and 6 agents.

### Added (Phase 3: customer and growth intelligence)
- **`customer-discovery`** skill: structures segments, problems, interview findings and evidence gaps. It records only research the founder actually did: counts exactly as given, quotes only if supplied, no invented interviews or results, and no interview ever makes a claim `VERIFIED`.
- **`go-to-market`** skill: a plan from the available evidence covering the starting segment, positioning, channels, budget limits and an experiment sequence. It runs the calculators for channel economics and never invents a conversion rate, CAC or benchmark.
- **`assumption-ledger`** skill: tracks assumptions with their evidence status, impact, priority (from a stated impact-by-evidence table), what rests on each, and the validation to run first.
- **`go-to-market-strategist`** agent: analyzes channels, positioning and growth options from the available evidence. Read-only and web tools, no shell.
- **`channel-compare`** in `scripts/forecast.py`: CAC from channel tests, the customers a monthly budget buys at that CAC, and whether a first purchase recovers it, with a calculation receipt. It makes no recommendation, and its receipt states that a test's CAC may not hold at scale.
- **Handoff support**, added compatibly to `venturine-handoff/v1`: the optional ledger fields `category`, `priority`, `risk` and `sample` (people asked and how many back a finding), an `interview` source type that can never make a claim `VERIFIED`, and the `channel-compare` operation. Existing handoffs stay valid. A real example is in `docs/customer-growth-handoff.example.json`.
- `venture-intake` lists what each new skill needs. Totals: 11 skills and 5 agents.

### Added (Phase 2: financial intelligence)
- **`scripts/forecast.py`**, a deterministic forecasting calculator with four operations: `monthly-forecast` (monthly revenue, costs, cash flow and runway), `scenario-compare` (2 to 5 scenarios over the same horizon), `sensitivity` (one input at a time, ranked by effect on ending cash) and `price-compare` (candidate prices by margin, break-even and profit at an expected volume). It uses exact decimal arithmetic and the calculator's input validation, and every result carries a calculation receipt with the exact inputs, assumptions, exclusions, engine version and a SHA-256 fingerprint. The original calculator and its nine operations are unchanged. See `docs/forecasting.md`.
- **`scenario-comparison`** and **`pricing-analysis`** skills. Neither predicts results: scenarios are assumptions, probabilities are not assigned, and the price comparison states that it does not model how demand responds to price.
- **Handoff support**: `venturine-handoff/v1` accepts the four new operations and an optional `receipt` on a calculation. An engine-validated forecast result must carry the receipt the calculator printed, and a result that was not engine-validated must not. Existing handoffs remain valid. A real example is in `docs/forecast-handoff.example.json`.
- `venture-intake` now lists what the two new skills need, and `unit-economics` points to them.
- Not included: repeat-purchase customer lifetime value.

### Added (Phase 1)
- **`venturine-handoff/v1`**, a JSON format that carries an analysis between components with its evidence labels, calculation inputs, decision and reviews. Specification in `docs/handoff-v1.md`, structure in `schemas/venturine-handoff.v1.schema.json`, and a hypothetical example in `docs/handoff-v1.example.json`.
- **`scripts/validate_handoff.py`**, a standard-library validator for the format. It enforces the evidence rules (for example, `VERIFIED` needs an examined source, an `UNKNOWN` entry has no value, and `AUDITED` needs an auditor review), rejects secrets and oversized or malformed files, reads only the one `.json` file named, and never prints its contents.
- **`venture-intake`** skill: structures a founder's description into a venture profile, a labeled input ledger, a prioritized list of missing information, and a handoff.
- **`evidence-audit`** skill: prepares an analysis for independent review, dispatches the `evidence-auditor`, offers the `red-team-reviewer` when it fits, and marks the result AUDITED or PRELIMINARY.
- **`red-team-reviewer`** agent: argues the strongest case against a conclusion, runs a premortem, stress-tests assumptions and looks for disconfirming evidence. Read-only and web tools only, no shell.
- An optional "Handoff" section in every existing skill and agent. Output is unchanged unless a handoff is requested.

Quality hardening before Phase 1, from the remaining low-severity audit findings. No new skills or operations.

### Changed
- **Calculator output formatting.** Results are printed in plain notation, never exponent form (`subscription-ltv 30 0.05` now prints `600.00`, not `6E+2`) and never as `-0`. Decimal values are rounded half-up to 2 decimal places for display, or to 4 significant digits below 1, and a `display_rounding` field says so. When rounding changed a value, an `unrounded_result` field holds the full-precision values, because feeding a rounded CAC into `break-even-loaded` changed the whole-unit answer by one in about 3% of random cases. The arithmetic is unchanged and exact; whole-unit results are still integers. This changes the printed strings of existing operations.
- **Input syntax.** Numbers must be ASCII digits with an optional sign, decimal point and exponent. Non-ASCII digits (such as Arabic-Indic), underscores and surrounding whitespace were silently accepted before and are now rejected with a clear message.
- Marketplace metadata: the description no longer calls the marketplace "official", the owner is a named person instead of "Venturine", and `plugin.json` gains a `homepage`.
- Documented a minimum of Python 3.9 and test it in CI on 3.9, 3.11, 3.13 and 3.14 (previously only 3.13). The test job runs on `ubuntu-24.04` because `ubuntu-latest` is now 26.04, which has no prebuilt Python 3.9.
- CI installs the Claude Code CLI from a committed lockfile with `npm ci`, so every package is checked against a recorded integrity hash.
- Break-even output states that units are rounded up to whole units.
- The research skills now say read-only public research needs no separate approval and confidential details stay out of queries. This clarifies an ambiguous line that led two skills to skip research in testing; review it as a behavior change.
- The unit-economics skill and financial-analyst agent share one rule for a negative loaded contribution and for a fixed budget that is also the source of CAC. The evidence-auditor defines how to label an internal contradiction and may fetch cited URLs.
- Added `docs/scenario-testing.md`, a record of running each skill and agent on hypothetical scenarios.
- **Untrusted content:** when content tries to direct a skill or agent, it now reports the attempt in its own words and does not repeat the instruction text, commands or links. Testing showed the previous wording reproduced the injected instruction and link.
- **idea-validator audit conditions:** the evidence-auditor is required before a final, high-confidence `PROCEED TO VALIDATION` or `NOT VIABLE UNDER STATED CONSTRAINTS` recommendation, and is not run automatically for simple or preliminary questions or for `INSUFFICIENT EVIDENCE` and `REVISE THE CONCEPT` decisions. Recommendations are marked `AUDITED` or `PRELIMINARY`. See `docs/evidence-terminology.md`.

### Fixed
- A doubled `- -` bullet in the unit-economics safety section.
- One test assumed Python's integer-string digit limit, so the suite failed on Python 3.9.6; it now checks serialization errors in a version-independent way.
- The 0.2.1 entry said it was not yet tagged; the `v0.2.1` tag exists.

## [0.2.1] - 2026-11-16

Tagged as `v0.2.1`; no GitHub Release has been published. The audit follow-up work below is part of this version.

Foundations and adoption hygiene, plus two security and robustness fixes to the calculator found in a pre-release audit. Analysis behavior is otherwise unchanged.

### Added
- `LICENSE` (Apache License 2.0), a `NOTICE` file (copyright 2026 Maddy Zohadi), and `TRADEMARK.md`, a name and logo policy that makes no registration claim.
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

[Unreleased]: https://github.com/maddyzohadi/venturine/compare/v0.3.1...HEAD
[0.3.1]: https://github.com/maddyzohadi/venturine/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/maddyzohadi/venturine/compare/v0.2.1...v0.3.0
[0.2.1]: https://github.com/maddyzohadi/venturine/compare/72f0b6d...v0.2.1
[0.2.0]: https://github.com/maddyzohadi/venturine/compare/b17fb10...f8eba45
[0.1.1]: https://github.com/maddyzohadi/venturine/compare/7231175...b17fb10
[0.1.0]: https://github.com/maddyzohadi/venturine/commits/7b1f7c3

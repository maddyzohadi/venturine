# Competitive Landscape

Research date: 2026-11-16. Facts re-verified: 2026-11-17. This is a snapshot, not a ranking.

## Purpose and method

Venturine's goal is to make founder analysis traceable. This document records which similar projects exist so that Venturine's README can avoid claims it cannot support.

**Method.** A few web searches located candidate projects. Repository facts below (description, license, stars, last push, archived status) were read directly from each repository through the GitHub API and re-read on the verification date. Statements about what a project contains come from its repository README or file listing where noted. Directory sites and search summaries disagree with each other on details such as star counts, so they are not used as facts.

**Limits.**

- This is not exhaustive. Only a small number of projects were examined.
- Only publicly visible repository information was reviewed. Nobody was contacted and no product was run.
- Features not listed here are not asserted to be absent. Where a feature was not checked it is marked "not examined".
- Star counts change daily and are shown only as a dated signal of visibility, not quality.

## Similar projects

| Project | Repository facts (verified 2026-11-17) | What its documentation describes | Not examined |
|---|---|---|---|
| [lool-ventures/founder-skills](https://github.com/lool-ventures/founder-skills) ("Founder Skills") | "AI agent skills for high-velocity startup founders". Apache-2.0. 55 stars. Last push 2026-11-12. Not archived. Latest release listed on GitHub: v0.28.0 (2026-11-12). | Its README describes a Claude plugin with six skills (market sizing, deck review, financial model review, investment-committee simulation, competitive positioning, cap-table modeling), a script-backed workflow, and a privacy section stating which skills use web search. Its repository root lists `scripts`, `tests`, `evals`, `agents` and `skills` directories. | Output quality, accuracy of its calculations, how its tests or evals behave, whether any of its claims hold in practice |
| [ferdinandobons/startup-skill](https://github.com/ferdinandobons/startup-skill) | "AI agent skills for startup validation, competitive intelligence, and planning". MIT. 1,299 stars. Last push 2026-07-01. Not archived. | Four skills: `startup-design`, `startup-competitors`, `startup-positioning`, `startup-pitch`. The README describes market research, competitor battle cards, positioning, pitch formats and financial projections, and has its own website and releases. | Calculator or script use, evidence labeling, test suite |
| [wshobson/agents](https://github.com/wshobson/agents) | Large multi-tool collection of plugins, agents and skills. MIT. 42,613 stars. Last push 2026-11-16. Not archived. | Contains a `startup-business-analyst` plugin with a `startup-financial-modeling` skill. Its directory holds `SKILL.md` and a `references/details.md` file, and no script file was listed in that skill's directory. | Other startup skills, tests of that skill |
| [elvismusli/business-validator](https://github.com/elvismusli/business-validator) | "AI-powered business idea validation pipeline for Claude Code". MIT. 4 stars. Last push 2026-02-18. Not archived. | Describes a single slash command that produces a Go/No-Go report with market research, competitor analysis, financial modeling and risk assessment. | Everything beyond the description |
| [j7an/ideaprobe](https://github.com/j7an/ideaprobe) | "Structured, data-backed business idea validation for coding agents". MIT. 0 stars. Last push 2026-04-16. **Archived.** | Description only. | Everything beyond the description |
| [SergeiGorbatiuk/startup-superpowers](https://github.com/SergeiGorbatiuk/startup-superpowers) | No description. GPL-3.0. 24 stars. Last push 2026-08-03. Not archived. | Description only. | Everything |

## Overlap and differences (documented facts only)

This compares what each project's public documentation describes. It does not rate quality, and no project was run. Venturine was written independently, and no Founder Skills code, prompts, instructions, documentation text or architecture was copied or used as a template.

| Topic | Venturine (this repository) | Founder Skills (per its README and file listing, 2026-11-17) |
|---|---|---|
| Overlapping area | Market sizing, competitor analysis, unit economics, idea validation | Market sizing, competitive positioning, financial model review, plus deck review, investment-committee simulation and cap-table modeling |
| Audience framing | Founders and independent builders validating a business idea | Startup founders, with an emphasis on investor scrutiny |
| License | Apache-2.0 | Apache-2.0 |
| Maturity signal | v0.2.1, private beta, four skills and three agents | v0.28.0 listed as the latest release, six skills, 55 stars |
| Not compared | Anything not stated in public documentation, including output quality and accuracy | |

Founder Skills is the more mature project by the release and star signals above. Venturine's goals, such as explicit evidence labels and an agent set with no shell access, are design choices, not demonstrated advantages.

**Name ambiguity.** Several unrelated GitHub repositories use the name "founder-skills" or similar (for example `ognjengt/founder-skills`, `firatcand/founder-skills`, `SanketSapkal/founder-skills`). This document refers only to `lool-ventures/founder-skills`, chosen because it overlaps with Venturine's analysis scope.

## Distribution context

- Anthropic maintains [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official), described as an "Official, Anthropic-managed directory of high quality Claude Code Plugins" (Apache-2.0, 47,542 stars, last push 2026-11-17).
- Claude Code documentation on [discovering plugins](https://code.claude.com/docs/en/discover-plugins) describes marketplaces. Search results also mention a separate community marketplace.
- **Open question.** Sources found during research disagree about which submission route feeds the official directory versus a community marketplace. Verify against the current Anthropic documentation before submitting Venturine anywhere.

## What this implies for Venturine

These are design hypotheses, not findings, and they are not marketing claims.

1. The founder-validation space already has several projects, so Venturine should not claim to be the first or the best.
2. Features Venturine intends to emphasize, and to demonstrate with tests and examples rather than assert, are:
   - Explicit evidence classes on claims.
   - A deterministic calculator whose outputs echo their inputs.
   - Agents with no shell access, enforced by a test.
   - (Planned, not yet shipped) validated handoffs between skills, scenario comparisons and an integrated report.
3. Whether any of this matters to users is untested. The adoption indicators in [roadmap.md](roadmap.md) are meant to measure that over time.

## Follow-up research

- Read each project's README and tests in depth before making any specific comparison.
- Try each project on the same hypothetical idea and compare outputs, with the method written down.
- Do not copy any project's code, prompts or text. Compare behavior only through each project's public documentation and legitimate use.
- Re-run this research before any public launch, since the data above ages quickly.
- Confirm the current submission routes for Anthropic's directories.

## Sources

Facts first read 2026-11-16 and re-verified 2026-11-17 through the GitHub REST API (repository metadata, README, root file listing).

- https://github.com/lool-ventures/founder-skills
- https://github.com/ferdinandobons/startup-skill
- https://github.com/wshobson/agents
- https://github.com/elvismusli/business-validator
- https://github.com/j7an/ideaprobe
- https://github.com/SergeiGorbatiuk/startup-superpowers
- https://github.com/anthropics/claude-plugins-official
- https://code.claude.com/docs/en/discover-plugins

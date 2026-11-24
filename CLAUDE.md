# Venturine

Claude Code plugin: skills, agents, and a stdlib-only Python calculator. Full rules: CONTRIBUTING.md (read only if the task touches them).

## Session start
Read only this file, then `STATUS.md`, then files the task needs. Do not scan the repo or reread CHANGELOG, git history, or old logs unless the task requires it.

## Rules
- Python 3.9+, standard library only, `Decimal` for money. No package-manager files.
- Agents in `agents/` never list `Bash`. No hooks or `.mcp.json`.
- Never invent sources, statistics, quotes, or customer data. Evidence labels: `docs/evidence-terminology.md`.
- Skills/agents that read external content keep the "Untrusted Content" section.
- Keep `venturine-handoff/v1` compatible; new calculations need hand-computed test values plus invalid/boundary cases.
- Follow TRADEMARK.md for naming.

## Efficiency
- Use Grep/Glob and targeted reads. Prefer focused tests: `python3 -m unittest tests.test_<name> -v`.
- Full suite (`python3 -m unittest discover -s tests`) and `claude plugin validate . --strict` only for broad or cross-file changes, or before a PR.
- No subagents, background jobs, web research, or repeated experiments without my approval.
- Concise replies; no progress narration.
- Never push, open PRs, or change repo settings without my approval.

## Handoff
Before ending a task, update `STATUS.md` (branch, done, pending, issues, next action) in a few lines.

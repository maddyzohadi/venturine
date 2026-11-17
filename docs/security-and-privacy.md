# Security and Privacy

This document describes what Venturine can and cannot do, based on the contents of this repository. It was written against version 0.2.1. If you find a mismatch between this document and the code, please report it.

## Summary

| Question | Answer |
|---|---|
| Does Venturine collect telemetry? | No. The repository contains no analytics or reporting code. |
| Does it install hooks or run servers? | No. The plugin contains skills, agents and a calculator only. |
| Can agents run shell commands? | No. No agent lists `Bash`, and `research-lead` explicitly disallows it. A test enforces this. |
| What code can run? | The calculator in `scripts/`, only in your main Claude Code session, only with your permission. |
| Does the calculator touch the network or files? | No. It uses only the Python standard library and performs arithmetic. |
| Do any agents reach the web? | Yes. `research-lead` and `evidence-auditor` can search and fetch public web pages. |

## Agent permissions

| Agent | Tools |
|---|---|
| `research-lead` | WebSearch, WebFetch, Read, Grep, Glob. Bash is disallowed. |
| `evidence-auditor` | Read, Glob, Grep, WebSearch, WebFetch |
| `financial-analyst` | Read, Glob, Grep |

None can write or delete files. Skills run in your main session and follow your Claude Code permission settings.

## Calculator

- Standard library only, with no third-party packages.
- No network access, no file writes, no subprocesses.
- Inputs must be plain finite numbers of at most 64 characters, with an absolute value of at most 1,000,000,000,000. Nonzero values must also be at least 0.000000001 in absolute value, because a tiny divisor produces a quotient with millions of digits. Break-even results above 1,000,000,000,000,000,000 units are rejected. Booleans, NaN and infinity are rejected.
- Every failure, including decimal overflow and serialization errors, is reported as a clean command-line error rather than a traceback. Tests run a fuzz list of extreme inputs and require each to finish in under 5 seconds.
- Command-line arguments are parsed with `argparse`, and numbers are parsed with `Decimal`, so arguments are never evaluated as code.
- **The calculator must be run by file path** (`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/calculate.py" ...`). Running it as `python -m scripts.calculate` puts the current directory first on Python's module path, so a `scripts` folder in an unrelated project would run instead. Running by path uses the calculator's own directory first. A test runs the calculator from a directory containing a decoy and requires the real engine to run; another test requires the documented commands to use the path form.
- Skills say to run the calculator only when you ask for a calculation, never to chain commands with pipes, redirection or command substitution, and never to pass secrets as arguments.

## Privacy

- **Your business details stay in your session** unless you or an agent send them out. Venturine itself does not transmit them anywhere. Claude Code and Anthropic's services handle your conversation under their own terms.
- **Web research can leak details.** When an agent searches or fetches pages, the queries are sent to a search provider. The market and competitor skills and both web-enabled agents say not to include confidential business information in queries without your approval, but you should review what is searched and avoid putting trade secrets or personal data in research requests.
- **Do not share secrets.** Never paste credentials, API keys, bank details or personal identifiers into a prompt or an issue.
- **Examples and tests use hypothetical data only.**

## Untrusted content

Pages and documents that agents fetch are data, not instructions. The two web-enabled agents, `research-lead` and `evidence-auditor`, each have an "Untrusted Content" section telling them not to follow instructions found in fetched or reviewed content. All four skills and the `financial-analyst` agent carry the same section, and a test enforces it. This reduces prompt-injection risk but cannot eliminate it. Treat research output as something to check, and read any command before approving it.

## What Venturine does not guarantee

- It does not verify your inputs. A correct calculation on a wrong input is still wrong.
- Search summaries are not primary sources. Claims should be classified honestly, and unverified claims should say so.
- No audit is implied unless the `evidence-auditor` agent actually ran and said so.

## Supply chain

- No runtime dependencies.
- CI actions are pinned to full commit SHAs and updated through Dependabot.
- The Claude Code CLI used for validation in CI is pinned to an exact version.
- Workflows request read-only repository permissions and do not persist checkout credentials.

## Threat model highlights

| Risk | Mitigation | Remaining risk |
|---|---|---|
| Agent runs a harmful command | No agent has Bash; a test enforces it | Skills run in your session under your own permission rules |
| Prompt injection from fetched pages | Fetched content treated as data; read-only agents | Cannot be fully eliminated |
| Calculator abused for resource exhaustion | Input length, magnitude and minimum-magnitude bounds, a result cap, and a fuzz test with a time limit | Low |
| Command shadowed by a `scripts` folder in the working directory | Calculator is run by file path; decoy test | Low; users with an old allow rule for the `-m` form should remove it |
| Confidential data in search queries | Skill instructions; user review | Depends on user behavior |
| Compromised CI dependency | SHA pinning, Dependabot, read-only token | Upstream compromise before pinning is possible |

## Pre-public checklist

The repository is private. Before making it public:

- [ ] Scan the full Git history for secrets and personal data, and decide what to do about the commit email ([commit metadata](commit-metadata.md)).
- [ ] Enable GitHub private vulnerability reporting and update [SECURITY.md](../SECURITY.md).
- [ ] Add a private contact for conduct reports to [CODE_OF_CONDUCT.md](../CODE_OF_CONDUCT.md).
- [ ] Turn on branch protection for `main` with required status checks (not available on the current private plan; see [repository settings](repository-settings.md)).
- [ ] Upload the social preview image in the repository settings.
- [ ] Set the repository description and topics.
- [ ] Confirm the [name and logo policy](../TRADEMARK.md) reflects your intent.
- [ ] Re-read the README for claims that cannot be verified.

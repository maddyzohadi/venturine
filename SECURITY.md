# Security Policy

## Supported versions

Security fixes are made against the latest released version on `main`. Older versions are not maintained.

## Reporting a vulnerability

Please do not open a public issue for a security problem.

- **While the repository is private:** contact the maintainer, Maddy Zohadi, privately through GitHub (account `maddyzohadi`).
- **After the repository is public:** use GitHub's "Report a vulnerability" private advisory form on the Security tab. Enabling that form is on the pre-public checklist in [docs/security-and-privacy.md](docs/security-and-privacy.md). It is not available under the current private configuration; see [docs/repository-settings.md](docs/repository-settings.md).

Include what you found, how to reproduce it, which version you used, and the impact you believe it has. Do not include real confidential business data.

Venturine is a volunteer-run project. Reports are handled on a best-effort basis, with no guaranteed response time.

## What is in scope

- The Python calculator in `scripts/`: input handling, resource use, and anything that could make it read or write files or reach the network.
- Agent and skill definitions: tool permissions that are broader than documented, or instructions that could be abused through untrusted content such as fetched web pages.
- CI workflows in `.github/`: unpinned or over-privileged actions and supply-chain risks.
- Documentation that could lead users to leak private information.

## Out of scope

- Vulnerabilities in Claude Code, Anthropic services or third-party websites. Report those to the relevant vendor.
- The accuracy of business analysis. Wrong or incomplete findings are bugs, but use the evidence or calculation issue template for them, not this process.

## Design stance

See [docs/security-and-privacy.md](docs/security-and-privacy.md) for the permissions each agent has, what the calculator can and cannot do, and how untrusted content is treated.

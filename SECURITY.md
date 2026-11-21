# Security Policy

## Supported versions

Security fixes are made against the latest released version on `main`. Older versions are not maintained.

## Reporting a vulnerability

Please do not put details of a security problem in a public issue.

- **Preferred:** if the repository's Security tab shows a "Report a vulnerability" button, use it. It opens a private advisory that only you and the maintainer can see.
- **If that button is not shown:** open a public issue titled "Security contact request" that says only that you have a security concern. Do not put details, proof of concept or affected versions in it. The maintainer, Maddy Zohadi (GitHub account `maddyzohadi`), will arrange a private channel. There is no security email address.

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

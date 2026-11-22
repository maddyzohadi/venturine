# Contributing to Venturine

Thank you for helping improve Venturine. This guide covers how to set up, what the project's rules are, and how to get a change merged. By participating you agree to the [Code of Conduct](CODE_OF_CONDUCT.md).

## Ways to contribute

- Report a bug, or a wrong or unsupported finding, using the issue templates.
- Improve documentation and examples. Examples must use clearly hypothetical businesses.
- Improve the calculator or its tests.
- Improve skills and agents.

For a larger change, open an issue first so the design can be agreed before you invest time.

## Development setup

Requirements: Python 3.9 or newer, and Git. Venturine has no third-party dependencies, so there is nothing to install. CI runs the tests on Python 3.9, 3.11, 3.13 and 3.14; a change must not use syntax or standard-library features newer than 3.9.

```bash
git clone https://github.com/maddyzohadi/venturine.git
cd venturine
python3 -m unittest discover -s tests -v
```

To validate the plugin and marketplace manifests (needs Claude Code):

```bash
claude plugin validate . --strict
```

CI installs Claude Code with the composite action in `.github/actions/install-claude-code/`. It installs one exact version, checks a pinned sha512 hash for every package before any install script runs, and fails on any mismatch. The repository holds no `package.json` or lockfile, because the plugin directory does not accept package-manager files, and a test keeps it that way. To change the pinned version, run `npm view @anthropic-ai/claude-code@VERSION dist.integrity` for the CLI and for each platform package listed in the action (`optionalDependencies` in `npm view @anthropic-ai/claude-code@VERSION`), then update every line of `PINNED_PACKAGES`. Do not install the CLI in a workflow any other way.

## Project rules

These are checked by tests where possible.

1. **Agents never get Bash.** Agent definitions in `agents/` must not list `Bash`. Calculator commands run only in the main session, with the user's permission. The hygiene tests fail if this changes.
2. **No dependencies.** The calculators and the handoff validator use only the Python standard library. They must not use the network, write files or run other programs. The validator reads only the one `.json` file it is given and never prints its contents.
3. **Calculations are reproducible.** Use `Decimal`, validate and bound inputs, and return clear errors. Every new calculation needs hand-computed expected values in its tests, and tests for invalid and boundary inputs.
4. **Evidence is honest.** Do not invent sources, statistics, quotes or testimonials, in code, skills, docs or examples. Use the evidence labels defined in [docs/evidence-terminology.md](docs/evidence-terminology.md). Any new skill or agent that reads external content must include the standard "Untrusted Content" section; a test checks this. A change to the handoff format must keep `venturine-handoff/v1` compatible (see [docs/handoff-v1.md](docs/handoff-v1.md)), or introduce a new schema id.
5. **No unsupported claims.** Do not claim Venturine is better than another tool, or that it guarantees any outcome. Describe what it does and let readers judge.
6. **Privacy.** Never put real customer, financial or confidential business data in issues, tests or examples.
7. **Naming.** Follow [TRADEMARK.md](TRADEMARK.md) when you refer to the project.

## Making a change

1. Fork the repository and create a branch from `main`, for example `feat/short-description` or `fix/short-description`.
2. Make your change. Keep it focused on one thing.
3. Add or update tests, and docs where behavior changes.
4. Run the full test suite and strict plugin validation.
5. Add a line under "Unreleased" in [CHANGELOG.md](CHANGELOG.md).
6. Open a pull request using the template and describe how you tested it.

Use clear commit messages in the form `type: short summary`, for example `feat: add scenario comparison`, `fix: reject negative CAC`, `docs: clarify quick start`.

## Reviewing

A maintainer reviews every pull request. Expect questions about evidence, assumptions and edge cases. CI must pass before merging.

## Licensing

Under Section 5 of the [Apache License 2.0](LICENSE), a contribution you intentionally submit for inclusion is licensed under that license unless you explicitly state otherwise. You keep your copyright. If you modify a file, mark it as changed as Section 4 of the license requires, and do not remove existing notices. Contributions do not grant rights to the Venturine name or logo; see [TRADEMARK.md](TRADEMARK.md).

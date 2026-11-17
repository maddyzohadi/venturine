# Release Process

This describes how a Venturine release is prepared and checked. **Nothing here publishes a release.** Creating a GitHub release, and making the repository public, are separate manual decisions by the maintainer.

## Versioning

Venturine uses [Semantic Versioning](https://semver.org/). Three version strings must always agree:

| Where | Field |
|---|---|
| `.claude-plugin/plugin.json` | `version` |
| `scripts/calculator.py` | `ENGINE_VERSION` (only changes when calculator behavior changes, so it may lag the plugin version) |
| `CHANGELOG.md` | a `## [X.Y.Z]` heading and a link reference at the bottom |

Tags are named `vX.Y.Z` and point at the commit on `main` that was released. No tag exists until the maintainer creates one.

## Checklist

1. All work is merged to `main` through a pull request with passing checks.
2. Move the `[Unreleased]` changelog entries under a new `## [X.Y.Z] - YYYY-MM-DD` heading, and add or update the link references at the bottom of `CHANGELOG.md`.
3. Set `version` in `.claude-plugin/plugin.json`. Update `ENGINE_VERSION` and the README only if the calculator changed.
4. Add `docs/release-notes/vX.Y.Z.md` (highlights, compatibility, upgrade steps, known limitations).
5. Run the checks locally:

   ```bash
   python3 -m unittest discover -s tests
   claude plugin validate . --strict
   ```

6. Re-read [docs/security-and-privacy.md](security-and-privacy.md), the pre-public checklist, and [commit metadata](commit-metadata.md).
7. Create an annotated tag on the release commit and push only that tag:

   ```bash
   git tag -a vX.Y.Z -m "Venturine vX.Y.Z" <commit>
   git push origin vX.Y.Z
   ```

8. Pushing the tag runs the **Release Check** workflow, which re-runs the tests and strict validation and confirms the tag matches `plugin.json` and the changelog. It does not create a release or upload anything.
9. If the check passes and the maintainer decides to publish, create the GitHub release manually from the tag, using the matching release notes file.

## Reproducibility

- CI uses commit-pinned actions and an exact Claude Code CLI version.
- The calculator has no dependencies, so a release is reproducible from the tagged commit alone.
- Changelog link references use commit ranges until tags exist. After the first tag is created, replace them with tag comparison links.

## What is not automated

- Publishing a GitHub release.
- Marketplace or directory submissions.
- Changing repository visibility.

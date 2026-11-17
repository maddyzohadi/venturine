# Repository Settings and Current Limits

Checked 2026-11-17 through the GitHub API for the private repository `maddyzohadi/venturine`. Repository visibility was not changed and no plan was purchased.

## Findings

| Control | Status under the current private configuration | Evidence |
|---|---|---|
| Branch protection on `main` | **Cannot be enabled.** GitHub's free plan does not offer branch protection on private repositories. | The branch-protection API call returned HTTP 403 with "Upgrade to GitHub Pro or make this repository public to enable this feature." |
| Repository rulesets | **Cannot be enabled** for the same reason. | The rulesets API call returned HTTP 403 with the same message. |
| Private vulnerability reporting | **Not available or not enabled.** It could not be confirmed. | The `private-vulnerability-reporting` endpoint returned HTTP 404. |
| Required status checks and required reviews | Unavailable, because they depend on branch protection or rulesets. | Follows from the above. |
| CODEOWNERS | Present at `.github/CODEOWNERS`, but it is only enforced with branch protection, so today it is advisory. | File exists. |

## What this means

- Nothing technically stops a direct push to `main` or a merge with failing checks. The workflow below is a convention, not a control.
- Security reports must go through the private contact in [SECURITY.md](../SECURITY.md) until private vulnerability reporting is available.

## Mitigations that work today

- Merge only through pull requests, and only after the Tests and Validate workflows pass.
- Do not push directly to `main`. Review the diff of every merge.
- Keep the account secured with two-factor authentication.
- Keep Actions permissions read-only (workflows already request `contents: read`) and keep actions pinned to commit SHAs.
- Keep `main` free of force-pushes by habit, since it cannot be enforced.

## When controls become available

They become available if the plan is upgraded or the repository becomes public. Neither is done here. At that point:

1. Enable branch protection or a ruleset on `main`: require a pull request, require the Tests and Validate workflows to pass, block force-pushes and deletion.
2. Enable private vulnerability reporting under Security, and update [SECURITY.md](../SECURITY.md).
3. Tick the matching items in the pre-public checklist in [security-and-privacy.md](security-and-privacy.md).

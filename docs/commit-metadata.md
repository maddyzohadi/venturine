# Commit Metadata and Personal Email Exposure

Assessment date: 2026-11-17. No Git history was rewritten for this assessment.

## Finding

Git records an author and committer name and email in every commit, and they are visible to anyone who can read the repository or clone it.

| Item | Result |
|---|---|
| Commits examined (all branches) | 38 |
| Commits whose author email is the maintainer's personal Gmail address | 38 of 38 |
| Commits whose committer email is that same personal address | 3 |
| Commits whose committer is GitHub's `noreply@github.com` (web-interface merges) | 35 |
| Author names in use | `Maddy` (35) and `maddyzohadi` (3) |
| Personal email address in tracked file contents or commit messages | Not found |

The repository is private, so exposure today is limited to people with access. Making it public, or sharing a clone, would publish the address permanently in the history, and it would be copied by forks and mirrors.

## Options, safest first

1. **Do nothing to history; prevent future exposure.** In GitHub account settings, enable "Keep my email addresses private" and "Block command line pushes that expose my email". Set the local Git identity to the account's GitHub no-reply address (`<id>+<username>@users.noreply.github.com`, shown under Settings → Emails):

   ```bash
   git config user.email "<id>+<username>@users.noreply.github.com"
   ```

   This protects new commits only. It does not change existing hashes, branches or PR #2.

2. **Add a `.mailmap`.** This changes how some Git commands display names, but it does not change the commits, and the address stays in the repository data. It is not a privacy fix.

3. **Rewrite history before the repository goes public** (for example with `git filter-repo` and a mailmap). This is the only option that removes the address from existing commits. It changes every commit hash, invalidates PR #2's commits, requires a force-push, and forces every clone to be replaced. Do it once, deliberately, after all open work is merged and before any public release or tag, and keep a backup. Rewriting an already-shared history cannot recall copies that exist elsewhere.

4. **Start a new public repository from a clean export** of the final tree, keeping this one as a private archive. This avoids rewriting but loses history and PR links.

5. **Accept the exposure.** Some maintainers decide that a long-lived commit email is acceptable. Treat it as an explicit decision.

## Recommendation

Apply option 1 now. Decide between options 3 and 4 before making the repository public, and record the decision in the pre-public checklist. Do not rewrite or force-push as part of this feature branch.

## Not covered

- Email addresses inside GitHub's own audit logs, forks, or caches.
- Other personal data, such as names in issue history. A full secrets and personal-data scan remains on the pre-public checklist.

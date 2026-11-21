# Commit Metadata and Personal Email Exposure

Git records an author and committer name and email in every commit, and they are visible to anyone who can read the repository or clone it. A public repository publishes them permanently, and forks and mirrors copy them.

## Current state (checked 2026-11-20)

| Item | Result |
|---|---|
| Commits examined (all local and remote branches and the `v0.2.1` tag) | 57 |
| Author email in every commit | The maintainer's GitHub no-reply address (`<id>+<username>@users.noreply.github.com`) |
| Committer email | The same no-reply address, or GitHub's `noreply@github.com` for web-interface merges |
| Head commits of all five pull requests | No-reply addresses only |
| Personal email address in tracked file contents or commit messages | Not found |

An earlier assessment (2026-11-17) found the maintainer's personal email in the author field of every commit at that time. The history has since been rewritten to the no-reply address, and this check confirms that no commit reachable from any branch, tag or pull request head carries a personal address.

## What this check cannot confirm

- Whether GitHub still serves the old, unreachable commits by their SHA or from cached views. GitHub removes them only after a cleanup. If this matters before the repository goes public, ask GitHub Support to run a garbage collection and purge cached views.
- Whether any clone, fork or mirror made before the rewrite still holds the old history. The repository is private, so any such copy is limited to people who had access.

## Preventing a repeat

In GitHub account settings, enable "Keep my email addresses private" and "Block command line pushes that expose my email". Set the local Git identity to the no-reply address:

```bash
git config user.email "<id>+<username>@users.noreply.github.com"
```

Re-run this check before each release:

```bash
git log --all --format='%ae %ce' | sort -u
```

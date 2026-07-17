---
description: "Git worktree hygiene for parallel agents — owned worktrees, no cross-boundary edits, commit per wave"
---

# Rule — worktree hygiene

Parallel agents that mutate files run in **isolated git worktrees** (`isolation: 'worktree'` on the
Agent tool, or `.claude/worktrees/<name>/`). Keep them clean.

- **Never edit the main checkout from inside a worktree.** If cwd is a worktree but an edit targets the
  main repo path, stop — that's a cross-boundary edit (the `warn-worktree-boundary` hook flags it).
- **Named worktrees have an owner + death condition.** `agent-*` worktrees are auto-cleaned (7-day TTL
  / removed if unchanged); an explicitly named one carries an owner note. The main checkout is never
  `git checkout`-ed by an agent.
- **The `.git` is shared across worktrees** — the stash stack and `.git/config` are shared. So inside a
  worktree: no bare `git add -A`, no `git stash pop`, no bare `git config user.name`. Stage explicit
  paths.
- **Commit per wave.** Each execution wave ends in a commit (bisectability). Loops self-clean their
  dated branches.
- **Judge merged-ness by patch-equivalence** (`git cherry -v` / `--cherry-pick`), not ancestry —
  squash-merge breaks ancestry checks.

Auto mode blocks destructive git (`reset --hard`, `checkout -- .`, `clean -fd`, `stash drop`) unless
explicitly requested — keep it that way.

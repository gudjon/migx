# HRN — execution waves

Each wave ends at a verifiability gate and a commit.

## Wave 1 — classify the surface
Add `permission` to every entry in `CAPABILITIES`, from the closed set. Lint it the way
`verify-command-vocabulary.py` lints nouns: a command without a class is a failure, so the field
cannot be forgotten on the next command added.

**Gate:** lint green; `system.capabilities --json` shows 35/35 classified.

## Wave 2 — the workspace boundary
One resolved workspace root (library root + state dir). Every mutating command checks its target
before acting. Outside → classified refusal naming the path, exit non-zero.

**Gate:** a test that attempts a write to `/tmp` and asserts refusal — *and* asserts the file was not
created, because "refused" and "refused after writing" are different.

## Wave 3 — transcript and resume
`_session.jsonl` already exists. Make it sufficient: every tool call and every policy decision appends.
`--resume <id>` rebuilds now/next/history from it.

**Gate:** kill mid-session, resume, state matches — with the music volume unmounted.

## Wave 4 — live gating
While a session is live, `deck.*` requires explicit approval. Approvals are **not** replayed by
`--resume`.

**Gate:** non-interactive `deck.*` with a live session refuses; a resumed session re-prompts.

## Halt condition
If wave 2 shows the workspace root cannot be resolved unambiguously (multiple library roots, symlinked
volumes), **halt** rather than guessing a boundary. Successor: a `config.workspace` decision. Re-fire
when the root is single-valued.

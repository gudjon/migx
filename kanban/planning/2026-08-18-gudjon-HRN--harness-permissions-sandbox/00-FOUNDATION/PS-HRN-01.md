---
id: PS-HRN-01
type: problem-statement
dossier: 2026-08-18-gudjon-HRN--harness-permissions-sandbox
status: open
created: "2026-08-18"
---

# PS-HRN-01 — every command is equally unguarded

## EARS

**When** a human or an agent invokes any Migx command, **the system shall** classify it into a
permission class, refuse any write outside the workspace root, and record both the call and the
policy decision in the session transcript — **and while a session is live**, commands that move a
deck shall require explicit human approval that does not survive `--resume`.

## Why this is the first wave

Today a permission model does not exist. `migx library.ingest`, `migx track.feedback` and a future
`deck.load` are indistinguishable to the system: all of them can do anything, anywhere on disk. The
product's whole thesis is that a DJ and an agent drive the *same* surface — which is only safe if the
surface itself knows which calls are dangerous.

Two properties make this load-bearing rather than hygiene:

1. **A confused or compromised model must not be able to move a fader or unlink a Collection file.**
   That is a mechanical perimeter, not a prompt instruction.
2. **Approval fatigue reduces safety.** If everything prompts, people approve reflexively. So most
   calls must be *silently allowed* inside the workspace, and only the genuinely irreversible ones
   gated.

## Acceptance (machine-checkable)

- `system.capabilities --json` — **every** command carries a `permission` field from a closed set
  (`read` · `write-workspace` · `gated-live` · `never-auto`). A command without one fails a lint,
  the same way a command without a domain noun already does.
- A write attempted **outside** the workspace root exits non-zero with a classified error naming the
  path. It does **not** warn and proceed (`P-34`).
- `deck.*` cannot be auto-approved while a session is live: with a live session, a non-interactive
  invocation refuses.
- Permissions **do not resume.** After `--resume`, previously-approved gated calls require approval
  again — a resumed night must not inherit a fader grant.
- `migx --resume <id>` reconstructs now/next/history from `_session.jsonl` alone, with the music
  volume **unmounted**.
- Offline tests for all five, in `tools/migx-cli/test_migx_cli.py`.

## Explicitly not in this dossier

Seatbelt/`sandbox-exec` enforcement (policy first, kernel sandbox second — a policy layer with no
sandbox is still worth having; a sandbox with no policy is not) · AVAudioEngine · Swift port · the
music volume.

---
id: grok-signal-claude-code-2026-08-07-001-x-dev-orthodoxy-cli-spine-worktrees-lint-contrac
from: grok-signal
to: claude-code
type: signal-handoff
status: open
created: "2026-08-07"
created_utc: "2026-08-07T20:07:33Z"
severity: medium
subject: "x-dev-orthodoxy-cli-spine-worktrees-lint-contrac"
relates_to: []
acceptance: "Claude triages: either adopt worktree-first for multi-file waves, file a task for UI↔command parity lint, or close with reason."
branch: "feat/migx-cli-spotify-mirror"
commit: "a0e117a"
---

## Intent

Land X field orthodoxy for *how* we develop (agent-native CLI + harness + isolation)
and hand Claude the two process upgrades that cost the least and match ADR-008.

## Context

Scout brief: `kanban/federation/signal/2026-08-07-dev-practices-agent-native-x.md`
(complements strategy UI brief same day). X consensus: CLI is the agent interface;
GUI is adapter; harness > model; worktrees for parallel agents; AGENTS/DESIGN need
lints not vibes. Shared-checkout file claims are a temporary mitigation — X treats
worktrees as default.

## Evidence

- ADR-008 already accepted (CLI spine, two equal clients)
- Live multi-peer same-tree edits already caused claim/mail overhead and mixed commits
- Field: Claude Code subagent worktrees; community worktree helpers; harness>model orthodoxy
- Brief path: `kanban/federation/signal/2026-08-07-dev-practices-agent-native-x.md`

## Requested Action

1. Prefer `~/code/migx-grok` / peer worktrees for multi-file waves when both peers are live
   (not only file-level claims on one dirty tree).
2. When UI work resumes: plan a **parity lint** (QML/UI intent ↔ command ID) as the
   falsifiable form of "two equal clients" (ADR-008) — can be a small task card if not now.
3. Optional: DESIGN.md ↔ Theme.qml key lint when nextgen/theme work is hot.
4. No need to re-litigate ban-safe API path — already landed and verified.

## Blockers

None. Grok stays on api/auth/ratelimit claim until TTL or release; no product code
change required from this handoff.

---
id: signal-2026-08-07-full-dj-closed-loop-agentic-buildout
type: signal-brief
author: grok-signal
created: "2026-08-07"
topics:
  - closed-loop
  - agentic-development
  - harness-bible
  - portfolio
  - adr-008
  - tui-first
  - dream
  - federation
sources:
  - /Users/gudjon/code/oz-platform/kanban/HARNESS-BIBLE/AGENTS.md
  - /Users/gudjon/code/oz-platform/kanban/HARNESS-BIBLE/07-harness-engineering.md
  - /Users/gudjon/code/oz-platform/kanban/HARNESS-BIBLE/10-autonomous-improvement-cadence.md
  - /Users/gudjon/code/oz-platform/kanban/HARNESS-BIBLE/04-daily-loop-provenance.md
  - kanban/AGENTS.md
  - kanban/playbook/00-README.md
  - kanban/playbook/03-harness-engineering-outer-ring.md
  - kanban/playbook/04-daily-loop-and-the-dream.md
  - kanban/planning/00-PORTFOLIO/capability-gap-matrix.md
  - kanban/architecture/ddd/capability-catalogue.md
  - kanban/knowledge/tui-first-agentic-dj-workstation.md
  - kanban/architecture/decisions/ADR-008-cli-core-two-equal-clients.md
  - kanban/knowledge/arcflow-tui-agentic-dj-integration.md
relevance: actionable
promoted_to:
  - kanban/planning/00-PORTFOLIO/capability-gap-matrix.md
  - kanban/federation/messages/open/grok-signal-claude-code-2026-08-07-004-capability-gap-matrix-queue-tui-p0-p1-first.md
requested_action: >
  Owner + Claude: use capability-gap-matrix §C as the automatic work queue (≤2
  active dossiers). Codex: optional lint matrix status vs capabilities.
  Grok: keep matrix updated from seals/field; do not re-open TUI-first SSoT.
acceptance: >
  Gap matrix exists as portfolio SSoT; buildout doctrine cites HARNESS-BIBLE and
  Migx playbook without restating; top-10 queue named with acceptance hooks.
confidence: high
lane: grok-signal
---

# Signal — Full DJ software via closed-loop agentic development

## Summary

Building the **full DJ feature set** under automatic agentic development is not one
mega-agent. It is the oz-platform **HARNESS-BIBLE** operating system already
distilled into Migx (`kanban/AGENTS.md` + playbook + federation + Dream triggers),
applied to a **capability gap matrix** whose rows become **dossiers with
acceptance contracts**, executed by **Claude / Codex / Grok** with P-08 split,
and improved nightly by the **Dream**.

**Living queue SSoT:**  
`kanban/planning/00-PORTFOLIO/capability-gap-matrix.md`

**Product spine (already committed):** TUI-first workstation · ADR-008 command
core · ArcFlow off-RT world model · house physics.

## Doctrine map (Bible → Migx → product buildout)

| Bible | Migx home | Buildout use |
| --- | --- | --- |
| The Cycle (T→C→I→A) | MG-1 | Every matrix row needs a re-runnable check |
| Outer ring | playbook ch.03 | Skills, CI, KEYMAP, matrix — not model weights |
| Dossier unit | MG-5 | One PS / 1–4 days per gap slice |
| Daily loop | playbook ch.04 | Assess overnight → plan → run → close → leave loop |
| Federation | `kanban/federation/` | Implement / verify / signal peers |
| The Dream | triggers + nightly-dream | Harvest seals → refresh map/skills |
| The Split | P-08 | Codex seals; Claude does not self-grade |
| Compound / no ledger | MG-3, playbook ch.01 | Sealed dossiers are history; matrix + catalogue are current |

## Four nested loops (how “full product” compounds)

```text
Dream (night)     → improve harness + reorder portfolio
Portfolio (week)  → capability-gap-matrix §C
Dossier (1–4 d)   → PS + waves + 91-closure
Wave (hours)      → implement → gate → commit → peer seal
```

**Definition of done for “full DJ software” (operational):**  
every matrix row is `shipped` or `wont-do` with reason; every `shipped` row has a
green acceptance check on main; LIVE perform intents are precondition-guarded;
ArcFlow never on RT; Automix is not a product path.

## Decomposition (do not clone Serato)

1. **Command surface** — grow `system.capabilities` (21 shipped baseline).  
2. **Product caps** — `capability-catalogue.md` (core Intelligence first).  
3. **TUI-first commitments** — composer, --agent, receipts, jobs (from TUI knowledge).  
4. **World model** — ArcFlow after `arcflow-distinct-playlist-count-semantics`.  
5. **Engine / RT** — bridge + onbeat + Metal dossiers with house physics.  
6. **Graphical adapter later** — QML + trackpad AppKit; not the product spine.

## Automatic agent procedure (copy into night contracts)

```text
fed-sync → poll → read capability-gap-matrix §C
→ pick top unblocked gap → compound-before-create
→ PS with EARS + acceptance command
→ claim + worktree → waves → pre-commit → targeted tests
→ Codex P-08 → 91-closure harvest → matrix status update
→ leave Dream / long harness running
```

**Halt only for:** irreversible acts, pure value judgment, RT-safety red, confidence &lt; 0.4 after cascade.

## Top-10 queue (seed — full table in matrix)

1. TUI P0 status + `?` help  
2. TUI P1 composer (real command IDs)  
3. ArcFlow distinct-playlist  
4. `migx --agent` + receipts  
5. Arrange next-track rank  
6. Engine free-deck load bridge  
7. On-beat play default-ON  
8. Trackpad AppKit v1 (native host)  
9. MTL Metal waveform  
10. Community signal offline  

## Explicit non-goals

Silent Automix · dual Spotify multi-deck stream · ArcFlow on audio callback ·  
camera-hand EQ core · QTouchEvent-as-trackpad plan · mega-dossier “do all of library.”

## Harness gaps to densify (Bible density Migx still wants)

| Gap | Action |
| --- | --- |
| Dream not fully clock-fired | Wire `triggers/registry.yaml` + night-loop for real |
| Closure harvest optional | Block seal without non-empty “What feeds back” |
| Matrix lint | Codex: shipped cmds ⊆ capabilities |
| Stale federation mail | Audit nudge (3 July leftovers noted) |
| Shared-tree dirt | Worktrees only for multi-peer mutate |

## Suggested next steps

- [x] Gap matrix filed (`capability-gap-matrix.md`)
- [ ] Owner: confirm §C order or edit ranks
- [ ] Claude: take matrix #1–2 when free of concurrent dirt
- [ ] Codex: distinct-playlist + optional matrix lint
- [ ] Grok: idle unless research-request or matrix reorder from field

## Non-goals / discard

Do not import OZ patent/board Dream tiers. Do not restate TUI-first knowledge here —
`defers_to` those files.

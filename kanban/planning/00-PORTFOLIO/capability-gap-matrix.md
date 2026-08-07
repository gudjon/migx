---
id: capability-gap-matrix
type: portfolio
title: "Capability gap matrix — closed-loop product buildout SSoT"
status: active
owner: gudjon
authored_by: grok-signal
created: "2026-08-07"
lastUpdated: "2026-08-07"
defers_to:
  - kanban/architecture/ddd/capability-catalogue.md
  - kanban/architecture/decisions/ADR-008-cli-core-two-equal-clients.md
  - kanban/knowledge/tui-first-agentic-dj-workstation.md
  - kanban/Strategy-Current.md
  - kanban/AGENTS.md
related:
  - kanban/knowledge/arcflow-tui-agentic-dj-integration.md
  - kanban/tasks/arcflow-distinct-playlist-count-semantics.md
  - kanban/tasks/macbook-trackpad-v1-appkit-gestures.md
  - kanban/federation/signal/2026-08-07-full-dj-closed-loop-agentic-buildout.md
  - kanban/federation/signal/2026-08-07-tui-first-dj-workstation-field.md
  - kanban/planning/00-PORTFOLIO/migx-harness-roadmap.md
note: >
  Living queue for agentic closed-loop buildout. Product capability ids defer to
  capability-catalogue.md. Command ids defer to `migx system.capabilities`.
  Status is operational (shipped / partial / gap / blocked / wont-do), not a second
  product catalogue. Update when a dossier seals or a command lands.
---

# Capability gap matrix

**Purpose:** single home for “what is not done yet” so automatic agentic development
opens **dossiers with contracts**, not vibes.  
**Law:** MG-1 (closed loop) · MG-3 (SSoT — this matrix cites, does not restate catalogue cards) ·
MG-5 (dossier unit) · ADR-008 (every product behavior is a command/query/event/capability).

## Status legend

| Status | Meaning |
| --- | --- |
| `shipped` | Acceptance check green on main; KEYMAP/capability row if human-facing |
| `partial` | Usable slice; named remaining contract |
| `gap` | Not started; ready to become a dossier/task |
| `blocked` | Depends on named blocker |
| `wont-do` | Explicit anti-identity or out of scope |

## Peer default

| Peer | Role |
| --- | --- |
| `claude-code` | Implement dossier waves |
| `codex-cli` | P-08 verify / seal |
| `grok-signal` | Field + research-request only |
| `dream` | Nightly harvest (triggers) |

**Active dossier budget:** ≤2 open implementer dossiers at a time; queue the rest here.

---

## A — Command surface (live `system.capabilities`, 21 rows)

Acceptance default: `python3 tools/migx-cli/test_migx_cli.py` + capability listed.

| command_id | kind | status | acceptance | next |
| --- | --- | --- | --- | --- |
| `spotify.login` | command | shipped | offline tests + OAuth dogfood | — |
| `spotify.status` | query | shipped | offline tests | — |
| `spotify.logout` | command | shipped | offline tests | — |
| `playlist.list` | query | shipped | offline tests | — |
| `playlist.pull` | command | shipped | mirror schema `migx.playlist-mirror/1` | — |
| `library.inspect` | query | shipped | quality tier fixtures | — |
| `library.resolve` | command | shipped | resolve report schema | — |
| `library.missing` | query | shipped | `migx.gap-list/1` | — |
| `library.ingest` | command | shipped | Collection path + quality gate | — |
| `crate.sync` | command | shipped | crate links only | — |
| `library.dedupe` | query | shipped | offline tests | — |
| `config.init` | command | shipped | offline tests | — |
| `config.show` | query | shipped | offline tests | — |
| `track.pull` | query | shipped | identity sheet (no store links) | — |
| `track.note` | command | shipped | sidecar | — |
| `track.cue` | command | shipped | sidecar | — |
| `track.show` | query | shipped | offline tests | — |
| `library.analyze` | command | partial | BPM/key sidecar; energy/structure deeper | cap-energy-structure dossier |
| `library.watch` | command | shipped | _Inbox auto-file | — |
| `library.rename` | command | shipped | re-file after analysis | — |
| `library.art` | query | shipped | chafa optional; placeholder degrade | brew install chafa for live art |
| `system.capabilities` | capability | shipped | 22 rows | grow only with command land |

### A2 — Surface commitments (TUI-first, not yet commands)

| commitment | status | acceptance | peer | next |
| --- | --- | --- | --- | --- |
| `migx` no-arg → TUI workspace | gap | launch opens TUI | claude-code | small task |
| `migx --json` everywhere | partial | all queries emit JSON | claude-code | audit missing |
| `migx --agent` JSONL | gap | request/event/receipt stream | claude-code | dossier |
| events / receipts | gap | schema + one LIVE path | claude-code | after --agent |
| `migx mcp-server` | gap | tools = capability IDs | claude-code | after --agent |
| engine command bridge | gap | guarded perform intents | claude-code | LIVE preconditions |
| composer in TUI | gap | dispatches real command IDs | claude-code | field P1 |
| TUI status line + `?` help | gap | pure snapshot + KEYMAP | claude-code | field P0 |
| stage-before-apply Prep | gap | preview/apply/discard | claude-code | field P1 |
| jobs strip (non-blocking) | gap | mode switch during analyze | claude-code | field P1 |
| three-column PREP workspace | gap | Yazi grammar | claude-code | after composer |
| AppKit trackpad v1 | gap | KEYMAP twins; native host only | claude-code | task `macbook-trackpad-v1-appkit-gestures` |

---

## B — Product capabilities (from `capability-catalogue.md`)

UI module status in the catalogue is **not** the same as **command-addressable shipped**.
This table is the **buildout queue** for closed loops.

### B1 — Core (Intelligence) — invest first

| cap_id | status | command / surface today | acceptance (target) | next unit |
| --- | --- | --- | --- | --- |
| `cap-copilot-suggestion` | partial | TUI Arrange + EXO tools | fixture rank vs scoring brief | dossier: arrange next-track |
| `cap-harmonic-key` | partial | `library.analyze` + KEY badge | analyze + camelot neighbors | finish scoring in TUI Deck |
| `cap-energy-structure` | gap | sparkline partial | structure/energy in sidecar + judge | analyzer MLX task exists |
| `cap-transition-intelligence` | partial | TUI Deck technique plan | transitions.json + tempo/key gates | fold EXO copilot_why_next |
| `cap-community-signal` | partial | fixtures only | offline chips; no network hot path | Grok sourcing already filed |

### B2 — Supporting (Playback / Mixing / Collection)

| cap_id | status | command / surface today | acceptance (target) | next unit |
| --- | --- | --- | --- | --- |
| `cap-deck-transport` | partial | engine CO; not CLI | engine ctest + KEYMAP | engine bridge dossier |
| `cap-track-identity` | partial | sidecars + TUI | identity sheet + deck load | — |
| `cap-deck-clock` | partial | engine CO | KEYMAP + UI | graphical later |
| `cap-waveform` | gap | TUI heatmap synthetic | Metal path + bench | MTL dossier |
| `cap-hotcues` | partial | `track.cue` notes | CO hotcue + KEYMAP | engine map dossier |
| `cap-loops` | gap | engine only | ctest + KEYMAP | planned |
| `cap-tempo-sync` | partial | engine; onbeat research | phase snap research | onbeat task |
| `cap-onbeat-play` | partial | research locked | default-ON contract | implement wave |
| `cap-mixer-eq` | gap | engine | CO + controller | planned |
| `cap-fx` | gap | engine | CO + KEYMAP | planned |
| `cap-stems` | gap | — | policy + RT-safe | later |
| `cap-library-crates` | partial | `crate.sync` | crate + Collection invariant | — |
| `cap-analysis-prep` | partial | analyze/watch/ingest | quality bar + sidecar | energy deepen |
| `cap-mode-shell` | partial | multi-mode `migx-tui` | KEYMAP TUI section | P0 status/help |

### B3 — Generic (commodity — correct + minimal)

| cap_id | status | notes |
| --- | --- | --- |
| `cap-streaming` | partial | Spotify **identity only**; no dual-stream Automix (anti-identity) |
| `cap-recording` | gap | inherit Mixxx; low priority vs core |
| `cap-broadcast` | gap | inherit; non-modal already noted |
| `cap-controllers-midi` | partial | Mixxx maps; need command receipts |
| `cap-keyboard-shortcuts` | shipped | KEYMAP + lint path |
| `cap-sampler` | gap | later |
| `cap-headphone-cue` | gap | PERFORM graphical |

### B4 — World model (ArcFlow substrate)

| id | status | acceptance | next |
| --- | --- | --- | --- |
| graph load (`mirrors-to-graph`) | partial | full corpus load numbers recorded | pin patched ArcFlow binary |
| distinct playlist counts | **blocked** | task acceptance | `arcflow-distinct-playlist-count-semantics` |
| co-occurrence / centrality rankings | blocked | on distinct-playlist | after task |
| TUI/CLI query commands for graph | gap | `migx graph.*` or query through ArcFlow socket | after rankings honest |
| RT use of ArcFlow | **wont-do** | house physics | never |

---

## C — Prioritised queue (max 2 active implementer dossiers)

Reorder weekly from Strategy + this matrix. **Current recommendation (2026-08-07):**

| # | Unit | Peer | Closed-loop acceptance |
| --- | --- | --- | --- |
| 1 | TUI P0: status line + `?` help | claude-code | snapshot fields + KEYMAP overlay; tests |
| 2 | TUI P1: composer dispatches command IDs | claude-code | `playlist.pull` / `track.show` from composer |
| 3 | ArcFlow distinct-playlist | codex-cli (ArcFlow) + claude later | task acceptance |
| 4 | `migx --agent` + receipt schema | claude-code | JSONL round-trip fixture |
| 5 | Arrange next-track rank (cap-copilot) | claude-code | ng-judge / fixtures |
| 6 | Engine bridge: load free-deck only | claude-code | precondition + receipt |
| 7 | On-beat play default-ON | claude-code | research contract |
| 8 | Trackpad AppKit v1 | claude-code | task `macbook-trackpad-v1-appkit-gestures` |
| 9 | MTL waveform Metal | claude-code | p99 bench vs baseline |
| 10 | Community signal offline enrich | grok→claude | fixtures only hot path |

**Wont-do / anti-identity (do not queue):** silent Automix, dual Spotify multi-deck stream, camera-hand EQ as core, ArcFlow on audio callback, QTouchEvent re-enable as trackpad plan.

---

## D — How an agent uses this matrix (automatic)

```text
1. fed-sync + poll
2. Read matrix §C — pick top unblocked gap with empty owner or assigned peer
3. Compound-before-create: fold into open dossier if scope overlaps
4. Else scaffold dossier: PS with EARS + acceptance check command
5. Claim paths + worktree
6. Waves → pre-commit → targeted ctest/CLI/judge
7. Codex P-08 seal when contract frozen
8. 91-closure harvest → update this matrix status
9. Dream reads seals → may reorder §C
```

**Night long harness pre-flight:** four beats named in dossier `contract.md` / PS; never open-loop “improve TUI.”

---

## E — Maintenance

| Event | Matrix update |
| --- | --- |
| Command lands | §A row → shipped; bump capability count note |
| Dossier seals | matching §B/C row → shipped/partial + link dossier path as prose provenance only |
| Strategy change | re-rank §C; never duplicate Strategy text |
| Weekly retro | §C reorder only if evidence (seals, CI, field) |

**Lint idea (Codex):** optional check that every `shipped` command_id appears in `system.capabilities` and every non-shipped `cap-*` still exists in capability-catalogue.

---

## Revision log

| Date | Change |
| --- | --- |
| 2026-08-07 | Initial matrix: 21 commands, TUI-first commitments, catalogue caps, ArcFlow, top-10 queue |

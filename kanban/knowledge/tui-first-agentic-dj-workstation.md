---
id: tui-first-agentic-dj-workstation
type: knowledge
title: "TUI-first agentic DJ workstation - product and interaction reference"
status: active
owner: gudjon
authored_by: codex-cli
created: "2026-08-07"
lastUpdated: "2026-08-07"
defers_to:
  - kanban/Strategy-Current.md
  - kanban/architecture/decisions/ADR-008-cli-core-two-equal-clients.md
related:
  - kanban/architecture/ddd/bounded-contexts/arch-cli-commands.md
  - kanban/knowledge/headless-sim-ground-truth-agentic-cli.md
  - kanban/knowledge/output-verification-formats-naming.md
  - kanban/planning/00-PORTFOLIO/capability-gap-matrix.md
  - kanban/planning/00-PORTFOLIO/README.md
  - kanban/federation/signal/2026-08-07-full-dj-closed-loop-agentic-buildout.md
  - kanban/federation/signal/2026-08-07-tui-first-dj-workstation-field.md
sources:
  - https://github.com/sxyazi/yazi
  - https://github.com/aristocratos/btop
  - https://lazygit.dev/
  - https://posting.sh/
  - https://zellij.dev/features/
  - https://github.com/wtfutil/wtf
  - https://docs.x.ai/build/overview
  - https://code.claude.com/docs/en/cli-usage
  - https://learn.chatgpt.com/docs/developer-commands?surface=cli
---

# TUI-first agentic DJ workstation

## Product thesis

Migx is built **TUI first**. The primary human product is a rich terminal DJ workstation. The same
application command surface is also available as a conventional CLI, one-shot JSON, and a long-lived
agent protocol so Claude Code, Codex, Grok, scripts, and future agents can operate Migx without GUI
scraping or a private control plane.

This is not a terminal skin over a separate desktop application. The TUI is the first human adapter
over the same command/query/event/capability core that every machine client uses. A later graphical
adapter may exist, but it neither defines nor bypasses the product contract.

Canonical decision: `ADR-008`. Product priority: `kanban/Strategy-Current.md`.

## One core, four adapters

```text
                         application command core
                   command | query | event | capability
                                   |
              +--------------------+--------------------+
              |                    |                    |
        human TUI             CLI / --json       --agent / MCP
     keyboard + mouse       shell + scripts       external agents
```

The external agent supplies intelligence; Migx supplies typed capabilities, state, validation,
sample-accurate execution, and receipts. An embedded model is optional. Claude Code or Codex must be
able to act as the DJ through the public surface without special in-process access.

## Launch contract

| Surface | Intended contract |
| --- | --- |
| `migx` | Start or resume the human TUI workspace |
| `migx <noun>.<verb> ...` | Deterministic human/script CLI command |
| `migx <noun>.<verb> ... --json` | One-shot machine-readable result |
| `migx --agent` | Long-lived JSONL request/event/receipt stream on stdin/stdout |
| `migx mcp-server` | Optional tool adapter over the same command core |

The conventional CLI, `--json` subset, and an interactive stdlib curses TUI exist today. The TUI is
launched by `tools/migx-cli/migx-tui`; it renders Overview, Library, Arrange, Prep, Track, and Deck
modes from a pure snapshot, including selection, analyzed BPM/key/energy, cues, DJ notes, sparklines,
color roles, a full-screen track heatmap, and data-backed transition support. The no-command `migx`
launch, three-column workspace,
`--agent`, events, receipts, MCP adapter, and engine command bridge remain product commitments.

## Interaction synthesis

The reference products contribute distinct behaviors. Copy the principle, not their surface syntax.

| Reference | Migx principle |
| --- | --- |
| Yazi | Three-column context/item/preview navigation; asynchronous work; cancellable jobs; artwork and waveform previews |
| btop | Dense live telemetry, sparklines, heatmaps, fast refresh, keyboard and mouse parity |
| Lazygit | Contextual actions, staged change sets, preview-before-apply, undo/receipt thinking |
| Posting | Capability workbench: structured input, execution, response, and history visible together |
| Zellij / Desktop-TUI | Persistent workspaces, tiled/floating panes, layout presets, focus and resize by mouse or keyboard |
| WTFutil | Composable dashboard grids and user-selectable workspace presets |
| Claude Code / Codex / Grok | Composer, streamed activity, resumable sessions, interruptible jobs, approvals, discoverable commands |

## Default PREP workspace

```text
+ MIGX - Friday Residency - PREP - LIVE - LIBRARY - JOBS ----------------+
| Sources              | Tracks                         | Inspector       |
|                      |                                |                 |
| > Spotify            |  #  Key  BPM  Title            | artwork         |
|   Liked Songs        | 01  8A   126  Blue Monday     | waveform        |
|   Friday Set         | 02  9A   127  Feel It         | quality / ISRC  |
| > Local              | 03  9B   128  Strings of Life | resolution      |
|   Collection         |                                | crate position  |
+----------------------+--------------------------------+-----------------+
| Jobs  ok mirror 84  running resolve 71/84  8 missing  5 upgrades      |
+------------------------------------------------------------------------+
| migx > @playlist:Friday stage unresolved tracks for acquisition       |
+ PREVIEW | Spotify linked | Collection healthy | 2 jobs | ? help ------+
```

The three central columns are stable: **context -> items -> inspection**. Workspace presets change
their contents, not the navigation grammar:

- `PREP`: playlists, tracks, quality, resolution, ingest, and staged changes.
- `LIVE`: deck state, queue, phase/BPM, levels, engine health, and agent activity.
- `LIBRARY`: collection, crates, analysis, duplicates, tags, and provenance.
- `MIRROR`: remote identities, snapshots, coverage, missing tracks, and upgrades.
- `JOBS`: scans, analysis, resolver work, ingest, failures, cancellation, and receipts.

Floating panes are for short-lived focus: command palette, track comparison, conflict resolution,
job detail, help, and approval. They must not become blocking modal failure paths during a live set.

## Composer and direct manipulation

The composer accepts deterministic command IDs and, when an external or embedded agent is attached,
natural-language intent. Selection references use stable entities rather than screen coordinates:

```text
@playlist:Friday pull and resolve against @collection
@track:isrc:GB... stage for Deck 2 at the next 16-bar boundary
```

Mouse and keyboard are equal input methods. Direct actions, command-palette actions, natural-language
intent, CLI calls, and agent calls all resolve to the same command handler. No adapter may become a
second writer.

## Stage before apply

Destructive or multi-item preparation work is represented as a reviewable change set:

```text
Proposed changes
  + ingest 12 files
  + create crate "Friday Residency"
  ~ replace 5 below-bar files
  ! 8 tracks unresolved

[p] Preview    [a] Apply    [x] Discard
```

Live actions use preconditions rather than a filesystem-style diff, but still return a receipt. For
example, loading a track may require `deck=free`; an agent cannot silently replace a playing deck.

## Agent operating modes

| Mode | Authority |
| --- | --- |
| Observe | Queries, capability discovery, and event subscriptions only |
| Prepare | Library, crate, cue, tag, analysis, and transition-plan changes with preview/receipt |
| Perform | Guarded deck/mixer intents with explicit arming and preconditions |
| Autonomous | Policy-bounded agent operation with persistent human override and complete receipts |

Autonomous does not mean opaque Automix. The agent explains decisions, Migx validates them, the
human can interrupt, and playback continues safely if the agent disconnects.

## Real-time boundary

Agents decide on musical timescales: select a track, plan a transition, or schedule an intent for a
beat/bar boundary. Migx performs sample-accurate execution. Agents and adapters never run per audio
buffer, write ControlObjects directly, or block the callback. The application handler remains the
single writer (`P-06`); commands cross to the engine through the sanctioned lock-free boundary.

## Product sequence

1. Grow the shipped multi-mode curses TUI into the three-column PREP workspace, with session and job
   receipts.
2. `--agent` JSONL discovery, request, event, completion, cancellation, and record/replay contract.
3. Deterministic two-deck simulation that external agents can drive and verify.
4. Guarded load/cue/play/schedule/crossfade command surface against simulation.
5. Single-writer application bridge to the real engine plus live telemetry.
6. Policy-bounded autonomous DJ operation with immediate human takeover.

This sequence makes the TUI and agent surface first-class now while retaining simulation as the gate
for live engine authority.

## Framework constraint

The command core stays independently usable and dependency-light. A TUI framework dependency, image
protocol, or renderer belongs to the TUI adapter and must not become required for CLI/JSON/agent use.
Choose the implementation framework from a measured prototype; do not let a framework choice redefine
the public command and event contracts.

## Non-goals

- A graphical app with a terminal-themed companion.
- Separate human and agent command implementations.
- GUI scraping by agents.
- Natural language as the only control surface.
- An agent or TUI loop on the real-time audio thread.
- Opaque consumer Automix with no intent, explanation, receipt, or takeover.

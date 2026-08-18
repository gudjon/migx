---
id: capability-gap-matrix
type: portfolio
title: "Capability gap matrix — closed-loop product buildout SSoT"
status: active
owner: gudjon
authored_by: grok-signal
created: "2026-08-07"
lastUpdated: "2026-08-18"
defers_to:
  - kanban/architecture/ddd/capability-catalogue.md
  - kanban/architecture/decisions/ADR-008-cli-core-two-equal-clients.md
  - kanban/knowledge/tui-first-agentic-dj-workstation.md
  - kanban/Strategy-Current.md
  - kanban/AGENTS.md
related:
  - kanban/knowledge/arcflow-tui-agentic-dj-integration.md
  - kanban/tasks/arcflow-distinct-playlist-count-semantics.md
  - kanban/tasks/arcflow-bounded-graph-query-cli.md
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

## A — Command surface (live `system.capabilities`, 35 rows)

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
| `library.ingest` | command | shipped | Collection path + quality gate; copies cover to cover.* | — |
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
| `library.covers` | command | shipped | backfill cover.* from thumbs + APIC | run once after mass ingest |
| `set.plan` | query | shipped | deterministic pair scoring | improve optimizer after evidence |
| `set.play` | command | partial | offline preview render | replace with live native transport |
| `track.feedback` | command | shipped | append-only structured verdict | — |
| `session.now` | query | shipped | live-status schema + unreachable distinction | — |
| `session.bind` | command | shipped | `_live.json` + session log | — |
| `session.room` | command | shipped | session-local room state | — |
| `session.clear` | command | shipped | unbind while retaining log | — |
| `session.show` | query | shipped | reconstruct append-only night log | — |
| `library.suspects` | query | shipped | analysis review queue | — |
| `library.pairs` | query | shipped | observed transitions from session evidence | — |
| `library.vocab` | query | shipped | vocabulary packs + drift report | — |
| `graph.rank` | query | shipped | native distinct-playlist fixtures + live corpus | add snapshot/rebuild gate |
| `system.capabilities` | capability | shipped | 35 rows | grow only with command land |

### A2 — Surface commitments (TUI-first, not yet commands)

| commitment | status | acceptance | peer | next |
| --- | --- | --- | --- | --- |
| `migx` no-arg → TUI workspace | gap | launch opens TUI | claude-code | small task |
| `migx --json` everywhere | shipped | all queries emit JSON | claude-code | audited 2026-08-08: 25/25 |
| `migx --agent` JSONL | gap | request/event/receipt stream | claude-code | dossier |
| events / receipts | gap | schema + one LIVE path | claude-code | after --agent |
| `migx mcp-server` | wont-do | — | — | see MCP note below |
| engine command bridge | gap | guarded perform intents | claude-code | LIVE preconditions |
| composer in TUI | partial | `:` opens it, stages against the live manifest; apply (running argv) remains | claude-code | field P1 |
| TUI status line + `?` help | shipped | drawn by run(); `?` toggles KEYMAP overlay | claude-code | 2026-08-08 |
| stage-before-apply Prep | partial | Prep pane renders the stage; apply/discard keys remain | claude-code | field P1 |
| live deck driver (livesession -> TUI tick) | shipped | `p` starts/stops; tick() on redraw timeout; Deck pane shows it | claude-code | 2026-08-10 |
| jobs strip (non-blocking) | gap | mode switch during analyze | claude-code | field P1 |
| three-column PREP workspace | gap | Yazi grammar | claude-code | after composer |
| AppKit trackpad v1 | gap | KEYMAP twins; native host only | claude-code | task `macbook-trackpad-v1-appkit-gestures` |
| `session.now` / `session.bind` / `session.clear` | shipped | `_live.json` off-RT | claude-code | — |
| `session.room` | shipped | theme/energy/note on `_live.json` | claude-code | — |
| `session.show` | shipped | `_session.jsonl` → plays[] + events[] | claude-code | night reconstruct |
| `track.feedback` (+ `now`) | shipped | sidecar + night log; verdict biases rank | claude-code | set.plan + Arrange |
| Session coach skill (speech→CLI) | shipped | `.claude/skills/migx-session-coach/` | claude-code | dogfood voice→flags |
| Engine-driven live position in `_live.json` | gap | app writes playposition off-RT | claude-code | later engine bridge |
| Session lock (one live session / OS user) | gap | lockfile; stale detectable | claude-code | before multi-writer hooks |
| `session/now.json` + `history.jsonl` | gap | level-triggered truth; atomic off-RT | claude-code | agent filesystem hooks |
| Hooks (TrackPlaying / Transition*/ Session*) | gap | command + JSON stdin + timeout | claude-code | **after** now.json; never RT |

### Program — Swift TUI workstation (ADR-011 proposed, 2026-08-18)

`initiative-swift-tui-workstation`. Max two active. Order is **Wave 0 → HRN → AUD**; `STO` starts when
the music volume is mounted; `SWF` is deliberately late; `IDX` last and may shrink.

| # | Unit | Peer | Acceptance (machine-checkable) |
| --- | --- | --- | --- |
| — | Wave 0 MAP | grok or claude | 17/17 cards carry `side:`; partition lint reports the **count** of pre-existing `src/engine/**` → `library/` includes and fails only on increase |
| — | HRN harness | claude-code | every command carries a permission class; a write outside the workspace is refused, not warned; `--resume` reconstructs a night from `_session.jsonl`; live `deck.*` cannot be auto-approved |
| — | AUD audio core | claude-code | per-deck gain moves audibly while both decks play; **100 consecutive** on-beat starts within one buffer; `ffplay` + `player.py` deleted (`P-11`); p99/max vs pinned baseline, zero underruns |
| — | STO collection | claude-code | `library.dedupe` exit 0 after apply; crate entries `samefile()` Collection; `--apply` requires the dry-run receipt hash; crates need APFS, a **pack to exFAT copies deliberately** and reports bytes |
| — | SWF Swift port | claude-code | `parity-check.sh` green for every ported ID; no second session store; the Python path is **deleted** for anything Swift now serves |
| — | IDX indexes | claude-code | rebuild fixtures **plus the negative case**: delete a cue from a sidecar, rebuild, confirm it is gone from SQLite |

| — | VIS visual compositor | claude-code | wall samples lock-free taps only; zero engine calls from the render path; killing the renderer does not interrupt playback (`P-21`) |
| — | lyrics producer (VIS) | claude-code | prep-time subprocess; timestamped `lyrics.json`; inferred fields carry provenance + confidence and are checked against the vocab pack |
| — | transition audio (`kind: sfx`) | claude-code | staged never auto-fired; excluded from next-track candidates; `fits_after`/bars in sidecar; plays as a third node |

**VIS comes after AUD** — a compositor needs a real playhead to subscribe to, and there is not one yet.
Designing it against a clock that does not exist is how you get a spec nobody can implement.

**Killed by ADR-011:** `EPL` (peel Qt off `process()`) and `BRG` (unpark EngineBridge). Both presuppose
a Qt engine on the booth path.

**Why HRN first:** it is the only piece that does not exist at all — no permission class, no workspace
boundary, no sandbox — and it needs neither the music volume nor audio, so it can start today.

**Acceptance discipline:** every row above is written so a weaker version could not pass by accident.
"Lint exits 0" is a tautology (you write the lint, then it passes); "ctest green" cannot detect a
timing fix, because the known engine race passes 3 runs in 5 and passes every time under a debugger.

### MCP is a non-goal (decided 2026-08-08)

`migx mcp-server` moves from `gap` to `wont-do`. Not "not yet" — **the adapter is the binary we
already ship.**

`ADR-008` makes the command surface the spine, so an MCP server could only ever be a wrapper over the
same command IDs: a second protocol, a second process to fail, and a second place for the surface to
drift out of sync with `system.capabilities`. That is a parallel implementation of an interface we
already have (`P-11`), bought for no capability we lack.

A coding agent integrates as a **shell client**, which is how these workflows actually run:

```text
migx <noun.verb> … --json   →   stdout: structured receipt   →   agent reads, plans, calls next
```

No registry, no handshake, no long-lived local server sitting on the library. The five things an
agent needs from us are all properties of the CLI, and all now hold:

| Need | State |
| --- | --- |
| Stable command IDs | `system.capabilities` is the manifest, lint-enforced against the DDD vocabulary |
| `--json` on every useful path | **25/25 commands**, audited 2026-08-08 |
| Discovery without "list tools" | `system.capabilities --json` |
| Exit codes usable as gates | `0` ok · `1` findings (e.g. `library.dedupe`) · `2` usage |
| Receipt-shaped, idempotent output | every command emits a versioned `migx.*/1` schema |

Cards in an IDE, if ever wanted, are thin views over that JSON — not embedded DJ chrome.

**Revisit only if** a host appears that we must support and it speaks *only* MCP. Fashion in the
wider ecosystem is not that trigger; `migx --agent` (a long-lived JSONL stream on stdin/stdout,
still direct CLI) covers the multi-turn case without adopting a protocol.

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
| graph load (`mirrors-to-graph`) | shipped | 83 mirrors / 6,765 nodes / 9,483 relationships on pinned runtime | prove rebuild equivalence |
| distinct playlist counts | shipped | native GQL + independent 4,300-membership reference | — |
| track / artist centrality | shipped | `graph.rank` bounded CLI + JSON | add co-occurrence query only when product-used |
| TUI graph inspector | gap | same command result rendered with evidence | after Swift command parity |
| snapshot export / rebuild | gap | restored/rebuilt store returns identical semantic ranking | ArcFlow sync snapshot filename mismatch is open |
| RT use of ArcFlow | **wont-do** | house physics | never |

---

## C — Prioritised queue (max 2 active implementer dossiers)

Reorder weekly from Strategy + this matrix. **Current recommendation (2026-08-07):**

| # | Unit | Peer | Closed-loop acceptance |
| --- | --- | --- | --- |
| 1 | TUI P0: status line + `?` help | claude-code | snapshot fields + KEYMAP overlay; tests |
| 2 | TUI P1: composer dispatches command IDs | claude-code | `playlist.pull` / `track.show` from composer |
| 3 | ArcFlow bounded graph rank | codex-cli | **shipped** `graph.rank` CLI/JSON; snapshot/rebuild remains |
| 4 | `migx --agent` + receipt schema | claude-code | JSONL round-trip fixture |
| 5 | Arrange next-track rank (cap-copilot) | claude-code | ng-judge / fixtures |
| 6 | Engine bridge: load free-deck only | claude-code | precondition + receipt |
| 7 | On-beat play default-ON | claude-code | research contract |
| 8 | Trackpad AppKit v1 | claude-code | task `macbook-trackpad-v1-appkit-gestures` |
| 9 | MTL waveform Metal | claude-code | p99 bench vs baseline |
| 10 | Community signal offline enrich | grok→claude | fixtures only hot path |
| 11 | Session coach v0 (skill + track.note/cue) | claude-code | **shipped** speech→sidecar bound to selected track |
| 12 | `session.now` / `_live.json` + `session.show` | claude-code | **shipped** file id + night log; engine position still gap |

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

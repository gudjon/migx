---
id: session-coaching-multimodal-agent
type: knowledge
title: "Session coaching — multimodal agent interface while Migx plays"
status: draft
owner: gudjon
authored_by: grok-signal
created: "2026-08-08"
lastUpdated: "2026-08-08"
defers_to:
  - kanban/Strategy-Current.md
  - kanban/architecture/decisions/ADR-008-cli-core-two-equal-clients.md
  - kanban/knowledge/tui-first-agentic-dj-workstation.md
  - kanban/knowledge/world-model-experience-ontology.md
  - kanban/AGENTS.md
related:
  - kanban/federation/signal/2026-08-08-multimodal-session-coaching-x.md
  - kanban/planning/00-PORTFOLIO/capability-gap-matrix.md
  - kanban/knowledge/arrange-nexttrack-copilot-scoring.md
  - kanban/architecture/decisions/ADR-005-open-core-plus-proprietary-intelligence.md
note: >
  Product research: continuous human feedback (voice/chat/keys/trackpad) bound to
  the currently playing track identity, captured as durable session/track memory.
  CLI-direct agent surface preferred over MCP. Co-pilot / learn — never silent Automix.
---

# Session coaching — multimodal agent while Migx plays

## One sentence

While a track is playing (known file / ISRC / path identity), the DJ talks or types
to a coding agent (Claude Code, Codex, Grok, Cursor) that **listens, structures
feedback, and writes learning into Migx** via **CLI commands** — without taking
over the mix and without requiring MCP.

## Why this is the product (not a gimmick)

| Booth reality | Agent role |
| --- | --- |
| Hands on faders / trackpad / keys | **Direct manipulation** for time-critical perform |
| Mouth free, ears full | **Voice** for continuous judgment (“this feels outdated”) |
| Eyes on crowd + waveform | **Glanceable TUI** + occasional chat when useful |
| Learning compounds across nights | Feedback becomes **sidecar / session ontology / scoring priors** |

This is **co-pilot learning**, not “AI DJs for you.” Field and Strategy already reject
silent Automix; the human remains the author of the set. The agent multiplies
**memory and next-prep intelligence**.

---

## Field: future of UI with AI (X, 2025–2026)

Durable patterns from recent X discussion (detail + links in companion signal):

1. **Modal pluralism** — voice is primary in some contexts (driving, ambient, alone-at-desk)
   but **lossy and non-scannable** for complex spatial work; keyboard/mouse still win for
   precise pointing. AI is the **adapter layer under** modalities, not a replacement for all of them.
2. **Simultaneous voice + text** — multimodal conversational agents (talk and type in one session).
3. **Voice to steer coding agents** — “talk, kick off task / unblock stuck agent” aimed at
   Claude Code / Codex / Cursor users (dictation → agent task).
4. **Pushback on pure voice-for-GUI** — serializing “scroll to third paragraph and bold”
   is higher load than pointing; voice re-expands what GUI collapsed.
5. **DJ culture on AI setlists** — strong anti-signal: auto-setlist tools are mocked;
   “AI multiplies the set, human drives the mix” is the acceptable frame.

**Implication for Migx:**  
Use **voice for continuous judgment**, **trackpad/keys for perform**, **CLI for durable
writes**, **TUI for state**. Never make voice the only way to ride EQ.

---

## Interaction model (four channels, one intent bus)

```text
┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Voice (STT)  │  │ Chat (agent) │  │ Keyboard     │  │ Trackpad     │
│ continuous   │  │ Claude/Codex │  │ KEYMAP / TUI │  │ zoom/mode †  │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                 │                 │
       └────────────┬────┴────────┬────────┴────────┬────────┘
                    ▼             ▼                 ▼
              Intent / feedback (structured)
                    │
                    ▼
         migx CLI  (library.*, track.*, session.*)  --json
                    │
         ┌──────────┼──────────┐
         ▼          ▼          ▼
    sidecar     session     scoring /
    notes/cues  ontology    ArcFlow later
```

**Preferred stack (owner preference):** coding agent runs **shell → `migx … --json`**.  
No MCP required. Optional later: `migx --agent` JSONL stream still CLI-direct.

---

## Context binding: “what is playing right now”

The agent must always know **which identity** feedback attaches to.

| Source | Content |
| --- | --- |
| Engine / app | deck group, playposition, loaded path |
| CLI query (target) | `deck.now` / `session.now` → `{path, isrc, title, artists, position_s, deck}` |
| Sidecar | notes, tags, cues, energy |
| Session log | ordered plays this night + transitions |

**Minimum viable binding (no engine bridge yet):**

1. Human or TUI selects track / agent reads last `library.analyze` / Deck A path from config.  
2. Or agent runs a future **`session.now --json`** that reads a small status file the app writes
   off-RT (atomic JSON sidecar: `~/.migx/live-status.json` or library root `_live.json`).

**Hard rule:** status file is **written by Migx**, read by agents. Agents never poke the audio
callback.

---

## Feedback vocabulary (what you said, as durable types)

Map free speech into **typed feedback events** so learning is queryable.

| Utterance (example) | Typed event | Write target |
| --- | --- | --- |
| “this song worked” | `fit: worked` + confidence | track sidecar tag / score |
| “feels outdated / not again” | `fit: retire` or `fit: skip` | tag `outdated` / `do-not-play` |
| “cutoff was good at 1:30” | cue / preference | `track.cue` or cue quality flag |
| “use shorter part next time” | `use: loop_region` / duration bias | sidecar `play_prefs` |
| “longer stretch next time” | `use: extend` | same |
| “better later in the night” | `placement: late` / energy band | session ontology + track tags |
| “crowd is more melodic now” | `room: theme` | **session** state, not track forever |
| “last transition was weak — try echo next time” | `transition: technique` + from/to | transition memory / EXO |
| “SFX in the next no-vocal gap” | `fx: suggest` + position | cue type `sfx` / note |
| “next few need higher energy” | `queue: energy_up` | arrange / next-track prior |
| “volume / EQ pull the lows” | `mix: eq_note` | ephemeral session note or deck checklist |

**CLI-shaped commands (target surface — not all exist yet):**

```text
migx session.now --json
migx session.note --text "..." --bind now
migx track.feedback <track> --fit worked|retire|weak --note "..."
migx track.cue <track> <at> "mix out — keep this"
migx track.note <track> --tag outdated --note "felt tired on floor"
migx session.room --theme melodic --energy mid
migx transition.feedback --from A --to B --verdict weak --prefer echo-out
```

Existing today: `track.note`, `track.cue`, `track.show`, library/analyze — enough for a **v0 dogfood**
where the coding agent maps speech → these commands.

---

## Modes of the agent (authority)

Align with TUI-first agent modes:

| Mode | Agent may | Agent must not |
| --- | --- | --- |
| **Observe** | Read `session.now`, sidecars, gaps | Change audio |
| **Coach / Learn** | Write notes, tags, cues, session log | Load decks, move faders |
| **Prepare** | Re-rank next candidates, stage crates | Silent auto-load |
| **Perform (armed)** | Propose load/EQ with explicit arming | Unsolicited transport |

Live coaching is **Observe + Coach** by default. Perform stays human + KEYMAP/controller.

---

## Multimodal UI while playing (practical booth)

| Channel | Best for | Bad for |
| --- | --- | --- |
| **Voice** | Continuous judgment, room read, “next energy” | Precise waveform scrub, exact dB |
| **Keyboard** | Hotcues, mode switch, confirm load | Long essays mid-phrase |
| **Trackpad** | Zoom, list fling, mode cycle (native host †) | Continuous fader (use hardware) |
| **Chat to coding agent** | After phrase / between transitions | Competing with full attention on drop |
| **TUI** | Now/next, heatmap, transition plan, cover | Replacing CDJs |

**Booth recipe:** voice → agent structures → CLI writes memory; hands stay on mixer;
glance TUI for confirmation.

---

## Learning loop (closed loop)

```text
Trigger   →  track plays (identity known)
Capture   →  voice/chat feedback + position_s + room tags
Intelligence → agent maps to typed events; updates scores/prefs
Adjustment → next arrange rank, cues, do-not-play, transition priors
Re-check  →  next time track is candidate, prefs visible in TUI/CLI
```

Harvest at night (Dream / session end): cluster “retire” tags, transition technique stats,
energy placement — into living scoring (`arrange-nexttrack-copilot-scoring`) not only chat logs.

---

## Implementation waves (capability-matrix friendly)

| Wave | Deliverable | Acceptance |
| --- | --- | --- |
| **0 dogfood** | Coding agent skill: “bind feedback to selected track via `track.note`/`track.cue`” | Manual: play → speak → agent writes sidecar |
| **1 live status** | Migx writes `_live.json` / `session.now` off-RT | CLI shows path+ISRC+position |
| **2 session log** | Append-only play + feedback events | `session.show` reconstructs night |
| **3 typed feedback CLI** | `track.feedback` / `session.room` | JSON schema + tests |
| **4 voice I/O** | STT into agent (host OS / Whisper / agent voice mode) | Latency OK between phrases |
| **5 arrange priors** | Feedback adjusts next-track rank | Fixture + offline judge |
| **6 optional perform proposals** | Armed only | Free-deck precondition |

**Wont-do:** MCP-required path; agent Automix; RT thread listening to STT; voice-only EQ.

---

## Relationship to coding agents

You stay in **Claude Code / Codex / Cursor** as the conversation surface:

1. Migx plays (or TUI shows Deck).  
2. Agent session has shell access to `migx`.  
3. You talk (voice→text) or type: “this feels outdated, don’t use again.”  
4. Agent runs `migx track.note … --tag outdated` (and/or future `track.feedback`).  
5. Next prep, arrange scoring / filters respect tags.

No second chat product required for v0 — the **coding agent is the session coach UI**.

---

## Open research questions

- Voice latency vs phrase boundaries (talk between 8-bar marks, not mid-drop).  
- Privacy of room commentary on disk (session logs local-first).  
- How hard to bind “current file id” without full engine bridge (`_live.json` first).  
- Separating **session-local** room theme from **lifetime** track quality judgments.  
- Multi-deck: feedback default to Master / active deck / explicit “deck B”.

---

## Anti-patterns

| Pattern | Why avoid |
| --- | --- |
| Auto-setlist from prompt only | Field rejects “AI does the set for you” |
| Voice replaces faders | Spatial mix is pointing work |
| Chat log as only memory | Not queryable; not closed-loop |
| MCP as gate | Owner prefers fast CLI |
| Agent writes CO from speech | P-06 / RT safety |

---

## Next docs / tasks

- Signal (X detail): `kanban/federation/signal/2026-08-08-multimodal-session-coaching-x.md`  
- Matrix rows: `session.now`, `track.feedback`, `session.room` (gap)  
- Skill for Claude: “session coach — map speech to migx track.note/cue”  

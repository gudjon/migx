---
id: ADR-009
type: decision
title: "CLI/TUI implementation language - Swift arm64, Python sunset on the booth path"
status: accepted
owner: gudjon
created: "2026-08-08"
lastUpdated: "2026-08-08"
supersedes: []
amends: [ADR-008]
related: [ADR-002, ADR-006, ADR-008, arch-cli-commands, P-02, P-11, P-34, swift-native-cli-direction]
---

# ADR-009 - CLI/TUI implementation language

**Status: accepted. Lane A, decided by Gudjon 2026-08-08.**

## Context
`migx-cli` is ~10k lines of stdlib-only Python: 33 commands, `--json` on all of them, a curses TUI,
a green offline suite. That choice optimised for zero install friction and it worked - it is why
there is a working command spine, a closed feedback loop, and an installer at all.

But `ADR-006` targets **macOS 26+ / Apple Silicon only**. There is no portable story to protect, so
Python's main advantage buys nothing here. Worse, it has started costing correctness: the claim that
a live crossfader was unachievable was **wrong**, and it was wrong because the question got framed as
*"what can stdlib Python shell out to"* instead of *"what does this platform offer"*. `afplay` cannot
seek, pitch or fade; `AVAudioEngine` can do all three plus per-deck gain, `AVAudioUnitTimePitch`,
sample-accurate scheduling and metering taps. The ceiling was in the runtime, not the platform.

Python in Migx is an accident of fast CLI glue, not a house-physics requirement.

## Decision
**The booth path becomes native; Python sunsets there.** Specifically:

- **The command contract is permanent; the runtime is not.** `ADR-008` binds command IDs, `--json`
  and exit codes - never an implementation language. An agent running `migx session.now --json`
  cannot tell which language answered, which is exactly what makes this migration safe.
- **The engine stays C++/Qt** (`ADR-002`). Swift is not a third engine language and must not leak
  into the RT graph.
- **Audio transport goes native first**, because it is the one piece Python genuinely blocks.
- **Filesystem SSoT is unchanged and language-agnostic**: `Collection/`, sidecars, `.migx` packages,
  the state dir, the session lock.

### Lane A - chosen
`migx` becomes a **Swift arm64 binary**; the live deck is **AVAudioEngine**; it reaches the C++ engine
over `engine.sock` when the full graph is up. The engine itself stays C++/Qt.

    migx (Swift binary on PATH)
      ├── commands   set.plan · session.* · track.feedback · research.*
      ├── TUI        Swift terminal host
      ├── live deck  AVAudioEngine player nodes: seek, time-pitch, real per-deck gain
      └── engine.sock → the existing C++ bridge

Accepted cost: **a third toolchain** alongside CMake and the Python being retired. Lane B (all C++)
was the alternative and would have kept one toolchain at the price of OAuth/JSONL ergonomics.

The decisive argument is the deck. Lane A reaches `AVAudioEngine` directly, which removes the false
ceiling this whole ADR exists to correct - subprocess players cannot give per-deck gain, so a real
crossfader was impossible in the current runtime and is straightforward in the chosen one.

## Migration order (no big-bang)
1. Freeze the contract - `system.capabilities` is the SSoT to port against
2. Swift `migx` stub: `config.show` + `session.now`, reading the **same files**
3. Port `session.*` + `track.feedback` - highest agent value, pure filesystem
4. Port `set.plan` scoring
5. Swift TUI + AVAudioEngine dual deck, **replacing** `player.py`
6. Spotify/Last.fm clients last
7. Delete `tools/migx-cli` when the booth path is at parity

Deliberately **not** first: the research harness and Spotify clients. They are the least
product-critical and the most work.

## Consequences
- Two runtimes during migration. That is a real cost and the reason for a schedule, not a vibe.
- `player.py`'s ffplay backend is **scaffolding to replace**, already labelled as such. Replacing it
  means deleting it - a Swift deck alongside a subprocess deck would be two audio paths (`P-11`).
- The stdlib-only constraint for `tools/` becomes irrelevant once the binary is compiled.

## What must not break
1. `ADR-008` command IDs, `--json`, exit codes (`0` ok / `1` findings / `2` usage)
2. Filesystem SSoT - sidecars, packages, session state
3. House physics - `P-02` holds for anything touching the real engine graph. A separate Swift player
   process for TUI dogfood is acceptable **only** while it is clearly not "the engine".
4. One session per OS user - the lock discipline stays
5. Agents integrate by shell only; no import surface in any language

**Migration test:** Claude Code still coaches via `migx track.feedback` after the rewrite, unchanged.

---
id: swift-native-cli-direction
type: task
title: "Language direction — Swift-native for macOS 26+, and what that means for migx-cli"
status: open
owner: gudjon
priority: high
initiative: initiative-ai-djing-product
authored_by: claude-code
authored_kind: agent
triggered_by: "Gudjon, 2026-08-08: 'I don't like Python' and 'we are focused on
  Apple Silicon / macOS 26+', immediately after the AVAudioEngine correction"
created: "2026-08-08"
lastUpdated: "2026-08-08"
---

# Swift-native direction

## The signal
Two statements, one direction: **Python is not the language this should be written in**, and the
target is **Apple Silicon / macOS 26+** (`ADR-006`). Those agree. `migx-cli` being stdlib-only Python
was a decision optimised for *zero install friction*, and it has been quietly costing correctness —
the live-crossfader claim was wrong precisely because the question was framed as "what can stdlib
Python shell out to" instead of "what does this platform offer".

## What is true today
~30 Python modules under `tools/migx-cli/`: 33 commands, `--json` on all of them, a curses TUI, an
offline test suite that is green. It works, it is tested, and it is shipped. That is the honest
starting position, not a strawman to knock down.

## The recommendation: migrate at the seam, do not rewrite
A full Swift rewrite of working, tested, shipped code is **motion, not progress** — it would spend
weeks re-earning behaviour that already exists, and every day of it the product gains nothing.

The seam is obvious, and one piece is *already blocked*:

| Piece | Language | Why |
| --- | --- | --- |
| **Audio transport** | **Swift, now** | Blocked on Python today. AVAudioEngine gives real faders, seek, `AVAudioUnitTimePitch`, sample-accurate on-beat starts, metering taps. Nothing in Python reaches this without a bridge. |
| New commands | Swift, going forward | swift-argument-parser; no new Python surface |
| Existing 33 commands | Python until replaced | They work and are gated; port only when one is touched anyway |
| The engine | C++/Qt, unchanged | `ADR-002`; Swift is not a third engine language |

**The contract is what makes this safe.** `system.capabilities` + `--json` + exit codes already define
the surface (`ADR-008`), so an agent cannot tell which language answered. A command can be ported one
at a time behind that contract with the same tests pointed at the binary. That is exactly why the
CLI-as-spine decision holds up: it makes the implementation language an *internal* detail.

## Do first
The Swift audio helper — line-delimited JSON on stdin/stdout, the same protocol `engine.py` already
defines and tests. It is the piece Python cannot do, it collapses the TUI transport and the engine
bridge into one contract, and it is the smallest useful Swift beachhead.

## Do not
- Do not rewrite the working Python for tidiness while the audio path is still missing.
- Do not add a *second* audio path in Swift alongside `player.py`'s ffplay backend — that backend is
  already labelled scaffolding to replace, and replacing means deleting it.
- Do not let Swift leak into the engine; `ADR-002` keeps that C++/Qt.

## Settled
`ADR-009` accepted 2026-08-08, **Lane A**: Swift arm64 CLI/TUI with an AVAudioEngine deck, C++
engine unchanged. The stdlib-only constraint for `tools/` is retired with the Python it constrained.
This card is now the working notes; the decision lives in the ADR.

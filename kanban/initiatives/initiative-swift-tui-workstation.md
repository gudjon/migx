---
id: initiative-swift-tui-workstation
type: initiative
status: active
title: "Migx as a Swift TUI workstation — harness first, Qt out"
owner: gudjon
dossier: []                # HRN/AUD/STO/SWF/IDX link here as they open
depends_on: [ADR-011]
blocks: []
pm_overlay:
  hypothesis: "If the product is a harness (permissions, sandbox, transcript, tools, skills) around a small native audio core and a filesystem library, then a DJ and an agent can drive the same night through one surface, because the thing that makes an agent safe and a DJ fast is the same thing: typed tools over inspectable files."
  primary_metric: "every action a human or agent takes is a typed tool call with a receipt, gated by a permission class — zero paths that mutate the library or a deck outside that table"
  guardrail: "the model never writes a fader (deck.* stays human-gated live); nothing added to the audio deadline (P-02); no second command core, no second library, no second audio engine (P-11)"
  validation: "per-dossier acceptance below; skill behaviour pinned by golden fixtures, not judgement"
---

# Swift TUI workstation

Thin initiative. Substance lives in `ADR-011` and the dossiers; this file exists to hold the bet and
point at them.

## Program

    Wave 0  MAP task   ADR-011 accepted · corrected src/ side: · partition lint
    HRN     dossier    the harness: permission classes · sandbox · transcript/resume
    AUD     dossier    AVAudioEngine core; ffplay + player.py deleted
    STO     dossier    Collection adopt · package · USB pack
    SWF     dossier    TUI + command core ported to Swift
    IDX     dossier    derived indexes rebuildable (last)

Max two active. **Order: Wave 0 → HRN → AUD**, with `STO` the moment the music volume is mounted.
`SWF` is deliberately **late** — porting a TUI whose shape is still moving is the most wasteful
possible order. `IDX` is last and may shrink: traversal starts as `pairs.jsonl` + `rg`, and a graph
store is added only when a skill eval proves grep too slow.

## Why HRN first

It is the piece that does not exist at all. Today every command can do anything: there is no permission
class, no workspace boundary, no sandbox. `library.ingest` and a hypothetical `deck.load` are equally
unguarded. That is the gap an agent-operated product cannot ship with, and it needs no music volume and
no audio — so it is also the one that can start today.

## Halt conditions

Each dossier seals `met`/`partial` with its acceptance cited, or **halts honestly** with a named
successor and a re-fire condition. A dossier that cannot meet acceptance does not lower it.

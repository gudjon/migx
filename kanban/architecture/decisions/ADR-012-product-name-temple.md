---
id: ADR-012
type: decision
title: "Temple is the next-generation product; Migx is the generation it succeeds"
status: accepted
owner: gudjon
created: "2026-08-18"
lastUpdated: "2026-08-18"
supersedes: []
amends: [ADR-011]
related: [ADR-002, ADR-008, ADR-009, P-11, P-34]
---

# ADR-012 — Temple is the next generation

## Decision

**Temple** is the next-generation product. `temple` on PATH. **Migx** is the generation it succeeds —
the Mixxx fork with the Python command core and the Qt engine.

That is a succession, not a rename, and the distinction matters mechanically: there is no window in
which one program answers to two names. Migx is what runs today; Temple is what `ADR-011` describes.

**Theme:** the Burning Man temple and the Tomorrowland mainstage — *the wall and the quiet in the
drop*. It holds DJ and VJ in one word without subordinating either, which no compound name managed:
a temple **is** the structure and the sound inside it. Grave, short, unambiguous in a terminal.

## Why a name is an architecture decision

A product name looks like branding and behaves like a path. It binds:

| Surface | Value |
| --- | --- |
| binary on PATH | `temple` |
| config | `~/.config/temple/config.json` |
| state · lock · transcript | `~/Library/Application Support/Temple/` |
| emitted schemas | `temple.set-plan/1`, `temple.taps/1`, `temple.intent/1` … |
| command IDs | **unchanged** — `library.ingest`, `set.plan` (`ADR-008` binds nouns, not the brand) |

Command IDs are deliberately untouched. `ADR-008` binds `noun.verb`, `--json` and exit codes; the
brand was never part of that contract, which is why an agent script survives the rename.

## The library outlives the generation — and that is the proof

Because Temple succeeds Migx rather than renaming it, the interesting question is not "what do we
rebrand" but **"what survives the change of program"** — and the answer is the thing the whole
architecture was built around:

    Collection/ · .migx packages · Crates/ · Playlists/ · Vocabulary/

Temple reads all of it unchanged. You can replace the entire program — language, engine, UI, process
model — and **the library does not move**. That is filesystem-as-SSoT being cashed in rather than
asserted, and it is the strongest available argument that the decision was right: a vendor whose
library is a database cannot do this, which is exactly why their format churn is a support theme.

## The package suffix

`<audio>.migx/` is **on-disk data**, not a label. 456 packages carry it today, and crate hardlinks,
`rename.py` and `sidecar.py` all resolve by adjacency to that suffix.

**Decision: the on-disk suffix stays `.migx/`.** Not a compromise — the point.

A data format should outlive the program that wrote it. The package travels with audio to other
machines and other tools; coupling it to whichever generation is current is the same instinct that
makes a vendor's Device Library a trap (`ADR-011`, `EXPORT`). Temple writing `.migx/` is not legacy
debt, it is the format keeping its promise across a full product generation — the first real test it
has had.

If it is renamed later it is a **deliberate one-time migration** gated on `package.version`, never a
side effect of a rename commit. Reserve `temple.package/2` for that.

## What must not happen

- **No dual-answering binary.** Migx and Temple are generations, so both may exist during the
  transition — but neither aliases the other. Two names for ONE program is `P-11`; two programs, one
  library, is the design.
- **No silent rename of data.** A command must never move a user's `.migx/` directories as a side
  effect of an upgrade. If it migrates, it says so and emits a receipt (`P-34`).
- The repo directory and git remote may lag the product name — that is cosmetic and not worth a
  history rewrite.

## Consequences

Renaming is cheap *now* and gets steadily more expensive: every schema string, installer path and doc
reference added from here carries the old name. Doing it before the Swift port (`SWF`) means the new
binary is born named — which is the natural moment, since that binary is written from scratch anyway.

The artifact deck, `install.sh`, `README`, and the `migx.*/1` schema strings are the surfaces to sweep.

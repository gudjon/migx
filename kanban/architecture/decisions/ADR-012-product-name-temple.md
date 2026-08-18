---
id: ADR-012
type: decision
title: "The product is called Temple — and what that binds on disk"
status: accepted
owner: gudjon
created: "2026-08-18"
lastUpdated: "2026-08-18"
supersedes: []
amends: [ADR-011]
related: [ADR-002, ADR-008, ADR-009, P-11, P-34]
---

# ADR-012 — the product is Temple

## Decision

The software is **Temple**. `temple` on PATH.

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

## The one genuinely expensive question: the package suffix

`<audio>.migx/` is **on-disk data**, not a label. 456 packages carry it today, and crate hardlinks,
`rename.py` and `sidecar.py` all resolve by adjacency to that suffix.

**Decision: the on-disk suffix stays `.migx/` for now.** Two reasons, and the second is the real one:

1. A rename touches every package on the volume and every path-resolving module — a migration with no
   product gain on the day it lands.
2. **A data format may outlive the brand.** The package is meant to be portable and to travel with
   audio to other machines and other tools. Coupling it to a product name is the same instinct that
   makes a vendor's Device Library a trap (`ADR-011`, `EXPORT`).

If it is renamed later it is a **deliberate one-time migration** gated on `package.version`, never a
side effect of a rename commit. Reserve `temple.package/2` for that.

## What must not happen

- **No dual naming window.** Two binaries, or `migx` aliased to `temple` indefinitely, is two truths
  about one product (`P-11`). Rename once; keep a shim only long enough to update scripts, and delete
  it on a date.
- **No silent rename of data.** A command must never move a user's `.migx/` directories as a side
  effect of an upgrade. If it migrates, it says so and emits a receipt (`P-34`).
- The repo directory and git remote may lag the product name — that is cosmetic and not worth a
  history rewrite.

## Consequences

Renaming is cheap *now* and gets steadily more expensive: every schema string, installer path and doc
reference added from here carries the old name. Doing it before the Swift port (`SWF`) means the new
binary is born named — which is the natural moment, since that binary is written from scratch anyway.

The artifact deck, `install.sh`, `README`, and the `migx.*/1` schema strings are the surfaces to sweep.

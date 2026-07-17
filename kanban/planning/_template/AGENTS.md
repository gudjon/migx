---
id: dossier-<PFX>
slug: <YYYY-MM-DD>-<owner>-<PFX>--<slug>
type: dossier
prefix: <PFX>
title: "<one-sentence dossier title>"
classification: none        # none | A agent-scaffolded | P program | G governance
phase: scaffold             # scaffold | foundation | research | architecture | execution | sealed
sealed: false               # true only after 91-LOOP-CLOSURE is scored
status_note: "<current-reality one-liner — what is actually true right now>"
completion-criteria:
  - "<the Definition-of-Done, one bullet per criterion — must be checkable>"
facilitator: <owner>        # the single DRI (MG-4)
initiative: initiative-<slug>   # the standing bet this serves, if any (dossiers are primary — MG-5)
authored_by: <agent-or-human>
authored_kind: mixed        # human | agent | mixed
triggered_by: <what caused this dossier to open>
created: "<YYYY-MM-DD>"
lastUpdated: "<YYYY-MM-DD>"
last_audited: "<YYYY-MM-DD>"
---

# <Dossier title> — agent routing

The card above is this dossier's identity. Below is routing-by-intent for an agent entering here.

## Routing by intent

| You want to… | Go to |
|---|---|
| Understand why this bet exists | `00-FOUNDATION/PROBLEM.md` |
| See the checkable spec | `00-FOUNDATION/PS-<PFX>-*.md` (EARS + `acceptance:`) |
| See prior art / upstream scan | `01-RESEARCH/00-RESEARCH.md` |
| See the chosen design + patterns cited | `02-ARCHITECTURE/00-ARCHITECTURE.md` |
| See the ordered plan + gates | `90-EXECUTION/00-PHASE-PLAN.md` |
| Score / seal the bet | `91-LOOP-CLOSURE/00-LOOP-CLOSURE.md` |
| Catch up on what happened | `JOURNAL.md` |

## The closed loop this dossier is (MG-1)

- **Trigger** — <what fires this: a benchmark regression, a missing capability, a north-star gap>
- **Capture** — <the PS `acceptance:` + baseline `EVD-*` records>
- **Intelligence** — <the measured delta / test verdict>
- **Adjustment** — <the merged change; re-closes on the next trigger run>

# Dossier template

Copy this directory to open a new unit of work (MG-5). Name the copy:

```
kanban/planning/<YYYY-MM-DD>-<owner>-<PFX>--<slug>/
```

where `<PFX>` is a 3-letter prefix **already registered** in
`kanban/planning/00-PORTFOLIO/prefix-registry.yaml` (register it first).

**Before you copy — compound before create.** Prove no OPEN dossier already owns this scope. If one
does, fold your work into it instead. New scope → new dossier; never route work into a sealed one.

## The skeleton

| Path | What it holds |
|---|---|
| `README.md` | Scope, success criteria, current status (this becomes the dossier's front page). |
| `AGENTS.md` | The dossier card (frontmatter) + routing-by-intent for agents entering it. |
| `00-FOUNDATION/PROBLEM.md` | The problem in prose — why this bet, for whom, what "done" means. |
| `00-FOUNDATION/PS-<PFX>-01.md` | One Problem Statement per problem (default: ONE per dossier). EARS + machine-consumable `acceptance:`. |
| `01-RESEARCH/00-RESEARCH.md` | Prior art, upstream (Mixxx) changelog scan, options considered. |
| `02-ARCHITECTURE/00-ARCHITECTURE.md` | The chosen design, its edges, the patterns/ADRs it cites. |
| `90-EXECUTION/00-PHASE-PLAN.md` | Ordered phases/waves, each with a verifiability gate. |
| `91-LOOP-CLOSURE/00-LOOP-CLOSURE.md` | The bet, scored. Seal here. THE most important file. |
| `JOURNAL.md` | Round-by-round log during execution (git holds chronology; this holds narrative). |

## Lifecycle

`scaffold` (prefix registered) → `FOUNDATION` (PSes with EARS + acceptance) → `RESEARCH` +
`ARCHITECTURE` → `EXECUTION` waves under `/loop` → **seal** at `91-LOOP-CLOSURE`.

A sealed dossier is a **dated snapshot** — a record of THEN, not current truth (MG-5). Before
`sealed: true`, every durable learning must re-home into the living layer (patterns, ADRs, in-code
annotations, the architecture map). Post-seal, the only allowed edit is an append-only dated
`enriched:` note.

---
id: migx-playbook-frame-cadence-compounding
type: playbook
title: "The Frame, the Cadence, and Compounding"
status: active
owner: gudjon
created: "2026-07-17"
lastUpdated: "2026-07-17"
defers_to:
  - kanban/AGENTS.md
---

# The Frame, the Cadence, and Compounding

Software now moves at agent speed. When the machine does the typing, the scarce
resource stops being code and becomes *direction* — knowing what is worth
building, which result is suspicious, where the system is drifting off the rails.
This chapter is the frame that keeps direction sound: two ground rules, one
cadence, and the compounding discipline that makes each loop cheaper than the last.

## The frame — two ground rules

Everything downstream is a corollary of these two. They are the most-cited rules
in the harness and the most-violated under time pressure, so they sit at the top.

### Ground rule 1 — Everything is a closed loop (MG-1)

A process is a *closed loop* when it has four beats and the last one is automatic:
**Trigger → Capture → Intelligence → Adjustment**, where the adjustment is
repeatable and verifiable against the same trigger. Open loops are the default
failure mode; closing them is the discipline.

In Migx the loop is rarely abstract. For performance work it is concrete: a
**benchmark is the trigger and the capture**, the measured delta against a pinned
baseline is the intelligence, the merged optimization is the adjustment — and the
next benchmark run re-closes it. That is `P-03` benchmark-as-contract in one
sentence.

The corollary is a stop rule: **if you are about to ship work with no loop
attached, it is not done.** Close the loop now, or write down at a stable path
exactly when and by whom it closes.

### Ground rule 2 — Everything is code (MG-2)

Anything load-bearing is expressed as code, or as a code-shaped artifact a machine
can `grep`, `jq`, or `find` — a file in `kanban/`, an ADR, a pattern card, an
in-source annotation. Slack threads, PR comments, and tribal knowledge are not
load-bearing. They are scratch.

The corollary: **if a load-bearing decision is not written at a stable path, it is
not load-bearing — it is scratch, and the next agent will re-derive it.**
Code-shaped artifacts are the only kind that compound. This is the structural
reason the harness is markdown-as-code and not a wiki: an agent can read it, a new
engineer can read it, and both read the *same* truth.

*Human-side companion.* You can outsource thinking; you cannot outsource
understanding. Producing plans, writing code, running benchmarks — delegate all of
it. Knowing what is worth building and which number is a lie stays in your head.
So read for understanding, not execution, and ask comprehension-shaped questions:
*what does this change delete? · what benchmark proves it? · where does this seam
end?* — not *who wrote it* or *how long will it take*.

## The cadence — the dossier is the sprint

The cadence is what turns two rules into daily life. The unit is the **dossier**
(MG-5): a **1–4-day closed-loop sprint** — not a ticket, not a branch, but a
directory under `kanban/planning/`. A dossier opens with a bounded problem, roots
its claims in real `file:line`, decides what gets *deleted* as well as added, and
**seals at `91-LOOP-CLOSURE/`** where the bet is scored: a verdict, a five-pass
retrospective, a wiring ledger, and a forecast-versus-actual. Until it seals, the
loop is open and the lesson has not compounded.

Three moves define the rhythm:

- **Name the closed loop first (`P-01`).** Before scaffolding, state the four
  beats out loud. If you cannot say what the trigger, capture, intelligence, and
  adjustment are, you are not ready to plan — you are about to open a loop you
  cannot close.
- **Compound before create.** Before opening a new dossier, prove no OPEN dossier
  already owns the scope, and fold into it if one does. New scope earns a new
  dossier; fresh work is never routed into a sealed one. A sealed dossier is a
  dated snapshot of THEN — current truth lives in the code, the `architecture/`
  map, and the pattern catalogue, never in a reopened record.
- **Leave a loop running.** The highest-value overnight run in Migx is a
  **benchmark-driven optimization loop**: build → bench → compare to the pinned
  baseline → propose and apply one optimization → re-bench. It scores itself, so
  no one has to watch it; morning's output is the trigger for the next iteration.

That is the north star the cadence serves: **Migx running blazingly fast on Apple
Silicon (M4/M5 + Metal)**, pursued as a standing stream of benchmark dossiers,
each a closed loop scored on real numbers.

## The Discipline Checklist

Seven gradeable rules. A reviewer reads a PR or a dossier and answers yes / no /
n-a for each. This is the checklist the harness applies to any non-trivial change.

1. **Closed loop named (MG-1, `P-01`).** Can you state Trigger / Capture /
   Intelligence / Adjustment? If not, the loop is open and the work is not done.

2. **Stable path (MG-2).** Is every load-bearing decision written where `grep`
   finds it? A decision in a PR thread is scratch — re-home it or lose it.

3. **Refactor over layering — the cardinal rule.** *Every change replaces or
   removes; a change that only adds has not done the work.* The acceptance test is
   one question: **what does this delete?** If the author claims the deletion is
   "coming later," it does not merge without a named future PR and acceptance.
   Layering compounds quadratically — each new path interacts with every prior
   one; refactor compounds linearly. That difference is why a layering team slows
   week over week and a refactoring team speeds up.

4. **Single source of truth (MG-3).** One canonical home per fact. Cite by typed
   ID (`P-03`, `PS-ASI-01`, `ADR-002`), never by prose ("the waveform thing"), and
   never copy a value another file can derive. Status is *derived* by the board,
   not hand-stamped.

5. **Evaluation contract (`P-03`).** For performance work, the claim is backed by
   a **benchmark with a numeric threshold**, measured against a pinned baseline
   commit — not a vibe, not an average eyeballed once. The benchmark is what the
   change has to move, and what a future agent re-runs to confirm it.

6. **House physics respected (MG-6, `P-02`).** No allocation and no locks on the
   real-time audio thread; Qt ownership via `parented_ptr` / `make_parented`;
   components talk through ControlObject / ControlProxy. `pre-commit` is clean.
   A change that is faster on average but allocates on the RT path is a
   **correctness regression, not an optimization** (this is `AP-02`
   speedup-regresses-house-physics — the seductive win that a raw benchmark
   rewards and the physics forbids).

7. **Feeds back this loop.** Durable learnings re-home into `patterns/`, ADRs, or
   annotations *before the dossier seals* — not "later." An unfilled retrospective
   is a scaffold, not a closed loop.

## Compounding — how the memory stays sharp

Loop closure produces patterns; patterns produce shorter dossiers; shorter
dossiers close faster. That is the steering loop, and it only runs if knowledge
**compounds instead of accumulating.**

- **Compound and refactor, don't layer.** Each pass *improves* an existing
  canonical surface rather than appending a parallel one. Add a new entry only when
  nothing already covers it. Denser and fewer beats longer and more.

- **No ledger — git holds history.** There is no growing `DECISIONS.md` trail. The
  current true state lives in the code, the `architecture/` map, and the pattern
  cards; the chronology lives in `git log`. A trail you scroll is noise. The
  keep-test is sharp: *does an agent load this by relevance to act now?* If yes it
  is memory — keep it. If it is a log you page through, collapse it. (A dossier's
  `JOURNAL.md` is the one bounded exception — it dies when the dossier seals.)

- **The deletion test.** For any artifact, ask: *would removing this make the team
  faster with no loss of safety?* If yes, delete it — or fold its substance into a
  surface that already exists. Sequence numbers and growing indexes are anti-shape;
  a directory listing is its own index.

- **Memory decays, it does not only grow.** The compounding loop *prunes* as well
  as accretes. Stale patterns and dead tasks get proposed for retirement on the
  same cadence that adds new ones. A catalogue that only grows becomes a catalogue
  that misleads — and a wrong citation produces wrong architecture.

The one green-instrument trap to name explicitly: never seal a loop over a red
gate. A benchmark that reads green because it measured the wrong thing is worse
than an honest red (`AP-01` green-over-red). Halt honestly with a named successor
instead — an honest red-but-scope-complete seal is legitimate; a fabricated green
is the worst failure shape there is.

> Everything is a closed loop. Everything is code. The day is one iteration of the
> bigger loop.

---
id: migx-playbook-daily-loop-and-the-dream
type: playbook
title: "The Daily Loop and the Dream"
status: active
owner: gudjon
created: "2026-07-17"
lastUpdated: "2026-07-17"
defers_to:
  - kanban/AGENTS.md
  - kanban/triggers/registry.yaml
---

# The Daily Loop and the Dream

The last chapter set the frame: two ground rules, the dossier as the unit of work,
and compounding as the discipline that makes each loop cheaper than the last. This
chapter is the *motion* — the hour-by-hour shape of a session, how a run behaves
when no human is watching, and the scheduled meta-loop that improves the harness
itself while you sleep. The through-line is one idea from the frame: **the day is
one iteration of the bigger loop.** It closes the same way a dossier does — with a
learning fed back — and it opens the next day already in motion.

## 1 — The daily developer loop

A session has five moves. Each produces an output the next move consumes, so the
day itself is a closed loop (MG-1).

**Assess.** Start with what ran while you slept. The overnight benchmark loop left
fresh `EVD-*` records; read the deltas first — *what moved, what regressed against
the pinned baseline?* A regression pre-empts today's plan. Then read the board
(derived live, never hand-stamped) and the active dossier's `JOURNAL.md` tail. The
first question is never "what shall I build" but "what did last night's harness
tell me." If nothing ran overnight, the previous day's loop did not close — it
paused — and today opens blind. That is the failure mode to notice at 09:00.

**Plan.** Open a dossier, or continue one. *Compound before create* (MG-5): before
scaffolding, prove no OPEN dossier already owns the scope and fold in if one does.
Name the four beats out loud before writing any code (`P-01`) — for a perf dossier
the trigger and capture are a benchmark, the intelligence is the delta against a
baseline commit, the adjustment is the merged optimization. Declare the evaluation
contract *up front*: the numeric threshold the change must move, measured against a
pinned baseline (`P-03`), named before the run, not inferred after. A dossier
whose four beats you cannot name is a vibe-coding session under a directory name.

**Run.** Execute in waves under `/loop`, **committing per wave**. The role is
directing, not typing: spawn a read-heavy research or review subagent off your
context; run `pre-commit` (clang-format/tidy, qmllint, cmake lint) as the fast gate
on every wave — the heavy full build and `ctest` are later rungs on the
verification ladder, not per-wave tolls. Do not interrupt the loop to check status;
status lives in the commits and the journal. Intervene only at a real fork — a
flagged decision, a `pre-commit`-to-red flip, an RT-safety concern.

**Close.** The run is not done when the commits stop; it is done when the closure
is written at `91-LOOP-CLOSURE/00-LOOP-CLOSURE.md`. Score the bet: the verdict, the
five-pass retrospective, the wiring ledger, forecast-versus-actual. **Feed the
learnings back this loop** — a durable lesson re-homes into `patterns/`, an ADR, or
a source annotation *before* the dossier seals, not "later" (an unfilled retro is a
scaffold, not a closed loop). Never seal green over a red gate: an honest
red-but-scope-complete seal is legitimate; a fabricated green is the worst shape
there is (`AP-01`). The `## Next bet` of one closure is the opening problem of the
next dossier — that is what makes the closure the *learning beat*, not paperwork.

**Leave.** The day's last move is to start the next day's intelligence. Kick off an
overnight benchmark loop: **build → bench → compare to the pinned baseline → propose
and apply one bounded optimization → re-bench.** It scores itself against `EVD-*`,
so no one has to watch it; morning's output becomes tomorrow's *assess* input. A
laptop closed with no loop running is a missed iteration cycle. The day closes when
the loop is running and the journal handoff is written; it opens when you read what
the loop produced.

## 2 — Running unattended — the autonomous decision cascade

Between waves, a `/loop` or a workflow hits forks a human never sees. The one rule
that catches you when unattended: **do not stop to ask.** Stopping mid-loop to
request a human decision is the default failure mode of an autonomous run — it
converts a tireless agent back into a blocked one. The cascade at every fork:

1. **Articulate the options.** Name the 2–4 real choices, each with its cost. An
   unnamed option cannot be reasoned about.
2. **Challenge with a 5-whys.** Push past the symptom to the root — most forks
   dissolve once the actual driver is named (the option that looked balanced was
   answering the wrong question).
3. **Decide with confidence ≥ 0.4, or flag-and-skip.** If one option clears the
   bar, take it. If none does, or the choice is genuinely a value judgment, record
   the fork, skip it, and *continue* the loop — never block the whole run on one
   ambiguous branch.
4. **Record at a stable path.** The decision lands where `grep` finds it (MG-2):
   the dossier `JOURNAL.md` for a routine call, an ADR for a path-pinning one, a
   `kanban/tasks/` card for a flagged judgment call. A decision only in the model's
   context is scratch — it evaporates at the next compaction.
5. **Continue.** Always keep the loop closed and moving.

The only two forks that legitimately halt a run are **irreversible** actions (a
destructive migration, a force-push over shared history) and **genuine value
judgments** only the owner can make (is this optimization worth the code
complexity?). Everything else the cascade decides and records. Confidence between
0.4 and 0.7 is decided *and* surfaced for morning review — decided so the loop
compounds, surfaced so the human can refine it cheaply. That is the whole trick:
bias toward motion, but leave an auditable trail behind every autonomous call.

## 3 — The Dream — the autonomous improvement cadence

The daily loop improves the *product*. The Dream improves the *harness* — the outer
ring that runs the loops. It is the outer-outer loop, made autonomous and scheduled
so the compounding never waits on a human remembering to run a retro. It lands in
Migx as three artifacts: the workflow `.claude/workflows/nightly-dream.js`, its
firing row in `kanban/triggers/registry.yaml` (a `TR-nightly-dream` entry naming
substrate and cadence), and a cloud `/schedule` Routine that wakes it nightly with
the repo pre-cloned as a source.

Four properties keep it closed-loop instead of a nightly report generator:

- **Delta-only.** A git watermark (`kanban/triggers/dream-watermark.json`) bounds
  every pass to the commits *since the last run*. The Dream never re-derives the
  whole repo; it reads the day's delta. A quiet day exits cheap.
- **Anti-stall.** Every pass records **new signal OR "converged"** — one or the
  other, explicitly. A pass that neither found a delta nor declared convergence is
  a silent stall, and that is the one thing the run may not do.
- **Refute by default (VERIFY).** A surfaced concern is treated as false until
  evidence makes it true. The Dream tries to *kill* its own findings before acting
  on them; the ones that survive refutation are the ones worth an artifact.
- **Prune, not only grow.** Every pass includes a retire/re-ground beat. Stale
  patterns, dead tasks, and mitigations whose substrate was deleted get proposed
  for removal. A catalogue that only grows becomes one that misleads — and a wrong
  `P-NN` citation produces wrong architecture. Memory decays; it does not only accrete.

The pass shape is **SENSE(delta) → DEEPEN → VERIFY(refute) → ACT → REPORT.** The ACT
step routes by shape: a **mechanical** fix (a broken cross-reference, a formatting
drift, a dead link, a stale derived value) becomes **its own PR** the human merges
in one glance; a **judgment call** (a benchmark regression needing a real decision,
a boundary that should change) becomes a **`kanban/tasks/` card** with provenance,
escalated, never auto-applied. Design-bearing changes are emitted for a human, not
landed by the Dream — the blast-radius rails hold (`.claude/rules/agentic-decision-authority.md`).
REPORT writes a one-line heartbeat and **advances the watermark** via the commit
message itself, so the compounding history is the git trail, not a growing ledger
file (MG-3).

### The Migx nightly-dream tier list

Concrete lenses over the same corpus (the code, the dossiers, the `EVD-*` records,
the pattern cards), each serving the north-star. All are delta-bounded.

| Tier | Lens | Senses | Acts by shape |
|---|---|---|---|
| **Benchmark-regression sweep** | the `EVD-*` baselines | any subsystem's p99 slipped vs its pinned baseline since the watermark | regression → `tasks/` card keyed to `initiative-apple-silicon`; clean → "converged" |
| **Stale-pattern prune** | `patterns/` | a `P-NN`/`AP-NN` no longer cited by any code or dossier | propose retirement PR (mechanical); contested → card |
| **Dossier-reality grooming** | `planning/` | sealed dossiers claiming state the code has since moved past; open dossiers gone dormant | re-ground map / flag dead-dossier routing → card |
| **Plan-vs-merged-code drift** | dossier `90-EXECUTION` vs `git log` | a phase plan diverged from what actually merged | reconcile the plan (mechanical) or surface the gap → card |
| **Upstream-Mixxx changelog delta** | the fork's upstream | new upstream commits touching paths Migx optimized (`src/waveform`, `src/engine`, `src/rendergraph`) | flag conflict/opportunity → card; trivial doc sync → PR |

A clean night across all tiers is a valid no-op — the Dream is event-shaped under a
clock. The payoff is structural: every morning's *assess* step starts against a map
the Dream already reconciled, so the human and the next agent start aligned instead
of cold re-deriving.

## 4 — Provenance — trusting what the Dream produced

The Dream writes artifacts a human must be able to trust and audit at a glance. Three
frontmatter fields (already in the `kanban/tasks/` schema) mark anything an agent
authored:

```yaml
authored_by: nightly-dream        # the operating unit (or a human name)
authored_kind: agent              # human | agent | mixed
triggered_by: TR-nightly-dream / EVD-0007 regression   # what surfaced this
```

`authored_by` names who wrote it; `authored_kind` says whether a human was in the
loop; `triggered_by` traces it back to the signal — a trigger row, a regressed
`EVD-*`, a drifted dossier. Together they let a reviewer sort the morning queue by
trust: an `authored_kind: agent` card from a benchmark regression gets read before
it is believed; a mechanical PR that only fixed a dead link needs a glance. This is
what makes autonomous authorship safe rather than opaque — every agent-authored
artifact carries its own chain of custody back to the commit that provoked it, and
the Dream's own commit trail (the advancing watermark) is the audit log of what it
did each night. Trust is not asked for; it is *shown*, in fields `grep` can filter.

## CUT from the reference

The reference harness ran a fleet of agents across many machines and vendors; Migx
is **one repo on one developer's Mac**. What that removes:

- **The whole cross-agent federation layer.** Git-mediated mailboxes
  (`kanban/federation/<topic>/messages/`), the six-section message protocol,
  symmetric SessionStart/UserPromptSubmit hooks, the append-only frontmatter
  contract, status-field handoff semantics, and the five federation failure modes —
  **all cut.** There are no peer agents on other machines to coordinate with.
- **The network-access machinery** — Tailscale/WireGuard mesh, self-hosted git
  nodes, bastion tunnels, deploy-key matrices, the 27-cell substrate matrix, the
  cloud-side `gh api` participant, the fleet-as-tmux-sessions sweep — **all cut.**
- **The heavy improvement-cadence portfolio** — weekly/corpus/management tiers,
  Dossier-360 open-corpus harvest, the patent invention engine, the FIC inbox loop.
  Migx keeps a single nightly Dream, not a nested portfolio.

**What survives the cut** (the few federation ideas that transfer to one repo):

- **Coordination is a commit, not a message.** Even solo, the durable decision lives
  at a stable git path every future session sees identically (MG-2) — the same
  reframe, minus the mailbox.
- **Per-agent worktree hygiene.** When background subagents or parallel `/loop`s
  touch the same checkout, give each its own `git worktree` so staging does not
  collide — the one same-repo lesson the trio pattern earned, kept as a rule.

> Everything is a closed loop. Everything is code. The day is one iteration of the
> bigger loop.

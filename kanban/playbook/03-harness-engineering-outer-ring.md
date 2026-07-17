---
id: migx-playbook-harness-engineering-outer-ring
type: playbook
title: "Harness Engineering — The Outer Ring"
status: active
owner: gudjon
created: "2026-07-17"
lastUpdated: "2026-07-17"
defers_to:
  - kanban/AGENTS.md
---

# Harness Engineering — The Outer Ring

The previous chapter set the frame: closed loops, code-shaped memory, the dossier
cadence. This chapter is about the machinery that *carries* that frame — the
control system we build around the model. It is the most leveraged thing we own,
because everything the agent does flows through it, and unlike the model we can
change it any afternoon.

## 1 — Agent = model + harness; we own the outer ring

An agent is a **model plus a harness**. Three rings wrap the work, and only one is
ours to design:

| Ring | Owner | What it is |
|---|---|---|
| Inner — the model | Anthropic | Weights, sampler, the raw capability |
| Middle — the agent harness | Claude Code | System prompt, retrieval, tool orchestration, context management |
| **Outer — the user harness** | **us** | **`kanban/`, `.claude/`, in-code annotations, `AGENTS.md` files, CI gates** |

We do not tune weights and we do not rewrite Claude Code's orchestrator. We own
the outer ring, and it is a real engineering surface with its own discipline. In
Migx the outer ring is concrete: the doctrine and patterns under `kanban/`; the
skills, subagents, hooks, and workflows under `.claude/`; the pattern-anchor
comments in `src/` that bind code to a `P-NN`; the per-directory `AGENTS.md`
routing files; and the `pre-commit` and CI gates. Every claim in this chapter is
about that ring and nothing else.

The reason to treat it as engineering rather than tidying is that the outer ring
**compounds**. A pattern written once is cited forever; a lint written once guards
forever; a skill written once loads itself into every relevant session without
anyone remembering to. The bottleneck moves upstream into understanding, and the
outer ring is where understanding is stored at a stable path (MG-2).

## 2 — The operating primitives and the keeper rule

Five primitives instantiate the outer ring. They have different lifetimes and
cadences, and the whole skill of harness engineering is reaching for the
**lightest one that fits**. Overreaching — a Workflow where a subagent would do,
a skill where a pattern citation would do — is its own antipattern (layering, the
cardinal sin of the previous chapter).

| Primitive | Where it lives | Who holds the plan | Reach for it when |
|---|---|---|---|
| **Subagent** (`Agent` tool) | spawned in-session | Claude, turn by turn | one bounded, read-heavy, or independent task you want off your context — research fan-out, an adversarial review |
| **Skill** (`.claude/skills/*/SKILL.md`) | on disk, auto-discovered | Claude, per the prompt | reusable *knowledge or procedure* loaded on demand. Skills don't run; operating units run them |
| **Workflow** (`.claude/workflows/*.js`, `Workflow` tool) | on disk | the **script** | a genuinely multi-agent shape — fan-out → verify → synthesize — that one context can't coordinate and you want rerunnable |
| **`/loop`** | invoked | the loop, across turns | long-horizon iterative work with a measurable completion condition — the overnight optimization run |
| **`/schedule`** (cloud Routine) | cron + webhooks | the cron fire | a cadence sensor with no human present — nightly bench, weekly retro, drift sweep |

### What "current Claude Code" gives each primitive

The primitives above are richer than the reference harness assumed — it predates
these. Use them accurately:

- **Subagents** run in a **fresh, isolated context** and, by default, **in the
  background** — you are notified on completion and get a summary back, not the
  whole transcript, which is exactly how they keep the main context lean. They form
  an **implicit per-session team**: address a running teammate by name via
  `SendMessage` instead of re-spawning. They **nest up to 5 levels deep**, honor a
  **session-wide spawn cap** (default 200), and take **per-agent `model`/`effort`
  overrides** (run a cheap sweep on a small model, a keystone review on a large
  one). For parallel *file-mutating* agents, give each `isolation: 'worktree'` so
  they edit isolated copies and never clobber each other — the Migx-shaped case is
  three agents each trying an optimization against the same `src/`.
- **Skills** trigger on their `description` (that string is the auto-load contract —
  write it as "use when…"), and the **body loads only on demand**, so a fat skill
  costs nothing until it fires. Set `disable-model-invocation: true` for a
  user-only `/name` skill the model must never auto-fire. Skills **nest**
  (`<dir>:<name>` disambiguates a collision), **hotload**, and **stack up to 5**
  (`/pat-03 /verify do X`). `skillOverrides` in settings hides or adjusts one you
  don't want. A load-bearing skill declares the **Class-A grounding contract** —
  `defers_to`, `audit_gate`, `verifiable_output_shape` — so its output is checkable,
  not vibes.
- **Hooks** (`.claude/hooks/`) fire on lifecycle events: `PreToolUse`,
  `PostToolUse`, `SessionStart`, `Setup`, `Stop` / `SubagentStop`, and
  **post-session**. `Stop`/`SubagentStop` can return `additionalContext` to feed a
  correction back and let the turn continue rather than hard-blocking. Matchers are
  **hyphenated exact-match**. The discipline is **warn-only and degrade-safe**:
  a hook on the shared `.claude/settings.json` must swallow its own errors and
  `exit 0` on failure, so a bug degrades to "no warning," never "blocked harness."
- **`/loop`** runs a prompt on an interval or self-paced; **`/schedule`** creates a
  cloud cron Routine with webhooks and post-session hooks. Background sessions
  (`/fork`), the `/resume` picker, and long-running commands **survive a restart**;
  MCP calls **auto-background past ~2 minutes**.
- **Workflows** are deterministic multi-agent JS orchestration with **dynamic size**
  — earn one only for a real fan-out-plus-verify shape, never to wrap what a single
  skill already does.

### The keeper rule (memorize it — it also settles Pattern vs Skill)

> *A rule you **cite*** → a **Pattern** (`P-NN`, SSoT in `kanban/patterns/`, enforced
> by a lint). *Knowledge or a procedure you **load*** → a **Skill** that **cites**
> the pattern, never restates it (`P-05`). *Multi-agent fan-out at scale* → a
> **Workflow**. *A long autonomous loop* → **`/loop`**. *A cadence with no human* →
> **`/schedule`**. *One isolated worker* → a **subagent**.

The Pattern-vs-Skill half is the one people trip on. A **pattern is knowledge**: the
durable `P-NN` card that is the single source of truth for *what good looks like*. A
**`pat-*` skill is the auto-load trigger**: a 2–4 line body whose `description` fires
on the relevant code and whose whole job is to point at the card. Two copies of a
rule is two sources of truth; they drift, and no reader can tell which is current.
So the skill **cites, never clones** — that is `P-05`, and it is MG-3 applied to the
skill/pattern seam.

## 3 — Guides × Sensors

Every outer-ring control is either a **guide** or a **sensor**. Guides are
*feedforward* — they steer the agent *before* it acts. Sensors are *feedback* — they
catch a problem *after*, and route the correction back. Cross that with whether the
control is **computational** (deterministic, fast, cheap) or **inferential**
(semantic, slow, an LLM judgment) and you get the 2×2 that tags every artifact we
build.

|  | **Computational** (deterministic, cheap) | **Inferential** (semantic, an LLM call) |
|---|---|---|
| **Guides** (steer *before*) | `clang-format`/`clang-tidy` config, `.clang-tidy`, CMake presets, type signatures, a `PreToolUse` hook | `kanban/AGENTS.md`, `.claude/skills/*`, per-dir `AGENTS.md`, a planning dossier, `NOTE(invariant:)` annotations |
| **Sensors** (correct *after*) | `pre-commit`, `ctest -R`, a Google-Benchmark delta vs a pinned baseline, a CI gate, a `Stop` hook running a lint | an adversarial-review subagent, a `/code-review` pass, a Workflow verify stage |

The central claim is that **each axis alone is unstable.** Guides without sensors are
rules nobody verifies — they rot silently. Sensors without guides are an agent that
keeps making the same mistake and getting corrected forever. The harness is healthy
only when both are present and pointing at the same invariant.

The hierarchy when both *could* apply: **push every check that can be computational
into computational form**, and reserve inferential checks for what only a semantic
read can see — over-engineering, a plausible-but-wrong benchmark, a convention not
yet codifiable. Inferential controls are correct but expensive and non-deterministic,
so each one must earn its invocation.

Four Migx examples, one per cell:

- **A pattern card is an inferential guide.** `P-02` (no allocation on the RT audio
  thread) steers the agent before it writes the code. It carries authority, but a
  human or an LLM still has to apply it — until it is also a lint.
- **`pre-commit` is a computational sensor.** `clang-format`, `clang-tidy`, `qmllint`,
  and the CMake lint fire after the edit and gate the commit deterministically. This
  is the fast quality gate (MG-6), not the heavy full build.
- **A benchmark is the load-bearing sensor for the north star.** A Google-Benchmark
  delta against a **pinned baseline commit** (`P-03`, benchmark-as-contract) is what
  turns "feels faster" into a number. It is a computational sensor with teeth.
- **The overnight `/loop` is a Stage-6 sensor** — a benchmark-driven optimization run
  that build → bench → compares → applies one change → re-benches, on cadence,
  outside any single change. It senses drift and improvement no PR-time gate would.

## 4 — The verification escalation ladder

A sensor is not one thing; it is a ladder. The rule is **cheapest sufficient check
first** — climb only as far as the claim's stakes and the run's autonomy demand.
Spending a full build or an adversarial review on a one-line, pre-commit-catchable
change is the same waste as layering.

| Rung | Check | Cost | Gates |
|---|---|---|---|
| 1 | `pre-commit` (clang-format/tidy, qmllint, cmake lint) | seconds | style, obvious defects, house-physics lints |
| 2 | targeted `ctest -R <name>` | seconds–a minute | the specific behavior you touched |
| 3 | **benchmark delta** vs pinned baseline | minutes | a **performance** claim (`P-03`) |
| 4 | full `cmake --build` + full `ctest` | many minutes | integration, nothing else broke |
| 5 | **adversarial subagent review** | an LLM call | semantic gaps only a fresh reader sees |

The load-bearing rung depends on the claim. **For a performance claim, rung 3 is
load-bearing** — no benchmark delta against a pinned baseline means the optimization
is not proven, full stop. **For a correctness claim, rung 2 is load-bearing** — the
test that exercises the changed behavior is the evidence; a green benchmark says
nothing about whether the output is right. Match the rung to the claim, don't just
climb by default.

Rung 5 has its own failure mode, and it must be run with two rules:

- **Generator ≠ Evaluator.** The agent that wrote the code cannot be the one that
  grades it — it is invested in its own answer. Spawn a **fresh subagent** (its
  isolated context is the point) to review, or a Workflow verify stage. This is why
  `isolation` and background subagents matter: the reviewer starts clean.
- **Refute by default, majority to kill.** A reviewer asked to find gaps *will* find
  some even when the work is sound — that is what it was told to do. So bound it:
  it flags **only** gaps that affect correctness or the stated acceptance criteria,
  never style or preference, and a finding sticks only if it survives scrutiny (a
  majority of independent reviewers, when you fan out several). Chasing every
  manufactured finding produces defensive code and tests for cases that can't happen
  — the review over-engineers the very thing it was meant to protect. Skepticism
  stays high; *what counts as a real refutation* is scoped tight.

## 5 — How to actually build one

The recipes, each pinned to its real home under `.claude/`. These directories exist
in Migx today (agents, hooks, rules, skills, workflows); the files below are what
lands in them.

**A skill** → `.claude/skills/<name>/SKILL.md`. Frontmatter carries a `description`
written as an auto-load trigger ("use when editing an RT engine path"), a
`defers_to:`, and for a pattern skill `metadata.cites_patterns: ["P-NN"]`. Keep a
`pat-*` skill body to 2–4 lines that point at the card (`P-05`) — the card is the
SSoT, the skill is only the *when*. Add `disable-model-invocation: true` for a
user-only `/command`. Register it in `.claude/skills/AGENTS.md`; it auto-discovers
on hitting disk. Verify a pattern skill with the Phase-3 lint
`verify-skill-defers-not-restates.py`.

**A subagent** → invoke the `Agent` tool with a tight prompt and let it run in the
background; you'll be notified with a summary. Give it `isolation: 'worktree'` if it
will edit files in parallel with others, and a `model`/`effort` override sized to the
task (cheap for a sweep, strong for a keystone review). Reusable agent definitions
live in `.claude/agents/`. Prefer a subagent over a Workflow whenever it is one
worker, not a fan-out — and gate its power in `.claude/settings.json` with a rule
like `Agent(model:opus)` where a large model needs an explicit grant.

**A hook** → a script in `.claude/hooks/`, wired in `.claude/settings.json` under its
event (`PreToolUse`, `SessionStart`, `Stop`, …) with a **hyphenated exact-match**
matcher. Build it **warn-only and degrade-safe**: swallow errors and `exit 0` on any
failure so a bug becomes "no warning," never "blocked harness." The highest-leverage
Migx hooks are a `PreToolUse` gate that warns before an edit touches an RT-thread
path (write-time prevention, ahead of the PR-time lint) and a `SessionStart` hook
that injects the current pinned-baseline commit as `additionalContext` so a
cold-starting agent benchmarks against the right base.

**A `/loop`** → `/loop` with a prompt or a slash command, self-paced or on an
interval. The Migx keystone loop is the overnight optimizer: *build → bench →
compare to the pinned baseline → apply one optimization → re-bench*, its completion
condition a numeric benchmark threshold (never prose like "until it's fast"). Inside
a loop **never stop to ask a human** for anything reversible — decide with a 5-whys,
record the decision at a stable path, keep the loop closed (that is the onboarding
rule that catches you when unattended). Enforce it structurally by disallowing
`AskUserQuestion` in the loop's driving skill.

**A workflow** → `.claude/workflows/<name>.js` via the `Workflow` tool, saved through
`/workflows` and listed in `.claude/workflows/AGENTS.md`. Earn it only for a real
`pipeline(items, ground, verify)` shape: one agent grounds each item, a **second,
independent** agent adversarially verifies it (`P-05`'s sibling discipline —
Generator ≠ Evaluator). **Trust the deterministic check, not the workflow's own
structured return** — re-run the lint or the benchmark after the run to confirm the
grounding actually landed. Bound the fan-out (≤16 concurrent) and the total cost.
A **`/schedule`** Routine is the same recipe fired on cron for a cadence sensor —
nightly bench, weekly grooming — with a post-session hook to snapshot the result.

A note on context economy, since it is the quiet reason all of this pays off: skills
and subagents exist largely to **keep the main context lean** — a fat skill body
loads only when it fires, a subagent's transcript stays in its own window and returns
a summary. `CLAUDE.md` is always loaded, `MEMORY.md`'s first ~200 lines / 25 KB load
each session, and `/context` shows you the budget. Spend it on what must be resident;
push everything else behind an on-demand primitive.

---

## CUT from the reference

What the reference harness carried that Migx deliberately drops or folds:

- **The three-usages disambiguation (§0) and the doctrine-naming table (§0b)** —
  "The Cycle / The Split / The Forge / The Long Harness / The Plan Forge." Migx has
  one codebase and one team; the naming ceremony is overhead. We keep plain terms:
  closed loop, benchmark loop, keeper rule.
- **The full six-stage lifecycle and three-regulation-category vertical axis** —
  distilled to the verification ladder (§4) and Guides × Sensors (§3), which carry
  the same weight without the taxonomy tax.
- **The four-tier control hierarchy (Org/User/Agent/Tool)** — collapsed into MG-3/MG-4
  (single source of truth, one owner). One repo doesn't need an org tier.
- **The durable-cloud-agent / subscription-vs-API-pricing constraint and the
  two-service always-on AIOps↔FIC loop** — those are an OZ operations concern. Migx's
  autonomous layer is the single `/schedule`d nightly loop of `HARNESS.md` §VII, not a
  supervised service pair.
- **All OZ-domain content** — venue/astro/framing services, the flywheel scores, NATS
  and Memgraph contracts, `data/context/`, per-device agent boxing. Replaced
  throughout by the one Migx north star: Apple-Silicon performance measured by
  benchmark dossiers.
- **The theoretical anchors section (Ashby / harnessability / ambient affordances)** —
  genuinely useful, but doctrine-level reading, not playbook. If we want it, it goes in
  `kanban/AGENTS.md`, not here.

> Own the outer ring. Reach for the lightest primitive that fits. Cheapest sufficient
> check first — and for a speed claim, the benchmark is the check.

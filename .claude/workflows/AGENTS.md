# .claude/workflows/ — multi-agent orchestration

A workflow is a `<name>.js` script run by the `Workflow` tool: a deterministic JS harness that fans
work across many isolated subagents and synthesizes the result. **Reach for a workflow only for
genuinely multi-agent shapes** (fan-out → verify → synthesize, or loop-until-dry). A single subagent +
a skill is preferred for anything simpler (playbook ch.03, the keeper rule).

## Format
- Begins with `export const meta = { name, description, phases }` — a **pure literal** (no vars/calls);
  `phases[]` titles must match the `phase()` calls in the body.
- Body is executed JS with injected primitives:
  - `agent(prompt, {schema, phase, label, model, effort, isolation})` — spawn a subagent; with a JSON
    `schema` it returns validated structured output.
  - `pipeline(items, stage1, stage2, ...)` — each item flows through all stages independently (NO
    barrier). **The default** for multi-stage work.
  - `parallel(thunks)` — run concurrently with a barrier (awaits all). Use only when a stage genuinely
    needs ALL prior results together (dedup, early-exit-on-zero).
  - `log(msg)`, `phase(title)`, `args`, `budget`.
- No `Date.now()`/`Math.random()`/argless `new Date()` (they break resume). The script does no fs/shell
  itself — only agents do.
- Invoked via the `Workflow` tool (`{name}` or inline `script`); a saved workflow becomes `/<name>`.

## Conventions
- **Adversarial verify** — refute-by-default; a finding needs ≥ majority of independent verifiers to
  survive (Generator ≠ Evaluator, `P-08`). Flag correctness/acceptance gaps, never style.
- **Gate-respecting in the script** — subagents run in `acceptEdits`; a workflow that must respect a
  gate (e.g. never touch a sealed dossier) enforces it in the JS, not by hoping.
- **`isolation: 'worktree'`** for agents that mutate files in parallel (avoids git collisions) — it's
  expensive, so only when needed.
- **Log what you cap** — if a run bounds coverage (top-N, no-retry), `log()` it; silent truncation reads
  as "covered everything."

## Inventory
| Script | Shape | Purpose |
|---|---|---|
| dossier-pass-fanout.js | fan-out → synthesize | Run the research/PS/architecture passes for a dossier in parallel, then synthesize a plan draft. |
| nightly-dream.js | sense → deepen → verify → act → report | The autonomous improvement cadence (the Dream) — delta-only, prunes as well as grows. Playbook ch.04. |

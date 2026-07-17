# .claude/skills/ — authoring conventions

A **skill** is a `<name>/SKILL.md` file: static knowledge or a procedure that Claude Code auto-loads
when its `description` matches the current context, or that a user invokes as `/<name>`. Skills don't
run — operating units (a session, a subagent, a `/loop`) run them. See `kanban/playbook/03` for when to
reach for a skill vs a subagent vs a workflow.

## Frontmatter (keys are kebab-case — camelCase is silently ignored)

```yaml
---
name: <kebab-name>                 # matches the directory
description: "<the AUTO-LOAD TRIGGER — when should Claude surface this? be specific about the code
  context / file paths / user phrasing that should fire it>"
disable-model-invocation: false    # true → user-only /name (keep description out of context until invoked)
user-invocable: true               # false → background knowledge, out of the / menu
allowed-tools: []                  # optional narrowing
disallowed-tools: []               # e.g. AskUserQuestion for hands-free loop skills
# --- grounding contract (required; lint-checked in Phase 3) ---
defers_to: [<real SSoT paths this cites, never restates>]
audit_gate: "<a deterministic verify-*.py/test, OR 'advisory — no deterministic artifact'>"
verifiable_output_shape: "<output schema, OR 'advisory — knowledge skill, no artifact'>"
metadata:
  cites_patterns: []               # for pat-* skills: the P-NN/AP-NN it surfaces
---
```

## Rules

1. **Description is the trigger.** Claude reads code/context and loads the skill when the description
   matches. Write it as *when to fire*, not *what it is*. Keep the SKILL.md **body short** — it stays
   in context across turns once loaded.
2. **Cite, don't restate (MG-3, `P-05`).** A skill points at its SSoT via `defers_to` and links; it
   never copies the text. A `pat-*` skill's body is 2–4 lines: "this surfaces `P-NN`, read the card."
3. **Grounding contract on every skill.** `defers_to` / `audit_gate` / `verifiable_output_shape` —
   knowledge skills use the `advisory — …` literals. Phase-3 `verify-skill-grounding.py` enforces it.
4. **Invocation control.** `disable-model-invocation: true` for user-only commands (e.g. `/add-task`);
   `user-invocable: false` for background knowledge; default = both user and model can invoke.
5. **Dynamic context.** `${CLAUDE_SKILL_DIR}` for bundled files; `` !`cmd` `` injects shell output;
   `$ARGUMENTS`/`$name` for args. Sibling reference files (`RULES.md`, `GOTCHAS.md`) the body points to
   keep the body lean.
6. **Skills stack (up to 5) and hotload.** Design a skill to compose — don't assume it's the only one
   loaded.

## Skill kinds in Migx

- **`pat-*`** — pattern auto-load triggers. Fire on the relevant `src/` path; cite the pattern card.
  (Roster: `kanban/patterns/PATTERN-CATALOGUE-PLAN.md`.)
- **Procedure skills** — repeatable workflows (e.g. `build-migx`, `run-tests`, `add-task`,
  `dossier-build`, `pattern-check`).
- **Knowledge skills** — `user-invocable: false` background context.

## Inventory

Keep a row per skill. `pat-*` skills are the auto-load layer over `kanban/patterns/`.

| Skill | Kind | Cites / purpose |
|---|---|---|
| pat-02-rt-no-alloc | pattern | P-02, AP-02 — fires on `src/engine/` `process*()` edits |
| pat-03-benchmark-as-contract | pattern | P-03, P-25 — fires on benchmarks / perf hot paths / perf claims |
| pat-06-controlobject-single-writer | pattern | P-06, AP-03 — fires on ControlObject writes |
| pat-08-generator-not-evaluator | pattern | P-08, P-09 — fires on review/promotion of a change |
| pat-11-refactor-over-layer | pattern | P-11, AP-07 — fires when an edit would add a `_v2`/parallel path |
| pat-16-lock-free-rt-handoff | pattern | P-16, P-17, AP-14 — fires on cross-thread engine edits |
| pat-19-parent-before-parented-ptr | pattern | P-19, AP-13 — fires on make_parented/parented_ptr use |
| pat-21-metal-offload-deadline | pattern | P-21, P-22, AP-12 — fires on `src/rendergraph/`/shaders/waveform edits |
| pat-27-db-schema-migration | pattern | P-27, P-28 — fires on `res/schema.xml` / `src/library/dao/` edits |
| pat-30-controller-via-controlobject | pattern | P-30, AP-15 — fires on `src/controllers/`/`res/controllers/` edits |
| mixxx-upstream-watch | procedure | Incremental upstream mixxxdj/mixxx signal via `gh` → dated log + port-candidate tasks (no git ancestry, ADR-002) |

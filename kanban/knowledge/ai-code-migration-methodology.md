---
id: ai-code-migration-methodology
type: knowledge
title: "AI-assisted code migration methodology — the rulebook for the UI framework port"
status: active
owner: gudjon
created: "2026-07-19"
lastUpdated: "2026-07-19"
source: "https://claude.com/blog/ai-code-migration (Bun Zig→Rust 1M LOC <2wk; Python→TS 165K LOC one weekend), distilled + mapped to the Migx harness"
related:
  - initiative-ui-modernization
  - tasks/ui-migration-judge-rulebook-inventory.md
  - ADR-004-ui-stack-qml-vs-rive-vs-react.md
  - fleet-operating-model.md
  - P-08
  - P-34
---

# AI-assisted code migration methodology (the UI-port rulebook)

The primary undertaking — porting the legacy Mixxx QWidget/XML-skin UI (174 XML skins, `src/skin/legacy`,
`src/widget`) into the **DESIGN.md-token-driven, QML-primary** framework (ADR-004; 212 QML files today),
**one bounded component at a time** — is a large AI code migration. This is the method it follows,
distilled from a proven 1M-LOC migration and mapped to our subagent/workflow/federation harness.

## The one law
**"You don't fix the code — you fix the loop (the rulebook) that produced it."** When adversarial review
catches the same error across components, update the **rulebook** and **regenerate the batch**. Never
hand-patch individual ported files — that hides a systemic rule gap and doesn't compound.

## Prerequisite: build the JUDGE before porting anything
No broad port begins until an equivalence judge exists (this is what
`tasks/ui-migration-judge-rulebook-inventory` builds). A judge is only trusted when it:
1. **passes against the original** component, and
2. **fails against deliberately-broken** code.
For UI, the judge is behavioural + visual: the QML component must match the legacy widget's
ControlObject reads/writes (`[Group],key`), rendered pixels (reuse the headless-CGL pixel harness,
`EVD-0005`), and state transitions. A judge that can't fail is theatre (P-08).

## The six steps (mapped to Migx)
| # | Step | Migx mechanism |
|---|---|---|
| 1 | **Foundation**: rulebook (legacy-widget→QML idiom map + DESIGN.md tokens), dependency map, gap inventory | `ui-migration-judge-rulebook-inventory`; deterministic script maps QML/skin/widget/CO/token edges → module IDs |
| 2 | **Stress-test the rules** on 3 sample components; **discard the output** (refine rules, not progress) | one `Agent` follows the rulebook, one acts as senior reviewer, one refines the rulebook from the diff |
| 3 | **Parallel translation**: implementers fan out, adversarial reviewers gate | `Workflow` pipeline; implementers = smaller model, reviewers = larger; 3rd agent arbitrates. Flag uncertainty `// TODO(port): <reason>` |
| 4 | **Compilation** loop | `just build` per pass (slow compiler → fix errors in parallel, not in-loop); pattern in errors → update rulebook |
| 5 | **Smoke test** — group crashes by root cause | launch via `just app`; crash logs are the source of truth |
| 6 | **Behavioural verification** — diff original vs port outputs | the judge: CO-trace + pixel diff per component; each failure → one fixer agent |

## Queue & resumability
`Done = "the QML module file exists on disk + its judge passes."` Rebuild the work queue from disk
state each iteration (mechanical decisioning: compiler errors, failed judges write the queue). This
makes the migration resumable by construction and lets Claude/Codex/Grok share one lane cleanly.

## Guardrails (failure modes → prevention)
- Hand-patching a ported file → **update the rulebook, regenerate the batch**.
- Weak verification → **judge validated against original + broken code first**.
- Unresumable state → **queue derived from filesystem**.
- Unbalanced tokens → small models fan out, large models write anything other agents follow (rulebook/review).
- Scope creep → the **stress test** catches rule gaps before fan-out.
- House physics still bind: a migrated deck/mixer component must keep **one writer per ControlObject**
  (P-06), never touch the RT thread (P-02), and **fail non-modally** (see `ui-non-modal-error-ux`).

## Migx-specific: UX is the product
This migration is not cosmetic — the project is first and foremost the **human↔software link** (the DJ
and the music). So the target framework must fix the interaction failures the legacy stack has, above
all **modal error dialogs mid-set** (see `ui-non-modal-error-ux`). Every migrated component is scored on
UX fidelity, not just CO/pixel equivalence.

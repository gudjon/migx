---
id: PS-<PFX>-01
type: problem-statement
title: "<one-sentence problem title>"
status: open              # open | resolved | superseded | wont-fix
severity: MUST            # MUST | SHOULD | MAY
ears_class: event-driven  # ubiquitous | state-driven | event-driven | optional | unwanted | complex
dossier: <YYYY-MM-DD-...>
prefix: <PFX>
resolves: []              # [P-NN] patterns this closes / applies
risks: []                 # [AP-NN] antipatterns this could trigger
related: []               # [PS-<PFX>-NN]
acceptance:
  - "<numeric threshold + the benchmark/test/query that checks it — this is the evaluation contract>"
verified_against_code: "<commit-or-date — every file:line below was opened at HEAD>"
created: "<YYYY-MM-DD>"
lastUpdated: "<YYYY-MM-DD>"
---

# PS-<PFX>-01 — <title>

**EARS statement (one sentence, matches `ears_class`):**
> When <trigger/state>, the <system/component> shall <required behavior> within <measurable bound>.

*(event-driven: "When X …" · state-driven: "While X …" · ubiquitous: "The system shall …" ·
unwanted: "If X, then the system shall …" · optional: "Where <feature>, the system shall …")*

## Context
<The specific code path this touches — file:line references, opened at HEAD (record the commit in
`verified_against_code`). For a perf PS: the hot loop, the current cost, the target cost.>

## Acceptance contract (how the loop closes)
The `acceptance:` block above is machine-consumable. Spell out here exactly how each criterion is
measured:
- **Benchmark / test:** `<ctest -R ... | mixxx-benchmark ... | a script>`
- **Baseline:** `<the EVD-* record of the pre-change number>`
- **Threshold:** `<e.g. ≥1.5× throughput, or frame time ≤ 8ms p99, with no RT-thread allocation>`
- **Guard:** `<the check that fails if we regress a house-physics invariant (MG-6)>`

## Out of scope
<Explicitly excluded so the PS stays atomic.>

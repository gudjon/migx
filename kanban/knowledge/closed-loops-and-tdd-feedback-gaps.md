---
id: closed-loops-and-tdd-feedback-gaps
type: knowledge
title: "Closed loops map — what we optimize, what's missing, TDD for agents"
status: active
owner: gudjon
created: "2026-07-18"
lastUpdated: "2026-07-18"
related:
  - P-01
  - P-03
  - P-08
  - P-09
  - AP-01
  - AP-05
  - AP-06
  - kanban/playbook/03-harness-engineering-outer-ring.md
sources:
  - "X field 2026: verification is the closed loop (Boris Cherny / Claude Code discourse)"
  - "X: RED-GREEN TDD enforcement for agents; plan→execute→independent review harnesses"
  - "In-repo: dossiers EVD-*, PS acceptance, federation P-08, pre-commit, ctest"
---

# Closed loops in Migx development — map + TDD gaps

**Question:** Where are the closed loops, what do they optimize, and where is feedback missing so TDD (especially for Claude Code) can be stronger?

**Doctrine:** `P-01` Trigger → Capture → Intelligence → Adjustment. Sensor independent of actuator (`P-08`). Contract frozen before work (`P-09`).

---

## 1. Closed loops that exist (and what they optimize)

| Loop | Trigger | Capture | Intelligence | Adjustment | Optimizes |
|---|---|---|---|---|---|
| **MTL waveform CPU preprocess** | Bench run / wave seal | `EVD-0001` (p50/p99 µs RGB/Filtered) | Compare to pin (`P-25`) | Next MTL dossier (VBO, scrub) | Frame-time **CPU rebuild** cost |
| **MTL VBO / upload** | Bench + GUI dogfood | `EVD-0002` | Delta vs EVD-0001 upload | Persistent VBO path | Per-frame **CPU→GPU copy** on static frames |
| **MTL scrub regime** | Combined scrub bench (CGL) | `EVD-0003` (~80% CPU / ~18% upload) | Lever selection | Sliding-window rebuild (in progress) | **Dirty scrub** combined frame cost |
| **DSP EQ IIR** | Headless filter bench | `EVD-DSP-01` | Budget share of RT period | **NO-GO** Wave-2 SIMD (parked) | Whether EQ is worth SIMD |
| **SoundIO / CA soak** | Soak tool + engine gtests | `EVD-PLT-0001` | Zero late/hard_err | No CA rewrite yet | **RT I/O stability** on macOS 26/M4 |
| **Platform CI surface** | PR / push | Single macOS arm64 job | Green/red CI | Packaging DORMANT | **CI clarity/speed** (not product audio) |
| **EXO transition proof** | Fixture-only agent run | `TRANSITION-PROOF` + `P08-EVAL-codex` | Camelot + energy legal | Hybrid/session co-pilot dogfood | **Agent can plan set offline** |
| **EXO co-pilot why-next** | `just exo-copilot-why` | `COPILOT-WHY-NEXT.*` | Ranked next + explain | QML fixture mirror | **Layer B offline co-pilot** UX contract |
| **Federation P-08** | Mail type evaluate / handoff | `messages/closed` + resolution | Independent peer | Seal or reopen | **Author ≠ grader** across agents |
| **pre-commit fast gate** | Commit attempt | format/tidy/qmllint | Hook fail | Fix before commit | **Style/static** quality |
| **Grok signal scout** | 15m scheduler | `signal/*.md` + progress | Relevance vs Strategy | Handoff or hold | **Field intel → product direction** |
| **House physics skills** | Edit engine/CO paths | skill + review | pat-02/06/08… | Block or fix | **RT / single-writer safety** |

### Loop quality scale

| Quality | Meaning | Examples |
|---|---|---|
| **Hard closed** | Numeric contract + re-runnable bench/test + independent pin | EVD-0001/0002/0003, EVD-DSP-01 |
| **Soft closed** | Measurable proof but partial seal / manual step | EXO P-08 PASS, PLT soak (no USB/AirPods), VBO mergeable-pending-GUI |
| **Process closed** | Peer mail or pre-commit, not product metric | Federation drain, clang-format |
| **Open / aspirational** | Named but no sensor or no re-check | Nightly underrun SLO, live co-pilot → CO, shared-library capability |

---

## 2. Missing or weak feedback loops (TDD gaps)

### A. Product correctness (RED-GREEN under-used)

| Gap | Symptom | Stronger TDD loop |
|---|---|---|
| **Few failing tests written first** for new features | Agent implements then hopes `ctest` green | Wave contract: **write failing gtest → commit RED → implement → GREEN** (frozen `PS` names the test filter) |
| **~950 TEST_* macros** but **sparse feature contracts** for Layer B/C | EXO/QML/shared-lib can ship without new tests | Each `PS` must name `ctest -R <Filter>` or fixture script in `acceptance:` |
| **No tautology guard in CI** | Easy to weaken test to match code (`AP-10`) | Evaluator session re-runs **frozen** test from parent commit of the PS |
| **Visual / GUI half often manual** | EVD-0002/0003 GUI residual | Headless CGL path is good — require it for waveform waves; screenshot golden optional |

### B. Performance loops incomplete

| Gap | Symptom | Stronger loop |
|---|---|---|
| **No scheduled re-run of EVD pins** | Baseline drifts; win not re-checked | Trigger: nightly or post-merge `mixxx-test --benchmark_filter=…` → Capture under `results/` → fail task if p99 regresses |
| **Underrun SLO not automated** | PLT soak is one-shot tool | Loop: soak script in CI-ish or cron on M4 box; open task on fail |
| **Sliding-window wave mid-flight** | Code dirty without EVD delta yet | RED: bench asserts p50 ≤ EVD-0003 − X%; GREEN only when threshold met |
| **DSP NO-GO not wired as permanent gate** | Someone may re-open SIMD without budget | Pin “EQ < N% of period” as guardrail in PS/ADR note |

### C. Independence (`P-08`) thin outside EXO

| Gap | Symptom | Stronger loop |
|---|---|---|
| **Codex verify mail can sit open forever** | `verify-evd0003` stayed open many waves | SLA: open evaluate mail auto-escalates; or CI job *is* the evaluator |
| **Generator often runs own ctest** | Convenient, violates spirit of P-08 | Default: author runs RED; **CI or second peer** owns GREEN verdict for seal |
| **check-work / review skills optional** | Not mandatory on every wave | Stop-hook or wave gate: `/check-work` or codex drain before “done” |

### D. Live product loops (co-pilot / share / library)

| Gap | Symptom | Stronger loop |
|---|---|---|
| **Intent → CO → deck behavior** | No automated “Ack moves playhead/load” | Integration test: fixture intent → mock CO → assert control value (no audio) |
| **Shared-library capability** | Spec only, no fixtures yet | W1: offline EXO 2-DJ share fixture + schema check (like EXO) |
| **Hybrid Spotify policy** | Policy in JSON; weak runtime enforce | Test: multi_deck_allowed=false refuses dual load |

### E. Harness / agent loops

| Gap | Symptom | Stronger loop |
|---|---|---|
| **Grok empty waves** | 15m poll with no intel | Either lower cadence or require one actionable artifact or explicit “no-op with reason” task advance |
| **No auto link commit ↔ PS acceptance** | Hard to bisect “which wave closed which PS” | Commit message / trailers: `Closes: PS-MTL-03 wave-2` + CI parses |
| **pre-commit ≠ product sensor** | Green format, broken bench | Ladder already in rules; enforce for perf PRs: bench filter required |

---

## 3. Target TDD shape for Claude Code (and Grok) on Migx

Align with field consensus (**verification is the loop** — not bigger prompts) and house physics:

```text
1. FREEZE contract     PS acceptance: command + threshold + machine (P-09)
2. RED                 write/extend test or bench; show fail (or NO-GO proof)
3. GREEN               minimal change; same command passes
4. REFACTOR            only while green
5. INDEPENDENT EVAL    second peer / CI / fresh session runs same command (P-08)
6. CAPTURE             EVD-* or test log at stable path
7. SEAL or HALT        91-LOOP-CLOSURE cites EVD; never green-over-red (AP-01)
```

### Concrete harness upgrades (high leverage, small)

1. **Wave template force-TDD**  
   Every execution wave row: `RED command` · `GREEN command` · `EVD path`. No wave without RED.

2. **CI as default evaluator for engine/render**  
   On PR: `ctest -R 'Engine|Waveform|SoundSource'` + optional `benchmark_filter` for labeled perf PRs.

3. **Mandatory independent eval for seal**  
   Seal checklist: codex/CI log path; author self-green insufficient.

4. **EVD regression job (nightly on M4)**  
   Re-run BM_Waveform* + BM_EngineFilter*; open task if p99 > pin × 1.1.

5. **Fixture-first for Layer B**  
   EXO-style: schema + fixtures + proof script before C++/QML chrome.

6. **Stop shipping open loops**  
   Shared-library, live co-pilot CO, dual-device soak: either attach a sensor or mark `status: research` not execution.

---

## 4. X field signal (implementation practices)

Themes (not vendor endorsements):

| Theme | Practice for Migx |
|---|---|
| **Verification is the closed loop** | Invest in sensors (tests, EVD, CI) more than prompt length |
| **Plan → execute → independent review → release** | Matches dossier waves + P-08 + 91-LOOP-CLOSURE |
| **RED-GREEN enforced** | Failing test first; some harnesses delete code written before tests |
| **Reproduce bug / watch fail / smallest fix** | Prefer over multi-file speculative refactors |
| **Hooks as loop infrastructure** | We have RT/worktree warns; add verify-gate: no claim “done” without named command green |
| **Subagent = evaluator** | Spawn read-only review / codex drain; never author seals |

---

## 5. Priority missing loops (if strengthening TDD now)

| Priority | Loop to close | Sensor to build |
|---|---|---|
| **P0** | Scrub optimization in flight | Failing/threshold bench vs EVD-0003 before merge |
| **P0** | Independent eval latency | CI or auto-close path for evaluate mail |
| **P1** | Nightly EVD re-pin | Cron/agent job writing delta report |
| **P1** | Layer B feature TDD | Every co-pilot/share change ships fixture test |
| **P2** | Live CO intent | Unit test CO reconciler without audio |
| **P2** | Underrun continuous | Soak in schedule, not only PLT one-shot |

---

## 6. One-line summary

We **already close** hard loops on **waveform/DSP/CA measurement** and **soft loops** on EXO offline co-pilot and federation review. We **under-close** **RED-GREEN TDD for new features**, **scheduled re-verification of EVD pins**, **fast independent eval**, and **live Layer B/C product sensors**. Strengthening TDD for Claude Code means making the **failing contract runnable first**, and making **CI/second peer** the default green light — not the authoring session.

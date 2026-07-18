---
id: signal-2026-07-18-ux-product-design-harness-migx
type: signal-brief
from: grok-signal
date: "2026-07-18"
relevance: actionable
topics: [ux, co-pilot, friction, evidence, layer-b, research-quality, delivery]
mapped_to:
  - ADR-005
  - world-model-experience-ontology
  - closed-loops-and-tdd-feedback-gaps
  - headless-sim-ground-truth-agentic-cli
  - output-verification-formats-naming
  - res/qml/CoPilot
  - initiative-ai-djing-product
sources:
  - "Product Design & UX Research knowledge harness (DC-PDUX; public-material integration; domains 1–6)"
  - "X field: paper-first design vs AI slop; AI music co-pilots; UX research method discipline"
  - "Migx HEAD 92e4b2c — federation clean; MTL Wave 2a landed"
---

# Signal — UX/product-design harness → Migx co-pilot & agent surfaces

## Federation / git hygiene (this wave)

| Check | Result |
|---|---|
| `migx-fed doctor` | OK |
| Open mail → grok-signal | **empty** |
| Open fleet queue | **empty** |
| Active claims | **none** |
| Working tree | **clean** |
| `main` vs `origin/main` | **92e4b2c** aligned |

Peers recently closed MTL Wave 2a verify loops (cache/axes-color). Grok stays off waveform sources.

---

## Method (harness runs applied to Migx)

Using the **Product Design & UX Research** compounded harness (not book summaries):

| Run | Harness focus | Migx target |
|---|---|---|
| **A — Interaction friction** | Understand → decide → enter → correct → trust → submit | Co-pilot chrome, shared-lib invite, prefs, load flow |
| **B — Research plan** | Decision risk → question → method → evidence standard | What we measure for co-pilot “good” (accept rate ≠ research theater) |
| **C — Design review prep** | Narrative, rationale, decision needed | Hand off design asks to Claude with scenario + evidence |
| **D — UX failure diagnosis** | Assumption → perception → behavior → org decision | Agent “done” without user success sensor |
| **E — Theme scan** | friction, evidence, ethics, implementation-quality | Cross Layer A/B/C |
| **F — Delivery quality** | Intent survives implementation | EXO/intent → CO → deck; output verification |

---

## Domain 1 — Interaction friction (Migx hotspots)

| Friction | Today | Design implication |
|---|---|---|
| **Co-pilot why-next** | Offline JSON → QML fixture; Predict→Ask→Explain | Minimize questions; one primary proposal; clear **Ack / Dismiss / Why** recovery |
| **Hybrid crate (local + stream)** | `sequence-only` vs multi-deck badges | Playability badge **before** load (local / lan / prep) — shared-lib note |
| **Intent without feedback** | Intent inbox fixture; CO reconciler incomplete | Always show **state**: proposed → active → expired (`_llm_guidance` + UI) |
| **Library external sources** | iTunes/Serato-shaped; shared-lib not built | Progressive disclosure: connect share → browse → import → plan |
| **Agent/CLI headless** | Spec only | Same verbs as GUI; never a second hidden flow |

**Operating rule:** Every forced decision needs a default, an escape, and a completion signal (harness Domain 1).

---

## Domain 2 — Research judgment (avoid theater)

| Decision risk | Bad evidence | Better sensor |
|---|---|---|
| “Co-pilot helps DJs” | Author likes JSON | Dogfood script: 5 scenarios, accept/reject, time-to-decide |
| “Sliding-window feels smoother” | Author greps EVD | EVD-0003 delta **and** short scrub usability (even n=3 internal) |
| “Shared crates wanted” | Plex feature envy | Interview 2–3 DJs: LAN share vs USB only; method fit before build |

**Rule:** Method follows **decision risk**, not available tooling. Agents must not treat EVD-only as UX validation when the claim is human experience.

---

## Domain 3 — Ethics / agency (co-pilot power)

| Risk | Migx stance |
|---|---|
| Co-pilot **manipulates** order without understanding | Always explain (Camelot + energy + policy); human Ack before CO write (`P-06`) |
| Automation hides RT risk | Never auto-load prep-only as multi-deck |
| Privacy of shared crates | Host ACL; no silent whole-disk share |

User-friendliness without agency = ethical debt (harness Domain 3).

---

## Domain 4–5 — Communication & evidence chain

**Stakeholder narrative for next design review (Claude/UI):**

1. **Audience:** DJ under set pressure + agent co-pilot.  
2. **Scenario:** Peak track ending; need next that lifts energy and is legal.  
3. **Rationale:** EXO graph + why-next ranking.  
4. **Evidence:** TRANSITION-PROOF / COPILOT-WHY-NEXT + fixture check.  
5. **Decision needed:** Ship QML Ack path to CO vs keep offline dogfood.  
6. **Feedback boundary:** No RT/network in this PR.

**Experience evidence chain (Domain 5):**

```text
Assumption: agent plan is useful
  → Design: Predict / Ask / Explain / Ack
  → Behavior: accept rate, edit rate, time-to-load
  → Instrumentation: intent log + outcome (played? cancelled?)
  → Decision: promote CO reconciler or revise ranking
```

Missing link today: **instrumentation of Ack outcomes** (closes the product loop).

---

## Domain 6 — Delivery quality (implementation survives intent)

| Intent | Spec / acceptance | Sensor |
|---|---|---|
| Offline co-pilot correct | `just exo-copilot-why` + fixtures | `exo-fixtures-check` |
| Output shapes stable | `output-verification-formats-naming` | proposed `verify-outputs` |
| Headless agent can mix | `headless-sim-…` phased go | SimScenario gtest (not built) |
| Perf win real | EVD pin | Independent bench re-run |

**Implementation-quality:** Wave TDD = RED test first; freeze acceptance (`P-09`); independent eval (`P-08`).

---

## X field (light, product-adjacent)

| Theme | Migx takeaway |
|---|---|
| Paper/sketch before AI UI (field designers) | Keep DESIGN.md → Theme; agents implement **after** scenario narrative |
| AI music co-pilots framing “inspiration → realization” | Migx differentiator is **engine-native depth**, not chat next to decks |
| UX research method discipline (qual/quant, generative/evaluative) | Match method to stage: EXO generative; scrub EVD evaluative |
| HCI “UX agents” research (simulated users) | Optional later for co-pilot A/B — **not** substitute for EVD/house physics |

---

## Actionable asks (for Claude / product)

1. **Friction audit (Run A)** on Co-Pilot.qml: list forced decisions; propose one-screen Ack + playability badges.  
2. **Instrument Ack** (even log-only fixture) so evidence chain has a sink.  
3. **Do not** treat MTL Wave 2a green as UX complete for co-pilot.  
4. When scheduling sim: scenarios double as **usability task scripts** (load A/B, xfade, assert).

## Out of scope this wave

`src/**` edits; inventing new UI chrome without scenario narrative.

## Handoffs

None mandatory (0/2). This brief is **signal** for when Layer B UX resumes; Claude can open a task/dossier from item 1–2.

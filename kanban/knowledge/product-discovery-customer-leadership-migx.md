---
id: product-discovery-customer-leadership-migx
type: knowledge
title: "Product discovery & customer leadership applied to Migx (DC-PDCL harness)"
status: active
owner: gudjon
created: "2026-07-18"
lastUpdated: "2026-07-18"
harness_ref: "07-Product-Discovery-Customer-Understanding-Leadership (DC-PDCL)"
related:
  - kanban/Strategy-Current.md
  - initiative-ai-djing-product
  - closed-loops-and-tdd-feedback-gaps
  - world-model-experience-ontology
  - dj-shared-library-capability
  - headless-sim-ground-truth-agentic-cli
  - signal-2026-07-18-ux-product-design-harness-migx
defers_to:
  - kanban/Strategy-Current.md
note: >
  Systematic pass of DC-PDCL runs A–F against Migx product bets. Fidelity: public discovery
  frameworks + in-repo strategy/code anchors. Not F1 book extraction. Longer harness work continues
  by re-running domain events against new evidence.
---

# Product discovery & leadership — Migx operating map

**Purpose:** Turn the **Product Discovery / Customer Understanding / Leadership** harness (DC-PDCL) into
**Migx-specific questions, evidence, opportunities, and tests** — rooted in Strategy, EXO, Apple Silicon
trust, and agent seams — so agents stop inventing “customer truth” from code green alone.

**Neighbor files:** UX interaction quality → `signal-2026-07-18-ux-product-design-harness-migx` / DC-PDUX.  
This file owns **what bets to make**, not button layout detail.

**Discovery → execution chain (harness):**

```text
market context → segment → lived situation → past behavior → problem evidence
  → opportunity map → desired outcome → assumptions → tests → product judgment
  → team decision → execution → shipped consequence → learning memory
```

---

## 0. Hygiene (this pass)

| Check | Result |
|---|---|
| Federation queue | empty (at pass start) |
| Git | clean `main` (signal commits after) |
| Active claims | none on grok lane |

---

## Run A — Customer truth audit (Domain 1)

### Who we claim to serve (Strategy)

| Claim (repo) | Segment | Risk if wrong |
|---|---|---|
| Cursor-for-AI-DJing | DJs who want **depth of permission** + AI in the mix | Build for “AI music toy” users |
| macOS 26+ Apple Silicon only | Pro/home Mac DJs on M-series | Ignore Windows club install base by design (ADR-006) |
| Freemium co-pilot → Pro | Willing to pay for Intelligence | Never tested willingness |

### Customer-truth questions (Mom-Test style — ask for past behavior)

| Ask | Strong evidence | Weak / theater |
|---|---|---|
| How do you **prep a set today**? | Screen share of Serato/rekordbox/USB | “I’d use AI if it were good” |
| Last time a **transition failed** mid-gig? | Specific track pair + what broke | “Co-pilot would be cool” |
| How do you **share crates** with a partner? | USB, Dropbox, Plex, nothing | Compliments about Migx vision |
| Ever **paid** for DJ AI / stems / cloud library? | Receipt / churn story | Hypothetical subscription |
| What would make you **not** load a suggested track? | Trust, audio glitch, wrong key | Feature wishlist |

### Repo reality check

| Source of “truth” today | Type | Bias |
|---|---|---|
| `Strategy-Current.md` pillars | Founder thesis | No field sample |
| EXO TRANSITION-PROOF | Technical feasibility | Not customer demand |
| MTL EVD-* | Performance trust | Necessary ≠ sufficient for buy |
| X DJ/AI co-pilot posts | Weak signal | Selection + hype |

**Audit verdict:** We have **strong technical opportunities** and **weak customer-behavior evidence**. Primary gap is **past-behavior interviews**, not more ontology schemas.

---

## Run B — Opportunity mapping (Domain 2)

### Desired outcomes (from `initiative-ai-djing-product`)

| Outcome ID | Customer behavior change | Business value | Sensor today |
|---|---|---|---|
| O1 | Accepts co-pilot next-track mid-session | Differentiator; freemium | **Missing** (no Ack instrumentation) |
| O2 | Dual-deck + co-pilot with **zero underruns** | Trust / word-of-mouth | EVD/soak partial |
| O3 | Preps hybrid set (local + stream ids) offline | Crate depth | EXO fixtures only |
| O4 | Shares crate with another DJ | Network effects | Spec only (`dj-shared-library-capability`) |

### Opportunity map (problem space first)

| Opportunity | Evidence | Solution space (do not jump early) |
|---|---|---|
| **Opp-A:** “Next track under pressure is costly” | DJ practice literature + co-pilot thesis; **no n≥5 interviews** | Ranking UI, keyboard Ack, controller map |
| **Opp-B:** “AI that glitches dies” | Industry lore + our P4; **EVD closed loops** | MTL/DSP measurement (in flight) |
| **Opp-C:** “Catalog is multi-source” | Spotify landscape research; hybrid EXO | Sequence-only policy, not dual Spotify stream |
| **Opp-D:** “Partner can’t see my crate” | Shared-lib capability note; Plex as prior art | Migx-native share (no Plex dep) |
| **Opp-E:** “Agents can’t prove mix quality” | TDD/sim research | Headless scenario harness |

### Smallest tests that change decisions

| Opportunity | Smallest test | Kill criterion |
|---|---|---|
| Opp-A | 3 working DJs dogfood offline why-next on their real crate export | 0/3 would Ack any proposal without heavy edit |
| Opp-B | EVD-0003 + soak gates on M4 | Underrun or p99 regression |
| Opp-C | Hybrid session fixture + policy badges | Users try dual Spotify multi-deck and blame us |
| Opp-D | Paper prototype of “known shares” list | “USB is enough forever” |
| Opp-E | One SimScenario gtest green in CI | Never used by agents for RED/GREEN |

---

## Run C — Assumption test design (Domain 2 + 3)

| Assumption | Type | Kill-risk | Test | Bias risk |
|---|---|---|---|---|
| DJs want AI **in** the decks, not a side chat | Solution | High | Observe prep+live workflow; competitor usage | Founder love of Cursor analogy |
| Camelot+energy is **enough** for trust | Capability | Medium | Show wrong-key proposal; measure reject | Availability of KeyUtils math |
| macOS-only is acceptable for first beachhead | Segment | High | Count target users already on M-Mac | WYSIATI on our build box |
| Offline EXO dogfood predicts live Ack | Transfer | High | Same users after live CO path | Lab vs gig |
| Shared crates > USB for partners | Behavior | Medium | Ask last 3 partner gigs | Status-quo inertia |
| Freemium co-pilot converts | Business | High | Fake-door or waitlist + willingness talk | Optimism |

**Bias control checklist (Domain 3):** outside view (what % of AI-DJ tools die?); base rate; planning fallacy on “90-day co-pilot”; anchoring on Mixxx feature count.

---

## Run D — Bias & inclusion (Domain 3 + 4)

### Missing realities (default-user is “us”)

| Missing | Why it matters | Coverage plan |
|---|---|---|
| Club / dark room / gloves controllers | UI density, font, latency feel | Controller dogfood script |
| Non-English DJs | Localization of co-pilot explain | Later; don’t English-only lock EXO guidance forever |
| Vinyl / DVS-first DJs | Different prep | Explicit non-goal or segment defer |
| Windows/Linux DJs | ADR-006 excludes | Honest marketing; no fake support |
| Women / underrepresented DJs in sample | Invisible-women style gap | Deliberate recruit in interviews |
| Time-poor residency DJs | Won’t run agent harness | Product must work in 30s under pressure |

**Data gaps:** no CRM of target DJs; no win/loss; no Accept-rate telemetry; no gig post-mortems stored as `CustomerEvidenceCaptured` events.

---

## Run E — Product leadership & execution (Domain 5 + 6)

### What the repo already institutionalizes (strength)

| Leadership system | Migx artifact |
|---|---|
| Quality / craft standards | House physics P-02/P-06; pre-commit |
| Independent eval | P-08; federation codex/claude roles |
| Evidence for perf | EVD-*, PS acceptance |
| Multi-agent decision rights | peers.yaml; claims; DRI per dossier |
| Learning memory | dossiers, signals, kanban tasks |

### Where leadership suppresses learning

| Failure | Symptom | Fix |
|---|---|---|
| **Tech evidence crowding customer evidence** | Green EVD → “product is ready” | Dual scorecard: EVD + customer outcome |
| **Discovery debt** | No interview log SSoT | `kanban/discovery/` or federation `signal` type for CustomerEvidence |
| **Escalation** | Value judgments only for Gudjon (good) but no cadence of customer reviews | Monthly discovery review ritual (even 30 min) |
| **Stage fit** | Building Layer C while O1 unvalidated | Time-box co-pilot live path vs more EXO polish |

**Truth-safe leadership rule:** Agents may **not** close a product bet with only technical EVD. Product bets need a **CustomerEvidenceCaptured** or explicit **assumption still open** flag in 91-LOOP-CLOSURE.

---

## Run F — Cross-domain theme scan (selected tags)

| Theme | Migx reading |
|---|---|
| `#customer-discovery` | Under-invested vs engineering discovery |
| `#assumption-testing` | Strong for DSP NO-GO; weak for freemium/co-pilot love |
| `#cognitive-bias` | Cursor analogy anchors solution space |
| `#learning-memory` | Excellent for code/dossiers; thin for customers |
| `#ethics` | Co-pilot agency + playability honesty (good specs) |
| `#systems` | Agents + federation are execution system; not discovery system |

---

## Domain events to start recording (governance)

Adopt harness event types as **lightweight markdown or YAML** under `kanban/discovery/` (proposed):

| Event | Minimum fields |
|---|---|
| `CustomerEvidenceCaptured` | segment, context, evidence type, quote/behavior, confidence, implication |
| `OpportunityFormed` | statement, linked evidence ids, uncertainty |
| `AssumptionDeclared` | type, kill-risk, test, threshold |
| `ProductBetChosen` | opportunity, assumptions, rejected alternatives, non-negotiables (link PS/ADR) |
| `LearningRecorded` | outcome, revisit trigger, owner |

Until that folder exists, use **federation signal** with type status + subject `discovery-*` and this note’s IDs.

---

## X field (light, discovery-aligned)

| Signal | Use carefully |
|---|---|
| Mom Test / Lean still canonical in 2026 indie discourse | Scripts for Opp-A interviews |
| Continuous discovery / four fits | Cadence: discovery weekly even while coding |
| AI music “DJ mode” hype (big labs) | Competitive context; not our beachhead proof |
| Test-anything / regression culture | Aligns with sim + EVD; apply to product claims too |

---

## Systematic loop (longer harness work)

**Cadence for agents (Grok + Claude):**

1. **Each product week:** one Run A or B micro-pass — update evidence table or kill an assumption.  
2. **Each EXO/co-pilot PR:** require link to Opportunity + Assumption or mark `tech-only`.  
3. **Each MTL/DSP seal:** dual scorecard — performance closed; product outcome still open/closed.  
4. **Quarterly:** Run E leadership diagnosis on whether discovery debt grew.  
5. **Never:** treat X likes or founder enthusiasm as `CustomerEvidenceCaptured`.

**Queue continuity:** this note is living SSOT for DC-PDCL@Migx; deepen with real interview notes (F1 customer, not F1 books).

---

## Immediate product bets (judgment)

| Bet | Status | Next discovery action |
|---|---|---|
| Offline EXO co-pilot | Tech feasible | **Dogfood with real crates** + Ack logging design |
| Live CO path | Incomplete | Assumption test: does offline accept predict live? |
| Shared libraries | Spec | 2 interviews on partner crate pain |
| Headless sim | Phased go | Build for **engineering** learning first; product narrative second |
| Freemium | Unvalidated | Explicit open assumption; no billing code yet |

---

## Bottom line

Migx has a **strong technical discovery system** (EVD, P-08, dossiers) and a **weak customer discovery system**. The DC-PDCL harness says the bottleneck is not more features — it is **past-behavior evidence**, **assumption tests for co-pilot value**, **inclusion of non-default DJs**, and **learning memory for customer truth** beside code truth.

**Next human step that unlocks agents:** 3 structured DJ conversations (Run A script) stored as `CustomerEvidenceCaptured`; then re-rank Opp-A–E.

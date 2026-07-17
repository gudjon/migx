---
id: design-md-ui-modernization
type: knowledge
title: "DESIGN.md-driven UI modernization for Migx — analysis & proposal"
status: active
owner: gudjon
created: "2026-07-17"
lastUpdated: "2026-07-17"
source: "https://github.com/google-labs-code/design.md · https://stitch.withgoogle.com/docs/design-md/specification"
defers_to:
  - kanban/architecture/ddd/bounded-contexts/arch-qml-ui.md
  - kanban/architecture/ddd/bounded-contexts/arch-skin-widgets.md
---

# DESIGN.md-driven UI modernization for Migx

**Vision (next major release):** Migx's skins and new UI are driven by **DESIGN.md** — a markdown
design-system spec — so look-and-feel is authored/versioned as code and applied consistently by humans
and coding agents alike.

## What DESIGN.md actually is (spec, alpha, Apache-2.0)
A two-layer file: **YAML front matter = machine-readable design tokens** (colors, typography, spacing,
elevation, shapes, component variant states) with a `{colors.primary}` token-reference system, plus
**markdown prose = human rationale** (Overview, Colors, Typography, Layout, Components, Do's/Don'ts). The
`@google/design.md` npm CLI provides `lint` (validates + checks **WCAG contrast**), `diff` (token
regressions), `export` (→ Tailwind v3/v4, W3C DTCG tokens), `spec` (format for agent prompts). It was
explicitly designed for **AI agents to apply a design system consistently** — which aligns exactly with
the Migx harness (everything-is-code, agent-native).

## The fit / the gap (honest)
DESIGN.md is **web/frontend-oriented**: `export` targets Tailwind + W3C DTCG only. It has **no Qt/QML
output**. So it is NOT a drop-in UI generator for Migx — it is a **design-token source of truth + a
bridge we build**. That bridge is small and squarely in harness territory (a generator + a lint gate),
because DESIGN.md tokens are just structured data.

## Proposed architecture — DESIGN.md as SSoT + a Qt bridge
```
res/design/DESIGN.md            # the SSoT: tokens + rationale (one home, MG-3)
   │  (generator, like our gen-index.py scripts)
   ├─▶ res/qml/Theme.qml         # a QML singleton: readonly color/typography/spacing/shape properties
   ├─▶ generated QSS variables   # for legacy QSS skins (arch-skin-widgets) — optional, phase 2
   └─▶ W3C DTCG / Tailwind        # via the stock `export` (for any web surface / docs / marketing)
```
- **First target = `arch-qml-ui`** (the new Qt Quick UI, `fork_delta: migx-new`) — QML consumes a
  generated `Theme` singleton; this is greenfield and low-risk.
- **Second target = `arch-skin-widgets`** (legacy QSS skins) — generate QSS design-token variables the
  skins reference; heavier, upstream-tracked, phase 2+.
- **Lint as a gate:** DESIGN.md `lint` (WCAG contrast, broken token refs) runs in `just lint-frontend`
  + the CI discipline suite — accessibility becomes an enforced gate, not a hope.
- **The `spec` output** feeds a Migx `pat-*`/skill so agents editing UI apply the tokens correctly.

## Why this fits Migx's harness (not just a UI change)
- Tokens at a stable path + a generator + a `--check` lint = the same pattern as our pattern-index /
  DDD-roster generators. It IS a closed loop (MG-1): edit DESIGN.md → regenerate Theme → lint → UI.
- Agent-native by construction — the whole point of DESIGN.md.
- Respects the fork: `res/design/` + a generator are **additive**; QML theming is new (`migx-new`); the
  legacy-QSS bridge tracks upstream skins carefully.

## Risks / unknowns to resolve in a dossier
- DESIGN.md is **alpha** — pin a version; the format is evolving (`diff`/lint help absorb churn).
- The Node `@google/design.md` CLI is a **build/dev dependency** (fine — it runs in the generator/CI,
  not shipped in the app).
- Component-level tokens map cleanly to QML properties; complex interaction states may need convention.
- Legacy QSS skins are the hard part — likely a separate, later dossier.

## Recommendation
This spans several dossiers (the bridge/generator; QML theme adoption; skin migration; the agent skill),
so it warrants a **standing initiative** — `initiative-design-md-ui` — for the **next major release**,
with dossiers under it (prefixes to register: e.g. `DUI`). Start with a **spike dossier**: adopt
DESIGN.md for one QML screen via a generated `Theme.qml`, prove the round-trip + the lint gate, measure
the authoring ergonomics. Then decide on the skin migration.

**Next step:** register `initiative-design-md-ui` + a `DUI` spike dossier when the next-release planning
opens. Backlog: `kanban/tasks/` (this doc is the analysis input). Do not adopt the alpha format
wholesale until the spike validates the bridge.

## Ground the DESIGN.md work in product-design/UX + discovery (required reading before the dossier)
The DESIGN.md UI modernization is not just a token pipeline — it must be driven by real product design,
UX research, and customer understanding so the AI-DJing UI serves actual DJ workflows. Before the `DUI`
dossier, incorporate pointers from:
- `/Users/gudjon/code/oz-platform/kanban/references/knowledge-base/05-Product-Design-UX-Research.md`
  (design + UX-research craft) — apply to: what a DJ needs to see/act on in a live set, the
  agent-co-pilot surface, accessibility (DESIGN.md's WCAG lint aligns here), and the token/component
  system's ergonomics.
- `/Users/gudjon/code/oz-platform/kanban/references/knowledge-base/07-Product-Discovery-Customer-Understanding-Leadership.md`
  (product discovery + customer understanding) — apply to: validating the AI-DJing UI direction with
  real DJs, discovery before building the skin engine, and framing the differentiator.

Distill-don't-clone: take the transferable design/discovery method (not OZ domain). These references
inform the spike dossier's PROBLEM (who feels it, what to validate) and the UX acceptance criteria.

---
id: signal-2026-08-07-strategy-ui-adr-x-alignment
type: signal-brief
author: grok-signal
created: "2026-08-07"
topics:
  - strategy
  - adr-004
  - adr-008
  - ai-dj-copilot
  - agent-cli-spine
  - design-md
  - freemium-privacy
  - anti-automix
sources:
  - kanban/AGENT-ONBOARDING.md
  - kanban/Strategy-Current.md
  - kanban/initiatives/initiative-ai-djing-product.md
  - kanban/architecture/decisions/ADR-004-ui-stack-qml-vs-rive-vs-react.md
  - kanban/architecture/decisions/ADR-005-open-core-plus-proprietary-intelligence.md
  - kanban/architecture/decisions/ADR-008-cli-core-two-equal-clients.md
  - kanban/federation/signal/2026-07-17-deep-x-community-alignment.md
relevance: actionable
promoted_to: null
---

# Signal — Strategy / UI ADRs × X (2026-08-07)

Complements `2026-07-17-deep-x-community-alignment.md`. **Does not reorder**
Strategy pillars. Amplifies Layer B + ADR-008 + anti-Automix messaging.

## Executive (one screen)

| Migx bet | Aug 2026 X | Action |
|---|---|---|
| Predict → Ask → Explain (not Automix) | Prompt-DJ / infinite-jam vs “human drives, AI multiplies” | Keep anti-identity; lead with **why** |
| Cursor depth of permission | Long-horizon agents; plan→verify loops | Session Composer + EXO urgency (S3) |
| **ADR-008 CLI spine** | CLI = agent-native; GUI = human adapter | Ship parity; agents discover via `system.capabilities` |
| **ADR-004 QML-primary** | Electron still wrong for continuous GPU+audio | **Accept ADR-004** — freeze Surface A |
| DESIGN.md tokens | Viral + “tokens alone drift” | DESIGN.md → Theme.qml **+ lint** |
| Freemium / privacy | Local-first music apps | Free = local co-pilot; Pro = cloud multi-model |
| Harness > model | Still orthodoxy | Onboarding Tier 2 cites ADR-008 |

**Net:** X still **amplifies** the board. New load-bearing piece since July: **ADR-008**
(CLI = product spine for UI *and* agents). ADR-004 remains correct and should leave `proposed`.

## Improvements (priority)

1. Accept ADR-004 (owner flag flip).
2. S3 agent seams cite ADR-008 + `tools/migx-cli` (not only QML chrome).
3. Product chrome: Predict → Ask → Explain on co-pilot UI.
4. Parity loop: UI action ↔ command ID (lint later).
5. DESIGN.md + token/key lint (drift guard).
6. Local-first freemium default for Layer C free tier.
7. Onboarding Tier 2: product strategy includes ADR-008.

## Do not change

- Electron/React for decks/waveforms
- Automix / gen-music as core identity
- Blocking MTL on Rive/React
- Reordering S1 perf trust behind AI features

## Orientation map (agents)

| Doc | Role |
|---|---|
| Strategy-Current | Product SSoT |
| initiative-ai-djing-product | Execution streams S0–S6 |
| ADR-003 / ADR-005 | MIT model + proprietary layers |
| ADR-004 | QML-primary (accept) |
| ADR-008 | CLI spine, two equal clients |
| AGENT-ONBOARDING | Reading tiers |

## Closed-loop note

This brief lands durable citations in onboarding + initiative (same session).
Strategy §6 gains a pointer to this file beside the July brief.

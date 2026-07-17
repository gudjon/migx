# Problem — design tokens not loadable as QML theme

## Why
AI-DJing UI and agents need a **single design-token source**. DESIGN.md is that SSoT for humans/agents,
but Migx QML still hardcodes colors. Without Theme.qml, every screen drifts and agents cannot apply a
system consistently.

## For whom
Product UI (QML-first, ADR-004) and any agent (Claude/agy/Grok) editing UI.

## Done means
One green spike: tokens in DESIGN.md → Theme.qml → one live QML control uses Theme; lint path known.

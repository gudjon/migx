---
# DESIGN.md — Migx design tokens (SSoT for QML Theme bridge)
# format: design-md inspired YAML front matter; see kanban/knowledge/design-md-ui-modernization.md
# Generator: tools/design/gen_theme_from_design.py → res/qml/Theme/Theme.qml
name: migx-default
version: "0.1.0"
colors:
  background: "#1e1e1e"
  text: "#D9D9D9"
  white: "#D9D9D9"
  accent: "#2D4EA1"
  accentColor: "#3a60be"
  blue: "#01dcfc"
  green: "#85c85b"
  red: "#ea2a4e"
  yellow: "#fca001"
  warning: "#7D3B3B"
  darkGray: "#0f0f0f"
  darkGray2: "#242424"
  darkGray3: "#3F3F3F"
  darkGray4: "#202020"
  midGray: "#696969"
  midGray2: "#676767"
  midGray3: "#626262"
  lightGray: "#747474"
  lightGray2: "#b0b0b0"
  lightGray3: "#939393"
  embeddedBackground: "#a0000000"
  sunkenBackground: "#0C0C0C"
  knobBackground: "#262626"
  libraryPanelSplitterBackground: "#1e1e1e"
  libraryPanelSplitterHandle: "#5f5f5f"
  libraryPanelSplitterHandleActive: "#7a7a7a"
  deckInfoBarBackground: "#0e0e0e"
  deckEmptyCoverArt: "#3F3F3F"
  # NextGen mode identity colors (nextgen-ui-architecture): each full-screen mode
  # has its own accent so the DJ always knows the context at a glance.
  modePerform: "#01dcfc"
  modeArrange: "#fca001"
  modeLibrary: "#9b7bf0"
typography:
  fontFamily: "Open Sans"
  buttonFontPixelSize: 10
  textFontPixelSize: 14
---

# Migx design system

## Overview
Dark DJ console theme. Tokens in the YAML front matter are the **single source of truth** for colors
and core typography consumed by QML via `res/qml/Theme/Theme.qml`.

## Colors
Primary surfaces use near-black backgrounds with light gray text. Accents: blue for transport/gain,
green for active deck, red for effects/danger, yellow for effect units.

## Typography
Open Sans; compact control labels (10px buttons), 14px body text.

## Components
QML controls import `"Theme"` singleton (`Theme.buttonActiveColor`, etc.). Do not hardcode hex in new
controls when a Theme token exists.

## Generator
```bash
python3 tools/design/gen_theme_from_design.py          # write Theme.qml from this file
python3 tools/design/gen_theme_from_design.py --check   # exit 1 if Theme drifts from DESIGN.md
```

## Do's / Don'ts
- **Do** change tokens here, then regenerate Theme.
- **Don't** edit Theme.qml by hand for token values covered by DESIGN.md (hand-only assets like img*
  paths stay in Theme until a later wave).

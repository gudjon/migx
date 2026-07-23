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
  transparent: "transparent"
  # NextGen mode identity colors (nextgen-ui-architecture): each full-screen mode
  # has its own accent so the DJ always knows the context at a glance.
  modePerform: "#01dcfc"
  modeArrange: "#fca001"
  modeLibrary: "#9b7bf0"
  # Camelot/Lancelot key-wheel colours (cap-harmonic-key): one hue per Camelot number
  # (1..12) around the wheel, so harmonically-compatible keys — same number, or the
  # adjacent number — are scannable by colour (Traktor learning). Minor (A) and major
  # (B) share the number's hue; the A/B letter is carried in text, not colour.
  keyWheel1: "#d44949"
  keyWheel2: "#d47e49"
  keyWheel3: "#d4a949"
  keyWheel4: "#d4d449"
  keyWheel5: "#a9d449"
  keyWheel6: "#49d449"
  keyWheel7: "#49d4a9"
  keyWheel8: "#49b4d4"
  keyWheel9: "#4979d4"
  keyWheel10: "#7e49d4"
  keyWheel11: "#b449d4"
  keyWheel12: "#d449a9"
typography:
  fontFamily: "Open Sans"
  buttonFontPixelSize: 10
  textFontPixelSize: 14
  fontSizeXs: 11
  fontSizeSm: 13
  fontSizeMd: 14
  fontSizeLg: 15
  fontSizeXl: 22
spacing:
  zero: 0
  xxs: 2
  xs: 3
  md: 12
  lg: 16
  xl: 18
  xxl: 28
radii:
  none: 0
motion:
  fastMs: 120
opacity:
  full: 1.0
  muted: 0.7
layout:
  nextgenWindowWidth: 1280
  nextgenWindowHeight: 800
---

# Migx design system

## Overview
Dark DJ console theme. Tokens in the YAML front matter are the **single source of truth** for colors,
spacing, radii, typography, motion, opacity, and shell layout consumed by QML via
`res/qml/Theme/Theme.qml`.

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

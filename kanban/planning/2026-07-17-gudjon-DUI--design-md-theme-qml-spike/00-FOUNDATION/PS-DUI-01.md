---
id: PS-DUI-01
type: problem-statement
prefix: DUI
title: "DESIGN.md tokens drive Theme.qml for one QML control"
status: open
---

# PS-DUI-01

## EARS
**When** a developer or agent updates design tokens in `res/design/DESIGN.md`,  
**the system shall** expose those tokens as a QML singleton `Theme` such that  
**at least one** existing control under `res/qml/` reads color (or spacing) via `Theme.*`  
**and** a documented lint/check fails if token refs break.

## acceptance
```yaml
acceptance:
  metric: "Theme.qml exists; ≥1 QML file binds Theme.*; generator or make step documented; lint command exits 0 on clean tokens"
  measure: |
    test -f res/qml/Theme.qml
    rg -n "Theme\." res/qml --glob '*.qml' | head
    # lint: npm or script from design-md-ui-modernization once present; else documented manual check
  baseline: "no Theme.qml; colors hardcoded in QML"
  threshold: "all of: file exists, ≥1 consumer, docs in 02-ARCHITECTURE or README"
```

## Non-goals
Full skin migration, Rive, React panel.

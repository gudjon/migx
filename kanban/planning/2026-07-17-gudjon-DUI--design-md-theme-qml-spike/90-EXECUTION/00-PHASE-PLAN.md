# Phase plan — DUI

## Wave 1 — tokens + Theme.qml (verify: files exist)
- [x] Create `res/design/DESIGN.md` minimal token set (colors primary/bg/text)  
- [x] Create generated `res/qml/Theme/Theme.qml` singleton matching tokens  
- [x] Existing QML imports/consumes Theme; no new registration required in this wave  

**Gate:** `python3 tools/design/gen_theme_from_design.py --check`

## Wave 2 — one consumer (verify: rg Theme.)
- [x] Confirm an existing simple control consumes Theme colors  
- [x] Note any qmllint/pre-commit issues in JOURNAL  

**Gate:** `rg -n "Theme\." res/qml --glob '*.qml' | head -1` succeeds; pre-commit on touched files

## Wave 3 — generator or freeze manual (verify: docs)
- [x] Generator script exists: `tools/design/gen_theme_from_design.py`  
- [x] DESIGN.md documents the sync path  
- [ ] Capture forecast vs actual in 91-LOOP-CLOSURE  

**Gate:** architecture note complete; ready for 91-LOOP-CLOSURE draft

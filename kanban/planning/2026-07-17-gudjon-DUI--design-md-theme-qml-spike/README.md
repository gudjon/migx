# DUI — DESIGN.md → Theme.qml spike

**Prefix:** `DUI` · **Owner/facilitator:** gudjon · **Current DRI agent:** `claude-code`  
**Historical note:** Wave 1 ran through the Antigravity lane before `antigravity-cli` was paused.  
**Initiative:** `initiative-ui-modernization` · **Status:** execution / closure pending

## Scope
Prove DESIGN.md tokens can drive one QML surface via a generated `res/qml/Theme.qml` singleton
(round-trip + lint gate). **No RT engine. No waveform/render paths.**

## Success
- [x] `res/design/DESIGN.md` holds tokens  
- [x] `tools/design/gen_theme_from_design.py` writes/checks `res/qml/Theme/Theme.qml`  
- [x] Existing QML already consumes Theme (e.g. Button.qml)  
- [x] Lint gate: `python3 tools/design/gen_theme_from_design.py --check`  
- [ ] 91-LOOP-CLOSURE scored (after optional pre-commit wiring)  

## Out of scope
Legacy QWidget skins, Metal/OpenGL pin, full deck parity.

## Entry
`AGENTS.md` · `00-FOUNDATION/PS-DUI-01.md` · federation: poll as `claude-code`

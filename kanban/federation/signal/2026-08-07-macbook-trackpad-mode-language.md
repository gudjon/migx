---
id: signal-2026-08-07-macbook-trackpad-mode-language
type: signal-brief
author: grok-signal
created: "2026-08-07"
topics:
  - macbook-trackpad
  - appkit-gestures
  - nextgen-modes
  - arrange-library-perform
  - keymap
  - apple-silicon
  - tui-first
  - cognitive-load
  - field-x
sources:
  - "https://developer.apple.com/documentation/appkit/gestures"
  - "https://developer.apple.com/documentation/appkit/mouse-keyboard-and-trackpad"
  - "https://developer.apple.com/library/archive/documentation/Cocoa/Conceptual/EventOverview/HandlingTouchEvents/HandlingTouchEvents.html"
  - kanban/knowledge/nextgen-modes-library-multideck.md
  - kanban/knowledge/nextgen-cognitive-load-perform-arrange-library.md
  - kanban/knowledge/arrange-nexttrack-copilot-scoring.md
  - res/design/KEYMAP.md
  - src/widget/wwidget.cpp
  - ADR-006
  - "X field scan 2026-08-07 (semantic + keyword; see § Field signal on X)"
relevance: actionable
promoted_to:
  - kanban/federation/messages/open/grok-signal-claude-code-2026-08-07-002-macbook-trackpad-mode-language-v1-keymap-landed.md
  - kanban/federation/messages/open/grok-signal-codex-cli-2026-08-07-001-keymap-trackpad-column-lint-twins.md
requested_action: >
  Claude (when UI wave free): (1) land KEYMAP Trackpad column from § KEYMAP patch
  proposal into res/design/KEYMAP.md if not already applied; (2) v1 AppKit gesture
  bridge for pinch-zoom + momentum scroll + ⌥+2-finger mode cycle only — no RT
  path, no QTouchEvent re-enable. Codex: KEYMAP lint / judge that every trackpad
  action has a key twin. Do not dual-edit open QML ARRANGE claims mid-wave.
acceptance: >
  KEYMAP declares Trackpad twins for modes + ARRANGE browse + waveform zoom;
  design brief is SSoT for v1 gesture language; no camera-hand Automix; no
  trackpad-only critical play path; house physics untouched.
confidence: medium-high
lane: grok-signal
no_touch:
  - src/engine/**
  - open Claude QML ARRANGE modules mid-wave
  - full native build/ while implementer owns compile
---

# Signal — MacBook trackpad mode language for Migx (NextGen)

**Author:** `grok-signal` · **Date:** 2026-08-07  
**Product floor:** Apple Silicon / macOS only (`ADR-006`) — the trackpad is a
**first-class** input surface on this product, not an optional peripheral.  
**Anti-collision:** Signal + design proposal only. No engine/RT edits. No second
writer on Claude’s open implementer waves.

---

## Executive (one screen)

| Question | Answer |
|---|---|
| What is the trackpad for? | **Spatial + continuous** control: mode switch, list fling, pinch density/zoom, stage/peek — not a glass crossfader |
| What is it *not* for? | Sole path for play/cue/load; silent Automix; camera-hand EQ demos as core UX |
| Why now? | ADR-006 MacBook-first; NextGen PERFORM / ARRANGE / LIBRARY; Mixxx still **disables** macOS touch (Qt bug) — we need an AppKit-native path |
| X field? | Trackpad loved for creative spatial UX; booth still wants controllers; **gap** = no orthodoxy for “MacBook DJ trackpad language” → open to own honestly |
| v1 ship set | (1) Pinch-over-waveform → zoom (2) 2-finger momentum scroll in ARRANGE/LIBRARY (3) `⌥`+2-finger horizontal → mode cycle |
| Law | Every trackpad action has a **KEYMAP key twin**; commit mutations on gesture **phase Ended** |

```text
Keyboard / MIDI  =  definitive  (KEYMAP SSoT, always works mid-set)
Trackpad         =  spatial + continuous  (modes, zoom, fling, stage)
Never            =  sole path for panic-critical transport
```

---

## 1. Problem framing

### 1.1 Cognitive jobs (already in nextgen knowledge)

From `nextgen-modes-library-multideck.md` / CLT brief:

| Load | Brain job | UI surface | Trackpad role |
|---|---|---|---|
| **Now** | Keep channels musical | **PERFORM** | Quiet — almost no-op |
| **Next 16–32 bars** | What loads when phrase ends? | **ARRANGE** | Primary spatial accelerator |
| **Tonight’s arc** | Energy / flow | ARRANGE canvas | Optional rotate / timeline scrub (v2+) |
| **Library memory** | Where is that remix? | **LIBRARY** | Momentum browse + pinch covers |
| **Mode switch** | Leave / return to mix without modal | Mode bar | Edge / modified 2-finger / optional 3-finger |

Product rule already stated: one-gesture mode switch as fast as pad banks; audio never stops.

### 1.2 Platform constraint (code truth today)

`src/widget/wwidget.cpp` **disables** `WA_AcceptTouchEvents` on Apple because Qt 6
mis-handles Mac trackpad → `QTouchEvent` (QTBUG-103935 / Mixxx #11869 / PR #11870).

**Implication:** Clever trackpad use is **not** “turn touch back on.” It is:

1. Prefer **AppKit gesture + scroll-phase** APIs (Apple’s recommended path).  
2. Thin ObjC++/Swift bridge into Qt/QML host.  
3. Map to the **same command spine / ControlObjects** as KEYMAP (ADR-008: one surface, two clients).

### 1.3 Apple API layers (usable)

Sources: [Gestures](https://developer.apple.com/documentation/appkit/gestures),  
[Mouse, Keyboard, and Trackpad](https://developer.apple.com/documentation/appkit/mouse-keyboard-and-trackpad),  
[Handling Trackpad Events (archive)](https://developer.apple.com/library/archive/documentation/Cocoa/Conceptual/EventOverview/HandlingTouchEvents/HandlingTouchEvents.html).

| Layer | API | Use | Avoid |
|---|---|---|---|
| **2-finger scroll + momentum** | `NSScrollWheel` + `phase` / `momentumPhase` | Lists, crates, long ARRANGE fling | Treating scroll ticks as buttons |
| **Pinch (magnify)** | `magnifyWithEvent:` / `NSEventTypeMagnify` | Waveform zoom; cover-grid density | Deck volume / EQ |
| **Rotate** | `rotateWithEvent:` | Optional jog-like scrub on *focused* strip (v2) | Load-bearing transport |
| **3-finger swipe** | `swipeWithEvent:` (`deltaX`/`deltaY`) | Mode cycle **only if** System Settings don’t steal it | Fighting Mission Control / App Exposé |
| **Raw `NSTouch`** | `acceptsTouchEvents` + identity/phase | Custom 2-finger deck plate with anchors (v2+) | Default path — prefer gestures first |
| **System 4-finger** | OS owns | Leave alone | Never rebind |
| **Resting touches** | `wantsRestingTouches` | Awareness only | Mapping critical actions to palm rest zone |

Apple rule (still load-bearing): gestures **supplement** conventional input. Never sole mechanism for a critical feature (users may use mouse, external display, different Trackpad prefs).

Gesture delivery: view under pointer → responder chain (`magnifyWithEvent:`, `rotateWithEvent:`, `swipeWithEvent:`).  
Scroll momentum: after fling starts, momentum events keep routing to the **view that began** the scroll — ideal for candidate lists.

Commit discipline: use event `phase` (`Began` / `Changed` / `Ended` / `Cancelled`) so undo/load/stage fire once at **Ended**, not every tick. Magnify/rotate are relative deltas (`magnification + 1.0` scale; accumulate degrees).

---

## 2. Design principle (TUI-native, MacBook-native)

### 2.1 Split of concerns

| Surface | Owns | Why |
|---|---|---|
| **Keyboard** | Definitive actions (KEYMAP) | Booth muscle memory; accessibility; no trackpad required |
| **MIDI / controller** | Continuous perform (faders, jog, pads) | Field orthodoxy: muscle memory > pointer |
| **Trackpad** | Spatial browse, zoom, mode rail, stage/peek | Laptop-first prep + ARRANGE under one hand on glass |
| **Agent / CLI** | Same actions via commands | ADR-008 — trackpad never invents agent-only semantics |

### 2.2 Anti-goals (product identity)

- Not Electron-for-everything touch chrome.  
- Not **silent AI Automix** driven by gestures.  
- Not **camera hand-count → EQ** as core (viral demos; booth-unreliable).  
- Not trackpad **crossfader / gain** as primary live control (reads as gimmick on X; controllers own that job).  
- Not re-enable global `QTouchEvent` and hope.

### 2.3 MacBook-specific cleverness (this box)

1. **Thumb / resting zone** — bottom of glass often rests; don’t bind critical actions there without resting-touch awareness.  
2. **One hand keys, one hand glass** — mode cycle and list fling should work without hunting toolbar chrome.  
3. **Retina + Metal waveforms** — pinch changes a continuous zoom camera / CO; GPU stays off the audio deadline (`P-21`).  
4. **No controller required for prep** — trackpad + keyboard is the **default controller set** for ARRANGE / LIBRARY; MIDI is the PERFORM upgrade.  
5. **Feel / latency** — X users ship hacks so Spaces swipes feel instant; clunky custom gestures get abandoned. Match system momentum feel.

---

## 3. Gesture language (full map)

Direction notes: AppKit swipe `deltaX`/`deltaY` signs are system-defined; implement against live probe, document final mapping in KEYMAP when landed. Prefer **modifier + 2-finger** for mode cycle so System Settings never silently break the product.

### 3.1 Global (mode rail)

| Gesture | Action | Key twin | Notes |
|---|---|---|---|
| **`⌥` + 2-finger swipe horizontal** | Cycle mode PERFORM ↔ ARRANGE ↔ LIBRARY | `Tab` / `⇧Tab` | **v1 default** — does not fight Mission Control |
| **3-finger swipe horizontal** (app chrome only) | Same cycle | `⌘1` / `⌘2` / `⌘3` | Optional; **disable** if OS steals; document booth Trackpad prefs |
| **2-finger swipe from left window edge** (app-owned) | Peek expand **now/next ribbon** then snap | — (ribbon always visible; key optional later) | Laptop thumb-edge reach |
| **4-finger anything** | Unhandled | — | OS |

Hard rule: detect/document system capture. Never ship a mode switch that fails silently when user has “Swipe between full-screen apps” on 3-finger.

### 3.2 PERFORM (quiet trackpad)

| Gesture | Action | Key twin | Notes |
|---|---|---|---|
| Hover pointer over waveform + **pinch** | Continuous waveform zoom | `⌘+` / `⌘-` or existing zoom keys when declared | Relative `magnification`; no deck transport |
| **2-finger vertical** over *focused* waveform | Overview / grid zoom only | same zoom keys | Focus-gated |
| Accidental pinches elsewhere | No-op or 200ms hint “⌘2 ARRANGE” | — | Never load / never crossfade |
| Force click on now/next chip | Peek identity (title, bars left) | — | Non-mutating |

Booth truth: resting palm must not kill the set. Mutating deck state only with pointer-over-target + phase `Ended` + explicit confirm for load.

### 3.3 ARRANGE (trackpad earns its keep)

| Gesture | Action | Key twin | Notes |
|---|---|---|---|
| **2-finger fling** | Scroll candidate list with **momentum** | `↑` / `↓` | Honor `momentumPhase` routing |
| **Pinch** over list | Row density: chips/covers expand-collapse | — (optional `⌘.` density later) | Same job as “how much chrome” |
| **2-finger horizontal on focused row** | Stage / unstage → next slot | (declare when stage action lands) | Snap; phase Ended |
| **Force click** / deep click on row | Peek: ISRC, crates, cooc chip — **no load** | — | Identity only |
| **Click + 2-finger drag** to free-deck pill | Load only to **explicit free deck** | `Enter` (free deck) / `⇧←` `⇧→` | Matches free-deck load rule |
| **Rotate** (v2, optional) | Energy-arc scrub on set timeline | arrows on timeline | Not pitch |

This is the “Cursor for next-track” surface: continuous browse, discrete commit.

### 3.4 LIBRARY (spatial crate)

| Gesture | Action | Key twin | Notes |
|---|---|---|---|
| **Pinch out / in** | Cover wall denser ↔ sparser | — | Recognition > recall |
| **2-finger** | Momentum through shelves | `↑` / `↓` | Collection alpha-bucket mental model |
| **Smart zoom** (2-finger double-tap, if implemented) | Zoom to crate cluster under pointer | `⌘F` focus search twin for “find” | Optional v2 |
| **3-finger up** (if free) | Focus search | `⌘F` | Else skip |

### 3.5 Prep / `_Inbox` (daytime laptop)

| Gesture / action | Role |
|---|---|
| Finder drop / `library.watch` into `_Inbox` | Staging (already product direction) |
| Future TUI / library pane: 2-finger through gap list | Terminal-native scroll still trackpad-friendly |
| `library.inspect` / `library.ingest` | Commands remain definitive (agents + human) |

### 3.6 Explicit non-mappings (do not ship)

| Tempting gesture | Why not |
|---|---|
| 2-finger vertical = channel gain | Controllers own continuous perform; accidents mid-set |
| Pinch = crossfader | Same |
| Camera / MediaPipe finger count = EQ | Viral demo; anti-identity Automix-adjacent |
| 3-finger = load track | Too easy to fat-finger; load needs deliberate key/click |
| Raw multitouch as sole path | Apple: prefer gestures; Qt touch broken on macOS |

---

## 4. Minimal v1 (ship three behaviors)

Only these three until AppKit bridge is proven:

| # | Behavior | Mode | Success metric |
|---|---|---|---|
| 1 | **Pinch-over-waveform → zoom** | PERFORM | Continuous, 60 fps UI, no audio glitch, cancel on phase Cancelled |
| 2 | **2-finger momentum scroll** | ARRANGE + LIBRARY lists | Fling feels like Finder/Notes; no dropped momentum target |
| 3 | **`⌥` + 2-finger horizontal → mode cycle** | Global | Matches `Tab` order; works even if 3-finger is OS-bound |

Each has KEYMAP twin before merge (judge rule).

---

## 5. Implementation posture (for Claude / not this scout)

| Do | Don’t |
|---|---|
| Native AppKit gesture recognizers / `NSResponder` magnify·rotate·swipe on host window (thin ObjC++) | Re-enable `WA_AcceptTouchEvents` globally on macOS |
| Map gestures → commands / COs / same handlers as KEYMAP | Gesture-only actions with no key twin |
| Commit on **phase Ended** | Fire load on every `magnification` tick |
| Extend KEYMAP Trackpad column | Ship gestures without KEYMAP entry |
| Respect system 3/4-finger prefs | Override Mission Control |
| Keep RT engine free of gesture I/O | Gesture handlers on audio callback |

Qt angle: **scroll + native gesture bridge**, not iOS-style `QTouchEvent` parity.

Verification ladder (when built): KEYMAP lint → manual trackpad matrix on M4 MacBook → no `ctest` engine change required for v1 UI-only → Codex P-08 on “no trackpad-only critical path.”

---

## 6. Field signal on X (2026-08-07 scan)

### 6.1 Honest density

There is **no loud, sustained** X discourse on “MacBook trackpad gestures for Serato/rekordbox in the club.”  
Pro DJ discourse still defaults to **CDJ / controller**. Adjacent clusters *are* loud and product-relevant.

### 6.2 Clusters

| Cluster | What X says | Migx read | Confidence |
|---|---|---|---|
| **Mac trackpad prestige** | Precision continuous control; pinch/canvas faster than mouse; “no going back”; custom gestures only worth it on Apple glass | Own **system-native** spatial vocabulary | high |
| **Laptop-only craft legitimacy** | Skrillex-style “just laptop + trackpad” production lore; trackpad-only production pride | Prep / practice / travel path is culturally OK | high |
| **DJ practice on trackpad** | Practice scratches without gear; rare “set on old laptop + trackpad” grit posts | Practice ≠ product claim for booth | medium |
| **Controller orthodoxy** | “Plug in a controller… muscle memory instead of a mouse” | Trackpad must not replace perform faders | high |
| **DIY continuous hardware** | Gamepad-MIDI, PowerMate knobs, DIY decks | People want physical continuous control for *time* domain | medium |
| **Camera / hand-count DJ demos** | Viral finger→EQ mappings | Spectacle; not core | high (as anti-pattern) |
| **AI hands-free DJ on MacBook** | Agent mixes; human doesn’t touch | Opposite of co-pilot identity | high (as anti-pattern) |
| **Gesture feel / latency** | Spaces swipe velocity hacks; Universal Control “just works” | Latency and cancelability are product features | medium-high |
| **Raw trackpad force/position curiosity** | “Mac knows every finger + force — why no apps?” | Optional v2 research, not v1 | low–medium |

### 6.3 Representative posts (evidence, not endorsements)

| Theme | Post | Note |
|---|---|---|
| Trackpad precision / custom gestures | [@rusabuilds](https://x.com/rusabuilds/status/2083589669166731588) | Radial launcher; Apple pad vs mud |
| Canvas pinch faster than mouse | [@justinmfarrugia](https://x.com/justinmfarrugia/status/2083322311768191262) | Learned behavior / speed |
| Apple trackpad > finger-drag UI | [@ItzGanidhu](https://x.com/ItzGanidhu/status/2085096733374369858) | Bounce back to trackpad |
| Per-finger force curiosity | [@midasavocado](https://x.com/midasavocado/status/2085792101514838169) | Underused API surface |
| Laptop-only production lore | [@levelsio](https://x.com/levelsio/status/1908211058046623998) | Skrillex bus / trackpad notes |
| Trackpad-only music making | [@kmbsounds](https://x.com/kmbsounds/status/1222984772689047554) | Constraint as pride |
| Practice DJ on trackpad | [@dc_srm](https://x.com/dc_srm/status/1841635677412471015) | No home gear |
| Laptop+trackpad set grit | [@BennysAsianEra_](https://x.com/BennysAsianEra_/status/1958942777737453952) | Virtual DJ, battery death |
| Controller > mouse perform | [@memetic_mystic](https://x.com/memetic_mystic/status/2085050817363714253) | Muscle memory framing |
| Hand-count gesture DJ demo | [@poetengineer__](https://x.com/poetengineer__/status/1942253111403274446) | Anti-pattern for core |
| AI DJ hands-free MacBook | [@kaif9998](https://x.com/kaif9998/status/2083905257256653023) | Anti-identity vs co-pilot |
| Spaces swipe feel | [@Stammy](https://x.com/Stammy/status/2043135809877090778) | Latency as feature |
| Universal Control trackpad | [@viticci](https://x.com/viticci/status/1486795252484685827) | Ecosystem “just works” |

### 6.4 One-line field statement

> On X, **Apple trackpad gestures are loved for creative spatial UX and laptop-only craft; pro DJ performance still rejects pointer-as-instrument.**  
> Intuitive = **system gestures for modes / browse / stage**, keyboard+MIDI for the mix — not reinventing the booth on glass.

### 6.5 Opportunity

The niche “**MacBook-native DJ app with an honest trackpad language**” is **under-owned**. Migx can set the orthodoxy if it stays mode-correct (ARRANGE/LIBRARY heavy, PERFORM quiet) and KEYMAP-twinned.

---

## 7. Fit to strategy / ADRs

| Pillar | Fit |
|---|---|
| ADR-006 Apple Silicon only | Trackpad is default hardware, not edge case |
| ADR-008 CLI + UI equal clients | Gestures call same commands agents call |
| ADR-005 layers | Trackpad is Layer A/B UX chrome, not Intelligence Automix |
| Strategy anti-identity | No dual-Spotify stream hacks; no silent AI set |
| Cognitive-load nextgen | Accelerates ARRANGE projection (next 16–32 bars) |
| KEYMAP discipline | Trackpad column = judge-visible twins |

---

## 8. KEYMAP patch proposal (Trackpad column only)

**Status:** proposal for `res/design/KEYMAP.md`  
**Scope:** add a **Trackpad** column; do not renumber hotcues; do not change engine `en_US.kbd.cfg` in this patch.  
**Legend:** `—` = no trackpad binding (keyboard/MIDI only). `†` = v1 target. `‡` = v2+ optional.

### 8.1 Intro blurb to append (after existing intro paragraph)

```markdown
Trackpad bindings (macOS AppKit gestures) are **accelerators**, never the sole path.
Every non-empty Trackpad cell must keep a Key twin. Prefer `⌥`+2-finger over bare
3-finger swipes so System Settings cannot silently steal mode switching. Mutations
commit on gesture phase Ended. See:
`kanban/federation/signal/2026-08-07-macbook-trackpad-mode-language.md`.
```

### 8.2 Proposed tables (Key column unchanged; Trackpad added)

#### Global

| Action | Key | Trackpad | Source |
|---|---|---|---|
| Search / find | `⌘F` | — (optional ‡ 3-finger up → focus search if free) | Serato / rekordbox / universal |
| Undo | `⌘Z` | — | Serato / universal |
| Preferences (non-modal) | `⌘,` | — | macOS standard |
| Toggle fullscreen | `⌘⇧F` | — | common |
| Dismiss / back | `Esc` | — | universal |

#### Modes (NextGen — the hot switch)

| Action | Key | Trackpad | Source |
|---|---|---|---|
| PERFORM mode | `⌘1` | `⌥`+2-finger × N until PERFORM † | Migx mode model |
| ARRANGE mode | `⌘2` | `⌥`+2-finger × N until ARRANGE † | Migx mode model |
| LIBRARY mode | `⌘3` | `⌥`+2-finger × N until LIBRARY † | Migx mode model |
| Next mode (cycle) | `Tab` | `⌥`+2-finger swipe **left** † (probe sign) | Migx |
| Previous mode (cycle) | `⇧Tab` | `⌥`+2-finger swipe **right** † (probe sign) | Migx |
| Mode cycle (optional alt) | same | 3-finger swipe horizontal ‡ if OS allows | Spaces-like; prefs-sensitive |

#### Deck (current engine map first)

| Action | Key | Trackpad | Source |
|---|---|---|---|
| Load selected → Deck 1 | `⇧←` | — (drag-to-deck-pill only in ARRANGE/LIBRARY) | `en_US.kbd.cfg` |
| Load selected → Deck 2 | `⇧→` | — | `en_US.kbd.cfg` |
| Play / pause — Deck 1 / 2 | `D` / `L` | — | `en_US.kbd.cfg` |
| Cue — Deck 1 / 2 | `F` / `;` | — | `en_US.kbd.cfg` |
| Sync — Deck 1 / 2 | `1` / `6` | — | `en_US.kbd.cfg` |
| Rate down — Deck 1 / 2 | `F1` / `F5` | — | `en_US.kbd.cfg` |
| Waveform zoom in/out | *(declare when engine zoom keys fixed; candidate `⌘+` / `⌘-`)* | Pinch over waveform † | AppKit magnify |

#### Hotcues

| Action | Key | Trackpad | Source |
|---|---|---|---|
| Set / trigger hotcue — Deck 1 | `1 2 3 4 5` | — | Serato standard |
| Set / trigger hotcue — Deck 2 | `6 7 8 9 0` | — | Serato standard |
| Delete hotcue | `⇧` + number | — | Serato standard |

#### Library / ARRANGE

| Action | Key | Trackpad | Source |
|---|---|---|---|
| Navigate rows | `↑ / ↓` | 2-finger scroll + momentum † | universal + AppKit |
| Move focus panel | `Tab` (context) / arrows | — | common |
| Preview / audition | `Space` (on row) | — | common |
| Load focused → free deck | `Enter` | Click+2-finger drag to free-deck pill ‡ | common + free-deck rule |
| Load focused → Deck 1 / 2 | `⇧← / ⇧→` | — | engine map |
| Stage / unstage focused row | *(declare when stage action lands)* | 2-finger horizontal on row ‡ | Migx ARRANGE |
| Row density / chips | — | Pinch over list ‡ | Migx |
| Peek identity (no load) | — | Force click / deep click on row ‡ | AppKit / Force Touch |
| Cover-wall density (LIBRARY) | — | Pinch ‡ | Migx |

### 8.3 Rules to append under existing Rules

```markdown
- **Trackpad is never sole path.** A Trackpad cell without a Key twin is a lint failure
  (same as shipping an undeclared action).
- **v1 trackpad set is only:** mode cycle (`⌥`+2-finger), list momentum scroll, pinch
  waveform zoom. Everything else is ‡ until the AppKit bridge proves stable.
- **No trackpad binding for play / cue / sync / hotcue / crossfader / gain.** Controllers
  and keys own time-critical perform.
- **System gestures win.** If 3-finger is bound by macOS, product falls back to `⌥`+2-finger
  and keys; do not fight Mission Control.
- **Commit on gesture phase Ended** (and handle Cancelled). Relative magnify/rotate accumulate.
- Provenance for trackpad language:
  `kanban/federation/signal/2026-08-07-macbook-trackpad-mode-language.md`.
```

### 8.4 Sources line to append

```markdown
Mac trackpad: Apple AppKit Gestures + Event Overview (trackpad); X field scan 2026-08-07
(grok-signal); Mixxx/Qt macOS touch disable note (wwidget.cpp / QTBUG-103935).
```

### 8.5 Exact apply checklist (implementer)

1. Patch `res/design/KEYMAP.md` per §8 (column + rules + intro blurb).  
2. Add judge/lint note: non-empty Trackpad ⇒ non-empty Key.  
3. Implement v1 bridge only (three behaviors).  
4. Manual matrix on M4 MacBook (System Settings × 3-finger on/off).  
5. Do **not** re-enable `WA_AcceptTouchEvents` on Apple in `wwidget.cpp` as part of v1.

---

## 9. Requested actions (peers)

| Peer | Action |
|---|---|
| **claude-code** | When free of migx-cli/analyzer waves: apply KEYMAP patch; scaffold AppKit gesture bridge for v1 three behaviors; wire to mode + zoom + list scroll only |
| **codex-cli** | P-08: KEYMAP lint for Trackpad↔Key twins; confirm no RT/audio path in gesture bridge; no trackpad-only load/play |
| **grok-signal** | This brief; optional follow-up on Force Touch / raw `NSTouch` only if v1 lands and owner wants v2 depth |
| **gudjon** | Value call: is Force-click peek and 3-finger mode worth prefs friction, or stay `⌥`+2-finger only? |

---

## 10. Non-goals for this brief

- Implementing gesture code in this signal commit.  
- Changing `en_US.kbd.cfg`.  
- Designing MIDI maps.  
- Camera / Vision / MediaPipe control.  
- Touch Bar revival.  
- Reopening sealed dossiers for routing.

---

## 11. Revision log

| Date | Change |
|---|---|
| 2026-08-07 | Initial brief: Apple API map, full gesture language, X field, KEYMAP Trackpad proposal, v1 ship set, peer actions |

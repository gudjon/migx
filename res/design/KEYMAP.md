# KEYMAP.md — Migx NextGen keyboard shortcuts (SSoT)

The design discipline: **every action has a clear keyboard shortcut, declared here.** This file is the
single source of truth for the NextGen keymap the way `DESIGN.md` is for visual tokens. Bindings adopt
the conventions of the top DJ software (Serato DJ Pro, rekordbox, Traktor Pro, VirtualDJ, Mixxx) so DJs
keep their muscle memory; Migx-specific additions (the mode model) use Mac-idiomatic, non-colliding keys.
On macOS `⌘` = Qt `Ctrl`. Deck actions run on the shared engine's keyboard system
(`res/keyboard/en_US.kbd.cfg`); NextGen surfaces current engine bindings first. Proposed DJ-software
aliases must be reconciled with that file before shipping.

Trackpad bindings (macOS AppKit gestures) are **accelerators**, never the sole path. Every non-empty
**Trackpad** cell must keep a **Key** twin. Prefer `⌥`+2-finger over bare 3-finger swipes so System
Settings cannot silently steal mode switching. Mutations commit on gesture phase Ended. Full language:
`kanban/federation/signal/2026-08-07-macbook-trackpad-mode-language.md`.

Legend: `—` = no trackpad binding (keyboard/MIDI only). `†` = v1 target. `‡` = v2+ optional.

## Global

| Action | Key | Trackpad | Source |
| --- | --- | --- | --- |
| Search / find | `⌘F` | — (optional ‡ 3-finger up → focus search if free) | Serato / rekordbox / universal |
| Undo | `⌘Z` | — | Serato / universal |
| Preferences (non-modal) | `⌘,` | — | macOS standard |
| Toggle fullscreen | `⌘⇧F` | — | common |
| Dismiss / back | `Esc` | — | universal |

## Modes (NextGen — the hot switch)

Mode switching is Migx's own model, so it uses **⌘+number** (the Mac-idiomatic "switch view/tab" gesture
from browsers/editors — instant muscle memory) plus **Tab** to cycle. It deliberately avoids the bare
number row (reserved for hotcues below). Trackpad v1 uses **`⌥`+2-finger** so Mission Control cannot
silently own the gesture.

| Action | Key | Trackpad | Source |
| --- | --- | --- | --- |
| PERFORM mode | `⌘1` | `⌥`+2-finger × N until PERFORM † | Migx mode model |
| ARRANGE mode | `⌘2` | `⌥`+2-finger × N until ARRANGE † | Migx mode model |
| LIBRARY mode | `⌘3` | `⌥`+2-finger × N until LIBRARY † | Migx mode model |
| Next mode (cycle) | `Tab` | `⌥`+2-finger swipe horizontal † (probe sign at impl) | Migx |
| Previous mode (cycle) | `⇧Tab` | `⌥`+2-finger swipe opposite † | Migx |
| Mode cycle (optional alt) | same keys | 3-finger swipe horizontal ‡ if OS allows | Spaces-like; prefs-sensitive |

## Deck (current engine map first)

| Action | Key | Trackpad | Source |
| --- | --- | --- | --- |
| Load selected → Deck 1 | `⇧←` | — (ARRANGE/LIBRARY: drag-to-deck-pill only ‡) | `res/keyboard/en_US.kbd.cfg` |
| Load selected → Deck 2 | `⇧→` | — | `res/keyboard/en_US.kbd.cfg` |
| Play / pause — Deck 1 / Deck 2 | `D` / `L` | — | `res/keyboard/en_US.kbd.cfg` |
| Cue — Deck 1 / Deck 2 | `F` / `;` | — | `res/keyboard/en_US.kbd.cfg` |
| Sync — Deck 1 / Deck 2 | `1` / `6` | — | `res/keyboard/en_US.kbd.cfg` |
| Rate down — Deck 1 / Deck 2 | `F1` / `F5` | — | `res/keyboard/en_US.kbd.cfg` |
| Waveform zoom in/out | *(declare when engine zoom keys fixed; candidate `⌘+` / `⌘-`)* | Pinch over waveform † | AppKit magnify |

`⌘←` / `⌘→` remain candidate NextGen aliases because they match common DJ-library muscle memory, but
they are not active until reconciled with the shared engine map.

## Hotcues (Serato standard — shared with Mixxx/rekordbox pads)

| Action | Key | Trackpad | Source |
| --- | --- | --- | --- |
| Set / trigger hotcue — Deck 1 | `1 2 3 4 5` | — | Serato standard |
| Set / trigger hotcue — Deck 2 | `6 7 8 9 0` | — | Serato standard |
| Delete hotcue | `⇧` + the number | — | Serato standard |

## Library / ARRANGE (find the next track — the core job)

| Action | Key | Trackpad | Source |
| --- | --- | --- | --- |
| Navigate rows | `↑ / ↓` | 2-finger scroll + momentum † | universal + AppKit |
| Move focus panel | `Tab` (context) / arrows | — | common |
| Preview / audition | `Space` (on a library row) | — | common |
| Load focused → free deck | `Enter` | Click+2-finger drag to free-deck pill ‡ | common + free-deck rule |
| Load focused → Deck 1 / 2 | `⇧← / ⇧→` | — | current engine map |
| Stage / unstage focused row | *(declare when stage action lands)* | 2-finger horizontal on row ‡ | Migx ARRANGE |
| Row density / chips | — | Pinch over list ‡ | Migx |
| Peek identity (no load) | — | Force click / deep click on row ‡ | AppKit / Force Touch |
| Cover-wall density (LIBRARY) | — | Pinch ‡ | Migx |

## TUI (terminal — `migx-tui`)

The terminal cannot see `⌘`: a TTY never receives it, so the Mac-idiomatic `⌘`+number mode switch has
no terminal equivalent. The TUI therefore uses **bare numbers for modes**, which does *not* break the
"bare `1–0` = hotcues" rule — that rule prevents a *collision within a context*, and the TUI has no
decks and no hotcues to collide with. `Tab` cycles modes exactly as declared above, so the documented
gesture still works.

| Action | Key | Trackpad | Source |
| --- | --- | --- | --- |
| Overview / Library / Arrange mode | `1` / `2` / `3` | — (no TTY gestures) | TUI twin of `⌘1–⌘3` |
| Prep / Track / Deck mode | `4` / `5` / `6` | — | Migx mode model |
| Next mode (cycle) | `Tab` | — | matches NextGen |
| Navigate rows | `↑ / ↓` or `j / k` | — | universal + vi convention |
| Page / jump | `PgUp / PgDn`, `g / G` | — | less(1) convention |
| Search / filter | `/` | — | TTY twin of `⌘F` (less/vim) |
| Clear filter | `Esc` | — | universal |
| Cycle sort | `s` | — | Migx ARRANGE |
| Load focused → Deck A / B | `a` / `b` | — | TTY twin of `⇧← / ⇧→` |
| Open focused in Track mode | `t` | — | Migx |
| Open Deck mode | `d` | — | Migx mode model (twin of `6`) |
| Start / stop live session | `p` | — | Migx live deck (drives livesession.tick) |
| Compatible with deck A (Library) | `m` | — | Migx ARRANGE scoring, reused as a browser filter |
| Composer — run a command | `:` | — | vi/less convention; dispatches real command IDs (ADR-008) |
| This help | `?` | — | universal; parsed FROM this table at runtime |
| Cover art in Track mode | *(automatic when chafa + cover file)* | — | optional `chafa`; CLI `library.art` |
| Add focused → crate | `c` | — | Migx ARRANGE (stage action) |
| Refresh snapshot | `r` | — | common |
| Quit | `q` | — | universal |

## Rules (the discipline)

- **No action ships without a KEYMAP entry.** A module's `MODULE.md` lists the shortcuts it adds; the
  judge fails an action with no declared key.
- **No shortcut collides within a context.** Bare `1–0` = hotcues; modes never use them.
- **Shortcuts never require a modal.** A hint may show inline (e.g. `PERFORM ⌘1`); help is non-blocking.
- Deck bindings stay reconciled with `res/keyboard/en_US.kbd.cfg` (current engine map first; proposed
  aliases require an explicit engine-map change).
- **Trackpad is never sole path.** A Trackpad cell without a Key twin is a lint failure (same as
  shipping an undeclared action). Pure-peek Force click is the only soft exception until a Key peek
  is declared.
- **v1 trackpad set is only:** mode cycle (`⌥`+2-finger), list momentum scroll, pinch waveform zoom.
  Everything else is `‡` until the AppKit bridge proves stable.
- **No trackpad binding for play / cue / sync / hotcue / crossfader / gain.** Controllers and keys own
  time-critical perform.
- **System gestures win.** If 3-finger is bound by macOS, product falls back to `⌥`+2-finger and keys;
  do not fight Mission Control.
- **Commit on gesture phase Ended** (and handle Cancelled). Relative magnify/rotate accumulate.
- Provenance for trackpad language:
  `kanban/federation/signal/2026-08-07-macbook-trackpad-mode-language.md`.

## Sources

Serato DJ Pro shortcut reference (phasedj.com, djmartindus.com); rekordbox/Serato/Traktor/VirtualDJ
comparison (recordcase.de, djtechreviews.com); Mixxx default keyboard mapping.
Mac trackpad: Apple AppKit Gestures + Event Overview (trackpad); X field scan 2026-08-07 (grok-signal);
Mixxx/Qt macOS touch disable note (`src/widget/wwidget.cpp` / QTBUG-103935).

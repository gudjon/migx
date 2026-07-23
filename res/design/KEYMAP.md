# KEYMAP.md — Migx NextGen keyboard shortcuts (SSoT)

The design discipline: **every action has a clear keyboard shortcut, declared here.** This file is the
single source of truth for the NextGen keymap the way `DESIGN.md` is for visual tokens. Bindings adopt
the conventions of the top DJ software (Serato DJ Pro, rekordbox, Traktor Pro, VirtualDJ, Mixxx) so DJs
keep their muscle memory; Migx-specific additions (the mode model) use Mac-idiomatic, non-colliding keys.
On macOS `⌘` = Qt `Ctrl`. Deck actions run on the shared engine's keyboard system
(`res/keyboard/en_US.kbd.cfg`); NextGen surfaces current engine bindings first. Proposed DJ-software
aliases must be reconciled with that file before shipping.

## Global
| Action | Key | Source |
|---|---|---|
| Search / find | `⌘F` | Serato / rekordbox / universal |
| Undo | `⌘Z` | Serato / universal |
| Preferences (non-modal) | `⌘,` | macOS standard |
| Toggle fullscreen | `⌘⇧F` | common |
| Dismiss / back | `Esc` | universal |

## Modes (NextGen — the hot switch)
Mode switching is Migx's own model, so it uses **⌘+number** (the Mac-idiomatic "switch view/tab" gesture
from browsers/editors — instant muscle memory) plus **Tab** to cycle. It deliberately avoids the bare
number row (reserved for hotcues below).
| Action | Key |
|---|---|
| PERFORM mode | `⌘1` |
| ARRANGE mode | `⌘2` |
| LIBRARY mode | `⌘3` |
| Next mode (cycle) | `Tab` |
| Previous mode (cycle) | `⇧Tab` |

## Deck (current engine map first)
| Action | Key | Source |
|---|---|---|
| Load selected → Deck 1 | `⇧←` | `res/keyboard/en_US.kbd.cfg` |
| Load selected → Deck 2 | `⇧→` | `res/keyboard/en_US.kbd.cfg` |
| Play / pause — Deck 1 / Deck 2 | `D` / `L` | `res/keyboard/en_US.kbd.cfg` |
| Cue — Deck 1 / Deck 2 | `F` / `;` | `res/keyboard/en_US.kbd.cfg` |
| Sync — Deck 1 / Deck 2 | `1` / `6` | `res/keyboard/en_US.kbd.cfg` |
| Rate down — Deck 1 / Deck 2 | `F1` / `F5` | `res/keyboard/en_US.kbd.cfg` |

`⌘←` / `⌘→` remain candidate NextGen aliases because they match common DJ-library muscle memory, but
they are not active until reconciled with the shared engine map.

## Hotcues (Serato standard — shared with Mixxx/rekordbox pads)
| Action | Key |
|---|---|
| Set / trigger hotcue — Deck 1 | `1 2 3 4 5` |
| Set / trigger hotcue — Deck 2 | `6 7 8 9 0` |
| Delete hotcue | `⇧` + the number |

## Library / ARRANGE (find the next track — the core job)
| Action | Key | Source |
|---|---|---|
| Navigate rows | `↑ / ↓` | universal |
| Move focus panel | `Tab` (context) / arrows | common |
| Preview / audition | `Space` (on a library row) | common |
| Load focused → free deck | `Enter` | common |
| Load focused → Deck 1 / 2 | `⇧← / ⇧→` | current engine map |

## Rules (the discipline)
- **No action ships without a KEYMAP entry.** A module's `MODULE.md` lists the shortcuts it adds; the
  judge fails an action with no declared key.
- **No shortcut collides within a context.** Bare `1–0` = hotcues; modes never use them.
- **Shortcuts never require a modal.** A hint may show inline (e.g. `PERFORM ⌘1`); help is non-blocking.
- Deck bindings stay reconciled with `res/keyboard/en_US.kbd.cfg` (current engine map first; proposed
  aliases require an explicit engine-map change).

## Sources
Serato DJ Pro shortcut reference (phasedj.com, djmartindus.com); rekordbox/Serato/Traktor/VirtualDJ
comparison (recordcase.de, djtechreviews.com); Mixxx default keyboard mapping.

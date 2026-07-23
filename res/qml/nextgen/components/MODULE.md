# MODULE — deck (NextGen bounded context)

The **deck** bounded context: the per-deck views bound to the shared engine. Built one component at a
time, each proving the full stack — primitive → view → ViewModel → engine — token-only and
fixture-runnable (nextgen-ui-architecture). Components live flat in `components/` while the deck is the
only context; they migrate to `components/deck/` when a second context (mixer) lands.

Components: **transport** (play/pause) · **clock** (elapsed/remaining/total) · **identity** (art · title ·
artist · BPM · colour-coded KEY) · **strip** (composes the three into one horizontal deck row; PERFORM
tiles N strips vertically — perform-multideck-layout).

## Files
| File | Layer | Role |
|---|---|---|
| `../primitives/NgButton.qml` | primitive | token-only console button (no engine) |
| `DeckTransport.qml` | component (view) | dumb: renders `deckLabel/playing/hasTrack`, emits `toggleRequested()` |
| `DeckTransportModel.qml` | component (ViewModel) | engine touch: `Mixxx.ControlProxy` for `play` + `track_loaded` |
| `DeckClock.qml` | component (view) | dumb: renders `elapsed/remaining/total/ending`; no engine touch |
| `DeckClockModel.qml` | component (ViewModel) | read-only engine touch: derives time from `duration` + `playposition` |
| `../primitives/NgBadge.qml` | primitive | token-only pill; `accent` = key-wheel colour (reused in ARRANGE) |
| `DeckIdentity.qml` | component (view) | dumb: art · title · artist · BPM/KEY badges; KEY coloured via `Theme.keyWheelN` |
| `DeckIdentityModel.qml` | component (ViewModel) | read-only: track (PlayerManager) + `bpm`/`key` COs; ChromaticKey→musical+Camelot |

## Engine bindings (CO/proxy)
| ControlObject | Proxy | Direction |
|---|---|---|
| `[ChannelN],play` | `DeckTransportModel.playControl` | read (`playing`) + write (`togglePlay()`, sole writer — P-06) |
| `[ChannelN],track_loaded` | `DeckTransportModel.loadedControl` | read (`hasTrack`) |
| `[ChannelN],track_loaded` | `DeckClockModel.loadedControl` | read (`hasTrack`) |
| `[ChannelN],duration` | `DeckClockModel.durationControl` | read (`total`, seconds) |
| `[ChannelN],playposition` | `DeckClockModel.positionControl` | read (0..1 → `elapsed`/`remaining`) |
| PlayerManager `getPlayer(group).currentTrack` | `DeckIdentityModel.currentTrack` | read (`title`/`artist`/`coverArtUrl`) |
| `[ChannelN],bpm` | `DeckIdentityModel.bpmControl` | read (`bpmText`) |
| `[ChannelN],key` | `DeckIdentityModel.keyControl` | read (ChromaticKey 1..24 → musical + Camelot + wheel colour) |

## States (all handled)
**Transport** — no track → button disabled, "no track loaded"; paused → "PLAY", "❚❚ paused";
playing → "PAUSE" (green fill), "▶ playing".
**Clock** — no track → "--:--"; loaded → `-mm:ss` remaining (loud) over `elapsed / total` (quiet);
ending (≤30 s left) → remaining turns `red` (mix-out warning).

## Tokens used
`space2/3/12/16`, `fontSizeXs/Sm/Md/Xl`, `opacityMuted/Full`, `green`, `red`, `textColor`, `midGray`,
`knobBackgroundColor`, `darkGray2`, `sunkenBackgroundColor`, `radius0`, `motionFastMs`. No hardcoded
visual literal.

## Shortcuts (KEYMAP.md)
Play/pause = the engine deck key (`D`/`L` per the current engine map); no NextGen-local shortcut added.

## Judge (acceptance)
- `just theme-check` + `just ng-ui-lint` green (token-only, no literal, no blocking modal).
- Fixture render: with `playing/hasTrack` set directly (no ViewModel), the view renders the three states
  correctly (pixel via the CGL harness).
- Live: `migx --nextgen`, load a track on Deck 1, the PLAY button toggles `[Channel1],play` and the
  state cue tracks it. Switching modes never disturbs playback (invariant #6).
- Clock live: as the track plays, `remaining` counts down (`-mm:ss`), `elapsed`/`total` are correct,
  and remaining turns `red` in the final 30 s. With no track it reads `--:--`.
- Non-modal: no `QMessageBox` reachable.

# MODULE — deck-transport (first NextGen component uplift)

The first real component built into the NextGen architecture: a deck's **transport** (play/pause),
bound to the shared engine. Proves the full stack end-to-end — primitive → view → ViewModel → engine —
token-only and fixture-runnable (nextgen-ui-architecture).

## Files
| File | Layer | Role |
|---|---|---|
| `../primitives/NgButton.qml` | primitive | token-only console button (no engine) |
| `DeckTransport.qml` | component (view) | dumb: renders `deckLabel/playing/hasTrack`, emits `toggleRequested()` |
| `DeckTransportModel.qml` | component (ViewModel) | the only engine touch: `Mixxx.ControlProxy` for `play` + `track_loaded` |

## Engine bindings (CO/proxy)
| ControlObject | Proxy | Direction |
|---|---|---|
| `[ChannelN],play` | `DeckTransportModel.playControl` | read (`playing`) + write (`togglePlay()`, sole writer — P-06) |
| `[ChannelN],track_loaded` | `DeckTransportModel.loadedControl` | read (`hasTrack`) |

## States (all handled)
- **no track** → button disabled, "no track loaded".
- **paused** → "PLAY" button, "❚❚ paused".
- **playing** → "PAUSE" button (green fill), "▶ playing".

## Tokens used
`space12`, `fontSizeSm/Md/Xs`, `opacityMuted/Full`, `green`, `textColor`, `midGray`, `knobBackgroundColor`,
`darkGray2`, `sunkenBackgroundColor`, `space2`, `radius0`, `motionFastMs`. No hardcoded visual literal.

## Shortcuts (KEYMAP.md)
Play/pause = the engine deck key (`D`/`L` per the current engine map); no NextGen-local shortcut added.

## Judge (acceptance)
- `just theme-check` + `just ng-ui-lint` green (token-only, no literal, no blocking modal).
- Fixture render: with `playing/hasTrack` set directly (no ViewModel), the view renders the three states
  correctly (pixel via the CGL harness).
- Live: `migx --nextgen`, load a track on Deck 1, the PLAY button toggles `[Channel1],play` and the
  state cue tracks it. Switching modes never disturbs playback (invariant #6).
- Non-modal: no `QMessageBox` reachable.

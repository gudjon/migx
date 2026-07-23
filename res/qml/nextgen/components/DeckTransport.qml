// DeckTransport — NextGen component (view). Dumb: renders a deck's transport from
// props and emits intent; no engine touch (invariant #2). Fixture-runnable — set
// deckLabel/playing/hasTrack directly with no ViewModel, so the judge renders it
// headless. Token-only (invariant #1). Minimal chrome: label + one action + a
// tiny state cue.
import QtQuick 2.12
import QtQuick.Controls
import QtQuick.Layouts
import "../primitives"
import "../../Theme"

RowLayout {
    id: view

    property string deckLabel: "DECK"
    property bool playing: false
    property bool hasTrack: false
    property bool onBeatArmed: false // pressing PLAY would snap on-beat (cap-onbeat-play)
    signal toggleRequested()

    spacing: Theme.space12

    Label {
        text: view.deckLabel
        color: Theme.textColor
        opacity: Theme.opacityMuted
        font.pixelSize: Theme.fontSizeSm
        font.bold: true
    }

    NgButton {
        text: view.playing ? "PAUSE" : "PLAY"
        accent: Theme.green
        checked: view.playing
        enabled: view.hasTrack
        onClicked: view.toggleRequested()
    }

    Label {
        text: view.hasTrack ? (view.playing ? "▶ playing"
                                             : (view.onBeatArmed ? "◇ on-beat" : "❚❚ paused"))
                            : "no track loaded"
        color: view.playing ? Theme.green : (view.onBeatArmed ? Theme.modePerform : Theme.midGray)
        font.pixelSize: Theme.fontSizeXs
    }
}

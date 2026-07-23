// DeckIdentityModel — ViewModel for DeckIdentity (nextgen-ui-architecture invariant #2).
// The only engine touch: the deck's loaded track (via PlayerManager) + bpm/key COs.
// READ-ONLY — no writer (no P-06 concern). Maps the engine ChromaticKey (1..24) to a
// musical name + Camelot label + Camelot number (the view colours the KEY badge from the
// number via Theme.keyWheelN — the model stays free of visual concerns). cap-track-identity
// + cap-harmonic-key. In fixture mode the view is driven directly and this is not built.
import QtQuick 2.12
import Mixxx 1.0 as Mixxx

QtObject {
    id: model

    property string group: "[Channel1]"

    readonly property var deckPlayer: Mixxx.PlayerManager.getPlayer(model.group)
    readonly property var currentTrack: deckPlayer ? deckPlayer.currentTrack : null

    readonly property bool hasTrack: loadedControl.value > 0
    readonly property string title: (currentTrack && currentTrack.title) ? currentTrack.title : ""
    readonly property string artist: (currentTrack && currentTrack.artist) ? currentTrack.artist : ""
    readonly property url artUrl: currentTrack ? currentTrack.coverArtUrl : ""

    readonly property real bpm: bpmControl.value
    readonly property string bpmText: (hasTrack && bpm > 0) ? bpm.toFixed(1) : "--"

    // ChromaticKey 1..24 (src/proto/keys.proto): 1..12 major, 13..24 minor. 0/invalid → none.
    readonly property int keyId: Math.round(keyControl.value)
    readonly property string keyText: keyLabel(keyId)
    readonly property int keyCamelot: camelotNumber(keyId) // 1..12, 0 = none (view → Theme["keyWheel"+n])

    // ChromaticKey → Camelot/Lancelot number (major=B, minor=A share the number's hue).
    function camelotNumber(k) {
        var t = [0, 8, 3, 10, 5, 12, 7, 2, 9, 4, 11, 6, 1, // 1..12  major
                    5, 12, 7, 2, 9, 4, 11, 6, 1, 8, 3, 10]; // 13..24 minor
        return (k >= 1 && k <= 24) ? t[k] : 0;
    }

    function keyLabel(k) {
        if (!hasTrack || k < 1 || k > 24) {
            return "--";
        }
        var names = ["", "C", "D♭", "D", "E♭", "E", "F", "G♭", "G", "A♭", "A", "B♭", "B",
                     "Cm", "C♯m", "Dm", "E♭m", "Em", "Fm", "F♯m", "Gm", "G♯m", "Am", "B♭m", "Bm"];
        var letter = (k <= 12) ? "B" : "A";
        return names[k] + " · " + camelotNumber(k) + letter;
    }

    property Mixxx.ControlProxy loadedControl: Mixxx.ControlProxy {
        group: model.group
        key: "track_loaded"
    }
    property Mixxx.ControlProxy bpmControl: Mixxx.ControlProxy {
        group: model.group
        key: "bpm"
    }
    property Mixxx.ControlProxy keyControl: Mixxx.ControlProxy {
        group: model.group
        key: "key"
    }
}

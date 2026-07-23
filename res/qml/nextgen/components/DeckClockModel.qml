// DeckClockModel — ViewModel for DeckClock (nextgen-ui-architecture invariant #2).
// The only engine touch: binds a deck's time ControlObjects over the [Group],key
// bus and derives formatted elapsed/remaining/total. READ-ONLY — no writer, so no
// P-06 concern. In fixture mode the view is driven directly and this is not built.
import QtQuick 2.12
import Mixxx 1.0 as Mixxx

QtObject {
    id: model

    property string group: "[Channel1]"

    // Seconds remaining below which the deck is "ending" (mix-out warning). Not a
    // visual value, so it lives here as a named binding, not a DESIGN.md token.
    property int endingThresholdSec: 30

    readonly property bool hasTrack: loadedControl.value > 0
    readonly property real durationSec: durationControl.value // seconds
    readonly property real positionRatio: Math.max(0, Math.min(1, positionControl.value))
    readonly property real elapsedSec: positionRatio * durationSec
    readonly property real remainingSec: Math.max(0, durationSec - elapsedSec)
    readonly property bool ending: hasTrack && remainingSec > 0 && remainingSec <= endingThresholdSec

    readonly property string elapsed: format(elapsedSec)
    readonly property string remaining: hasTrack ? "-" + format(remainingSec) : format(0)
    readonly property string total: format(durationSec)

    function format(sec) {
        if (!hasTrack || sec < 0 || isNaN(sec)) {
            return "--:--";
        }
        var whole = Math.floor(sec);
        var m = Math.floor(whole / 60);
        var r = whole % 60;
        return m + ":" + (r < 10 ? "0" : "") + r;
    }

    property Mixxx.ControlProxy durationControl: Mixxx.ControlProxy {
        group: model.group
        key: "duration"
    }
    property Mixxx.ControlProxy positionControl: Mixxx.ControlProxy {
        group: model.group
        key: "playposition"
    }
    property Mixxx.ControlProxy loadedControl: Mixxx.ControlProxy {
        group: model.group
        key: "track_loaded"
    }
}

// DeckTransportModel — the ViewModel for DeckTransport (nextgen-ui-architecture
// invariant #2). The ONLY engine touch: binds the deck's ControlObjects via typed
// proxies over the [Group],key bus. The view stays dumb. In fixture mode the view
// is driven directly and this model is not instantiated. One writer per CO (P-06):
// togglePlay() is the authoritative writer for [group],play here.
import QtQuick 2.12
import Mixxx 1.0 as Mixxx

QtObject {
    id: model

    property string group: "[Channel1]"
    readonly property bool playing: playControl.value > 0
    readonly property bool hasTrack: loadedControl.value > 0

    function togglePlay() {
        playControl.value = playControl.value > 0 ? 0 : 1;
    }

    property Mixxx.ControlProxy playControl: Mixxx.ControlProxy {
        group: model.group
        key: "play"
    }
    property Mixxx.ControlProxy loadedControl: Mixxx.ControlProxy {
        group: model.group
        key: "track_loaded"
    }
}

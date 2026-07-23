// DeckTransportModel — the ViewModel for DeckTransport (nextgen-ui-architecture
// invariant #2). The ONLY engine touch: binds the deck's ControlObjects via typed
// proxies over the [Group],key bus. The view stays dumb. In fixture mode the view
// is driven directly and this model is not instantiated. One writer per CO (P-06):
// togglePlay() is the authoritative writer for [group],play here.
//
// On-beat play (cap-onbeat-play; SSoT: kanban/knowledge/research-onbeat-play-phase-snap):
// pressing PLAY while a leader deck plays composes the existing sync/quantize/phase COs
// so the deck starts already on-beat (Mode A). Default ON; honest degrade to a raw play
// if there is no leader / no track. Policy at the play edge — GUI thread setting COs,
// never RT DSP. This is Grok research ladder wave 1 (compose, no new beat tracker).
import QtQuick 2.12
import Mixxx 1.0 as Mixxx

QtObject {
    id: model

    property string group: "[Channel1]"
    // The deck to align to when starting (set by the shell; "" = none). v1 = one leader
    // (the 2-deck default); the 3+-deck timebase rule is the open owner question.
    property string leaderGroup: ""
    property bool onBeatPlay: true // default ON (opt-out lands with settings)

    readonly property bool playing: playControl.value > 0
    readonly property bool hasTrack: loadedControl.value > 0
    readonly property bool leaderPlaying: model.leaderGroup !== "" && leaderPlayControl.value > 0
    // Shown as the quiet "◇ on-beat" cue on the strip when a start would snap.
    readonly property bool onBeatArmed: model.onBeatPlay && model.leaderPlaying && model.hasTrack

    function togglePlay() {
        if (playControl.value > 0) {
            playControl.value = 0; // pause — never snaps
            return;
        }
        if (model.onBeatArmed) {
            // Mode A: quantize on → match tempo (while stopped) → play → align phase.
            // beatsync_* target Mixxx's sync leader (the playing deck) automatically.
            quantizeControl.value = 1;
            syncTempoControl.value = 1;
            playControl.value = 1;
            syncPhaseControl.value = 1;
        } else {
            playControl.value = 1; // honest degrade: raw play
        }
    }

    property Mixxx.ControlProxy playControl: Mixxx.ControlProxy {
        group: model.group
        key: "play"
    }
    property Mixxx.ControlProxy loadedControl: Mixxx.ControlProxy {
        group: model.group
        key: "track_loaded"
    }
    property Mixxx.ControlProxy leaderPlayControl: Mixxx.ControlProxy {
        group: model.leaderGroup
        key: "play"
    }
    property Mixxx.ControlProxy quantizeControl: Mixxx.ControlProxy {
        group: model.group
        key: "quantize"
    }
    property Mixxx.ControlProxy syncTempoControl: Mixxx.ControlProxy {
        group: model.group
        key: "beatsync_tempo"
    }
    property Mixxx.ControlProxy syncPhaseControl: Mixxx.ControlProxy {
        group: model.group
        key: "beatsync_phase"
    }
}

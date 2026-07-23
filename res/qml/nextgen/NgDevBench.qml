// NgDevBench — NextGen dev test-bench. Auto-loads the generated demo tracks onto
// Deck 1/2 at startup so the deck-shell (identity/clock/transport) always has real
// data to render against — the fixture-mode base (nextgen-ui-architecture invariant #4).
//
// Opt-in by PRESENCE: the tracks live in res/dev-fixtures/ (gitignored, made by
// `just dev-fixtures`). In a release bundle that directory is absent, so the load is a
// quiet no-op (non-modal law). Always play=false — it loads, never auto-plays.
import QtQuick 2.12
import Mixxx 1.0 as Mixxx

QtObject {
    id: bench

    // Resolved relative to this file: res/qml/nextgen/ -> ../../dev-fixtures/
    // (bundle: Resources/qml/nextgen/ -> Resources/dev-fixtures/).
    readonly property url fixtureA: Qt.resolvedUrl("../../dev-fixtures/Demo Deck A - 128 BPM Am.wav")
    readonly property url fixtureB: Qt.resolvedUrl("../../dev-fixtures/Demo Deck B - 125 BPM Gm.wav")

    function load() {
        var p1 = Mixxx.PlayerManager.getPlayer("[Channel1]");
        var p2 = Mixxx.PlayerManager.getPlayer("[Channel2]");
        if (p1) {
            p1.loadTrackFromLocationUrl(bench.fixtureA, false);
        }
        if (p2) {
            p2.loadTrackFromLocationUrl(bench.fixtureB, false);
        }
    }

    Component.onCompleted: load()
}

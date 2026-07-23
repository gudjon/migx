// DeckClock — NextGen component (view). Dumb: renders a deck's time readout from
// props; no engine touch (invariant #2). Fixture-runnable — set elapsed/remaining/
// total/ending directly with no ViewModel, so the judge renders it headless.
// Token-only (invariant #1). The DJ's mix-out clock: remaining is the loud number;
// elapsed / total sit quiet beneath. Turns red when the track is ending.
import QtQuick 2.12
import QtQuick.Controls
import QtQuick.Layouts
import "../../Theme"

ColumnLayout {
    id: view

    property string elapsed: "--:--"
    property string remaining: "--:--"
    property string total: "--:--"
    property bool hasTrack: false
    property bool ending: false

    spacing: Theme.space2

    // Remaining — the DJ's mix-out clock, the prominent number.
    Label {
        Layout.alignment: Qt.AlignHCenter
        text: view.remaining
        color: view.ending ? Theme.red : (view.hasTrack ? Theme.textColor : Theme.midGray)
        font.pixelSize: Theme.fontSizeXl
        font.bold: true
        Behavior on color {
            ColorAnimation {
                duration: Theme.motionFastMs
            }
        }
    }

    // Elapsed / total — quiet context beneath.
    RowLayout {
        Layout.alignment: Qt.AlignHCenter
        spacing: Theme.space3
        Label {
            text: view.elapsed
            color: Theme.midGray
            font.pixelSize: Theme.fontSizeXs
        }
        Label {
            text: "/"
            color: Theme.midGray
            font.pixelSize: Theme.fontSizeXs
        }
        Label {
            text: view.total
            color: Theme.midGray
            font.pixelSize: Theme.fontSizeXs
        }
    }
}

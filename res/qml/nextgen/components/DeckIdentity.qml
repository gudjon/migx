// DeckIdentity — NextGen component (view). Dumb: renders "what's loaded / is it
// mixable" from props; no engine touch (invariant #2). Fixture-runnable — set
// title/artist/bpmText/keyText/keyCamelot/hasTrack directly. Token-only (invariant #1);
// the KEY badge is coloured from the Camelot number via the DESIGN.md key-wheel tokens.
// Compact + left-aligned so the header tiles for multi-deck (Traktor). cap-track-identity.
import QtQuick 2.12
import QtQuick.Controls
import QtQuick.Layouts
import "../primitives"
import "../../Theme"

RowLayout {
    id: view

    property string title: ""
    property string artist: ""
    property url artUrl: ""
    property string bpmText: "--"
    property string keyText: "--"
    property int keyCamelot: 0 // 1..12 → Theme.keyWheelN; 0 → no colour
    property bool hasTrack: false

    readonly property color keyColor: keyCamelot > 0 ? Theme["keyWheel" + keyCamelot] : Theme.transparent

    spacing: Theme.space12

    // Album art — small anchor, fail-quiet placeholder (never a dialog).
    Rectangle {
        Layout.alignment: Qt.AlignVCenter
        implicitWidth: Theme.space28 * 2
        implicitHeight: Theme.space28 * 2
        radius: Theme.radius0
        color: Theme.deckEmptyCoverArt
        clip: true
        Image {
            anchors.fill: parent
            source: view.hasTrack ? view.artUrl : ""
            fillMode: Image.PreserveAspectCrop
            asynchronous: true
            visible: status === Image.Ready
        }
    }

    ColumnLayout {
        spacing: Theme.space3

        Label {
            text: view.hasTrack ? (view.title !== "" ? view.title : "Untitled") : "— no track —"
            color: view.hasTrack ? Theme.textColor : Theme.midGray
            font.pixelSize: Theme.fontSizeLg
            font.bold: true
            elide: Text.ElideRight
            Layout.maximumWidth: Theme.nextgenWindowWidth / 3
        }
        Label {
            text: view.artist
            color: Theme.midGray
            font.pixelSize: Theme.fontSizeSm
            visible: view.hasTrack && view.artist !== ""
            elide: Text.ElideRight
            Layout.maximumWidth: Theme.nextgenWindowWidth / 3
        }
        RowLayout {
            spacing: Theme.space3
            NgBadge {
                text: view.bpmText + " BPM"
            }
            NgBadge {
                text: view.keyText
                accent: view.keyColor
            }
        }
    }
}

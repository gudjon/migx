// NgBadge — reusable token-only pill for a compact labelled value (BPM, KEY, tag).
// No engine (invariant #1: token-only, no ControlProxy). `accent` (optional) shows as
// a thin left colour bar — used for the Camelot key-wheel colour on the KEY badge, and
// left transparent for a neutral badge (BPM). Reused on the deck and, later, ARRANGE rows.
import QtQuick 2.12
import QtQuick.Controls
import "../../Theme"

Rectangle {
    id: badge

    property string text: ""
    property color accent: Theme.transparent

    implicitWidth: row.implicitWidth + Theme.space12
    implicitHeight: label.implicitHeight + Theme.space3 + Theme.space3
    radius: Theme.radius0
    color: Theme.knobBackgroundColor

    Row {
        id: row
        anchors.centerIn: parent
        spacing: Theme.space3

        Rectangle {
            id: accentBar
            visible: badge.accent !== Theme.transparent
            width: Theme.space2
            height: label.implicitHeight
            radius: Theme.radius0
            color: badge.accent
            anchors.verticalCenter: parent.verticalCenter
        }

        Label {
            id: label
            text: badge.text
            color: Theme.textColor
            font.pixelSize: Theme.fontSizeSm
            font.bold: true
        }
    }
}

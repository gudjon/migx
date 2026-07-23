// NgModePlaceholder — a NextGen primitive (nextgen-ui-architecture, primitives layer).
// Token-only, engine-free: renders a full-screen mode placeholder with the mode's
// accent. Replaced by the real module (deck-shell, music-management, …) in each
// mode panel as those land. Demonstrates the primitive contract: explicit typed
// props, all visual values from `Theme`, no hardcoded literals.
import QtQuick 2.12
import QtQuick.Controls
import "../../Theme"

Rectangle {
    id: placeholder

    property color accent: Theme.accent
    property string title: ""
    property string body: ""

    color: Theme.sunkenBackgroundColor

    // Mode identity: a thin accent bar at the top of the panel.
    Rectangle {
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        height: 3
        color: placeholder.accent
    }

    Column {
        anchors.centerIn: parent
        spacing: 12
        Label {
            anchors.horizontalCenter: parent.horizontalCenter
            text: placeholder.title
            color: placeholder.accent
            font.pixelSize: 22
            font.bold: true
        }
        Label {
            anchors.horizontalCenter: parent.horizontalCenter
            text: placeholder.body
            color: Theme.midGray
            font.pixelSize: 14
            horizontalAlignment: Text.AlignHCenter
        }
    }
}

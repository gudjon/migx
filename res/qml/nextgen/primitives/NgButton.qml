// NgButton — NextGen primitive (nextgen-ui-architecture, primitives layer).
// Token-only, engine-free. A flat console button: sharp corners, accent border,
// fills with the accent when active. All visual values from `Theme` (invariant #1).
import QtQuick 2.12
import QtQuick.Controls
import "../../Theme"

Button {
    id: control

    // The caller sets the accent (e.g. Theme.green for a live/playing action).
    property color accent: Theme.accent

    flat: true
    padding: Theme.space12

    contentItem: Label {
        text: control.text
        color: control.checked ? Theme.sunkenBackgroundColor : Theme.textColor
        opacity: control.enabled ? Theme.opacityFull : Theme.opacityMuted
        font.pixelSize: Theme.fontSizeMd
        font.bold: true
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
    }

    background: Rectangle {
        radius: Theme.radius0
        color: control.checked
                ? control.accent
                : (control.hovered ? Theme.darkGray2 : Theme.knobBackgroundColor)
        border.color: control.accent
        border.width: Theme.space2
        Behavior on color { ColorAnimation { duration: Theme.motionFastMs } }
    }
}

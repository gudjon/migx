// Migx NextGen — shadow UI shell (ADR-007 · nextgen-ui-architecture).
// The shell owns the active mode and hosts the three full-screen modes. Every
// visual value is a DESIGN.md token via `Theme` (invariant #1: no hardcoded
// literals). Modes are modes, never blocking dialogs; nothing here interrupts
// playback (invariant #5, ui-non-modal-error-ux). Real modules land in the mode
// panels per the ADR-007 build order.
import QtQuick 2.12
import QtQuick.Controls
import QtQuick.Layouts
import "../Theme"
import "primitives"

ApplicationWindow {
    id: root
    visible: true
    width: 1280
    height: 800
    title: "Migx NextGen"
    color: Theme.sunkenBackgroundColor

    // Full-screen modes the DJ switches between (nextgen-dj-ux-modes-and-signal).
    readonly property var modeNames: ["PERFORM", "ARRANGE", "LIBRARY"]
    readonly property var modeColors: [Theme.modePerform, Theme.modeArrange, Theme.modeLibrary]
    property int mode: 0
    readonly property color currentModeColor: modeColors[mode]

    header: ToolBar {
        padding: 0
        background: Rectangle {
            color: Theme.backgroundColor
            // The active mode's identity color, as a thin bottom seam.
            Rectangle {
                anchors.bottom: parent.bottom
                width: parent.width
                height: 2
                color: root.currentModeColor
            }
        }
        RowLayout {
            anchors.fill: parent
            spacing: 0
            Label {
                text: "◆ Migx NextGen"
                color: root.currentModeColor
                font.pixelSize: 15
                font.bold: true
                leftPadding: 18
                rightPadding: 28
                Behavior on color { ColorAnimation { duration: 120 } }
            }
            Repeater {
                model: root.modeNames
                delegate: Button {
                    required property int index
                    required property string modelData
                    flat: true
                    checkable: true
                    checked: root.mode === index
                    padding: 16
                    onClicked: root.mode = index
                    contentItem: Label {
                        text: modelData
                        color: parent.checked ? root.modeColors[index] : Theme.textColor
                        opacity: parent.checked ? 1.0 : 0.7
                        font.pixelSize: 13
                        font.bold: parent.checked
                        verticalAlignment: Text.AlignVCenter
                    }
                    background: Rectangle {
                        color: "transparent"
                        Rectangle { // active-tab underline in the mode's color
                            anchors.bottom: parent.bottom
                            width: parent.width
                            height: 2
                            color: root.modeColors[index]
                            visible: parent.parent.checked
                        }
                    }
                }
            }
            Item { Layout.fillWidth: true }
            Label {
                text: "engine: shared · non-modal"
                color: Theme.midGray
                font.pixelSize: 11
                rightPadding: 16
            }
        }
    }

    StackLayout {
        anchors.fill: parent
        currentIndex: root.mode

        // 0 · PERFORM — the live multi-deck mix surface
        NgModePlaceholder {
            accent: Theme.modePerform
            title: "PERFORM"
            body: "multi-deck mix surface — the deck-shell module lands here\n(dual-deck default · vertical N-deck · ~4–6 playable)"
        }
        // 1 · ARRANGE — the differentiator: find the next track, fast
        NgModePlaceholder {
            accent: Theme.modeArrange
            title: "ARRANGE"
            body: "music management under cognitive load — find the next track\n(artwork · key/bpm/energy · tags · playlists · community-signal chips)"
        }
        // 2 · LIBRARY
        NgModePlaceholder {
            accent: Theme.modeLibrary
            title: "LIBRARY"
            body: "browse the collection"
        }
    }
}

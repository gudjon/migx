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
import "components"

ApplicationWindow {
    id: root
    visible: true
    width: Theme.nextgenWindowWidth
    height: Theme.nextgenWindowHeight
    title: "Migx NextGen"
    color: Theme.sunkenBackgroundColor

    // Full-screen modes the DJ switches between (nextgen-dj-ux-modes-and-signal).
    readonly property var modeNames: ["PERFORM", "ARRANGE", "LIBRARY"]
    readonly property var modeColors: [Theme.modePerform, Theme.modeArrange, Theme.modeLibrary]
    readonly property var modeKeys: ["⌘1", "⌘2", "⌘3"] // ⌘1/2/3
    property int mode: 0
    readonly property color currentModeColor: modeColors[mode]

    // Hot mode switching (KEYMAP.md): ⌘1/2/3 direct, Tab cycles. On macOS
    // Qt "Ctrl" is ⌘. Deck/hotcue/library shortcuts land with their modules.
    Shortcut { sequences: ["Ctrl+1"]; onActivated: root.mode = 0 }
    Shortcut { sequences: ["Ctrl+2"]; onActivated: root.mode = 1 }
    Shortcut { sequences: ["Ctrl+3"]; onActivated: root.mode = 2 }
    Shortcut { sequence: "Tab"; onActivated: root.mode = (root.mode + 1) % root.modeNames.length }
    Shortcut { sequence: "Shift+Tab"; onActivated: root.mode = (root.mode + root.modeNames.length - 1) % root.modeNames.length }

    header: ToolBar {
        padding: Theme.space0
        background: Rectangle {
            color: Theme.backgroundColor
            // The active mode's identity color, as a thin bottom seam.
            Rectangle {
                anchors.bottom: parent.bottom
                width: parent.width
                height: Theme.space2
                color: root.currentModeColor
            }
        }
        RowLayout {
            anchors.fill: parent
            spacing: Theme.space0
            Label {
                text: "◆ Migx NextGen"
                color: root.currentModeColor
                font.pixelSize: Theme.fontSizeLg
                font.bold: true
                leftPadding: Theme.space18
                rightPadding: Theme.space28
                Behavior on color { ColorAnimation { duration: Theme.motionFastMs } }
            }
            Repeater {
                model: root.modeNames
                delegate: Button {
                    required property int index
                    required property string modelData
                    flat: true
                    checkable: true
                    checked: root.mode === index
                    padding: Theme.space16
                    onClicked: root.mode = index
                    // Minimal admin chrome: the tab shows only the name. The
                    // shortcut is on-demand (hover), zero permanent space — it is
                    // a stable, fast-learned feature.
                    ToolTip.text: modelData + "   " + root.modeKeys[index]
                    ToolTip.visible: hovered
                    contentItem: Label {
                        text: modelData
                        color: root.mode === index ? root.modeColors[index] : Theme.textColor
                        opacity: root.mode === index ? Theme.opacityFull : Theme.opacityMuted
                        font.pixelSize: Theme.fontSizeSm
                        font.bold: root.mode === index
                        verticalAlignment: Text.AlignVCenter
                    }
                    background: Rectangle {
                        color: Theme.transparent
                        Rectangle { // active-tab underline in the mode's color
                            anchors.bottom: parent.bottom
                            width: parent.width
                            height: Theme.space2
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
                font.pixelSize: Theme.fontSizeXs
                rightPadding: Theme.space16
            }
        }
    }

    StackLayout {
        anchors.fill: parent
        currentIndex: root.mode

        // 0 · PERFORM — first uplifted component: deck transport (Deck 1)
        Rectangle {
            color: Theme.sunkenBackgroundColor
            Rectangle { // mode accent bar
                anchors.top: parent.top
                anchors.left: parent.left
                anchors.right: parent.right
                height: Theme.space3
                color: Theme.modePerform
            }
            DeckTransportModel {
                id: deck1
                group: "[Channel1]"
            }
            ColumnLayout {
                anchors.centerIn: parent
                spacing: Theme.space16
                DeckTransport {
                    Layout.alignment: Qt.AlignHCenter
                    deckLabel: "DECK 1"
                    playing: deck1.playing
                    hasTrack: deck1.hasTrack
                    onToggleRequested: deck1.togglePlay()
                }
                Label {
                    Layout.alignment: Qt.AlignHCenter
                    text: "first uplifted component · the deck-shell grows here"
                    color: Theme.midGray
                    font.pixelSize: Theme.fontSizeXs
                }
            }
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

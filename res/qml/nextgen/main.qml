// Migx NextGen — shadow UI shell (ADR-007). Loaded via QmlApplication with
// `--nextgen`, reusing the shared engine + ControlObject bus; NO legacy skin/
// widget chrome. This scaffold (module step 0) proves the shell + the full-screen
// mode model + the DESIGN.md aesthetic. Real modules (deck-shell, music-management)
// land in the mode panels per the ADR-007 build order. Non-modal by construction:
// modes are modes, never blocking dialogs; nothing here interrupts playback.
import QtQuick 2.12
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
    id: root
    visible: true
    width: 1280
    height: 800
    title: "Migx NextGen"

    // DESIGN.md tokens (scaffold; res/design/DESIGN.md → Theme.qml generation lands
    // as the design-system module — kept inline here so the shell is self-contained
    // and carries no legacy Theme dependency).
    readonly property color surface: "#1e1e1e"
    readonly property color sunken: "#0c0c0c"
    readonly property color textPrimary: "#ededed"
    readonly property color textMuted: "#8a8a8a"
    readonly property color accent: "#3b82f6"

    // The DJ switches between full-screen modes (nextgen-dj-ux-modes-and-signal).
    property int mode: 0 // 0 PERFORM · 1 ARRANGE · 2 LIBRARY

    color: sunken

    header: ToolBar {
        padding: 0
        background: Rectangle {
            color: root.surface
            Rectangle {
                anchors.bottom: parent.bottom
                width: parent.width
                height: 1
                color: "#000000"
            }
        }
        RowLayout {
            anchors.fill: parent
            spacing: 0
            Label {
                text: "◆ Migx NextGen"
                color: root.accent
                font.pixelSize: 15
                font.bold: true
                leftPadding: 18
                rightPadding: 28
            }
            Repeater {
                model: ["PERFORM", "ARRANGE", "LIBRARY"]
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
                        color: parent.checked ? root.accent : root.textPrimary
                        font.pixelSize: 13
                        font.bold: parent.checked
                        verticalAlignment: Text.AlignVCenter
                    }
                    background: Rectangle { color: "transparent" }
                }
            }
            Item { Layout.fillWidth: true }
            Label {
                text: "engine: shared · non-modal"
                color: root.textMuted
                font.pixelSize: 11
                rightPadding: 16
            }
        }
    }

    StackLayout {
        anchors.fill: parent
        currentIndex: root.mode

        // 0 · PERFORM — the live multi-deck mix surface
        Rectangle {
            color: root.sunken
            Label {
                anchors.centerIn: parent
                horizontalAlignment: Text.AlignHCenter
                color: root.textMuted
                font.pixelSize: 15
                text: "PERFORM\nmulti-deck mix surface — the deck-shell module lands here\n(dual-deck default · vertical N-deck · ~4–6 playable)"
            }
        }

        // 1 · ARRANGE — the differentiator: find the next track, fast
        Rectangle {
            color: root.sunken
            Label {
                anchors.centerIn: parent
                horizontalAlignment: Text.AlignHCenter
                color: root.textMuted
                font.pixelSize: 15
                text: "ARRANGE\nmusic management under cognitive load — find the next track\n(artwork · key/bpm/energy · tags · playlists · community-signal chips)"
            }
        }

        // 2 · LIBRARY
        Rectangle {
            color: root.sunken
            Label {
                anchors.centerIn: parent
                color: root.textMuted
                font.pixelSize: 15
                text: "LIBRARY"
            }
        }
    }
}

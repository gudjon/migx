import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs
import Mixxx 1.0 as Mixxx
import ".." as Skin
import "../Theme"

// Layer B dogfood: show offline co-pilot why-next (Predict → Ask → Explain).
// Loads res/qml/CoPilot/fixture_why_next.json (synced by `just exo-copilot-why`).
// No engine / ControlObject writes — Ack/Reject update UI status only.

Category {
    id: root
    label: "Co-Pilot (dogfood)"

    property var proposalDoc: ({})
    property string intentStatus: "proposed"
    property string loadError: ""
    property string fixtureUrl: Qt.resolvedUrl("../CoPilot/fixture_why_next.json")

    function badgeFor(source) {
        if (source === "spotify")
            return "SP";
        if (source === "local")
            return "LCL";
        if (source === "hybrid")
            return "HYB";
        return "??";
    }

    function loadFixture(url) {
        root.loadError = "";
        var xhr = new XMLHttpRequest();
        xhr.open("GET", url);
        xhr.onreadystatechange = function () {
            if (xhr.readyState !== XMLHttpRequest.DONE)
                return;
            if (xhr.status !== 0 && xhr.status !== 200) {
                root.loadError = "HTTP " + xhr.status + " loading fixture";
                return;
            }
            try {
                root.proposalDoc = JSON.parse(xhr.responseText);
                root.intentStatus = "proposed";
            } catch (e) {
                root.loadError = "JSON parse error: " + e;
            }
        };
        xhr.send();
    }

    Component.onCompleted: loadFixture(fixtureUrl)

    Mixxx.SettingParameter {
        label: "Offline why-next (Layer B)"

        ColumnLayout {
            spacing: 10
            width: parent ? parent.width : 480

            Text {
                Layout.fillWidth: true
                wrapMode: Text.WordWrap
                color: Theme.textColor
                font.family: Theme.fontFamily
                font.pixelSize: Theme.textFontPixelSize
                text: "Predict → Ask → Explain. Dogfood only — does not load decks or write ControlObjects. " + "Regenerate fixture with `just exo-copilot-why`."
            }

            RowLayout {
                Layout.fillWidth: true
                spacing: 8

                Skin.FormButton {
                    text: "Reload fixture"
                    activeColor: Theme.blue
                    onPressed: root.loadFixture(root.fixtureUrl)
                }
                Skin.FormButton {
                    text: "Open JSON…"
                    activeColor: Theme.midGray2
                    onPressed: openDialog.open()
                }
                Item {
                    Layout.fillWidth: true
                }
                Text {
                    color: root.intentStatus === "acked" ? Theme.green : (root.intentStatus === "rejected" ? Theme.red : Theme.yellow)
                    font.family: Theme.fontFamily
                    font.pixelSize: Theme.buttonFontPixelSize
                    font.bold: true
                    text: "STATUS: " + root.intentStatus.toUpperCase()
                }
            }

            Text {
                visible: root.loadError.length > 0
                Layout.fillWidth: true
                wrapMode: Text.WordWrap
                color: Theme.red
                font.family: Theme.fontFamily
                font.pixelSize: Theme.textFontPixelSize
                text: root.loadError
            }

            // Current
            Rectangle {
                Layout.fillWidth: true
                implicitHeight: currentCol.implicitHeight + 16
                color: Theme.sunkenBackgroundColor
                radius: 6
                border.color: Theme.darkGray3
                border.width: 1

                ColumnLayout {
                    id: currentCol
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.top: parent.top
                    anchors.margins: 8
                    spacing: 4

                    Text {
                        color: Theme.lightGray2
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.buttonFontPixelSize
                        font.capitalization: Font.AllUppercase
                        text: "Current"
                    }
                    RowLayout {
                        Text {
                            color: Theme.deckTextColor
                            font.family: Theme.fontFamily
                            font.pixelSize: Theme.textFontPixelSize
                            font.bold: true
                            text: root.proposalDoc.current_song_id || "—"
                        }
                        Rectangle {
                            radius: 3
                            color: Theme.darkGray3
                            implicitHeight: badgeCur.implicitHeight + 4
                            implicitWidth: badgeCur.implicitWidth + 10
                            Text {
                                id: badgeCur
                                anchors.centerIn: parent
                                color: Theme.blue
                                font.family: Theme.fontFamily
                                font.pixelSize: Theme.buttonFontPixelSize
                                font.bold: true
                                text: root.badgeFor(root.proposalDoc.current_source)
                            }
                        }
                        Text {
                            color: Theme.lightGray2
                            font.family: Theme.fontFamily
                            font.pixelSize: Theme.textFontPixelSize
                            text: root.proposalDoc.current_camelot || ""
                        }
                    }
                    Text {
                        color: Theme.midGray
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.buttonFontPixelSize
                        text: root.proposalDoc.generated_utc ? ("Generated " + root.proposalDoc.generated_utc) : ""
                    }
                }
            }

            // Proposal
            Rectangle {
                Layout.fillWidth: true
                implicitHeight: propCol.implicitHeight + 16
                color: Theme.darkGray2
                radius: 6
                border.color: Theme.green
                border.width: 1

                ColumnLayout {
                    id: propCol
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.top: parent.top
                    anchors.margins: 8
                    spacing: 6

                    Text {
                        color: Theme.green
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.buttonFontPixelSize
                        font.capitalization: Font.AllUppercase
                        text: "Proposal (Predict)"
                    }
                    RowLayout {
                        Text {
                            color: Theme.white
                            font.family: Theme.fontFamily
                            font.pixelSize: Theme.textFontPixelSize
                            font.bold: true
                            text: (root.proposalDoc.proposal && root.proposalDoc.proposal.song_id) || "— no proposal —"
                        }
                        Rectangle {
                            radius: 3
                            color: Theme.darkGray3
                            implicitHeight: badgeProp.implicitHeight + 4
                            implicitWidth: badgeProp.implicitWidth + 10
                            Text {
                                id: badgeProp
                                anchors.centerIn: parent
                                color: (root.proposalDoc.proposal && root.proposalDoc.proposal.source === "spotify") ? Theme.yellow : Theme.green
                                font.family: Theme.fontFamily
                                font.pixelSize: Theme.buttonFontPixelSize
                                font.bold: true
                                text: root.badgeFor(root.proposalDoc.proposal ? root.proposalDoc.proposal.source : "")
                            }
                        }
                    }
                    Text {
                        color: Theme.lightGray2
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.textFontPixelSize
                        text: {
                            var p = root.proposalDoc.proposal;
                            if (!p)
                                return "";
                            var md = p.playback && p.playback.multi_deck_allowed;
                            return "relation: " + (p.relation || "?") + " · score " + (p.score !== undefined ? p.score : "?") + " · Camelot " + (p.camelot || "?") + " · multi_deck=" + md;
                        }
                    }
                }
            }

            // Why
            Rectangle {
                Layout.fillWidth: true
                implicitHeight: whyCol.implicitHeight + 16
                color: Theme.sunkenBackgroundColor
                radius: 6
                border.color: Theme.darkGray3
                border.width: 1

                ColumnLayout {
                    id: whyCol
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.top: parent.top
                    anchors.margins: 8
                    spacing: 4

                    Text {
                        color: Theme.lightGray2
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.buttonFontPixelSize
                        font.capitalization: Font.AllUppercase
                        text: "Why (Explain)"
                    }

                    Repeater {
                        model: (root.proposalDoc.proposal && root.proposalDoc.proposal.reasons) || []
                        delegate: Text {
                            required property string modelData
                            Layout.fillWidth: true
                            wrapMode: Text.WordWrap
                            color: Theme.textColor
                            font.family: Theme.fontFamily
                            font.pixelSize: Theme.textFontPixelSize
                            text: "• " + modelData
                        }
                    }

                    Text {
                        visible: !(root.proposalDoc.proposal && root.proposalDoc.proposal.reasons && root.proposalDoc.proposal.reasons.length)
                        color: Theme.midGray
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.textFontPixelSize
                        text: "No reasons loaded. Run just exo-copilot-why and Reload."
                    }
                }
            }

            // Ask
            RowLayout {
                Layout.fillWidth: true
                spacing: 8

                Skin.FormButton {
                    text: "Ack (Ask → yes)"
                    activeColor: Theme.green
                    enabled: root.intentStatus === "proposed" && root.proposalDoc.proposal
                    onPressed: root.intentStatus = "acked"
                }
                Skin.FormButton {
                    text: "Reject"
                    activeColor: Theme.red
                    enabled: root.intentStatus === "proposed" && root.proposalDoc.proposal
                    onPressed: root.intentStatus = "rejected"
                }
                Skin.FormButton {
                    text: "Reset"
                    activeColor: Theme.midGray2
                    onPressed: root.intentStatus = "proposed"
                }
            }

            Text {
                Layout.fillWidth: true
                wrapMode: Text.WordWrap
                color: Theme.midGray
                font.family: Theme.fontFamily
                font.pixelSize: Theme.buttonFontPixelSize
                text: "House physics: no RT JSON parse; Ack does not call LoadTrack yet (P-06 path future). Spotify dual multi-deck remains forbidden."
            }
        }
    }

    FileDialog {
        id: openDialog
        title: "Open COPILOT-WHY-NEXT.json"
        nameFilters: ["JSON (*.json)"]
        fileMode: FileDialog.OpenFile
        onAccepted: {
            var u = selectedFile;
            if (u)
                root.loadFixture(u);
        }
    }
}

// DeckStrip — composes one deck's identity + clock + transport into a single horizontal
// strip for the vertical multi-deck PERFORM layout (perform-multideck-layout draft).
// Parameterized by `group` so PERFORM tiles N of these from a list (dual-deck default,
// flexible to 4–6). Token-only; the three child ViewModels are the only engine touch
// (each read-only except transport's sole play writer — P-06). Consistent row shape so
// the eye lands in the same place on every deck.
import QtQuick 2.12
import QtQuick.Controls
import QtQuick.Layouts
import "../../Theme"

Rectangle {
    id: strip

    property string group: "[Channel1]"
    property string deckLabel: "DECK"
    property string leaderGroup: "" // the deck on-beat play aligns to (shell sets it)

    Layout.fillWidth: true
    implicitHeight: row.implicitHeight + Theme.space16 + Theme.space16
    radius: Theme.radius0
    color: Theme.deckInfoBarBackgroundColor

    DeckTransportModel {
        id: transportModel
        group: strip.group
        leaderGroup: strip.leaderGroup
    }
    DeckClockModel {
        id: clockModel
        group: strip.group
    }
    DeckIdentityModel {
        id: identityModel
        group: strip.group
    }

    RowLayout {
        id: row
        anchors.fill: parent
        anchors.margins: Theme.space16
        spacing: Theme.space18

        DeckIdentity {
            Layout.fillWidth: true
            Layout.alignment: Qt.AlignVCenter
            hasTrack: identityModel.hasTrack
            title: identityModel.title
            artist: identityModel.artist
            artUrl: identityModel.artUrl
            bpmText: identityModel.bpmText
            keyText: identityModel.keyText
            keyCamelot: identityModel.keyCamelot
        }

        DeckClock {
            Layout.alignment: Qt.AlignVCenter
            hasTrack: clockModel.hasTrack
            elapsed: clockModel.elapsed
            remaining: clockModel.remaining
            total: clockModel.total
            ending: clockModel.ending
        }

        DeckTransport {
            Layout.alignment: Qt.AlignVCenter
            deckLabel: strip.deckLabel
            playing: transportModel.playing
            hasTrack: transportModel.hasTrack
            onBeatArmed: transportModel.onBeatArmed
            onToggleRequested: transportModel.togglePlay()
        }
    }
}

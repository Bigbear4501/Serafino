// Pingulinux „Restzeit“ – gut lesbare Anzeige in der Taskleiste der Kinder:
// „⏳ Noch 45 Min“, gelb ab 15 Minuten, rot ab 5 Minuten.
// Steht die Zeit gerade (nur Lernen/Malen offen, b29): „🎨 Noch 16 Min · zählt nicht“ in Blau.
// Liest /run/pingulinux/restzeit/BENUTZER („übrig_sek genutzt_sek“), das
// pingulinux-restzeit.sh jede Minute schreibt. Ohne Begrenzung: unsichtbar.
import QtQuick
import QtQuick.Layouts
import org.kde.plasma.plasmoid
import org.kde.plasma.core as PlasmaCore
import org.kde.plasma.components as PlasmaComponents
import org.kde.plasma.plasma5support as P5Support
import org.kde.kirigami as Kirigami

PlasmoidItem {
    id: root

    property int uebrig: -1          // Sekunden, -1 = keine Begrenzung / unbekannt
    property bool steht: false       // true = Zeit zählt gerade nicht (3. Wert = 0)
    readonly property bool aktiv: uebrig >= 0
    readonly property int minuten: Math.max(0, Math.ceil(uebrig / 60))

    preferredRepresentation: compactRepresentation
    Plasmoid.status: aktiv ? PlasmaCore.Types.ActiveStatus : PlasmaCore.Types.HiddenStatus
    toolTipMainText: "Bildschirmzeit"
    toolTipSubText: aktiv ? ("Heute noch " + langText() + (steht ? " – die Zeit zählt gerade nicht" : ""))
                          : "Heute ohne Zeitbegrenzung"

    function kurzText() {
        if (!aktiv) return ""
        if (uebrig <= 0) return "⏳ Zeit ist um"
        if (steht) return "🎨 Noch " + kurzZeit() + " · zählt nicht"
        if (minuten >= 60) {
            var h = Math.floor(minuten / 60), m = minuten % 60
            return "⏳ Noch " + h + " Std" + (m > 0 ? " " + m + " Min" : "")
        }
        return "⏳ Noch " + minuten + " Min"
    }
    function kurzZeit() {
        if (minuten >= 60) {
            var h = Math.floor(minuten / 60), m = minuten % 60
            return h + " Std" + (m > 0 ? " " + m + " Min" : "")
        }
        return minuten + " Min"
    }
    function langText() {
        if (minuten >= 60) {
            var h = Math.floor(minuten / 60), m = minuten % 60
            return h + (h === 1 ? " Stunde" : " Stunden") + (m > 0 ? " und " + m + " Minuten" : "")
        }
        return minuten + (minuten === 1 ? " Minute" : " Minuten")
    }
    function farbe() {
        if (steht && uebrig > 0) return "#3b7dd8"
        if (minuten <= 5) return "#c2412d"
        if (minuten <= 15) return "#f2a51f"
        return "#2e8a57"
    }

    P5Support.DataSource {
        id: lesen
        engine: "executable"
        connectedSources: []
        onNewData: (quelle, daten) => {
            var t = String(daten["stdout"] || "").trim().split(/\s+/)
            var u = parseInt(t[0]), g = parseInt(t[1])
            if (t.length >= 2 && !isNaN(u) && !isNaN(g) && u <= 86000 && (u + g) > 0)
                root.uebrig = u
            else
                root.uebrig = -1
            root.steht = (t.length >= 3 && t[2] === "0")
            disconnectSource(quelle)
        }
    }
    P5Support.DataSource {          // startet „Mehr Zeit bitte“ (be15)
        id: starten
        engine: "executable"
        connectedSources: []
        onNewData: (quelle, daten) => disconnectSource(quelle)
    }
    Timer {
        id: uhr
        interval: 5000; running: true; repeat: true; triggeredOnStart: true   // 5 s: „Mehr Zeit“ zeigt sich gleich (b29)
        onTriggered: lesen.connectSource("cat /run/pingulinux/restzeit/\"$(id -un)\" 2>/dev/null")
    }

    compactRepresentation: Item {
        Layout.minimumWidth: root.aktiv ? schild.width + Kirigami.Units.smallSpacing * 2 : 0
        Layout.preferredWidth: Layout.minimumWidth
        Layout.maximumWidth: Layout.minimumWidth
        visible: root.aktiv

        Rectangle {
            id: schild
            anchors.centerIn: parent
            height: Math.min(parent.height - 4, text.implicitHeight + Kirigami.Units.smallSpacing * 2)
            width: text.implicitWidth + Kirigami.Units.largeSpacing * 2
            radius: height / 2
            color: root.farbe()

            PlasmaComponents.Label {
                id: text
                anchors.centerIn: parent
                text: root.kurzText()
                font.bold: true
                font.pointSize: Kirigami.Theme.defaultFont.pointSize * 1.1
                color: (!root.steht && root.minuten <= 15 && root.minuten > 5) ? "#1d2329" : "#ffffff"
            }
        }
        MouseArea {
            anchors.fill: parent
            onClicked: root.expanded = !root.expanded
        }
    }

    fullRepresentation: ColumnLayout {
        Layout.preferredWidth: Kirigami.Units.gridUnit * 16
        Kirigami.Heading {
            Layout.fillWidth: true
            level: 2
            wrapMode: Text.WordWrap
            text: root.aktiv ? ("Heute noch " + root.langText()) : "Heute ohne Zeitbegrenzung"
        }
        PlasmaComponents.Label {
            Layout.fillWidth: true
            wrapMode: Text.WordWrap
            visible: root.aktiv && root.steht
            text: "🎨 Gerade zählt die Zeit nicht – Lernen, Malen und Schreiben sind frei. Bei Spielen und Videos läuft sie weiter."
        }
        PlasmaComponents.Label {
            Layout.fillWidth: true
            wrapMode: Text.WordWrap
            text: "Bei 15, 5 und 1 Minute sagt Fino Bescheid. Mehr Zeit gibt es nur von Mama oder Papa."
        }
        PlasmaComponents.Button {
            Layout.alignment: Qt.AlignHCenter
            visible: root.aktiv
            text: "🙋 Mehr Zeit bitte"
            font.pointSize: Kirigami.Theme.defaultFont.pointSize * 1.2
            onClicked: {
                root.expanded = false
                starten.connectSource("setsid -f /usr/local/bin/serafino-mehr-zeit.py >/dev/null 2>&1")
            }
        }
    }
}

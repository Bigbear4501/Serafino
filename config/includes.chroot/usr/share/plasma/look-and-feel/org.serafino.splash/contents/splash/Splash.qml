// Serafino (v1y): Ladebildschirm beim Anmelden – Nachthimmel, Fino,
// „Einen Moment, ich mache alles bereit …“
import QtQuick

Rectangle {
    id: root
    color: "#0e1630"
    property int stage            // von KSplash gesetzt (1 … 6)

    Image {
        anchors.fill: parent
        source: "images/himmel.png"
        fillMode: Image.PreserveAspectCrop
        smooth: true
    }

    Column {
        anchors.centerIn: parent
        spacing: root.height * 0.035

        Image {
            id: fino
            source: "images/fino.png"
            height: root.height * 0.32
            width: height
            fillMode: Image.PreserveAspectFit
            smooth: true
            mipmap: true
            anchors.horizontalCenter: parent.horizontalCenter
            transform: Translate { id: schweben; y: 0 }
            SequentialAnimation {
                running: true; loops: Animation.Infinite
                NumberAnimation { target: schweben; property: "y"; to: -root.height * 0.015; duration: 1100; easing.type: Easing.InOutSine }
                NumberAnimation { target: schweben; property: "y"; to: 0; duration: 1100; easing.type: Easing.InOutSine }
            }
        }

        Text {
            text: "Einen Moment, ich mache alles bereit …"
            color: "#ffffff"
            font.pixelSize: Math.max(18, root.height * 0.034)
            font.family: "Noto Sans"
            anchors.horizontalCenter: parent.horizontalCenter
        }

        // kleiner Fortschrittsbalken (Stufen von KSplash)
        Rectangle {
            width: root.width * 0.18; height: Math.max(4, root.height * 0.006)
            radius: height / 2
            color: "#33ffffff"
            anchors.horizontalCenter: parent.horizontalCenter
            Rectangle {
                height: parent.height; radius: parent.radius
                color: "#f6c945"
                width: parent.width * Math.min(1, Math.max(0.08, root.stage / 6))
                Behavior on width { NumberAnimation { duration: 400; easing.type: Easing.OutCubic } }
            }
        }
    }
}

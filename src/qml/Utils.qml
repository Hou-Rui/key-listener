pragma Singleton

import QtQuick
import org.kde.kirigami as Kirigami

import "../../keylistener/backend" as Backend

Item {
    readonly property var constants: Item {
        property int columnWidth: 12 * Kirigami.Units.gridUnit
        property int rowItemHeight: 2 * Kirigami.Units.gridUnit
        property int windowWidth: 40 * Kirigami.Units.gridUnit
        property int windowHeight: 30 * Kirigami.Units.gridUnit
    }

    readonly property var commonActions: Item {
        property var startListeningAction: Kirigami.Action {
            icon.name: "media-playback-start"
            text: qsTr("Start Listening")
            visible: !Backend.EventListener.isListening
            displayHint: Kirigami.DisplayHint.KeepVisible
            onTriggered: {
                const keys = Backend.PresetManager.getCurrentListenedKeys();
                Backend.EventListener.startListening(keys);
            }
        }

        readonly property var stopListeningAction: Kirigami.Action {
            icon.name: "media-playback-stop"
            text: qsTr("Stop Listening")
            visible: Backend.EventListener.isListening
            displayHint: Kirigami.DisplayHint.KeepVisible
            onTriggered: Backend.EventListener.stopListening()
        }
    }
}

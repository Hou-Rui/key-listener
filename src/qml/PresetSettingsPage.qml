pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Controls as Controls
import org.kde.kirigami as Kirigami

import "../../keylistener/backend" as Backend

Kirigami.ScrollablePage {
    id: page
    title: qsTr("Settings")
    required property var preset
    signal editBindingsRequested

    Kirigami.Action {
        id: editAction
        icon.name: "document-edit"
        text: qsTr("Edit Bindings")
        displayHint: Kirigami.DisplayHint.KeepVisible
        onTriggered: page.editBindingsRequested()
    }


    actions: [
        Utils.commonActions.startListeningAction,
        Utils.commonActions.stopListeningAction,
        editAction,
    ]

    Kirigami.FormLayout {
        anchors.fill: parent
        enabled: !Backend.EventListener.isListening

        Kirigami.Separator {
            Kirigami.FormData.isSection: true
            Kirigami.FormData.label: qsTr("Preset Settings")
        }

        Controls.TextField {
            Kirigami.FormData.label: qsTr("Name:")
            text: page.preset.name
            onEditingFinished: page.preset.name = text
        }

        Controls.TextField {
            Kirigami.FormData.label: qsTr("Shell:")
            text: page.preset.shell
            onEditingFinished: page.preset.shell = text
        }
    }
}

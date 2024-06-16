pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Controls as Controls
import org.kde.kirigami as Kirigami

Kirigami.ScrollablePage {
    id: page
    title: qsTr("Preset Settings")
    required property var preset
    signal editBindingsRequested

    actions: [
        Kirigami.Action {
            icon.name: "document-edit"
            text: qsTr("Edit Bindings")
            onTriggered: page.editBindingsRequested()
        }
    ]

    Kirigami.FormLayout {
        anchors.fill: parent

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

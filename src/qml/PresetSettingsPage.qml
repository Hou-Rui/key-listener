pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Controls
import org.kde.kirigami as Kirigami

import keylistener.backend as Backend

Kirigami.ScrollablePage {
    id: page
    title: qsTr("Settings")
    required property var preset

    signal editBindingsRequested
    signal currentNameChanged(string name)

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

        TextField {
            id: nameField
            Kirigami.FormData.label: qsTr("Name:")
            text: page.preset.name
        }

        TextField {
            id: shellField
            Kirigami.FormData.label: qsTr("Shell:")
            text: page.preset.shell
        }
    }

    footer: PageFooter {
        isDirty: nameField.text !== page.preset.name
              || shellField.text !== page.preset.shell

        onReset: {
            nameField.text = page.preset.name;
            shellField.text = page.preset.shell;
        }

        onApplied: {
            page.preset.name = nameField.text;
            page.preset.shell = shellField.text;
            page.currentNameChanged(page.preset.name);
            Backend.PresetManager.savePresets();
        }
    }
}

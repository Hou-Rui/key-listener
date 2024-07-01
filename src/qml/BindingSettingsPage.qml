pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import org.kde.kirigami as Kirigami

import keylistener.backend as Backend

Kirigami.ScrollablePage {
    id: page
    title: qsTr("Settings")
    required property var binding
    signal editPresetsRequested

    Kirigami.Action {
        id: editAction
        icon.name: "document-edit"
        text: qsTr("Edit Presets")
        displayHint: Kirigami.DisplayHint.KeepVisible
        onTriggered: page.editPresetsRequested()
    }

    actions: [
        Utils.commonActions.startListeningAction,
        Utils.commonActions.stopListeningAction,
        editAction,
    ]

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 0
        spacing: 0

        Kirigami.FormLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            enabled: !Backend.EventListener.isListening

            Kirigami.Separator {
                Kirigami.FormData.isSection: true
                Kirigami.FormData.label: qsTr("Binding Settings")
            }

            TextField {
                id: descField
                Kirigami.FormData.label: qsTr("Description:")
                text: page.binding.desc
            }

            TextField {
                id: keyField
                Kirigami.FormData.label: qsTr("Key:")
                text: page.binding.key
            }

            ComboBox {
                id: eventBox
                Kirigami.FormData.label: qsTr("Triggered When:")
                Layout.fillWidth: true
                model: [qsTr("Pressed"), qsTr("Released")]
                currentIndex: page.indexFromEvent(page.binding.event)
            }

            Kirigami.Separator {
                Kirigami.FormData.isSection: true
                Kirigami.FormData.label: qsTr("Execution Settings")
            }

            CheckBox {
                id: useShellBox
                Kirigami.FormData.label: qsTr("Run in Preset Shell:")
                checked: page.binding.useShell
            }

            TextArea {
                id: cmdArea
                Kirigami.FormData.label: qsTr("Execute Command:")
                Layout.fillWidth: true
                wrapMode: TextEdit.WordWrap
                Kirigami.FormData.labelAlignment: Qt.AlignCenter
                text: page.binding.cmd
            }
        }
    }

    function indexFromEvent(event: string): int {
        switch (event) {
        case "pressed":
            return 0;
        case "released":
            return 1;
        }
        print(`Unknown event: ${event}`);
        return -1;
    }

    function eventFromIndex(index: int): string {
        const events = ["pressed", "released"]
        if (0 <= index && index < events.length) {
            return events[index];
        }
        print(`Unknown event index: ${index}`);
        return "";
    }

    footer: PageFooter {
        isDirty: descField.text !== page.binding.desc
              || keyField.text !== page.binding.key
              || eventBox.currentIndex !== page.indexFromEvent(page.binding.event)
              || cmdArea.text !== page.binding.cmd
              || useShellBox.checked !== page.binding.useShell

        onReset: {
            descField.text = page.binding.desc;
            keyField.text = page.binding.key;
            eventBox.currentIndex = page.indexFromEvent(page.binding.event);
            cmdArea.text = page.binding.cmd;
            useShellBox.checked = page.binding.useShell;
        }

        onApplied: {
            page.binding.desc = descField.text;
            page.binding.key = keyField.text;
            page.binding.event = page.eventFromIndex(eventBox.currentIndex);
            page.binding.cmd = cmdArea.text;
            page.binding.useShell = useShellBox.checked;
            Backend.PresetManager.savePresets();
        }
    }
}

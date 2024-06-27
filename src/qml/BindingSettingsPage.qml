pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as Controls
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

            Controls.TextField {
                id: descTextField
                Kirigami.FormData.label: qsTr("Description:")
                text: page.binding.desc
                onEditingFinished: page.binding.desc = text
            }

            Controls.TextField {
                id: keyTextField
                Kirigami.FormData.label: qsTr("Key:")

                text: page.binding.key
                onEditingFinished: page.binding.key = text
            }

            Controls.ComboBox {
                id: eventComboBox
                Kirigami.FormData.label: qsTr("Triggered When:")
                Layout.fillWidth: true
                model: [qsTr("Pressed"), qsTr("Released")]
                currentIndex: {
                    switch (page.binding.event) {
                    case "pressed":
                        return 0;
                    case "released":
                        return 1;
                    default:
                        return -1;
                    }
                }
                onActivated: index => page.binding.event = model[index]
            }

            Kirigami.Separator {
                Kirigami.FormData.isSection: true
                Kirigami.FormData.label: qsTr("Execution Settings")
            }

            Controls.CheckBox {
                id: useShellCheckBox
                Kirigami.FormData.label: qsTr("Run in Preset Shell:")
                checked: page.binding.useShell
                onToggled: page.binding.useShell = checked
            }

            Controls.TextArea {
                id: cmdTextArea
                Kirigami.FormData.label: qsTr("Execute Command:")
                Layout.fillWidth: true
                wrapMode: TextEdit.WordWrap
                Kirigami.FormData.labelAlignment: Qt.AlignCenter
                text: page.binding.cmd
                onEditingFinished: page.binding.cmd = text
            }
        }
    }

    footer: Controls.DialogButtonBox {
        Controls.Button {
            text: qsTr("Reset")
            Controls.DialogButtonBox.buttonRole: Controls.DialogButtonBox.ResetRole
        }

        Controls.Button {
            text: qsTr("Apply")
            Controls.DialogButtonBox.buttonRole: Controls.DialogButtonBox.ApplyRole
        }
    }
}

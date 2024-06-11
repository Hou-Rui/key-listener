pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as Controls
import org.kde.kirigami as Kirigami

import "../../keylistener/backend" as Backend

Kirigami.ScrollablePage {
    id: page
    title: qsTr("Settings")
    required property var binding

    actions: [
        Kirigami.Action {
            id: actionStartListener
            icon.name: "media-playback-start"
            text: qsTr("Start")
            visible: !Backend.EventListener.isListening
            displayHint: Kirigami.DisplayHint.KeepVisible
            onTriggered: {
                const keys = Backend.PresetManager.getCurrentListenedKeys();
                Backend.EventListener.startListening(keys);
            }
        },
        Kirigami.Action {
            id: actionStopListener
            icon.name: "media-playback-stop"
            text: qsTr("Stop")
            visible: Backend.EventListener.isListening
            displayHint: Kirigami.DisplayHint.KeepVisible
            onTriggered: {
                Backend.EventListener.stopListening();
            }
        }
    ]

    Kirigami.FormLayout {
        anchors.fill: parent
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
            Kirigami.FormData.label: qsTr("Triggered when:")

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
            Kirigami.FormData.label: qsTr("Run in preset shell:")

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

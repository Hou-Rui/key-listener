pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as Controls
import org.kde.kirigami as Kirigami

import "../../keylistener/backend" as Backend

Kirigami.ApplicationWindow {
    id: root
    visible: true
    title: qsTr("Key Listener")

    readonly property int columnWidth: 12 * Kirigami.Units.gridUnit
    readonly property int rowItemHeight: 2 * Kirigami.Units.gridUnit

    pageStack.defaultColumnWidth: columnWidth
    wideScreen: width >= 3 * columnWidth
    minimumWidth: 2 * columnWidth

    width: 40 * Kirigami.Units.gridUnit
    height: 30 * Kirigami.Units.gridUnit

    function showMessage(message: string) {
        root.hidePassiveNotification();
        root.showPassiveNotification(message);
    }

    globalDrawer: Kirigami.GlobalDrawer {
        id: presetsDrawer
        modal: true
        width: root.columnWidth

        contentItem: ColumnLayout {
            Layout.margins: Kirigami.Units.mediumSpacing

            Kirigami.Heading {
                text: qsTr("Presets")
                level: 2
            }

            ListView {
                id: presetListView
                Layout.fillHeight: true
                Layout.fillWidth: true

                reuseItems: true
                model: presetManager.getPresets()

                onCurrentIndexChanged: {
                    if (eventListener.isListening) {
                        eventListener.stopListening();
                        root.showMessage(qsTr("Listener has stopped due to switching preset"));
                    }
                    presetManager.currentPresetIndex = currentIndex;
                }

                delegate: Controls.ItemDelegate {
                    required property string name
                    required property int index

                    height: root.rowItemHeight
                    width: presetListView.width
                    text: name
                    padding: Kirigami.Units.smallSpacing

                    highlighted: ListView.isCurrentItem
                    onClicked: presetListView.currentIndex = index
                }
            }
        }
    }

    pageStack.initialPage: Kirigami.Page {
        title: qsTr("Key Listener")
        padding: 0

        actions: [
            Kirigami.Action {
                id: actionStartListener
                icon.name: "media-playback-start"
                text: qsTr("Start")
                visible: !eventListener.isListening
                displayHint: Kirigami.DisplayHint.KeepVisible
                onTriggered: {
                    const keys = presetManager.getCurrentListenedKeys();
                    eventListener.startListening(keys);
                    root.showMessage(qsTr("Listener has started"));
                }
            },
            Kirigami.Action {
                id: actionStopListener
                icon.name: "media-playback-stop"
                text: qsTr("Stop")
                visible: eventListener.isListening
                displayHint: Kirigami.DisplayHint.KeepVisible
                onTriggered: {
                    eventListener.stopListening();
                    root.showMessage(qsTr("Listener has stopped"));
                }
            },
            Kirigami.Action {
                id: actionAddListener
                icon.name: "list-add"
                text: qsTr("Add")
            },
            Kirigami.Action {
                id: actionRemoveListener
                icon.name: "list-remove"
                text: qsTr("Remove")
                onTriggered: removeBindingDialog.visible = true
            }
        ]

        Kirigami.PromptDialog {
            id: removeBindingDialog
            title: qsTr("Confirm Removal?")
            subtitle: {
                const binding = bindingListView.currentBinding;
                return qsTr(`The binding "${binding.desc}" will be removed.`);
            }
            standardButtons: Kirigami.Dialog.Ok | Kirigami.Dialog.Cancel
            // onAccepted: document.save()
        }

        RowLayout {
            anchors.fill: parent
            spacing: 0

            Controls.ScrollView {
                Layout.fillHeight: true
                Layout.preferredWidth: root.columnWidth
                Layout.topMargin: Kirigami.Units.smallSpacing
                Layout.bottomMargin: Kirigami.Units.smallSpacing
                clip: true

                ListView {
                    id: bindingListView
                    reuseItems: true
                    model: presetManager.currentPreset.bindings
                    property var currentBinding: model[currentIndex]

                    delegate: Controls.ItemDelegate {
                        required property string key
                        required property string cmd
                        required property string desc
                        required property int index

                        text: desc
                        width: bindingListView.width
                        height: root.rowItemHeight
                        highlighted: ListView.isCurrentItem
                        onClicked: bindingListView.currentIndex = index
                    }
                }
            }

            Kirigami.Separator {
                Layout.fillHeight: true
            }

            ColumnLayout {
                Layout.fillHeight: true
                Layout.fillWidth: true

                Kirigami.FormLayout {
                    Layout.fillHeight: true
                    Layout.leftMargin: Kirigami.Units.mediumSpacing
                    Layout.rightMargin: Kirigami.Units.mediumSpacing

                    Kirigami.Separator {
                        visible: bindingListView.model.count != 0
                        Kirigami.FormData.isSection: true
                        Kirigami.FormData.label: qsTr("Binding Settings")
                    }

                    Controls.TextField {
                        id: descTextField
                        visible: bindingListView.model.count != 0
                        Kirigami.FormData.label: qsTr("Description:")
                        text: bindingListView.currentBinding.desc
                    }

                    Controls.TextField {
                        id: keyTextField
                        visible: bindingListView.model.count != 0
                        Kirigami.FormData.label: qsTr("Key:")
                        text: bindingListView.currentBinding.key
                    }

                    Controls.ComboBox {
                        id: eventComboBox
                        visible: bindingListView.model.count != 0
                        Kirigami.FormData.label: qsTr("Triggered when:")
                        Layout.fillWidth: true
                        model: [qsTr("Pressed"), qsTr("Released")]
                        currentIndex: {
                            switch (bindingListView.currentBinding.event) {
                            case "pressed":
                                return 0;
                            case "released":
                                return 1;
                            default:
                                return -1;
                            }
                        }
                        onCurrentIndexChanged: {
                            const event = model[currentIndex];
                            if (bindingListView.currentBinding) {
                                bindingListView.currentBinding.event = event;
                            }
                        }
                    }

                    Kirigami.Separator {
                        Kirigami.FormData.isSection: true
                        visible: bindingListView.model.count != 0
                        Kirigami.FormData.label: qsTr("Execution Settings")
                    }

                    Controls.CheckBox {
                        id: useShellCheckBox
                        visible: bindingListView.model.count != 0
                        Kirigami.FormData.label: qsTr("Run in preset shell:")
                        checked: bindingListView.currentBinding.useShell
                    }

                    Controls.TextArea {
                        id: cmdTextArea
                        visible: bindingListView.model.count != 0
                        Layout.fillWidth: true
                        wrapMode: TextEdit.WordWrap
                        Kirigami.FormData.label: qsTr("Execute Command:")
                        Kirigami.FormData.labelAlignment: Qt.AlignCenter
                        text: bindingListView.currentBinding.cmd
                    }
                    
                }

                Kirigami.Separator {
                    Layout.fillWidth: true
                }

                RowLayout {
                    Layout.alignment: Qt.AlignVCenter | Qt.AlignRight
                    Layout.rightMargin: Kirigami.Units.smallSpacing
                    Layout.bottomMargin: Kirigami.Units.smallSpacing

                    Controls.Button {
                        text: qsTr("Reset")
                        icon.name: "document-cleanup"
                    }

                    Controls.Button {
                        text: qsTr("Apply")
                        icon.name: "dialog-ok-apply"
                        onClicked: {
                            const binding = bindingListView.currentBinding;
                            binding.key = keyTextField.text;
                            binding.desc = descTextField.text;
                            binding.useShell = useShellCheckBox.checked;
                            binding.cmd = cmdTextArea.text;
                            presetManager.savePresets();
                        }
                    }
                }
            }
        }
    }

    function cleanClose() {
        eventListener.cleanUp();
        presetManager.cleanUp();
        root.close();
    }

    Kirigami.PromptDialog {
        id: confirmCloseDialog
        title: qsTr("Exit Key Listener?")
        subtitle: qsTr("All current bindings will be stopped.")
        standardButtons: Kirigami.Dialog.Yes | Kirigami.Dialog.No
        onAccepted: root.cleanClose()
    }

    onClosing: close => {
        if (eventListener.isListening) {
            close.accepted = false;
            confirmCloseDialog.visible = true;
        } else {
            root.cleanClose();
        }
    }

    Backend.PresetManager {
        id: presetManager
        onErrorHappened: error => {
            root.showMessage(error);
        }
    }

    Backend.EventListener {
        id: eventListener
        onKeyPressed: key => {
            root.showMessage(qsTr(`Key pressed: ${key}`));
            presetManager.execKeyPressCommand(key);
        }
        onKeyReleased: key => {
            root.showMessage(qsTr(`Key released: ${key}`));
            presetManager.execKeyReleaseCommand(key);
        }
    }
}

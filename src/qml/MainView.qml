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

    pageStack.defaultColumnWidth: Constants.columnWidth
    wideScreen: width >= 3 * Constants.columnWidth
    minimumWidth: 2 * Constants.columnWidth

    width: Constants.windowWidth
    height: Constants.windowHeight

    function showMessage(message: string) {
        root.hidePassiveNotification();
        root.showPassiveNotification(message);
    }

    globalDrawer: PresetsDrawer {}

    pageStack.initialPage: Kirigami.Page {
        title: qsTr("Key Listener")
        padding: 0

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
                    root.showMessage(qsTr("Listener has started"));
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
            onAccepted: {
                const index = bindingListView.currentIndex;
                Backend.PresetManager.removeBindingAtIndex(index);
                bindingListView.currentIndex = index;
                if (index >= bindingListView.model.length) {
                    bindingListView.currentIndex -= 1;
                }
                Backend.PresetManager.savePresets();
            }
        }

        RowLayout {
            anchors.fill: parent
            spacing: 0

            Controls.ScrollView {
                Layout.fillHeight: true
                Layout.preferredWidth: Constants.columnWidth
                Layout.topMargin: Kirigami.Units.smallSpacing
                Layout.bottomMargin: Kirigami.Units.smallSpacing
                clip: true

                ListView {
                    id: bindingListView
                    reuseItems: true
                    model: Backend.PresetManager.currentPreset.bindings
                    property var currentBinding: model[currentIndex]

                    delegate: Controls.ItemDelegate {
                        required property string desc
                        required property int index

                        text: desc
                        width: bindingListView.width
                        height: Constants.rowItemHeight
                        highlighted: ListView.isCurrentItem
                        onClicked: bindingListView.currentIndex = index
                    }
                }
            }

            Kirigami.Separator {
                Layout.fillHeight: true
                Layout.margins: 0;
            }

            Kirigami.FormLayout {
                Layout.fillHeight: true
                Layout.leftMargin: Kirigami.Units.mediumSpacing
                Layout.rightMargin: Kirigami.Units.mediumSpacing

                Kirigami.Separator {
                    Kirigami.FormData.isSection: true
                    Kirigami.FormData.label: qsTr("Binding Settings")
                }

                Controls.TextField {
                    id: descTextField
                    Kirigami.FormData.label: qsTr("Description:")
                    text: bindingListView.currentBinding.desc
                    onTextChanged: {
                        if (bindingListView.currentBinding) {
                            bindingListView.currentBinding.desc = text;
                            bindingListView.currentItem.text = text;
                        }
                    }
                }

                Controls.TextField {
                    id: keyTextField
                    Kirigami.FormData.label: qsTr("Key:")
                    text: bindingListView.currentBinding.key
                    onTextChanged: {
                        if (bindingListView.currentBinding) {
                            bindingListView.currentBinding.key = text;
                        }
                    }
                }

                Controls.ComboBox {
                    id: eventComboBox
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
                        if (bindingListView.currentBinding) {
                            const event = model[currentIndex];
                            bindingListView.currentBinding.event = event;
                        }
                    }
                }

                Kirigami.Separator {
                    Kirigami.FormData.isSection: true
                    Kirigami.FormData.label: qsTr("Execution Settings")
                }

                Controls.CheckBox {
                    id: useShellCheckBox
                    Kirigami.FormData.label: qsTr("Run in preset shell:")
                    checked: bindingListView.currentBinding.useShell
                    onToggled: {
                        if (bindingListView.currentBinding) {
                            bindingListView.currentBinding.useShell = checked;
                        }
                    }
                }

                Controls.TextArea {
                    id: cmdTextArea
                    Layout.fillWidth: true
                    wrapMode: TextEdit.WordWrap
                    Kirigami.FormData.label: qsTr("Execute Command:")
                    Kirigami.FormData.labelAlignment: Qt.AlignCenter
                    text: bindingListView.currentBinding.cmd
                    onTextChanged: {
                        if (bindingListView.currentBinding) {
                            bindingListView.currentBinding.cmd = text;
                        }
                    }
                }
            }
        }
    }

    function cleanClose() {
        Backend.EventListener.cleanUp();
        Backend.PresetManager.cleanUp();
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
        if (Backend.EventListener.isListening) {
            close.accepted = false;
            confirmCloseDialog.visible = true;
        } else {
            root.cleanClose();
        }
    }

    Connections {
        target: Backend.PresetManager
        function onErrorHappened(error) {
            root.showMessage(error);
        }
    }

    Connections {
        target: Backend.EventListener
        function onKeyPressed(key: string) {
            root.showMessage(qsTr(`Key pressed: ${key}`));
            Backend.PresetManager.execKeyPressCommand(key);
        }
        function onKeyReleased(key: string) {
            root.showMessage(qsTr(`Key released: ${key}`));
            Backend.PresetManager.execKeyReleaseCommand(key);
        }
    }
}

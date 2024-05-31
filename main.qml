pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as Controls
import org.kde.kirigami as Kirigami

import keylistener.backend as Backend

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
                // onTriggered: addListenerDialog.visible = true
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
                const binding = bindingListView.currentBinding();
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
                    model: presetManager.currentPreset.binding

                    function currentBinding() {
                        return model[currentIndex];
                    }

                    onCurrentIndexChanged: {
                        const binding = currentBinding();
                        cmdTextField.text = binding.cmd;
                        keyTextField.text = binding.key;
                        descTextField.text = binding.desc;
                    }

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

                    Controls.TextField {
                        id: descTextField
                        Kirigami.FormData.label: qsTr("Description:")
                    }

                    Controls.TextField {
                        id: keyTextField
                        Kirigami.FormData.label: qsTr("Keys:")
                    }

                    Controls.TextField {
                        id: cmdTextField
                        wrapMode: TextEdit.WordWrap
                        Kirigami.FormData.label: qsTr("Execute Command:")
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
    }

    Backend.EventListener {
        id: eventListener
        onKeyPressed: key => {
            root.showMessage(qsTr(`Key pressed: ${key}`));
            presetManager.execKeyPressCommand(key);
        }
    }
}

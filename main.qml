pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as Controls
import org.kde.kirigami as Kirigami

import backend.Backend

Kirigami.ApplicationWindow {
    id: root
    visible: true
    title: qsTr("Key Listener")

    readonly property int columnWidth: 180
    readonly property int rowItemHeight: 32
    readonly property int gapSmall: 4
    readonly property int gapMedium: 8
    readonly property int gapLarge: 12

    pageStack.defaultColumnWidth: columnWidth
    wideScreen: width >= 3 * columnWidth
    minimumWidth: 2 * columnWidth

    width: 550
    height: 400

    globalDrawer: Kirigami.GlobalDrawer {
        id: presetsDrawer
        modal: true
        width: root.columnWidth

        contentItem: ColumnLayout {
            Layout.margins: 12

            Kirigami.Heading {
                text: qsTr("Presets")
                level: 2
            }

            ListView {
                id: presetListView
                Layout.fillHeight: true
                Layout.fillWidth: true

                reuseItems: true
                model: backend.getPresets()

                delegate: Controls.ItemDelegate {
                    required property string name
                    required property int index

                    height: root.rowItemHeight
                    width: presetListView.width
                    text: name
                    padding: root.gapSmall

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
                id: actionAddListener
                icon.name: "list-add"
                text: qsTr("Add Listener")
                // onTriggered: addListenerDialog.visible = true
            },
            Kirigami.Action {
                id: actionRemoveListener
                icon.name: "list-remove"
                text: qsTr("Remove Listener")
                onTriggered: removeListenerDialog.visible = true
            }
        ]

        Kirigami.PromptDialog {
            id: removeListenerDialog
            title: "Confirm Removal?"
            subtitle: {
                const listener = listenerListView.getCurrentListener();
                return qsTr(`The listener "${listener.desc}" will be removed.`);
            }
            standardButtons: Kirigami.Dialog.Ok | Kirigami.Dialog.Cancel
            // onAccepted: document.save()
        }

        RowLayout {
            anchors.fill: parent
            spacing: 0
            focus: true

            Keys.onPressed: event => {
                if (!event.isAutoRepeat) {
                    backend.processKey(event.key);
                }
            }

            Controls.ScrollView {
                Layout.fillHeight: true
                Layout.preferredWidth: root.columnWidth
                Layout.topMargin: root.gapSmall
                Layout.bottomMargin: root.gapSmall
                clip: true

                ListView {
                    id: listenerListView
                    reuseItems: true
                    model: backend.getCurrentPreset().pressed

                    function getCurrentListener() {
                        return model[currentIndex];
                    }

                    onCurrentIndexChanged: {
                        const listener = getCurrentListener();
                        cmdTextField.text = listener.cmd;
                        keyTextField.text = listener.key;
                        descTextField.text = listener.desc;
                    }

                    delegate: Controls.ItemDelegate {
                        required property string key
                        required property string cmd
                        required property string desc
                        required property int index

                        text: desc
                        width: listenerListView.width
                        height: root.rowItemHeight
                        highlighted: ListView.isCurrentItem
                        onClicked: listenerListView.currentIndex = index
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
                    Layout.leftMargin: root.gapMedium
                    Layout.rightMargin: root.gapMedium

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
                    Layout.rightMargin: root.gapSmall
                    Layout.bottomMargin: root.gapSmall

                    Controls.Button {
                        text: qsTr("Reset")
                        icon.name: "document-cleanup"
                    }

                    Controls.Button {
                        text: qsTr("Apply")
                        icon.name: "dialog-apply"
                    }
                }
            }
        }
    }

    Backend {
        id: backend
        onMessageEmitted: message => {
            root.showPassiveNotification(message);
        }
    }
}

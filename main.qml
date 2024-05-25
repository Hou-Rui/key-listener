pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Layouts as Layouts
import QtQuick.Controls as Controls
import org.kde.kirigami as Kirigami

import "./backend/Backend"

Kirigami.ApplicationWindow {
    id: root
    title: qsTr("Key Listener")

    pageStack.defaultColumnWidth: 200
    pageStack.initialPage: [presetsComponent, listenersComponent]

    Component {
        id: presetsComponent

        Kirigami.ScrollablePage {
            title: qsTr("Presets")
            topPadding: 0
            bottomPadding: 0
            leftPadding: 0
            rightPadding: 0

            ListView {
                id: presetListView
                reuseItems: true
                model: backend.getPresets()

                delegate: Controls.ItemDelegate {
                    required property string name
                    required property int index

                    height: 32
                    width: presetListView.width
                    text: name

                    highlighted: ListView.isCurrentItem
                    onClicked: presetListView.currentIndex = index
                }
            }
        }
    }

    Component {
        id: listenersComponent

        Kirigami.Page {
            title: qsTr("Key Listener")
            padding: 0

            actions: [
                Kirigami.Action {
                    id: actionAddListener
                    icon.name: "list-add"
                    text: qsTr("Add Listener")
                },
                Kirigami.Action {
                    id: actionRemoveListener
                    icon.name: "list-remove"
                    text: qsTr("Remove Listener")
                }
            ]

            Layouts.RowLayout {
                anchors.fill: parent
                spacing: 0
                focus: true

                Keys.onPressed: event => {
                    if (!event.isAutoRepeat) {
                        backend.processKey(event.key);
                    }
                }

                Controls.ScrollView {
                    Layouts.Layout.fillHeight: true
                    implicitWidth: 180
                    clip: true

                    ListView {
                        id: listenerListView
                        reuseItems: true
                        model: backend.getCurrentPreset().pressed

                        onCurrentIndexChanged: {
                            const listener = model[listenerListView.currentIndex];
                            cmdTextField.text = listener.cmd;
                            keyTextField.text = listener.key;
                            descTextField.text = listener.desc;
                        }

                        delegate: Controls.ItemDelegate {
                            required property string key
                            required property string cmd
                            required property string desc
                            required property int index

                            text: "listen " + key
                            width: listenerListView.width
                            height: 32
                            highlighted: ListView.isCurrentItem
                            onClicked: listenerListView.currentIndex = index
                        }
                    }
                }

                Kirigami.Separator {
                    Layouts.Layout.fillHeight: true
                }

                Kirigami.FormLayout {
                    Layouts.Layout.fillHeight: true
                    Layouts.Layout.leftMargin: 12
                    Layouts.Layout.rightMargin: 12
                    Layouts.Layout.topMargin: 4
                    Layouts.Layout.bottomMargin: 4

                    Controls.TextField {
                        id: descTextField
                        Kirigami.FormData.label: qsTr("Description")
                    }

                    Controls.TextField {
                        id: keyTextField
                        Kirigami.FormData.label: qsTr("Keys:")
                    }

                    Controls.TextField {
                        id: cmdTextField
                        Kirigami.FormData.label: qsTr("Execute Command:")
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

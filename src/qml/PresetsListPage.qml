pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Controls as Controls
import org.kde.kirigami as Kirigami

import "../../keylistener/backend" as Backend

Kirigami.ScrollablePage {
    title: qsTr("Presets")
    width: Constants.columnWidth

    actions: [
        Kirigami.Action {
            icon.name: "list-add"
            text: qsTr("Add Preset")
            // onTriggered: bindingListView.currentIndex = Backend.PresetManager.addNewBinding()
        },
        Kirigami.Action {
            icon.name: "list-remove"
            text: qsTr("Remove Preset")
            // onTriggered: removeBindingDialog.visible = true
        }
    ]

    ListView {
        id: presetListView
        implicitWidth: parent.width

        reuseItems: true
        model: Backend.PresetManager.getPresets()

        onCurrentIndexChanged: {
            if (Backend.EventListener.isListening) {
                Backend.EventListener.stopListening();
            }
            Backend.PresetManager.currentPresetIndex = currentIndex;
        }

        delegate: Controls.ItemDelegate {
            required property string name
            required property int index

            height: Constants.rowItemHeight
            width: presetListView.width
            text: name
            padding: Kirigami.Units.smallSpacing

            highlighted: ListView.isCurrentItem
            onClicked: presetListView.currentIndex = index
        }
    }
}

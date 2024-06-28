pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Controls
import org.kde.kirigami as Kirigami

import keylistener.backend as Backend

Kirigami.ScrollablePage {
    title: qsTr("Presets")
    implicitWidth: Utils.constants.columnWidth

    actions: [
        Kirigami.Action {
            icon.name: "list-add"
            text: qsTr("Add Preset")
            displayHint: Kirigami.DisplayHint.AlwaysHide
            onTriggered: Backend.PresetManager.addNewPreset()
        },
        Kirigami.Action {
            icon.name: "list-remove"
            text: qsTr("Remove Preset")
            displayHint: Kirigami.DisplayHint.AlwaysHide
            onTriggered: removePresetDialog.visible = true
        }
    ]

    Kirigami.PromptDialog {
        id: removePresetDialog
        title: qsTr("Remove Selected Preset")
        subtitle: {
            const preset = Backend.PresetManager.currentPreset
            return qsTr(`The preset "${preset.name}" will be removed.`);
        }
        standardButtons: Kirigami.Dialog.Ok | Kirigami.Dialog.Cancel
        onAccepted: Backend.PresetManager.removeCurrentPreset()
    }

    ListView {
        id: presetListView
        anchors.fill: parent

        reuseItems: true
        model: Backend.PresetManager.presets

        onCurrentIndexChanged: {
            if (Backend.EventListener.isListening) {
                Backend.EventListener.stopListening();
            }
            Backend.PresetManager.currentPresetIndex = currentIndex;
        }

        delegate: ItemDelegate {
            required property string name
            required property int index

            height: Utils.constants.rowItemHeight
            width: presetListView.width
            text: name
            padding: Kirigami.Units.smallSpacing

            highlighted: ListView.isCurrentItem
            onClicked: presetListView.currentIndex = index
        }
    }
}

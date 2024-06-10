pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Controls as Controls
import org.kde.kirigami as Kirigami

import "../../keylistener/backend" as Backend

Kirigami.ScrollablePage {
    title: qsTr("Bindings")
    property var currentBinding: bindingListView.currentBinding

    actions: [
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
        }
    }

    ListView {
        id: bindingListView
        implicitWidth: parent.width
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
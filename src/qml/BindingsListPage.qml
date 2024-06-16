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
            icon.name: "list-add"
            text: qsTr("Add Binding")
            displayHint: Kirigami.DisplayHint.AlwaysHide
            onTriggered: bindingListView.currentIndex = Backend.PresetManager.addNewBinding()
        },
        Kirigami.Action {
            icon.name: "list-remove"
            text: qsTr("Remove Binding")
            displayHint: Kirigami.DisplayHint.AlwaysHide
            onTriggered: removeBindingDialog.visible = true
        }
    ]

    Kirigami.PromptDialog {
        id: removeBindingDialog
        title: qsTr("Remove Selected Binding")
        subtitle: {
            const binding = bindingListView.currentBinding;
            return qsTr(`The binding "${binding.desc}" will be removed.`);
        }
        standardButtons: Kirigami.Dialog.Ok | Kirigami.Dialog.Cancel
        onAccepted: {
            const index = bindingListView.currentIndex;
            Backend.PresetManager.removeBindingAtIndex(index);
            if (index >= bindingListView.model.length) {
                bindingListView.currentIndex = index - 1;
            } else {
                bindingListView.currentIndex = index;
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

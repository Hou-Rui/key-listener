pragma ComponentBehavior: Bound

import QtQuick
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

    BindingsListPage {
        id: bindingListPage
    }

    FormPage {
        id: formPage
        binding: bindingListPage.currentBinding
    }

    pageStack.initialPage: [bindingListPage, formPage]

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

        function onListeningChanged() {
            if (Backend.EventListener.isListening) {
                root.showMessage(qsTr(`Listener started`));
            } else {
                root.showMessage(qsTr(`Listener stopped`));
            }
        }
    }
}

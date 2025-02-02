pragma ComponentBehavior: Bound

import QtQuick
import org.kde.kirigami as Kirigami

import keylistener.backend as Backend

Kirigami.ApplicationWindow {
    id: root
    visible: true
    title: qsTr("Key Listener")

    pageStack.defaultColumnWidth: Utils.constants.columnWidth
    wideScreen: width >= 3 * Utils.constants.columnWidth
    minimumWidth: 2 * Utils.constants.columnWidth

    width: Utils.constants.windowWidth
    height: Utils.constants.windowHeight

    function showMessage(message: string) {
        root.hidePassiveNotification();
        root.showPassiveNotification(message);
    }

    PresetsListPage {
        id: presetsListPage
    }

    PresetSettingsPage {
        id: presetSettingsPage
        preset: Backend.PresetManager.currentPreset
        onEditBindingsRequested: {
            root.pageStack.push(bindingsListPage);
            root.pageStack.push(bindingSettingsPage);
        }
        onCurrentNameChanged: name => {
            presetsListPage.updateCurrentName(name);
        }
    }

    BindingsListPage {
        id: bindingsListPage
    }

    BindingSettingsPage {
        id: bindingSettingsPage
        binding: bindingsListPage.currentBinding
        onEditPresetsRequested: {
            root.pageStack.pop();
            root.pageStack.pop();
        }
        onCurrentDescChanged: desc => {
            bindingsListPage.updateCurrentDesc(desc);
        }
    }

    pageStack.interactive: false
    pageStack.globalToolBar.showNavigationButtons: 0
    pageStack.initialPage: [presetsListPage, presetSettingsPage]

    function cleanClose() {
        Backend.EventListener.cleanUp();
        Backend.PresetManager.cleanUp();
        root.quitAction.trigger();
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
        function onErrorHappened(error: string) {
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

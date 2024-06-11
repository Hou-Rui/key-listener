pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as Controls
import org.kde.kirigami as Kirigami

import "../../keylistener/backend" as Backend

Kirigami.GlobalDrawer {
    id: presetsDrawer
    modal: true
    width: Constants.columnWidth

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
}

pragma Singleton

import QtQuick
import org.kde.kirigami as Kirigami

Item {
    readonly property int columnWidth: 12 * Kirigami.Units.gridUnit
    readonly property int rowItemHeight: 2 * Kirigami.Units.gridUnit
    readonly property int windowWidth: 40 * Kirigami.Units.gridUnit
    readonly property int windowHeight: 30 * Kirigami.Units.gridUnit
}

import QtQuick.Controls
import QtQuick.Layouts
import org.kde.kirigami as Kirigami

ColumnLayout {
	id: footer
	required property bool isDirty
	signal reset
	signal applied

	spacing: 0

	Kirigami.Separator {
		Layout.fillWidth: true
	}

	DialogButtonBox {
		id: buttonBox
		Layout.fillWidth: true
		Layout.fillHeight: true
		padding: Kirigami.Units.smallSpacing

		Button {
			text: qsTr("Reset")
			DialogButtonBox.buttonRole: DialogButtonBox.ResetRole
			icon.name: "document-revert"
			enabled: footer.isDirty
		}

		Button {
			text: qsTr("Apply")
			DialogButtonBox.buttonRole: DialogButtonBox.ApplyRole
			icon.name: "document-save"
			enabled: footer.isDirty
		}

		onReset: footer.reset()
		onApplied: footer.applied()
	}
}

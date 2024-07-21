from typing import Callable
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (QCheckBox, QComboBox, QDialogButtonBox,
                               QFormLayout, QLabel, QLineEdit, QSizePolicy,
                               QSpacerItem, QTextEdit, QVBoxLayout, QWidget)

from utils import ROW_HEIGHT


class SettingsForm(QWidget):
    applyRequested = Signal()
    resetRequested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self._formLayout = QVBoxLayout()
        self._currentForm: QFormLayout | None = None
        layout.addLayout(self._formLayout)
        layout.addSpacerItem(self._createSpaceItem())
        layout.addWidget(self._createFooter())

    def addRow(self, text: str, field: QWidget) -> None:
        if not self._currentForm:
            self._currentForm = QFormLayout()
        self._currentForm.addRow(text, field)

    def end(self) -> None:
        if self._currentForm:
            self._formLayout.addLayout(self._currentForm)
            self._currentForm = None

    def addHeader(self, title: str) -> QLabel:
        self.end()
        label = QLabel(f'<center><b>{title}</b></center>')
        label.setFixedHeight(ROW_HEIGHT)
        self._formLayout.addWidget(label)
        return label

    def _createSpaceItem(self) -> QSpacerItem:
        policy = QSizePolicy.Policy.Expanding
        return QSpacerItem(0, 0, policy, policy)

    def _createFooter(self) -> QDialogButtonBox:
        footer = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Apply |
            QDialogButtonBox.StandardButton.Reset |
            QDialogButtonBox.StandardButton.Help)
        footer.button(footer.StandardButton.Apply).clicked.connect(
            self.applyRequested.emit)
        footer.button(footer.StandardButton.Reset).clicked.connect(
            self.resetRequested.emit)
        return footer


class PresetSettingsForm(SettingsForm):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.addHeader(self.tr("Preset Settings"))

        self._descField = QLineEdit()
        self.addRow(self.tr("Description:"), self._descField)

        self._shellField = QLineEdit()
        self.addRow(self.tr("Shell:"), self._shellField)

        self.end()

    def desc(self) -> str:
        return self._descField.text()

    def shell(self) -> str:
        return self._shellField.text()

    def setDesc(self, desc: str) -> None:
        self._descField.setText(desc)

    def setShell(self, shell: str) -> None:
        self._shellField.setText(shell)


class BindingSettingsForm(SettingsForm):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.addHeader(self.tr("Binding Settings"))

        self._descField = QLineEdit()
        self.addRow(self.tr("Description:"), self._descField)

        self._keyField = QLineEdit()
        self.addRow(self.tr("Key:"), self._keyField)

        self._eventField = QComboBox()
        self._eventField.addItems((self.tr("pressed"), self.tr("released")))
        self.addRow(self.tr("event:"), self._eventField)

        self._useShellField = QCheckBox()
        self.addRow(self.tr("Use Shell:"), self._useShellField)

        self._cmdField = QTextEdit()
        self.addRow(self.tr("Command:"), self._cmdField)

        self.end()

    def desc(self) -> str:
        return self._descField.text()

    def setDesc(self, desc: str) -> None:
        self._descField.setText(desc)

    def key(self) -> str:
        return self._keyField.text()

    def setKey(self, key: str) -> None:
        self._keyField.setText(key)

    def keyEvent(self) -> str:
        return self._eventField.currentText()

    def setKeyEvent(self, event: str) -> None:
        indexes = {
            'pressed': 0,
            'released': 1,
        }
        self._eventField.setCurrentIndex(indexes[event])

    def useShell(self) -> bool:
        return self._useShellField.isChecked()

    def setUseShell(self, useShell: bool) -> None:
        self._useShellField.setChecked(useShell)

    def cmd(self) -> str:
        return self._cmdField.toPlainText()

    def setCmd(self, cmd: str) -> None:
        self._cmdField.setText(cmd)

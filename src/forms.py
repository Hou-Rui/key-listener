from typing import Callable, TypeVar

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (QCheckBox, QComboBox, QDialogButtonBox,
                               QFormLayout, QLabel, QLineEdit, QSizePolicy,
                               QSpacerItem, QTextEdit, QVBoxLayout, QWidget)

from utils import preferredRowHeight


class SettingsForm(QWidget):
    Widget = TypeVar('Widget', bound=QWidget)
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

    def addRow(self, text: str,
               factory: Callable[[], Widget] = QLineEdit) -> Widget:
        if not self._currentForm:
            self._currentForm = QFormLayout()
        field = factory()
        self._currentForm.addRow(text, field)
        return field

    def end(self) -> None:
        if self._currentForm:
            self._formLayout.addLayout(self._currentForm)
            self._currentForm = None

    def addHeader(self, title: str) -> QLabel:
        self.end()
        label = QLabel(f'<center><b>{title}</b></center>')
        label.setFixedHeight(preferredRowHeight())
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
        self._descField = self.addRow(self.tr("Description:"))
        self._shellField = self.addRow(self.tr("Shell:"))
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
        self._descField = self.addRow(self.tr("Description:"))
        self._keyField = self.addRow(self.tr("Key:"))
        self._eventField = self.addRow(self.tr("Event:"), QComboBox)
        self._eventField.addItems((self.tr("Pressed"), self.tr("Released")))
        self._useShellField = self.addRow(self.tr("Use Shell:"), QCheckBox)
        self._cmdField = self.addRow(self.tr("Command:"), QTextEdit)
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
        return {
            0: 'pressed',
            1: 'released',
        }[self._eventField.currentIndex()]

    def setKeyEvent(self, event: str) -> None:
        self._eventField.setCurrentIndex({
            'pressed': 0,
            'released': 1,
        }[event])

    def useShell(self) -> bool:
        return self._useShellField.isChecked()

    def setUseShell(self, useShell: bool) -> None:
        self._useShellField.setChecked(useShell)

    def cmd(self) -> str:
        return self._cmdField.toPlainText()

    def setCmd(self, cmd: str) -> None:
        self._cmdField.setText(cmd)

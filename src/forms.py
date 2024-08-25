from typing import Callable, TypeVar

from PySide6.QtCore import SIGNAL, Qt, Signal
from PySide6.QtWidgets import (QCheckBox, QComboBox, QDialogButtonBox,
                               QFormLayout, QLabel, QLineEdit, QSizePolicy,
                               QSpacerItem, QTextEdit, QVBoxLayout, QWidget, QMessageBox)

from utils import preferredRowHeight


class SettingsForm(QWidget):
    Widget = TypeVar('Widget', bound=QWidget)
    applyRequested = Signal()
    resetRequested = Signal()
    dirtyChanged = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._formLayout = QVBoxLayout()
        self._currentForm: QFormLayout | None = None
        self._isDirty: bool = False
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        layout.addLayout(self._formLayout)
        layout.addSpacerItem(self._createSpaceItem())
        layout.addWidget(self._createFooter())

    def addRow(self, text: str,
               factory: Callable[[], Widget] = QLineEdit,
               dirtySignal: Signal = QLineEdit.editingFinished) -> Widget:
        if not self._currentForm:
            self._currentForm = QFormLayout()
        field = factory()
        field.connect(SIGNAL(str(dirtySignal)),  # type: ignore reportArgumentType
                      lambda: self.setDirty(True))
        self._currentForm.addRow(text, field)
        return field

    def end(self) -> None:
        if self._currentForm:
            self._formLayout.addLayout(self._currentForm)
            self._currentForm = None
        self.setDirty(False)

    def addHeader(self, title: str) -> QLabel:
        self.end()
        label = QLabel(f'<center><b>{title}</b></center>')
        label.setFixedHeight(preferredRowHeight())
        self._formLayout.addWidget(label)
        return label

    def isDirty(self) -> bool:
        return self._isDirty

    def setDirty(self, dirty: bool) -> None:
        if self._isDirty != dirty:
            self._isDirty = dirty
            self.dirtyChanged.emit()

    def checkDirty(self) -> bool:
        if not self.isDirty():
            return True
        button = QMessageBox.warning(
            self, self.tr("Save Changes?"),
            self.tr("Do you want to save or discard your changes?"),
            QMessageBox.StandardButton.Save |
            QMessageBox.StandardButton.Discard |
            QMessageBox.StandardButton.Cancel)
        if button == QMessageBox.StandardButton.Save:
            self.applyRequested.emit()
            return True
        elif button == QMessageBox.StandardButton.Discard:
            self.resetRequested.emit()
            return True
        return False

    def _createSpaceItem(self) -> QSpacerItem:
        policy = QSizePolicy.Policy.Expanding
        return QSpacerItem(0, 0, policy, policy)

    def _createFooter(self) -> QDialogButtonBox:
        footer = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Apply |
            QDialogButtonBox.StandardButton.Reset |
            QDialogButtonBox.StandardButton.Help)
        apply = footer.button(footer.StandardButton.Apply)
        reset = footer.button(footer.StandardButton.Reset)
        apply.clicked.connect(self.applyRequested.emit)
        reset.clicked.connect(self.resetRequested.emit)
        self.dirtyChanged.connect(
            lambda: apply.setDisabled(not self.isDirty()))
        self.dirtyChanged.connect(
            lambda: reset.setDisabled(self.isDirty()))
        self.dirtyChanged.emit()
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
        self._eventField = self.addRow(
            self.tr("Event:"), QComboBox, QComboBox.currentIndexChanged)
        self._eventField.addItems((self.tr("Pressed"), self.tr("Released")))
        self._useShellField = self.addRow(
            self.tr("Use Shell:"), QCheckBox, QCheckBox.toggled)
        self._cmdField = self.addRow(
            self.tr("Command:"), QTextEdit, QTextEdit.textChanged)
        self.end()

    def desc(self) -> str:
        return self._descField.text()

    def key(self) -> str:
        return self._keyField.text()

    def keyEvent(self) -> str:
        return {
            0: 'pressed',
            1: 'released',
        }[self._eventField.currentIndex()]

    def useShell(self) -> bool:
        return self._useShellField.isChecked()

    def cmd(self) -> str:
        return self._cmdField.toPlainText()

    def setDesc(self, desc: str) -> None:
        self._descField.setText(desc)

    def setKey(self, key: str) -> None:
        self._keyField.setText(key)

    def setKeyEvent(self, event: str) -> None:
        self._eventField.setCurrentIndex({
            'pressed': 0,
            'released': 1,
        }[event])

    def setUseShell(self, useShell: bool) -> None:
        self._useShellField.setChecked(useShell)

    def setCmd(self, cmd: str) -> None:
        self._cmdField.setText(cmd)

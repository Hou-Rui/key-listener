import logging
import shlex
from subprocess import Popen
from typing import Any, Iterable, Self

from PySide6.QtCore import (Property, QObject, QProcess, Signal,
                            SignalInstance, Slot)

from binding import Binding, BindingListModel


class Preset(QObject):
    nameChanged = Signal()
    bindingsChanged = Signal()
    shellChanged = Signal()
    errorHappened = Signal(str)

    def __init__(self, data: dict[str, Any],
                 parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._data = data
        self._name = self._initName()
        self._shell, self._shellProcess = self._initShell()
        self._bindings = self._initBinding()

    def signals(self) -> Iterable[SignalInstance]:
        return (self.nameChanged, self.shellChanged)

    @classmethod
    def sample(cls, parent: QObject | None = None) -> Self:
        data = {
            'name': 'New Preset',
            'shell': '/bin/sh',
            'bindings': []
        }
        preset = cls(data, parent)
        preset._bindings.append(Binding.sample(preset))
        return preset

    def toDict(self) -> dict[str, Any]:
        return {
            'name': self.name,
            'shell': self.shell,
            'bindings': [p.toDict() for p in self._bindings]
        }

    @Property(str, notify=nameChanged)
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, newName: str) -> None:
        self._name = newName
        self.nameChanged.emit()

    @Property(str, notify=shellChanged)
    def shell(self) -> str:
        return self._shell

    @shell.setter
    def shell(self, newShell: str) -> None:
        self._shell = newShell
        self.shellChanged.emit()

    @Property('QVariant', notify=bindingsChanged)
    def bindings(self) -> BindingListModel:
        return self._bindings

    def stopShell(self) -> None:
        if self._shellProcess.state() == QProcess.ProcessState.Running:
            self._shellProcess.terminate()
            self._shellProcess.waitForFinished()

    @Slot()
    def addNewBinding(self) -> None:
        self._bindings.append(self._createBinding())
        self.bindingsChanged.emit()

    @Slot(int, result=int)
    def removeBindingAtIndex(self, index: int) -> None:
        self._bindings.pop(index)
        self.bindingsChanged.emit()

    def exec(self, key: str, event: str) -> None:
        if self._shellProcess.state() != QProcess.ProcessState.Running:
            self._shellProcess.startCommand(self._shell)
            self._shellProcess.waitForStarted()
        if self._shellProcess.state() != QProcess.ProcessState.Running:
            msg = self.tr(f"Process {self._shell} time out")
            self.errorHappened.emit(msg)
        for binding in self._bindings:
            if binding.key == key and binding.event == event:
                logging.debug(f'executing {binding._cmd}')
                cmd = binding._cmd + '\n'
                if binding.useShell:
                    self._shellProcess.write(cmd.encode())
                else:
                    Popen(shlex.split(f'sh -c "{cmd}"'))

    def _initName(self) -> str:
        return self._data['name']

    def _initShell(self) -> tuple[str, QProcess]:
        shell = self._data.get('shell', '/bin/sh')
        shellProcess = QProcess(self)
        return shell, shellProcess

    def _createBinding(self, data: dict[str, Any] | None = None) -> Binding:
        if data is None:
            binding = Binding.sample()
        else:
            desc: str = data.get('desc', '')
            key: str = data.get('key', '')
            cmd: str = data.get('cmd', '')
            event: str = data.get('event', 'pressed')
            useShell: bool = data.get('useShell', True)
            binding = Binding(key, event, desc, cmd, useShell, parent=self)
        for sig in binding.signals():
            sig.connect(self.bindingsChanged.emit)
        return binding

    def _initBinding(self) -> BindingListModel:
        data: list[dict[str, Any]] = self._data['bindings']
        if not data or not isinstance(data, Iterable):
            return []
        return BindingListModel([self._createBinding(p) for p in data], self)

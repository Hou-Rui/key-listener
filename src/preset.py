import logging
import shlex
from subprocess import Popen
from typing import Any, Self

from PySide6.QtCore import Property, QObject, QProcess, Signal, Slot

from binding import Binding


class Preset(QObject):
    nameChanged = Signal()
    bindingsChanged = Signal()
    shellChanged = Signal()
    errorHappened = Signal(str)

    def __init__(self, data: dict[str, Any],
                 parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.data = data
        self._name = self.initName()
        self._shell, self._shellProcess = self.initShell()
        self._bindings = self.initBinding()

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

    @Property(str, notify=nameChanged)  # type: ignore
    def name(self) -> str:  # type: ignore
        return self._name

    @name.setter
    def name(self, newName: str) -> None:
        self._name = newName
        self.nameChanged.emit()

    @Property(str, notify=shellChanged)  # type: ignore
    def shell(self) -> str:  # type: ignore
        return self._shell

    @shell.setter
    def shell(self, newShell: str) -> None:
        self._shell = newShell
        self.shellChanged.emit()

    @Property(list, notify=bindingsChanged)  # type: ignore
    def bindings(self) -> list[Binding]:
        return self._bindings

    @Slot(int)
    def removeBindingAtIndex(self, index: int):
        self._bindings.pop(index)
        self.bindingsChanged.emit()

    def ensure(self, key: str, data: dict | None = None) -> Any:
        if not data:
            data = self.data
        if result := data.get(key):
            return result
        msg = self.tr(f'config "{key}" missing')
        self.errorHappened.emit(msg)

    def initName(self) -> str:
        return self.ensure('name')

    def initShell(self) -> tuple[str, QProcess]:
        shell = self.data.get('shell', '/bin/sh')
        shellProcess = QProcess(self)
        return shell, shellProcess

    def stopShell(self) -> None:
        if self._shellProcess.state() == QProcess.ProcessState.Running:
            self._shellProcess.terminate()
            self._shellProcess.waitForFinished()

    def initBinding(self) -> list[Binding]:
        bindings: list[dict[str, Any]] = self.ensure('bindings')
        if not bindings:
            return []
        result = []
        for p in bindings:
            key = self.ensure('key', p)
            desc = self.ensure('desc', p)
            cmd = self.ensure('cmd', p)
            event = p.get('event', 'pressed')
            useShell = p.get('useShell', True)
            binding = Binding(key, event, desc, cmd, useShell, parent=self)
            logging.debug(f'Add binding: {binding}')
            for sig in binding.signals():
                sig.connect(self.bindingsChanged.emit)
            result.append(binding)
        return result

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

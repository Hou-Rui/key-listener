from typing import Any, Iterable

import yaml
from PySide6.QtCore import (Property, QObject, QProcess, Signal,
                            SignalInstance, Slot)
from PySide6.QtQml import QmlElement

QML_IMPORT_NAME = "keylistener.backend"
QML_IMPORT_MAJOR_VERSION = 1


class Binding(QObject):
    keyChanged = Signal()
    descChanged = Signal()
    cmdChanged = Signal()

    def __init__(self, key: str, desc: str, cmd: str,
                 parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._key = key
        self._desc = desc
        self._cmd = cmd

    def signals(self) -> Iterable[SignalInstance]:
        return (self.keyChanged, self.descChanged, self.cmdChanged)

    @Property(str, notify=keyChanged)  # type: ignore
    def key(self) -> str:  # type: ignore
        return self._key

    @key.setter
    def key(self, newKey: str) -> None:
        self._key = newKey

    @Property(str, notify=descChanged)  # type: ignore
    def desc(self) -> str:  # type: ignore
        return self._desc

    @desc.setter
    def desc(self, newDesc: str) -> None:
        self._desc = newDesc

    @Property(str, notify=cmdChanged)  # type: ignore
    def cmd(self) -> str:  # type: ignore
        return self._cmd

    @cmd.setter
    def cmd(self, newCmd: str) -> None:
        self._cmd = newCmd


class Preset(QObject):
    nameChanged = Signal()
    bindingChanged = Signal()

    def __init__(self, data: dict[str, Any],
                 parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.data = data
        self._name = self.initName()
        self._shell, self._shellProcess = self.initShell()
        self._binding = self.initBinding()

    @Property(str, notify=nameChanged)  # type: ignore
    def name(self) -> str:  # type: ignore
        return self._name

    @name.setter
    def name(self, newName: str) -> None:
        self._name = newName

    @Property(list, notify=bindingChanged)  # type: ignore
    def binding(self) -> list[Binding]:
        return self._binding

    def ensure(self, key: str, data: dict | None = None) -> Any:
        if not data:
            data = self.data
        if result := data.get(key):
            return result
        raise RuntimeError(f"Missing field {key}")

    def initName(self) -> str:
        return self.ensure('name')

    def initShell(self) -> tuple[str, QProcess]:
        if not (shell := self.data.get('shell')):
            shell = '/bin/sh'
        shellProcess = QProcess(self)
        return shell, shellProcess

    def stopShell(self) -> None:
        self._shellProcess.terminate()

    def initBinding(self) -> list[Binding]:
        bindings: list[dict[str, Any]] = self.ensure('bindings')
        result = []
        for p in bindings:
            binding = Binding(self.ensure('key', p),
                              self.ensure('desc', p),
                              self.ensure('cmd', p), parent=self)
            for sig in binding.signals():
                sig.connect(self.bindingChanged.emit)
            result.append(binding)
        return result

    def exec(self, key: str) -> None:
        if self._shellProcess.state() != QProcess.ProcessState.Running:
            self._shellProcess.startCommand(self._shell)
            self._shellProcess.waitForStarted(5)
        for event in self._binding:
            if event.key != key:
                continue
            cmd = event._cmd.encode() + b'&\n'
            print(f'executing {cmd}')
            self._shellProcess.write(cmd)


@QmlElement
class PresetManager(QObject):
    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.path = "preset.yml"
        self.presets = self.initPresets()
        self.currentPreset = self.presets[0]

    def initPresets(self) -> list[Preset]:
        with open(self.path) as config_file:
            return [Preset(p, self) for p in yaml.safe_load(config_file)]

    @Slot(result=list)
    def getPresets(self) -> list[Preset]:
        return self.presets

    @Slot(result=Preset)
    def getCurrentPreset(self) -> Preset:
        return self.currentPreset

    @Slot(result=list)
    def getCurrentListenedKeys(self) -> list:
        return [p.key for p in self.currentPreset._binding]

    @Slot(str)
    def execKeyPressCommand(self, key: str) -> None:
        self.currentPreset.exec(key)

    @Slot()
    def cleanUp(self) -> None:
        self.currentPreset.stopShell()

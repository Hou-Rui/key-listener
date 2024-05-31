from typing import Any, Iterable

import yaml
from PySide6.QtCore import (QObject, Signal, SignalInstance,
                            Slot, Property, QProcess)
from PySide6.QtQml import QmlElement

QML_IMPORT_NAME = "keylistener.backend"
QML_IMPORT_MAJOR_VERSION = 1


class Event(QObject):
    keyChanged = Signal()
    descChanged = Signal()
    cmdChanged = Signal()

    def __init__(self, key: str, desc: str, cmd: str,
                 parent: QObject | None = None):
        super().__init__(parent)
        self._key = key
        self._desc = desc
        self._cmd = cmd

    def signals(self) -> Iterable[SignalInstance]:
        return (self.keyChanged, self.descChanged, self.cmdChanged)

    @Property(str, notify=keyChanged)  # type: ignore
    def key(self):
        return self._key

    @Property(str, notify=descChanged)  # type: ignore
    def desc(self):
        return self._desc

    @Property(str, notify=cmdChanged)  # type: ignore
    def cmd(self):
        return self._cmd


class Preset(QObject):
    nameChanged = Signal()
    bindingChanged = Signal()

    def __init__(self, data: dict[str, Any],
                 parent: QObject | None = None):
        super().__init__(parent)
        self.data = data
        self._name = self.initName()
        self._shell, self._shellProcess = self.initShell()
        self._binding = self.initBinding()

    @Property(str, notify=nameChanged)  # type: ignore
    def name(self):
        return self._name

    @Property(list, notify=bindingChanged)  # type: ignore
    def binding(self):
        return self._binding

    def ensure(self, key: str, data: dict | None = None):
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

    def initBinding(self) -> list[Event]:
        binding: list[dict[str, Any]] = self.ensure('binding')
        result = []
        for p in binding:
            event = Event(self.ensure('key', p),
                          self.ensure('desc', p),
                          self.ensure('cmd', p), parent=self)
            for sig in event.signals():
                sig.connect(self.bindingChanged.emit)
            result.append(event)
        return result

    def exec(self, key: str):
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
    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)
        self.path = "preset.yml"
        self.presets = self.initPresets()
        self.current = self.presets[0]

    def initPresets(self) -> list[Preset]:
        with open(self.path) as config_file:
            return [Preset(p, self) for p in yaml.safe_load(config_file)]

    @Slot(result=list)
    def getPresets(self) -> list[Preset]:
        return self.presets

    @Slot(result=Preset)
    def getCurrentPreset(self) -> Preset:
        return self.current

    @Slot(result=list)
    def getCurrentListenedKeys(self) -> list:
        return [p.key for p in self.current._binding]

    @Slot(str)
    def execKeyPressCommand(self, key: str) -> str | None:
        self.current.exec(key)

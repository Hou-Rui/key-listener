from typing import Any, Iterable

import yaml
from PySide6.QtCore import (Property, QObject, QProcess, Signal,
                            SignalInstance, Slot)
from PySide6.QtQml import QmlElement

QML_IMPORT_NAME = "keylistener.backend"
QML_IMPORT_MAJOR_VERSION = 1


class Binding(QObject):
    keyChanged = Signal()
    eventChanged = Signal()
    descChanged = Signal()
    cmdChanged = Signal()

    def __init__(self, key: str, event: str, desc: str, cmd: str,
                 parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._key = key
        self._event = event
        self._desc = desc
        self._cmd = cmd

    def signals(self) -> Iterable[SignalInstance]:
        return (self.keyChanged, self.eventChanged,
                self.descChanged, self.cmdChanged)

    @Property(str, notify=keyChanged)  # type: ignore
    def key(self) -> str:  # type: ignore
        return self._key

    @key.setter
    def key(self, newKey: str) -> None:
        self._key = newKey
        self.keyChanged.emit()

    @Property(str, notify=eventChanged)  # type: ignore
    def event(self) -> str:  # type: ignore
        return self._event

    @event.setter
    def event(self, newKey: str) -> None:
        self._event = newKey.lower()
        self.eventChanged.emit()

    @Property(str, notify=descChanged)  # type: ignore
    def desc(self) -> str:  # type: ignore
        return self._desc

    @desc.setter
    def desc(self, newDesc: str) -> None:
        self._desc = newDesc
        self.descChanged.emit()

    @Property(str, notify=cmdChanged)  # type: ignore
    def cmd(self) -> str:  # type: ignore
        return self._cmd

    @cmd.setter
    def cmd(self, newCmd: str) -> None:
        self._cmd = newCmd
        self.cmdChanged.emit()


class Preset(QObject):
    nameChanged = Signal()
    bindingChanged = Signal()
    errorHappened = Signal(str)

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
        self.nameChanged.emit()

    @Property(list, notify=bindingChanged)  # type: ignore
    def binding(self) -> list[Binding]:
        return self._binding

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

    def initBinding(self) -> list[Binding]:
        bindings: list[dict[str, Any]] = self.ensure('bindings')
        result = []
        for p in bindings:
            key = self.ensure('key', p)
            desc = self.ensure('desc', p)
            cmd = self.ensure('cmd', p)
            event = p.get('event', 'pressed')
            binding = Binding(key, event, desc, cmd, parent=self)
            for sig in binding.signals():
                sig.connect(self.bindingChanged.emit)
            result.append(binding)
        return result

    def exec(self, key: str, event: str) -> None:
        if self._shellProcess.state() != QProcess.ProcessState.Running:
            self._shellProcess.startCommand(self._shell)
            self._shellProcess.waitForStarted()
        if self._shellProcess.state() != QProcess.ProcessState.Running:
            msg = self.tr(f"Process {self._shell} time out")
            self.errorHappened.emit(msg)
        for binding in self._binding:
            if binding.key == key and binding.event == event:
                print(f'executing {binding._cmd}')
                cmd = binding._cmd + '\n'
                self._shellProcess.write(cmd.encode())


@QmlElement
class PresetManager(QObject):
    currentPresetChanged = Signal()
    errorHappened = Signal(str)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.path = "preset.yml"
        self.presets = self.initPresets()
        self._currentPresetIndex = 0

    def initPresets(self) -> list[Preset]:
        try:
            with open(self.path) as config_file:
                result = []
                for p in yaml.safe_load(config_file):
                    preset = Preset(p, self)
                    preset.errorHappened.connect(self.errorHappened.emit)
                    result.append(preset)
                return result
        except OSError as err:
            self.errorHappened.emit(self.tr(f'OS error: {err}'))
        except yaml.YAMLError as err:
            self.errorHappened.emit(self.tr(f'YAML error: {err}'))
        return []

    @Property(int, notify=currentPresetChanged) # type: ignore
    def currentPresetIndex(self) -> int: # type: ignore
        return self._currentPresetIndex
    
    @currentPresetIndex.setter
    def currentPresetIndex(self, newIndex: int) -> None:
        self.currentPreset.stopShell()
        self._currentPresetIndex = newIndex
        self.currentPresetChanged.emit()

    @Slot(result=list)
    def getPresets(self) -> list[Preset]:
        return self.presets

    @Property("QVariant", notify=currentPresetChanged) # type: ignore
    def currentPreset(self) -> Preset:
        return self.presets[self.currentPresetIndex]

    @Slot(result=list)
    def getCurrentListenedKeys(self) -> list:
        return [p.key for p in self.currentPreset.binding]

    @Slot(str)
    def execKeyPressCommand(self, key: str) -> None:
        self.currentPreset.exec(key, event='pressed')

    @Slot(str)
    def execKeyReleaseCommand(self, key: str) -> None:
        self.currentPreset.exec(key, event='released')

    @Slot()
    def cleanUp(self) -> None:
        self.currentPreset.stopShell()

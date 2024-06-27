from pathlib import Path
from typing import Any, Iterable

import json
from PySide6.QtCore import Property, QObject, QStandardPaths, Signal, Slot
from PySide6.QtQml import QmlElement, QmlSingleton

from preset import Preset

QML_IMPORT_NAME = "keylistener.backend"
QML_IMPORT_MAJOR_VERSION = 1


@QmlElement
@QmlSingleton
class PresetManager(QObject):
    presetsChanged = Signal()
    currentPresetChanged = Signal()
    errorHappened = Signal(str)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.path = self.initPath()
        self._presets = self.initPresets()
        self._currentPresetIndex = 0

    def initPath(self) -> str:
        type = QStandardPaths.StandardLocation.ConfigLocation
        user_config_dir = QStandardPaths.writableLocation(type)
        config_path = Path(user_config_dir, 'keylistener')
        config_path.mkdir(exist_ok=True)
        config_file_path = config_path / 'config.json'
        if not config_file_path.exists():
            config_file_path.touch()
        return str(config_file_path)

    def initPresets(self) -> list[Preset]:
        try:
            with open(self.path, 'r') as config_file:
                result = []
                data = json.load(config_file)
                if not isinstance(data, Iterable):
                    return []
                for p in data:
                    preset = self.createPreset(p)
                    result.append(preset)
                return result
        except OSError as err:
            self.errorHappened.emit(self.tr(f'OS error: {err}'))
        except json.JSONDecodeError as err:
            self.errorHappened.emit(self.tr(f'JSON error: {err}'))
        return []

    def createPreset(self, data: dict[str, Any]) -> Preset:
        if data is None:
            preset = Preset.sample(self)
        else:
            preset = Preset(data, self)
        preset.errorHappened.connect(self.errorHappened.emit)
        preset.bindingsChanged.connect(self.savePresets)
        for sig in preset.signals():
            sig.connect(self.presetsChanged.emit)
        return preset

    @Slot()
    def savePresets(self):
        try:
            with open(self.path, 'w') as config_file:
                data = [p.toDict() for p in self._presets]
                json.dump(data, config_file, sort_keys=True)
        except OSError as err:
            self.errorHappened.emit(self.tr(f'OS error: {err}'))
        except json.JSONDecodeError as err:
            self.errorHappened.emit(self.tr(f'JSON error: {err}'))

    @Property(int, notify=currentPresetChanged)
    def currentPresetIndex(self) -> int:
        return self._currentPresetIndex

    @currentPresetIndex.setter
    def currentPresetIndex(self, newIndex: int) -> None:
        self.currentPreset.stopShell()
        self._currentPresetIndex = newIndex
        self.currentPresetChanged.emit()

    @Property('QVariantList', notify=presetsChanged)
    def presets(self) -> list[Preset]:
        return self._presets

    @Property('QVariant', notify=currentPresetChanged)
    def currentPreset(self) -> Preset:
        if not self.presets:
            self.addNewPreset()
        return self._presets[self._currentPresetIndex]

    @Slot(result=list)
    def getCurrentListenedKeys(self) -> list[tuple[str, str]]:
        return [(p.key, p.event) for p in self.currentPreset.bindings]

    @Slot(result=int)
    def addNewPreset(self) -> int:
        self._presets.append(self.createPreset(None))
        self.savePresets()
        self._currentPresetIndex = len(self._presets) - 1
        self.presetsChanged.emit()
        self.currentPresetChanged.emit()
        return self._currentPresetIndex

    @Slot(result=int)
    def removeCurrentPreset(self) -> int:
        self._presets.pop(self._currentPresetIndex)
        self.savePresets()
        if self._currentPresetIndex >= len(self._presets):
            self._currentPresetIndex -= 1
        self.presetsChanged.emit()
        self.currentPresetChanged.emit()
        return self._currentPresetIndex

    @Slot(result=int)
    def addNewBinding(self) -> int:
        index = self.currentPreset.addNewBinding()
        self.savePresets()
        return index

    @Slot(int)
    def removeBindingAtIndex(self, index: int) -> None:
        print(f'removing index {index}')
        self.currentPreset.removeBindingAtIndex(index)
        self.savePresets()

    @Slot(str)
    def execKeyPressCommand(self, key: str) -> None:
        self.currentPreset.exec(key, event='pressed')

    @Slot(str)
    def execKeyReleaseCommand(self, key: str) -> None:
        self.currentPreset.exec(key, event='released')

    @Slot()
    def cleanUp(self) -> None:
        self.currentPreset.stopShell()

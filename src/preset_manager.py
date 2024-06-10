from pathlib import Path
from typing import Iterable

import yaml
from PySide6.QtCore import Property, QObject, QStandardPaths, Signal, Slot
from PySide6.QtQml import QmlElement, QmlSingleton

from preset import Preset

QML_IMPORT_NAME = "keylistener.backend"
QML_IMPORT_MAJOR_VERSION = 1


@QmlElement
@QmlSingleton
class PresetManager(QObject):
    currentPresetChanged = Signal()
    errorHappened = Signal(str)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.path = self.initPath()
        self.presets = self.initPresets()
        self._currentPresetIndex = 0

    def initPath(self) -> str:
        type = QStandardPaths.StandardLocation.ConfigLocation
        user_config_dir = QStandardPaths.writableLocation(type)
        config_path = Path(user_config_dir, 'keylistener')
        config_path.mkdir(exist_ok=True)
        config_file_path = config_path / 'config.yml'
        if not config_file_path.exists():
            config_file_path.touch()
        return str(config_file_path)

    def initPresets(self) -> list[Preset]:
        try:
            with open(self.path, 'r') as config_file:
                result = []
                data = yaml.safe_load(config_file)
                if not isinstance(data, Iterable):
                    return []
                for p in data:
                    preset = Preset(p, self)
                    preset.errorHappened.connect(self.errorHappened.emit)
                    preset.bindingsChanged.connect(self.savePresets)
                    result.append(preset)
                return result
        except OSError as err:
            self.errorHappened.emit(self.tr(f'OS error: {err}'))
        except yaml.YAMLError as err:
            self.errorHappened.emit(self.tr(f'YAML error: {err}'))
        return []

    @Slot()
    def savePresets(self):
        try:
            with open(self.path, 'w') as config_file:
                data = [p.toDict() for p in self.presets]
                config_file.write(yaml.safe_dump(data, sort_keys=False))
        except OSError as err:
            self.errorHappened.emit(self.tr(f'OS error: {err}'))
        except yaml.YAMLError as err:
            self.errorHappened.emit(self.tr(f'YAML error: {err}'))

    @Property(int, notify=currentPresetChanged)  # type: ignore
    def currentPresetIndex(self) -> int:  # type: ignore
        return self._currentPresetIndex

    @currentPresetIndex.setter
    def currentPresetIndex(self, newIndex: int) -> None:
        self.currentPreset.stopShell()
        self._currentPresetIndex = newIndex
        self.currentPresetChanged.emit()

    @Slot(result=list)
    def getPresets(self) -> list[Preset]:
        return self.presets

    @Property('QVariant', notify=currentPresetChanged)  # type: ignore
    def currentPreset(self) -> Preset:
        if not self.presets:
            self.presets.append(Preset.sample())
            self.currentPresetIndex = 0
        return self.presets[self.currentPresetIndex]

    @Slot(result=list)
    def getCurrentListenedKeys(self) -> list[str]:
        return [p.key for p in self.currentPreset.bindings]

    @Slot(int)
    def removeBindingAtIndex(self, index: int) -> None:
        print(f'removing index {index}')
        self.currentPreset.removeBindingAtIndex(index)

    @Slot(str)
    def execKeyPressCommand(self, key: str) -> None:
        self.currentPreset.exec(key, event='pressed')

    @Slot(str)
    def execKeyReleaseCommand(self, key: str) -> None:
        self.currentPreset.exec(key, event='released')

    @Slot()
    def cleanUp(self) -> None:
        self.currentPreset.stopShell()

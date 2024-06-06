import yaml
from PySide6.QtCore import Property, QObject, Signal, Slot
from PySide6.QtQml import QmlElement

from preset import Preset

QML_IMPORT_NAME = "keylistener.backend"
QML_IMPORT_MAJOR_VERSION = 1


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
    def getCurrentListenedKeys(self) -> list[str]:
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

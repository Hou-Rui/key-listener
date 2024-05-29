from subprocess import Popen

import yaml
from PySide6.QtCore import QObject, Slot
from PySide6.QtQml import QmlElement

QML_IMPORT_NAME = "keylistener.backend"
QML_IMPORT_MAJOR_VERSION = 1


@QmlElement
class PresetManager(QObject):
    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)
        self.path = "preset.yml"
        self.presets = self.initPresets()
        self.current = self.presets[0]

    def initPresets(self) -> list[dict]:
        with open(self.path) as config_file:
            return yaml.safe_load(config_file)

    @Slot(result=list)
    def getPresets(self) -> list[dict]:
        return self.presets

    @Slot(result=dict)
    def getCurrentPreset(self) -> dict:
        return self.current

    @Slot(result=list)
    def getCurrentListenedKeys(self) -> list:
        return [p["key"] for p in self.current["pressed"]]

    @Slot(str)
    def execKeyPressCommand(self, key: str) -> str | None:
        for p in self.current["pressed"]:
            if p["key"] == key:
                cmd = p["cmd"]
                Popen(cmd, shell=True)

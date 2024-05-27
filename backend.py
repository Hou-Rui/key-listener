import os
from subprocess import Popen

import evdev
import yaml
from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtGui import QKeySequence
from PySide6.QtQml import QmlElement

QML_IMPORT_NAME = "backend.Backend"
QML_IMPORT_MAJOR_VERSION = 1


class PresetManager:
    def __init__(self, path: str) -> None:
        self.path = path
        self.presets = self.initPresets()
        self.current = self.presets[0]

    def initPresets(self) -> list[dict]:
        with open(self.path) as config_file:
            return yaml.safe_load(config_file)


class EventDeviceManager:
    EVDEV_PATH = '/dev/input'

    def __init__(self):
        self.devices = self.initDevices()

    def initDevices(self) -> evdev.InputDevice:
        result = []
        for p in os.listdir(self.EVDEV_PATH):
            path = os.path.join(self.EVDEV_PATH, p)
            if not path.startswith('event'):
                continue
            device = evdev.InputDevice(path)
            caps = device.capabilities()
            if keys := caps.get(evdev.ecodes.EV_KEY):
                if evdev.ecodes.KEY_ENTER in keys:
                    result.append(device)
        return result



@QmlElement
class Backend(QObject):
    messageEmitted = Signal(str)

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)
        self.presetManager = PresetManager("preset.yml")

    @Slot(result=list)
    def getPresets(self) -> list[dict]:
        return self.presetManager.presets

    @Slot(result=dict)
    def getCurrentPreset(self) -> dict:
        return self.presetManager.current

    def getCommand(self, keyText: str) -> str | None:
        for p in self.presetManager.current["pressed"]:
            if p["key"] == keyText:
                return p["cmd"]

    @Slot(int)
    def processKey(self, key: int):
        keyText = QKeySequence(key).toString()
        print(f"{keyText} is pressed!")
        if cmd := self.getCommand(keyText):
            print(f"Executing {cmd}...")
            Popen(cmd.split(" "))
            self.messageEmitted.emit(f"Event: {keyText} pressed")

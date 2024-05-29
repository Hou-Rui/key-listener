from dataclasses import dataclass
from subprocess import PIPE, Popen
from typing import Any
import shlex

import yaml
from PySide6.QtCore import QObject, Slot
from PySide6.QtQml import QmlElement

QML_IMPORT_NAME = "keylistener.backend"
QML_IMPORT_MAJOR_VERSION = 1


@dataclass
class Event:
    key: str
    desc: str
    cmd: str


type YamlDict = dict[str, Any]


class Preset:
    def __init__(self, data: YamlDict):
        self.data = data
        self.name = self.get('name')
        self.shell = self.initShell()
        self.pressed = self.initPressed()

    def get(self, key: str, data: dict | None = None):
        if not data:
            data = self.data
        if result := data.get(key):
            return result
        raise RuntimeError(f"Missing field {key}")
    
    def initShell(self) -> Popen:
        if not (shell := self.get('shell')):
            shell = '/bin/sh'
        args = shlex.split(shell)
        return Popen(args, stdin=PIPE)

    def initPressed(self) -> list[Event]:
        root: list[dict] = self.get('pressed')
        return [Event(self.get('key', p), self.get('desc', p),
                      self.get('cmd', p))
                for p in root]

    def exec(self, key: str):
        for event in self.pressed:
            if event.key != key:
                continue
            self.shell.communicate(event.cmd)


@QmlElement
class PresetManager(QObject):
    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)
        self.path = "preset.yml"
        self.presets = self.initPresets()
        self.current = self.presets[0]

    def initPresets(self) -> list[Preset]:
        with open(self.path) as config_file:
            return [Preset(p) for p in yaml.safe_load(config_file)]

    @Slot(result=list)
    def getPresets(self) -> list[Preset]:
        return self.presets

    @Slot(result=dict)
    def getCurrentPreset(self) -> Preset:
        return self.current

    @Slot(result=list)
    def getCurrentListenedKeys(self) -> list:
        return [p.key for p in self.current.pressed]

    @Slot(str)
    def execKeyPressCommand(self, key: str) -> str | None:
        self.current.exec(key)

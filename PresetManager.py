from dataclasses import dataclass
from subprocess import PIPE, Popen
from typing import Any
import shlex

import yaml
from PySide6.QtCore import QObject, Slot, Property
from PySide6.QtQml import QmlElement

QML_IMPORT_NAME = "keylistener.backend"
QML_IMPORT_MAJOR_VERSION = 1


class Event(QObject):
    def __init__(self, key: str, desc: str, cmd: str,
                 parent: QObject | None = None):
        super().__init__(parent)
        self._key = key
        self._desc = desc
        self._cmd = cmd

    @Property(str)  # type: ignore
    def key(self):
        return self._key

    @Property(str)  # type: ignore
    def desc(self):
        return self._desc
    
    @Property(str)  # type: ignore
    def cmd(self):
        return self._cmd

type YamlDict = dict[str, Any]


class Preset(QObject):
    def __init__(self, data: YamlDict,
                 parent: QObject | None = None):
        super().__init__(parent)
        self.data = data
        self._name = self.initName()
        self._shell = self.initShell()
        self._pressed = self.initPressed()

    @Property(str)  # type: ignore
    def name(self):
        return self._name
    
    @Property(list)  # type: ignore
    def pressed(self):
        return self._pressed

    def get(self, key: str, data: dict | None = None):
        if not data:
            data = self.data
        if result := data.get(key):
            return result
        raise RuntimeError(f"Missing field {key}")

    def initName(self) -> str:
        return self.get('name')

    def initShell(self) -> Popen:
        if not (shell := self.get('shell')):
            shell = '/bin/sh'
        args = shlex.split(shell)
        return Popen(args, stdin=PIPE)

    def initPressed(self) -> list[Event]:
        root: list[dict] = self.get('pressed')
        return [Event(self.get('key', p),
                      self.get('desc', p),
                      self.get('cmd', p), parent=self)
                for p in root]

    def exec(self, key: str):
        for event in self._pressed:
            if event.key != key:
                continue
            cmd = event._cmd.encode() + b'\n'
            print(f'executing {cmd}')
            if not (stdin := self._shell.stdin):
                raise RuntimeError(f"{self._shell.args} has no stdin")
            stdin.write(cmd)


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
        return [p.key for p in self.current._pressed]

    @Slot(str)
    def execKeyPressCommand(self, key: str) -> str | None:
        self.current.exec(key)

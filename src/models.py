import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, override

from PySide6.QtCore import (QByteArray, QModelIndex, QObject, QSize,
                            QStandardPaths, Qt)
from PySide6.QtGui import QStandardItem, QStandardItemModel

import utils


@dataclass
class Binding:
    desc: str = 'New Binding'
    key: str = 'KEY_ENTER'
    event: str = 'pressed'
    useShell: bool = True
    cmd: str = ''


@dataclass
class Preset:
    desc: str = 'New Preset'
    shell: str = '/bin/sh'
    bindings: list[Binding] = [Binding()]

    def getBindings(self, key: str, event: str) -> list[Binding]:
        return [b for b in self.bindings
                if key == b.key and event == b.event]


class ConfigModel(QStandardItemModel):
    PresetRole = Qt.ItemDataRole.UserRole
    BindingRole = Qt.ItemDataRole.UserRole + 1

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._path = self._initPath()
        self._setupModel()

    def _initPath(self) -> str:
        path = Path(QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.ConfigLocation), 'keylistener')
        path.mkdir(exist_ok=True)
        file = path / 'config.json'
        if not file.exists():
            file.touch()
        return str(file)

    def _setupModel(self) -> None:
        with open(self._path, 'r') as config:
            root = self.invisibleRootItem()
            for raw in json.load(config):
                preset = Preset(**raw)
                preset.bindings = [Binding(**b) for b in raw['bindings']]
                presetItem = QStandardItem()
                presetItem.setData(preset, self.PresetRole)
                for binding in preset.bindings:
                    bindingItem = QStandardItem()
                    bindingItem.setData(binding, self.BindingRole)
                    presetItem.appendRow(bindingItem)
                root.appendRow(presetItem)

    @override
    def data(self, index: QModelIndex, role: int) -> Any:
        if role == Qt.ItemDataRole.DisplayRole:
            item = self.itemData(index)
            for role in (self.PresetRole, self.BindingRole):
                if data := item.get(role):
                    assert isinstance(data, (Binding, Preset))
                    return data.desc
            return None
        if role == Qt.ItemDataRole.SizeHintRole:
            return QSize(0, utils.ROW_HEIGHT)
        return super().data(index, role)

    @override
    def roleNames(self) -> dict[int, QByteArray]:
        return {
            self.PresetRole: QByteArray(b'preset'),
            self.BindingRole: QByteArray(b'binding'),
            **super().roleNames()
        }

    def addPreset(self, preset: Preset) -> QModelIndex:
        item = QStandardItem()
        item.setData(preset, self.PresetRole)
        self.appendRow(item)
        return item.index()

    def addBinding(self, binding: Binding, parent: QStandardItem) -> QModelIndex:
        item = QStandardItem()
        item.setData(binding, self.BindingRole)
        parent.appendRow(item)
        return item.index()

    def save(self) -> None:
        with open(self._path, 'w') as config:
            raw = [asdict(self.item(row).data(self.PresetRole))
                   for row in range(self.rowCount())]
            json.dump(raw, config, indent=2)

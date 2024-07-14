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
    desc: str
    key: str
    event: str
    useShell: bool
    cmd: str


@dataclass
class Preset:
    desc: str
    shell: str
    bindings: list[Binding]

    def getBindings(self, key: str, event: str) -> list[Binding]:
        return [b for b in self.bindings
                if key == b.key and event == b.event]


class ConfigModel(QStandardItemModel):
    PresetRole = Qt.ItemDataRole.UserRole
    BindingRole = Qt.ItemDataRole.UserRole + 1

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._path = self._initPath()
        self._presets = self._initPresets()
        self._setupModel()

    def _initPath(self) -> str:
        path = Path(QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.ConfigLocation), 'keylistener')
        path.mkdir(exist_ok=True)
        file = path / 'config.json'
        if not file.exists():
            file.touch()
        return str(file)

    def _initPresets(self) -> list[Preset]:
        with open(self._path, 'r') as config:
            result = []
            for raw in json.load(config):
                p = Preset(**raw)
                p.bindings = [Binding(**b) for b in raw['bindings']]
                result.append(p)
            return result

    def _setupModel(self) -> None:
        root = self.invisibleRootItem()
        for preset in self._presets:
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

    def save(self) -> None:
        with open(self._path, 'w') as config:
            raw = [asdict(p) for p in self._presets]
            json.dump(raw, config, indent=2)

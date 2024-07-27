import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, TypeVar, override

from PySide6.QtCore import (QByteArray, QModelIndex, QObject, QSize,
                            QStandardPaths, Qt)
from PySide6.QtGui import QStandardItem, QStandardItemModel

PROJECT_CODE_NAME = 'keylistener'


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
    bindings: list[Binding] = field(default_factory=list)

    def getBindings(self, key: str, event: str) -> list[Binding]:
        return [b for b in self.bindings
                if key == b.key and event == b.event]


class ConfigModel(QStandardItemModel):
    Data = TypeVar('Data', bound=Preset | Binding)
    PresetRole = Qt.ItemDataRole.UserRole
    BindingRole = Qt.ItemDataRole.UserRole + 1

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._path = self._initPath()
        self._setupModel()

    def _initPath(self) -> str:
        loc = QStandardPaths.StandardLocation.ConfigLocation
        path = Path(QStandardPaths.writableLocation(loc), PROJECT_CODE_NAME)
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

    def _itemTypeData(self, item: QModelIndex | QStandardItem,
                      t: type[Data], role: int) -> Data | None:
        if isinstance(item, QStandardItem):
            item = item.index()
        data = self.itemData(item).get(role)
        if isinstance(data, t):
            return data
        return None

    def itemPresetData(self, item: QModelIndex | QStandardItem) -> Preset | None:
        return self._itemTypeData(item, Preset, self.PresetRole)

    def itemBindingData(self, item: QModelIndex | QStandardItem) -> Binding | None:
        return self._itemTypeData(item, Binding, self.BindingRole)

    @override
    def data(self, index: QModelIndex, role: int) -> Any:
        if role == Qt.ItemDataRole.DisplayRole:
            item = self.itemData(index)
            for role in (self.PresetRole, self.BindingRole):
                if data := item.get(role):
                    assert isinstance(data, (Binding, Preset))
                    return data.desc
            return None
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
        preset: Preset = parent.data(self.PresetRole)
        preset.bindings.append(binding)
        return item.index()

    def removeItem(self, item: QStandardItem) -> None:
        if item.data(ConfigModel.PresetRole):
            self.removeRow(item.row())
        else:
            parent = item.parent()
            preset: Preset = parent.data(ConfigModel.PresetRole)
            preset.bindings.pop(item.row())
            self.removeRow(item.row(), parent.index())
        self.save()

    def save(self) -> None:
        with open(self._path, 'w') as config:
            raw = [asdict(self.item(row).data(self.PresetRole))
                   for row in range(self.rowCount())]
            json.dump(raw, config, indent=2)

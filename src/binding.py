from dataclasses import dataclass
from typing import Iterable

from PySide6.QtCore import Property, QObject, Signal, SignalInstance


@dataclass
class Binding(QObject):
    _key: str
    _event: str
    _desc: str
    _cmd: str

    keyChanged = Signal()
    eventChanged = Signal()
    descChanged = Signal()
    cmdChanged = Signal()

    def __init__(self, key: str, event: str, desc: str, cmd: str,
                 parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._key = key
        self._event = event
        self._desc = desc
        self._cmd = cmd

    def signals(self) -> Iterable[SignalInstance]:
        return (self.keyChanged, self.eventChanged,
                self.descChanged, self.cmdChanged)

    @Property(str, notify=keyChanged)  # type: ignore
    def key(self) -> str:  # type: ignore
        return self._key

    @key.setter
    def key(self, newKey: str) -> None:
        self._key = newKey
        self.keyChanged.emit()

    @Property(str, notify=eventChanged)  # type: ignore
    def event(self) -> str:  # type: ignore
        return self._event

    @event.setter
    def event(self, newKey: str) -> None:
        self._event = newKey.lower()
        self.eventChanged.emit()

    @Property(str, notify=descChanged)  # type: ignore
    def desc(self) -> str:  # type: ignore
        return self._desc

    @desc.setter
    def desc(self, newDesc: str) -> None:
        self._desc = newDesc
        self.descChanged.emit()

    @Property(str, notify=cmdChanged)  # type: ignore
    def cmd(self) -> str:  # type: ignore
        return self._cmd

    @cmd.setter
    def cmd(self, newCmd: str) -> None:
        self._cmd = newCmd
        self.cmdChanged.emit()

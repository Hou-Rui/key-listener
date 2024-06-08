from dataclasses import dataclass
from typing import Any, Iterable, Self

from PySide6.QtCore import Property, QObject, Signal, SignalInstance


@dataclass
class Binding(QObject):
    _key: str
    _event: str
    _desc: str
    _cmd: str
    _useShell: bool

    keyChanged = Signal()
    eventChanged = Signal()
    descChanged = Signal()
    cmdChanged = Signal()
    useShellChanged = Signal()

    def __init__(self, key: str, event: str, desc: str, cmd: str,
                 useShell: bool, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._key = key
        self._event = event
        self._desc = desc
        self._cmd = cmd
        self._useShell = useShell

    def signals(self) -> Iterable[SignalInstance]:
        return (self.keyChanged, self.eventChanged, self.descChanged,
                self.cmdChanged, self.useShellChanged)

    def toDict(self) -> dict[str, Any]:
        return {
            'key': self.key,
            'event': self.event,
            'desc': self.desc,
            'cmd': self.cmd,
            'useShell': self.useShell
        }

    @classmethod
    def sample(cls, parent: QObject | None = None) -> Self:
        return cls(key='KEY_ENTER', event='pressed', desc='New Binding',
                   cmd='', useShell=True, parent=parent)

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

    @Property(bool, notify=useShellChanged)  # type: ignore
    def useShell(self) -> bool:  # type: ignore
        return self._useShell

    @useShell.setter
    def useShell(self, newUseShell: bool) -> None:
        self._useShell = newUseShell
        self.useShellChanged.emit()

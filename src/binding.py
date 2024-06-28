from dataclasses import dataclass
from typing import Any, Iterable, Literal, Self

from PySide6.QtCore import Property, QObject, Signal, SignalInstance

Event = Literal['pressed'] | Literal['released']


@dataclass
class Binding(QObject):
    _key: str
    _event: Event
    _desc: str
    _cmd: str
    _useShell: bool

    keyChanged = Signal()
    eventChanged = Signal()
    descChanged = Signal()
    cmdChanged = Signal()
    useShellChanged = Signal()

    def __init__(self, key: str, event: Event, desc: str, cmd: str,
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

    @Property(str, notify=keyChanged)
    def key(self) -> str:
        return self._key

    @key.setter
    def key(self, newKey: str) -> None:
        self._key = newKey
        self.keyChanged.emit()

    @Property(str, notify=eventChanged)
    def event(self) -> Event:
        return self._event

    @event.setter
    def event(self, newKey: str) -> None:
        self._event = newKey.lower()
        self.eventChanged.emit()

    @Property(str, notify=descChanged)
    def desc(self) -> str:
        return self._desc

    @desc.setter
    def desc(self, newDesc: str) -> None:
        self._desc = newDesc
        self.descChanged.emit()

    @Property(str, notify=cmdChanged)
    def cmd(self) -> str:
        return self._cmd

    @cmd.setter
    def cmd(self, newCmd: str) -> None:
        self._cmd = newCmd
        self.cmdChanged.emit()

    @Property(bool, notify=useShellChanged)
    def useShell(self) -> bool:
        return self._useShell

    @useShell.setter
    def useShell(self, newUseShell: bool) -> None:
        self._useShell = newUseShell
        self.useShellChanged.emit()

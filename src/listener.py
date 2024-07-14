import asyncio
import os

import evdev
from evdev.ecodes import ecodes
from PySide6.QtCore import QObject, QThread, Signal
from qasync import QEventLoop

EV_KEY = ecodes["EV_KEY"]
EVDEV_PATH = "/dev/input"

KeyEventPair = tuple[str, str]


class EventListener(QObject):
    keyCaptured = Signal(str, str)
    listeningChanged = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.loop, self.loopThread = self._initLoop()
        self.devices: list[evdev.InputDevice] = []
        self.tasks: list[asyncio.Task] = []
        self.keyEvents: list[KeyEventPair] = []

    def setKeyEvents(self, keyEvents: list[KeyEventPair]) -> None:
        self.keyEvents = keyEvents

    def isListening(self) -> bool:
        return len(self.tasks) > 0

    def cleanUp(self) -> None:
        self.stopListening()
        self.loop.stop()
        self.loopThread.exit()

    def startListening(self, keyEvents: list[KeyEventPair]) -> None:
        if self.isListening():
            return
        self.setKeyEvents(keyEvents)
        self.devices = self._initDevices()
        for device in self.devices:
            task = asyncio.ensure_future(self._listenAsync(device))
            self.tasks.append(task)
        self.listeningChanged.emit()

    def stopListening(self) -> None:
        if not self.isListening():
            return
        for device in self.devices:
            device.close()
        self.devices.clear()
        for task in self.tasks:
            task.cancel()
        self.tasks.clear()
        self.listeningChanged.emit()

    def _supportsKeys(self, device: evdev.InputDevice) -> bool:
        caps = device.capabilities()
        keys = (k for k, _ in self.keyEvents)
        if supported := caps.get(EV_KEY):
            return all(ecodes.get(key) in supported for key in keys)
        return False

    def _initDevices(self) -> list[evdev.InputDevice]:
        result = []
        for p in os.listdir(EVDEV_PATH):
            if not p.startswith("event"):
                continue
            path = os.path.join(EVDEV_PATH, p)
            device = evdev.InputDevice(path)
            if self._supportsKeys(device):
                result.append(device)
        return result

    def _initLoop(self) -> tuple[QEventLoop, QThread]:
        thread = QThread(self)
        thread.start()
        loop = QEventLoop(thread)
        asyncio.set_event_loop(loop)
        return loop, thread

    async def _listenAsync(self, device: evdev.InputDevice) -> None:
        async for evdevEvent in device.async_read_loop():
            if evdevEvent.type != EV_KEY:
                continue
            keyEvent = evdev.KeyEvent(evdevEvent)
            key = keyEvent.keycode
            match keyEvent.keystate:
                case evdev.KeyEvent.key_down:
                    event = 'pressed'
                case evdev.KeyEvent.key_up:
                    event = 'released'
                case _:
                    event = None
            if (key, event) in self.keyEvents:
                self.keyCaptured.emit(keyEvent.keycode, event)

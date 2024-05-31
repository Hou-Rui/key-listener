import asyncio
import os

import evdev
from evdev.ecodes import ecodes
from PySide6.QtCore import Property, QObject, QThread, Signal, Slot
from PySide6.QtQml import QmlElement
from qasync import QEventLoop

QML_IMPORT_NAME = "keylistener.backend"
QML_IMPORT_MAJOR_VERSION = 1

EV_KEY = ecodes["EV_KEY"]
EVDEV_PATH = "/dev/input"


@QmlElement
class EventListener(QObject):
    keyPressed = Signal(str)
    keyReleased = Signal(str)
    listeningChanged = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.loop, self.loopThread = self.initLoop()
        self.devices: list[evdev.InputDevice] = []
        self.tasks: list[asyncio.Task] = []

    def supportsKeys(self, device: evdev.InputDevice,
                     keys: list[str]) -> bool:
        caps = device.capabilities()
        if supported := caps.get(EV_KEY):
            return all(ecodes.get(key) in supported for key in keys)
        return False

    def initDevices(self, supported: list[str]) -> list[evdev.InputDevice]:
        result = []
        for p in os.listdir(EVDEV_PATH):
            if not p.startswith("event"):
                continue
            path = os.path.join(EVDEV_PATH, p)
            device = evdev.InputDevice(path)
            if self.supportsKeys(device, supported):
                result.append(device)
        return result

    def initLoop(self) -> tuple[QEventLoop, QThread]:
        thread = QThread(self)
        thread.start()
        loop = QEventLoop(thread)
        asyncio.set_event_loop(loop)
        return loop, thread

    async def listenAsync(self, device: evdev.InputDevice,
                          keys: list[str]) -> None:
        async for event in device.async_read_loop():
            if event.type != EV_KEY:
                continue
            keyEvent = evdev.KeyEvent(event)
            if keyEvent.keycode not in keys:
                continue
            match keyEvent.keystate:
                case evdev.KeyEvent.key_down:
                    self.keyPressed.emit(keyEvent.keycode)
                case evdev.KeyEvent.key_up:
                    self.keyReleased.emit(keyEvent.keycode)

    @Property(bool, notify=listeningChanged)  # type: ignore
    def isListening(self) -> bool:
        return len(self.tasks) > 0

    @Slot()
    def cleanUp(self) -> None:
        self.stopListening()
        self.loop.stop()
        self.loopThread.exit()

    @Slot(list)
    def startListening(self, keys: list[str]) -> None:
        if self.isListening:
            return
        self.devices = self.initDevices(keys)
        for device in self.devices:
            task = asyncio.ensure_future(self.listenAsync(device, keys))
            self.tasks.append(task)
        self.listeningChanged.emit()

    @Slot()
    def stopListening(self) -> None:
        if not self.isListening:
            return
        for device in self.devices:
            device.close()
        self.devices.clear()
        for task in self.tasks:
            task.cancel()
        self.tasks.clear()
        self.listeningChanged.emit()

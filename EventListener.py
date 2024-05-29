import asyncio
import os

import evdev
from PySide6.QtCore import Property, QCoreApplication, QObject, Signal, Slot
from PySide6.QtQml import QmlElement
from PySide6.QtAsyncio import QAsyncioEventLoop
from qasync import QEventLoop

QML_IMPORT_NAME = "keylistener.backend"
QML_IMPORT_MAJOR_VERSION = 1

EV_KEY = evdev.ecodes.ecodes["EV_KEY"]
KEY_ENTER = evdev.ecodes.ecodes["KEY_ENTER"]
EVDEV_PATH = "/dev/input"


@QmlElement
class EventListener(QObject):
    keyPressed = Signal(str)
    keyReleased = Signal(str)
    runningChanged = Signal()

    def __init__(self):
        super().__init__()
        self.loop = self.initLoop()
        self.devices: list[evdev.InputDevice] = []
        self.tasks: list[asyncio.Task] = []

    def isDeviceKeyboard(self, device: evdev.InputDevice) -> bool:
        caps = device.capabilities()
        if keys := caps.get(EV_KEY):
            return KEY_ENTER in keys
        return False

    def initDevices(self) -> list[evdev.InputDevice]:
        result = []
        for p in os.listdir(EVDEV_PATH):
            if not p.startswith("event"):
                continue
            path = os.path.join(EVDEV_PATH, p)
            device = evdev.InputDevice(path)
            if self.isDeviceKeyboard(device):
                result.append(device)
        return result

    def initLoop(self) -> QEventLoop:
        if app := QCoreApplication.instance():
            loop = QEventLoop(app)
            asyncio.set_event_loop(loop)
            return loop
        raise RuntimeError("QCoreApplication no instance")

    async def listenAsync(self, device: evdev.InputDevice, keys: list[str]):
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

    @Property(bool, notify=runningChanged)  # type: ignore
    def isRunning(self) -> bool:
        return len(self.tasks) > 0

    @Slot(list)
    def start(self, keys: list[str]):
        if self.isRunning:
            return
        self.devices = self.initDevices()
        for device in self.devices:
            task = asyncio.ensure_future(self.listenAsync(device, keys))
            self.tasks.append(task)
        self.runningChanged.emit()

    @Slot()
    def stop(self):
        if not self.isRunning:
            return
        for device in self.devices:
            device.close()
        self.devices.clear()
        for task in self.tasks:
            task.cancel()
        self.tasks.clear()
        self.runningChanged.emit()

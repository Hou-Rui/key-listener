import os

import evdev
from PySide6.QtCore import Property, QObject, QThread, Signal, Slot
from PySide6.QtQml import QmlElement

QML_IMPORT_NAME = "keylistener.backend"
QML_IMPORT_MAJOR_VERSION = 1

EV_KEY = evdev.ecodes.ecodes["EV_KEY"]
KEY_ENTER = evdev.ecodes.ecodes["KEY_ENTER"]
EVDEV_PATH = "/dev/input"


class EventListenerWorker(QThread):
    class Signals(QObject):
        keyPressed = Signal(str)
        keyReleased = Signal(str)

    def __init__(self, device: evdev.InputDevice, keys: list[str],
                 parent: QObject | None = None):
        super().__init__(parent)
        self.signals = self.Signals()
        self.device = device
        self.keys = keys

    def run(self):
        for event in self.device.read_loop():
            if event.type != EV_KEY:
                continue
            keyEvent = evdev.KeyEvent(event)
            if keyEvent.keycode not in self.keys:
                continue
            match keyEvent.keystate:
                case evdev.KeyEvent.key_down:
                    self.signals.keyPressed.emit(keyEvent.keycode)
                case evdev.KeyEvent.key_up:
                    self.signals.keyReleased.emit(keyEvent.keycode)


@QmlElement
class EventListener(QObject):
    keyPressed = Signal(str)
    keyReleased = Signal(str)
    runningChanged = Signal()

    def __init__(self):
        super().__init__()
        self.devices = self.initDevices()
        self.workers: set[EventListenerWorker] = set()

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

    @Property(bool, notify=runningChanged)  # type: ignore
    def isRunning(self) -> bool:
        return len(self.workers) > 0

    @Slot(list)
    def start(self, keys: list[str]):
        for device in self.devices:
            worker = EventListenerWorker(device, keys)
            worker.signals.keyPressed.connect(self.keyPressed.emit)
            worker.signals.keyReleased.connect(self.keyReleased.emit)
            self.workers.add(worker)
            worker.start()
            self.runningChanged.emit()

    @Slot()
    def stop(self):
        for worker in self.workers:
            worker.terminate()
        self.workers.clear()
        self.runningChanged.emit()

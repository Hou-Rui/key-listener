#!/usr/bin/env python

import os
import signal
import sys
from pathlib import Path

from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from event_listener import EventListener
from preset_manager import PresetManager

assert PresetManager is not None
assert EventListener is not None


def main() -> None:
    app = QGuiApplication(sys.argv)
    app.setApplicationName("keylistener")
    app.setDesktopFileName(app.applicationName())
    app.setApplicationDisplayName(app.tr("Key Listener"))

    engine = QQmlApplicationEngine()

    signal.signal(signal.SIGINT, signal.SIG_DFL)

    if "QT_QUICK_CONTROLS_STYLE" not in os.environ:
        os.environ["QT_QUICK_CONTROLS_STYLE"] = "org.kde.desktop"

    engine.load(Path(__file__).parent / "qml" / "MainView.qml")

    if not engine.rootObjects():
        exit(-1)

    exit(app.exec())


if __name__ == "__main__":
    main()

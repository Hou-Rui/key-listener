#!/usr/bin/env python3

import os
import signal
import sys

from pathlib import Path

from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from backend import Backend


def main():
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()

    signal.signal(signal.SIGINT, signal.SIG_DFL)

    if not os.environ.get("QT_QUICK_CONTROLS_STYLE"):
        os.environ["QT_QUICK_CONTROLS_STYLE"] = "org.kde.desktop"

    engine.load(Path(__file__).parent / "main.qml")

    if not engine.rootObjects():
        exit(-1)

    app.exec()


if __name__ == "__main__":
    main()

import sys
from subprocess import Popen

import yaml
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent, QKeySequence
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget

from main_ui import Ui_MainWindow


class Preset:
    def __init__(self, path: str):
        self.path = path


class MainWindow(QMainWindow):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.preset = Preset("preset.yml")
        self.initWindow()

    def initWindow(self) -> None:
        self.ui.statusBar.showMessage("Waiting for key...")

    def keyPressEvent(self, event: QKeyEvent) -> None:
        key = event.key()
        keyText = QKeySequence(key).toString()
        self.ui.statusBar.showMessage(f"Event: {keyText}")
        match key:
            case Qt.Key.Key_Left:
                Popen(["adb", "shell", "input", "swipe", "960", "540", "800", "540", "200"])
            case Qt.Key.Key_Right:
                Popen(["adb", "shell", "input", "swipe", "800", "540", "960", "540", "200"])
            case Qt.Key.Key_Up:
                Popen(["adb", "shell", "input", "swipe", "960", "540", "960", "400", "200"])
            case Qt.Key.Key_Down:
                Popen(["adb", "shell", "input", "swipe", "960", "400", "960", "540", "200"])
        return super().keyPressEvent(event)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("KeyListener")
    app.setApplicationDisplayName("Key Listener")
    win = MainWindow()
    win.show()
    exit(app.exec())


if __name__ == "__main__":
    main()

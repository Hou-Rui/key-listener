import sys
from subprocess import Popen

import yaml
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent, QKeySequence
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget

from main_ui import Ui_MainWindow


class Preset:
    def __init__(self, name: str) -> None:
        self.name = name
        self.pressed: dict[str, str] = {}
        self.released: dict[str, str] = {}


class PresetManager:
    def __init__(self, path: str) -> None:
        self.path = path
        self.presets = self.initPresets()
        self.current = self.presets[0]

    def initPresets(self) -> list[Preset]:
        result: list[Preset] = []
        with open(self.path) as config_file:
            data = yaml.safe_load(config_file)
            for p in data:
                preset = Preset(name=p['name'])
                if 'pressed' in p:
                    for key, cmd in p['pressed'].items():
                        preset.pressed[key] = cmd
                result.append(preset)
        return result


class MainWindow(QMainWindow):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.presetManager = PresetManager("preset.yml")
        self.initWindow()

    def initWindow(self) -> None:
        self.ui.statusBar.showMessage("Waiting for key...")

    def keyPressEvent(self, event: QKeyEvent) -> None:
        key = event.key()
        keyText = QKeySequence(key).toString()
        cmd = self.presetManager.current.pressed[keyText]
        Popen(cmd.split(' '))
        self.ui.statusBar.showMessage(f"Event: {keyText}")
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

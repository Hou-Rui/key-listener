import sys

from PySide6.QtWidgets import QApplication

from window import MainWindow
from utils import PROJECT_CODE_NAME

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setDesktopFileName(PROJECT_CODE_NAME)
    win = MainWindow()
    win.show()
    exit(app.exec())

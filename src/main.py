import sys
from pathlib import Path

from PySide6.QtCore import QLocale, QTranslator
from PySide6.QtWidgets import QApplication

from utils import getCodeName, getDisplayName
from window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setDesktopFileName(getCodeName())
    app.setApplicationName(getCodeName())
    app.setApplicationDisplayName(getDisplayName())

    translator = QTranslator(app)
    i18n = Path(__file__).parent.parent / 'i18n'
    locale = QLocale.system().name()
    if not translator.load(locale, str(i18n)):
        print(f'Warning: no translation for "{locale}".', file=sys.stderr)
    app.installTranslator(translator)

    win = MainWindow()
    win.show()
    exit(app.exec())


if __name__ == '__main__':
    main()

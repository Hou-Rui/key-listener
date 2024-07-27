from PySide6.QtWidgets import QApplication


def getDisplayName() -> str:
    app = QApplication.instance()
    assert app is not None
    return app.tr('Key Listener')


def getCodeName() -> str:
    return 'keylistener'


def preferredRowHeight() -> int:
    return 30
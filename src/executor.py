from PySide6.QtCore import QObject, QProcess


class Executor(QObject):
    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._shell = ''
        self._process = QProcess(self)

    def setShell(self, shell: str) -> None:
        self._shell = shell

    def isRunning(self) -> bool:
        return self._process.state() == QProcess.ProcessState.Running

    def start(self, shell: str = '') -> None:
        if shell:
            self.setShell(shell)
        if not self.isRunning():
            self._process.startCommand(self._shell)
            self._process.waitForStarted()

    def run(self, cmd: str, useShell: bool = True) -> None:
        if useShell:
            self.start()
            raw = cmd.encode()
            if not raw.endswith(b'\n'):
                raw += b'\n'
            self._process.write(raw)
        else:
            temp = QProcess(self)
            temp.startCommand(f'sh -c "{cmd}"')
            temp.finished.connect(temp.deleteLater)

    def stop(self) -> None:
        if self.isRunning():
            self._process.terminate()
            self._process.waitForFinished()
            self._process.close()

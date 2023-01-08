from PyQt5.QtCore import pyqtSlot, QRunnable, QObject, pyqtSignal, QThreadPool
from control.Voice import VoiceSpeech


class WorkerSignals(QObject):
    finish = pyqtSignal()


class WorkerKilledException(Exception):
    pass


class Worker(QRunnable):
    def __init__(self, *, text: str, voice: VoiceSpeech):
        super().__init__()
        self.signals = WorkerSignals()
        self.voice = voice
        self.message = text

    @pyqtSlot()
    def run(self):
        print("Thread start")
        self.voice.text(self.message)
        print(f'Thread: {self.message}')
        self.signals.finish.emit()

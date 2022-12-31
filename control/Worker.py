from PyQt5 import uic, QtGui, QtCore
from PyQt5.QtCore import Qt, pyqtSlot, QRunnable, QThreadPool, QObject, pyqtSignal
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import QApplication, QPushButton, QDialog, QVBoxLayout, QHBoxLayout,  QLabel, QScrollArea, QWidget, QGroupBox, QFileDialog
from PyQt5.QtGui import QPixmap, QIcon, QImage, QIntValidator
from PyQt5 import QtWidgets, uic
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

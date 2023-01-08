from PyQt5.QtCore import Qt, pyqtSlot, QRunnable, QThreadPool, QObject, pyqtSignal, QUrl
from PyQt5.QtWidgets import QApplication, QPushButton, QDialog, QVBoxLayout, QHBoxLayout,  QLabel, QScrollArea, QWidget, QGroupBox, QFileDialog
from PyQt5.QtMultimedia import QSound, QMediaPlayer, QMediaContent, QSoundEffect
from PyQt5 import QtWidgets, uic
from control import VoiceSpeech
from control import MusicType
import os
import time

class WorkerSignals(QObject):
    finish = pyqtSignal()


class WorkerKilledException(Exception):
    pass


class WorkerMusic(QRunnable):
    def __init__(self, *, music_type: MusicType):
        super().__init__()
        self.signals = WorkerSignals()
        self.music_type = music_type

    @pyqtSlot()
    def run(self):
        print("Thread start")
        self.play_music()
        self.signals.finish.emit()

    def play_music(self):
        path = os.path.join(os.getcwd(), 'music', self.music_type.value)
        print(f'Path = {path}')
        player = QMediaPlayer()
        player.setMedia(QMediaContent(QUrl.fromLocalFile(path)))
        player.setVolume(50)
        player.play()
        time.sleep(2)

from PyQt5 import QtCore, QtWidgets

"""
class NeuLabel(QtWidgets.QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
    def mousePressEvent(self, e):
        super().mousePressEvent(e)
        if e.button() == QtCore.Qt.LeftButton:
            print("press")
"""


class ImageLabel(QtWidgets.QLabel):
    clicked = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)

    def mousePressEvent(self, ev):
        super().mousePressEvent(ev)
        print('Image clicked')
        self.clicked.emit()

from PyQt5 import QtCore
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt, QVariant


class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data

    def data(self, index, role):
        # if role == Qt.DisplayRole:
        #     value = self._data.iloc[index.row(), index.column()]
        #     return str(value)

        row = index.row()
        column = index.column()

        if role == Qt.DisplayRole:
            value = self._data.iloc[index.row(), index.column()]
            return str(value)

        if role == Qt.BackgroundColorRole:
            if row % 2:
                bgColor = QColor(Qt.white)
            else:
                bgColor = QColor(Qt.gray)
            return QVariant(QColor(bgColor))

    def rowCount(self, index):
        return self._data.shape[0]

    def columnCount(self, index):
        return self._data.shape[1]

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._data.columns[section])
        if orientation == Qt.Vertical:
            return str(self._data.index[section])

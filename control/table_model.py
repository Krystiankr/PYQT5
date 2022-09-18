from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt, QVariant


class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, data: 'dataframe' = '', df_type: str = ''):
        super().__init__()
        self._data = data
        self.df_type = df_type

    def data(self, index, role):
        row = index.row()
        column = index.column()

        if role == Qt.DisplayRole:
            value = self._data.iloc[index.row(), index.column()]
            return str(value)

        if role == Qt.BackgroundColorRole:
            bgColor = QColor(255, 255, 255)
            if row % 2:
                bgColor = QColor(Qt.white)
                if self.df_type == 'green':
                    bgColor = QColor(119, 150, 109)
                if self.df_type == 'red':
                    bgColor = QColor(53, 13, 17)
            else:
                bgColor = QColor(206, 206, 206)
                if self.df_type == 'green':
                    bgColor = QColor(188, 235, 203)
                if self.df_type == 'red':
                    bgColor = QColor(106, 57, 55)
            return QVariant(QColor(bgColor))

        if role == Qt.TextColorRole:
            bgColor = QColor(0, 0, 0)
            if self.df_type == 'green':
                bgColor = QColor(0, 0, 0)
            if self.df_type == 'red':
                bgColor = QColor(255, 255, 255)
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

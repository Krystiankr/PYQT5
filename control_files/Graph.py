import sys

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QLabel, QPushButton

import matplotlib
import pandas as pd
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import matplotlib.pyplot as plt
import matplotlib

matplotlib.use("Qt5Agg")

class Graph(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.df = pd.DataFrame({"A": [0]})

        self.canvas = FigureCanvasQTAgg(plt.Figure(figsize=(7, 7), facecolor='grey'))

        self.increase = QPushButton("increase")
        self.decrease = QPushButton("decrease")
        self.increase.clicked.connect(lambda: self.add_item(1))
        self.decrease.clicked.connect(lambda: self.add_item(-1))

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.addWidget(self.increase, alignment=QtCore.Qt.AlignLeft)
        layout.addWidget(self.decrease, alignment=QtCore.Qt.AlignLeft)

        self.value = 0
        self.ax = self.canvas.figure.subplots()
        self.bar = None

        widget = QWidget()
        widget.setLayout(layout)

        self.ax.set_title("Statistic progress", fontsize=20, color='azure')
        self.ax.set_xlabel('number of solved words', fontsize=20, color='gold')
        self.ax.set_ylabel('difference correctly/badly', fontsize=20, color='gold')
        self.ax.set_facecolor('powderblue')

        self.setCentralWidget(widget)
        self.show()

    def add_item(self, val):
        max = self.df.index.max() + 1
        self.value += val

        self.ax.set_xlim([max-10, max+2])
        self.ax.set_ylim([self.value-6, self.value+6])

        self.df.loc[max] = [self.value]
        print(self.df)

        if val == 1:
            color = 'limegreen'
        else:
            color = 'firebrick'

        if self.bar:
            del self.bar
        self.bar = self.ax.plot("A", data=self.df, color=color)
        plt.tight_layout()
        self.canvas.draw()

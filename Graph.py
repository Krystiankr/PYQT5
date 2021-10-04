from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtGui import QPixmap

from datetime import datetime
import pandas as pd
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import matplotlib.pyplot as plt
import matplotlib

matplotlib.use("Qt5Agg")


class Graph(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.df = pd.DataFrame({"A": [0]})

        self.canvas = FigureCanvasQTAgg(plt.Figure(figsize=(3, 3),
                                                   facecolor=(240/255, 240/255, 240/255),
                                                   tight_layout=True))

        self.increase = QPushButton("increase")
        self.decrease = QPushButton("decrease")
        self.increase.clicked.connect(lambda: self.add_item(1))
        self.decrease.clicked.connect(lambda: self.add_item(-1))

        self.value = 0
        self.ax = self.canvas.figure.subplots()
        self.bar = None
        self.last = 0
        self.last2 = 0

        fontsize = 10
        color = 'steelblue'

        self.ax.set_title("Statistic progress", fontsize=fontsize+5, color='navy')
        self.ax.set_xlabel('number of solved words', fontsize=fontsize, color=color)
        self.ax.set_ylabel('difference correctly/badly', fontsize=fontsize, color=color)
        self.ax.set_facecolor('aliceblue')

    def return_canvas(self):
        return self.canvas

    def add_item(self, val):
        max_value = self.df.index.max() + 1
        self.value += val

      #  if val == -1:
      #      self.last = max_value - 10
      #      self.last2 = self.value - 6
      #      self.ax.set_xlim([max_value - 10, max_value + 2])
      #      self.ax.set_ylim([self.value - 6, self.value + 6])
     #   else:
      #      self.ax.set_xlim([self.last, max_value + 2])
      #      self.ax.set_ylim([self.last2, self.value + 6])
      #     self.last -= 0.3
        self.ax.set_xlim([0, max_value + 2])
     #   self.ax.set_ylim([0, self.value + 6])

        self.df.loc[max_value] = [self.value]
        print(self.df)
        if self.bar:
            del self.bar
        self.bar = self.ax.plot("A", data=self.df)

        fig = plt.gcf()
        # fig.savefig('output.png')
        fig.savefig(f'42.png', format='png')

        plt.tight_layout()

        self.canvas.draw()

    # def save_fige(self):
    #     now = datetime.now()
    #     now = now.strftime("%d-%m-%Y_%H-%M-%S")
    #     print(now)
    #     fig = plt.gcf()
    #    # fig.savefig('output.png')
    #     fig.savefig(f'42.png', format='png')
    #


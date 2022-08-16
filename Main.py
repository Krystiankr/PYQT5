
from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtCore import Qt, pyqtSlot
from interface.table_view import TableModel
import sys
import pandas as pd
import json
from control.json_operations import set_dimension, get_dimension, set_current_page, get_last_page

main_dialog = uic.loadUiType("interface/main.ui")[0]

# self.tableView.setModel(TableModel(df))


class MyWindowClass(QtWidgets.QMainWindow, main_dialog):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        ############ CONFIGURATIONS ############
        self.setupUi(self)
        # Action setup
        self.actionDisplay_words.triggered.connect(lambda:
                                                   self.stackedWidget.setCurrentWidget(self.DisplayPage))
        self.actionMain.triggered.connect(lambda:
                                          self.stackedWidget.setCurrentWidget(self.MainPage))
        self.actionMigrate_Words.triggered.connect(lambda:
                                                   self.stackedWidget.setCurrentWidget(self.MigratePage))

        self.actionStatystyki.triggered.connect(lambda:
                                                self.stackedWidget.setCurrentWidget(self.StatsPage))
        self.actionSave_cords.triggered.connect(self.save_dimensions)
        self.actionLoad_cords.triggered.connect(self.load_dimensions)
        self.actionOptions.triggered.connect(
            lambda: self.grpMenu.setVisible(self.actionOptions.isChecked()))
        self.actionSave_last_page.triggered.connect(self.set_last_page_index)
        # DataFrame setup
        self.df = pd.read_csv('control/Data.csv')
        self.tableView.setModel(TableModel(self.df))

        # Another
        self.load_dimensions()
        self.load_last_page_index()

    def current_page_index(self) -> int:
        return self.stackedWidget.currentIndex()

    def save_last_page(self):
        pages = [self.MainPage, self.DisplayPage,
                 self.StatsPage, self.MigratePage]
        lista_a = dict(map(lambda x, y: (x, y), range(4), [11, 22, 33, 44]))
        print(lista_a)

    def load_last_page_index(self) -> None:
        pages = ["MainPage", "DisplayPage",
                 "StatsPage", "MigratePage"]
        index = get_last_page()
        self.stackedWidget.setCurrentIndex(index)
        self.statusbar.showMessage(f"Loaded Last page: {pages[index]}")

    def set_last_page_index(self) -> int:
        pages = ["MainPage", "DisplayPage",
                 "StatsPage", "MigratePage"]
        index = self.current_page_index()
        set_current_page(index)
        self.statusbar.showMessage(f"Saved Last page: {pages[index]}")

    def load_dimensions(self):
        wymiary = get_dimension()
        self.statusbar.showMessage(f"Load dimensions from file: {wymiary}")
        self.setGeometry(QtCore.QRect(*wymiary))
        print(wymiary)

    def save_dimensions(self):
        wymiary = self.frameGeometry().getCoords()
        self.statusbar.showMessage(f"Save dimensions to file: {wymiary}")
        set_dimension(*wymiary)
        # self.setGeometry(QtCore.QRect(*wymiary))
        print("Wymiary")
        print(wymiary)

    # Btn configurations

    @pyqtSlot()
    def on_btnMain_clicked(self):
        self.stackedWidget.setCurrentWidget(self.MainPage)

    @pyqtSlot()
    def on_btnDisplay_clicked(self):
        self.stackedWidget.setCurrentWidget(self.DisplayPage)

    @pyqtSlot()
    def on_btnMigrate_clicked(self):
        self.stackedWidget.setCurrentWidget(self.MigratePage)

    @pyqtSlot()
    def on_btnStats_clicked(self):
        self.stackedWidget.setCurrentWidget(self.StatsPage)

    @pyqtSlot()
    def on_btnLoadJson_clicked(self):
        print("Load JSON!")
        try:
            parsed = json.loads(self.txtJSON.toPlainText())
            df = pd.DataFrame.from_dict(
                dict(parsed), orient='index').reset_index()
            df.columns = ['English', 'Polish']
            df['Exists'] = False
            self.tableView_2.setModel(TableModel(df))
            print(self.txtJSON.toPlainText())
        except Exception:
            self.statusbar.showMessage("Error with parsing data")


def main():
    app = QtWidgets.QApplication(sys.argv)
    myWindow = MyWindowClass()
    myWindow.show()
    app.exec_()


if __name__ == "__main__":
    main()

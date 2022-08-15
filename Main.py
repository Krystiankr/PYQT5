
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import Qt, pyqtSlot
from interface.table_view import TableModel
import sys
import pandas as pd
import json

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

        # DataFrame setup
        self.df = pd.read_csv('control/Data.csv')
        self.tableView.setModel(TableModel(self.df))

        # Another
        self.actionOptions.triggered.connect(
            lambda: self.grpMenu.setVisible(self.actionOptions.isChecked()))

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
        self.stackedWidget.setCurrentWidget(self.MainPage)

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


from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtCore import Qt, pyqtSlot
from interface.table_view import TableModel
import sys
import json
import pandas as pd
from datetime import datetime
from control.json_operations import set_dimension, get_dimension, set_current_page, get_last_page
from control.pd_operations import return_df, transform_df

main_dialog = uic.loadUiType("interface/main.ui")[0]


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
        # Set up words buttons
        self.buttons = [self.btnWord1, self.btnWord2,
                        self.btnWord3]
        for index, btn in enumerate(self.buttons):
            btn.clicked.connect(self.btn_random_word)
            btn.setObjectName(str(index))

        # Btn
        #self.btnStart.clicked.connect(lambda: print("Start btn"))

        # Input
        self.txtDisplaySearch.textChanged.connect(
            self.txt_search_input_changed)
        # DataFrame setup
        self.df = return_df('control/Data.csv')
        self.set_table_model(self.df)

        # Another
        self.load_dimensions()
        self.load_last_page_index()

    # SETTINGS
    def set_table_model(self, _df: pd.DataFrame):
        self.tableView.setModel(TableModel(_df))

    def refresh_df(self, text: str):
        tmp_df = transform_df(self.df, text)
        self.set_table_model(tmp_df)

    def txt_search_input_changed(self):
        self.refresh_df(self.txtDisplaySearch.text())
        print(self.txtDisplaySearch.text())

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

    # Random words key pressed
    def keyPressEvent(self, e):
        if e.key() == Qt.Key_1:
            self.buttons[0].click()
        if e.key() == Qt.Key_2:
            self.buttons[1].click()
        if e.key() == Qt.Key_3:
            self.buttons[2].click()

    # Btn configurations
    def btn_random_word(self):
        obj = self.sender().objectName()
        value = self.progressBar.value() + 10
        self.progressBar.setValue(value)
        if value == 100:
            self.result_setup()
        print(f'value: {value}')
        print(obj)

    def result_setup(self):
        self.stackedWidget.setCurrentWidget(self.StatsPage)
        self.lblResult.setText(f"{self.correct_words},\n {self.bad_words}")
        result_time = int((datetime.today() - self.start_time).total_seconds())
        self.btnTimerResult.setText(f'Competition took {result_time} seconds')

    @pyqtSlot()
    def on_btnStart_clicked(self):
        # set scores
        self.correct_words = [f'good{i}' for i in range(10)]
        self.bad_words = [f'bad{i}' for i in range(10)]
        self.start_time = datetime.today()
        self.btnStart.setEnabled(False)
        self.btnStart.setStyleSheet(
            "QPushButton""{""background-color : rgb(209,245,255);color:rgb(0,0,0)""}")
        print("start")

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

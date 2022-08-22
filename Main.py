
from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtCore import Qt, pyqtSlot
from interface.table_view import TableModel
import sys
import json
import pandas as pd
import random
from datetime import datetime
from control.json_operations import set_dimension, get_dimension, set_current_page, get_last_page
from control.pd_operations import return_df, transform_df
from control.data_operations import DataOperations

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

        ####
        self.data = DataOperations()
        # Btn
        #self.btnStart.clicked.connect(lambda: print("Start btn"))

        # Input
        self.txtDisplaySearch.textChanged.connect(
            self.txt_search_input_changed)
        # DataFrame setup
        self.set_table_model(self.data.get_df())
        # self.lblNumerWords.setText(
        #     f'Number of words: {self.data.get_num_all_words()}')
        self.set_len_df_lbl(self.data.get_num_all_words())
        # Another
        self.load_dimensions()
        self.load_last_page_index()

    # SETTINGS
    def set_len_df_lbl(self, number_of_words: int) -> None:
        self.lblNumerWords.setText(
            f'Number of words: {number_of_words}')

    def set_table_model(self, _df: pd.DataFrame):
        self.tableView.setModel(TableModel(_df))

    def refresh_df(self, text: str):
        tmp_df = transform_df(self.data.get_df(), text)
        self.set_table_model(tmp_df)
        return tmp_df

    def txt_search_input_changed(self):
        tmp_df = self.refresh_df(self.txtDisplaySearch.text())
        self.set_len_df_lbl(DataOperations.get_numm_words_from_tmp_df(tmp_df))
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
            self.set_start_btn(mode='end')
            self.progressBar.setValue(0)
        print(f'value: {value}')
        print(obj)

    def set_start_btn(self, mode: str = ''):
        color = "rgb(0,123,255)" if mode == 'end' else "rgb(209,245,255)"
        text = "Start" if mode == 'end' else "In game..."
        print(f"Change to: {mode} color: {color}")
        self.btnStart.setStyleSheet(
            "QPushButton""{""background-color:"+color+";color:rgb(0,0,0)""}")
        self.btnStart.setText(text)
        self.btnStart.setEnabled(mode == 'end')

    def result_setup(self):
        self.stackedWidget.setCurrentWidget(self.StatsPage)
        self.lblResult.setText(f"{self.correct_words},\n {self.bad_words}")
        result_time = int((datetime.today() - self.start_time).total_seconds())
        self.btnTimerResult.setText(f'Competition took {result_time} seconds')

    def set_status_message(self, mess: str) -> None:
        self.statusbar.showMessage(mess)

    def refresh_display_page(self):
        self.refresh_df(self.txtDisplaySearch.text())
        self.set_len_df_lbl(
            self.data.get_num_all_words())

    # Buttons setup
    @pyqtSlot()
    def on_btnAddWord_clicked(self):
        english_word, polish_word = self.txtEnglishWord.text(
        ), self.txtPolishWord.text()
        mess = self.data.add_new_word(english_word=english_word,
                                      polish_word=polish_word)
        if mess.startswith('Added new word'):
            self.refresh_display_page()
        self.set_status_message(mess)
        #print(f'add word clicked! {english_word} {polish_word}')

    @pyqtSlot()
    def on_btnRandom_clicked(self):
        winning_word = self.data.sample_row()
        english_word = self.data.get_english_word(winning_word)
        polish_word = self.data.get_polish_word(winning_word)
        random_word_1, random_word_2 = self.data.get_sample_polish(
        ), self.data.get_sample_polish()
        buttons = self.buttons.copy()
        self.lblMainWord.setText(english_word)
        random.shuffle(buttons)
        for word, btn in zip([polish_word, random_word_1, random_word_2], buttons):
            btn.setText(word)

    @pyqtSlot()
    def on_btnStart_clicked(self):
        # set scores
        self.correct_words = [f'good{i}' for i in range(10)]
        self.bad_words = [f'bad{i}' for i in range(10)]
        self.start_time = datetime.today()
        self.set_start_btn(mode='start')
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

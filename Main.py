
from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtCore import Qt, pyqtSlot
from interface.table_view import TableModel
import sys
import json
import pandas as pd
import random
from datetime import datetime
from control.json_operations import *
from control.pd_operations import return_df, transform_df
from control.data_operations import DataOperations
from control.toggle import AnimatedToggle
from control.Worker import *
from PyQt5.QtCore import QProcess

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
        self.buttons_disable_all()

        ####
        self.data = DataOperations()
        # Btn
        #self.btnStart.clicked.connect(lambda: print("Start btn"))
        self.speaker = True
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
        # Word configurations
        self.tournament_dict = {"corrects": [], "bads": []}

        # Toggle setup
        self.toggle_settings = AnimatedToggle(
            checked_color="#FFB000",
            pulse_checked_color="#44FFB000"
        )
        self.toggle_settings.clicked.connect(
            lambda: self.toggle_settings_func(self.toggle_settings.isChecked()))
        self.verSettings.addWidget(self.toggle_settings)

        self.load_settings()
        self.thredapool = QThreadPool()
        self.voice = VoiceSpeech()
        self.lblSpeaker.clicked.connect(self.speaker_on)

    def toggle_settings_func(self, value):
        set_json_value(name='settings_page', name2='speaker', value=value)

    # SETTINGS
    def load_settings(self):
        self.toggle_settings.setChecked(
            get_json_value('settings_page')['speaker'])

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

    def random_word(self):
        self.winning_row = self.data.sample_row()
        english_word = self.data.get_english_word(self.winning_row)
        polish_word = self.data.get_polish_word(self.winning_row)
        random_word_1, random_word_2 = self.data.get_sample_polish(
        ), self.data.get_sample_polish()
        buttons = self.buttons.copy()
        self.lblMainWord.setText(english_word)
        random.shuffle(buttons)
        for word, btn in zip([polish_word, random_word_1, random_word_2], buttons):
            btn.setText(word)

    def worker_result(self):
        print('Finish project')
        self.speaker = True

    # Random words key pressed
    def keyPressEvent(self, e):
        if e.key() == Qt.Key_1:
            self.buttons[0].click()
        if e.key() == Qt.Key_2:
            self.buttons[1].click()
        if e.key() == Qt.Key_3:
            self.buttons[2].click()
        if e.key() == Qt.Key_R:
            print("random word")
            self.button_default_stylesheet()
            self.random_word()
            
            self.speaker_on()

    def speaker_on(self):
        text = DataOperations.get_english_word(
                self.winning_row)
        if self.speaker:
                self.worker = Worker(text=text, voice=self.voice)
                self.speaker = False
                self.worker.signals.finish.connect(self.worker_result)
                self.thredapool.start(self.worker)

    def button_default_stylesheet(self):
        for btn in self.buttons:
            btn.setEnabled(True)
            btn.setStyleSheet(
                "QPushButton""{""background-color : rgb(0, 123, 255);""}")

    def buttons_disable_all(self):
        for btn in self.buttons:
            btn.setEnabled(False)
            # btn.setStyleSheet(
            #     "QPushButton""{""background-color : rgb(66, 189, 255);""}")

    # Btn configurations
    def btn_random_word(self):
        # background-color: rgb(66, 189, 255);
        obj = self.sender().objectName()
        self.buttons[int(obj)].setStyleSheet(
            "QPushButton""{""background-color: rgb(66, 189, 255); color : white;""}")
        self.buttons[int(obj)].setEnabled(False)

        print(f'Button: {self.buttons[int(obj)].text()}')
        if str(self.buttons[int(obj)].text()) in str(self.winning_row["Polski"]):
            self.buttons_disable_all()
            self.buttons[int(obj)].setStyleSheet(
                "QPushButton""{""background-color: rgb(40, 179, 90); color : white;""}")
            self.tournament_dict['corrects'].append(
                str(self.buttons[int(obj)].text()))

        else:
            self.tournament_dict['bads'].append(
                str(self.buttons[int(obj)].text()))
            self.buttons[int(obj)].setStyleSheet(
                "QPushButton""{""background-color: rgb(220, 237, 255); color : black;""}")
        self.buttons[int(obj)].setEnabled(False)

        print(f'Winning: {self.winning_row["Polski"]}')
        value = self.progressBar.value() + 10
        self.progressBar.setValue(value)
        if value == 100:
            self.result_setup()
            self.set_start_btn(mode='end')
            self.progressBar.setValue(0)
            print(self.tournament_dict)
        print(f'value: {value}')
        print(obj)

    def set_start_btn(self, mode: str = ''):
        color = "rgb(0,123,255)" if mode == 'end' else "rgb(209,245,255)"
        text = "Start" if mode == 'end' else "In game..."
        print(f"Change to: {mode} color: {color}")
        self.btnStart.setStyleSheet(
            "QPushButton""{""background-color:"+color+";color:rgb(255,255,255)""}")
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
    def on_btnTest_clicked(self):
        self.toggle_settings.setChecked(True)
        print(f"Btn test ")

    @pyqtSlot()
    def on_btnAddWords_clicked(self):
        for index, row in self.json_df.iterrows():
            self.data.add_new_word(english_word=row.English,
                                   polish_word=row.Polish)
        self.refresh_display_page()
        self.stackedWidget.setCurrentWidget(self.DisplayPage)
        self.set_status_message(f'Added {len(self.json_df)} words.')

    @pyqtSlot()
    def on_btnAddWord_clicked(self):
        english_word, polish_word = self.txtEnglishWord.text(
        ), self.txtPolishWord.text()
        if english_word == '' or polish_word == '':
            self.set_status_message('New words can\'t be empty!')
        else:
            mess = self.data.add_new_word(english_word=english_word,
                                          polish_word=polish_word)
            if mess.startswith('Added new word'):
                self.refresh_display_page()
            self.stackedWidget.setCurrentWidget(self.DisplayPage)
            self.set_status_message(mess)
        #print(f'add word clicked! {english_word} {polish_word}')

    @pyqtSlot()
    def on_btnRandom_clicked(self):
        self.random_word()

    @pyqtSlot()
    def on_btnStart_clicked(self):
        # set scores
        self.correct_words = [f'good{i}' for i in range(10)]
        self.bad_words = [f'bad{i}' for i in range(10)]
        self.start_time = datetime.today()
        self.set_start_btn(mode='start')
        print("start")

    @pyqtSlot()
    def on_btnSettings_clicked(self):
        self.stackedWidget.setCurrentWidget(self.SettingsPage)

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
            self.json_df = pd.DataFrame.from_dict(
                dict(parsed), orient='index').reset_index()
            self.json_df.columns = ['English', 'Polish']
            self.json_df['Exists'] = False
            self.tableView_2.setModel(TableModel(self.json_df))
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

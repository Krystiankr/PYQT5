
import enum
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
from control.table_model import TableModel
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
        # Set up checkbox
        self.checkboxs = [self.cbxAngielski, self.cbxPolski,
                          self.cbxFrequency, self.cbxBadlyAnswer, self.cbxPerfectScore]
        for index, cbx in enumerate(self.checkboxs):
            cbx.setObjectName(str(index))
            cbx.clicked.connect(self.checkbox_display)
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
        self.speaker = get_json_value('settings_page')['speaker']
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
        self.winning_status = True
        self.is_game = False

        # Toggle setup
        self.toggle_settings = AnimatedToggle(
            checked_color="#FFB000",
            pulse_checked_color="#44FFB000"
        )
        self.toggle_settings.clicked.connect(
            lambda: self.toggle_settings_func(self.toggle_settings.isChecked()))
        self.verSettings.addWidget(self.toggle_settings)

        self.load_settings()
        self.setup_checkbox_display()
        self.thredapool = QThreadPool()
        self.voice = VoiceSpeech()
        self.lblSpeaker.clicked.connect(self.speaker_on)

    def checkbox_display(self):
        obj_index = int(self.sender().objectName())
        bool_value = self.checkboxs[obj_index].isChecked()
        set_display_value(index=obj_index, bool_value=bool_value)
        print(f'obj clicked: {obj_index} = {bool_value}')

    def toggle_settings_func(self, value):
        set_json_value(name='settings_page', name2='speaker', value=value)
        self.speaker = get_json_value('settings_page')['speaker']
        self.set_status_message(f'Change speaker status: {self.speaker}')

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

    def set_status_message(self, text: str) -> None:
        self.statusbar.showMessage(text)

    def load_last_page_index(self) -> None:
        pages = ["MainPage", "DisplayPage",
                 "StatsPage", "MigratePage"]
        index = get_last_page()
        self.stackedWidget.setCurrentIndex(index)
        self.set_status_message(f"Loaded Last page: {pages[index]}")

    def set_last_page_index(self) -> int:
        pages = ["MainPage", "DisplayPage",
                 "StatsPage", "MigratePage"]
        index = self.current_page_index()
        set_current_page(index)
        self.set_status_message(f"Saved Last page: {pages[index]}")

    def load_dimensions(self):
        wymiary = get_dimension()
        self.set_status_message(f"Load dimensions from file: {wymiary}")
        self.setGeometry(QtCore.QRect(*wymiary))
        print(wymiary)

    def save_dimensions(self):
        wymiary = self.frameGeometry().getCoords()
        self.set_status_message(f"Save dimensions to file: {wymiary}")
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
        self.speaker_on()

    def worker_result(self):
        print('Finish project')
        self.speaker = True
        self.pix_map(label=self.lblSpeaker,
                     file_path='icons/Speaker_black.svg')

    # Random words key pressed
    def keyPressEvent(self, e):
        if e.key() == Qt.Key_1:
            self.buttons[0].click()
        if e.key() == Qt.Key_2:
            self.buttons[1].click()
        if e.key() == Qt.Key_3:
            self.buttons[2].click()
        if e.key() == Qt.Key_S:
            self.start_game()
            self.button_default_stylesheet()
        if e.key() == Qt.Key_R:
            print("random word")
            if not self.is_game:
                self.set_status_message(f'First start the game!')
                return
            if self.winning_status:
                self.button_default_stylesheet()
                self.random_word()
                self.winning_status = False
            else:
                self.set_status_message(f'Answer the current question first')

    def setup_checkbox_display(self) -> None:
        for index, cbx in enumerate(self.checkboxs):
            cbx.setChecked(get_display_value(index))

    def speaker_on(self):
        text = DataOperations.get_english_word(
            self.winning_row)
        if self.speaker:
            self.pix_map(label=self.lblSpeaker,
                         file_path='icons/Speaker_gray.svg')
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
            self.winning_status = True
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
            self.lblResult.setText(
                f"Corrects: {len(self.tournament_dict['corrects'])}, Bads: {len(self.tournament_dict['bads'])}")
            df_corrects = pd.DataFrame.from_dict(
                self.tournament_dict['corrects'])
            df_bads = pd.DataFrame.from_dict(self.tournament_dict['bads'])
            df_corrects.columns, df_bads.columns = ['Polski'], ['Polski']
            df_corrects['English'] = df_corrects.Polski.apply(
                lambda x: self.data.get_translation_from_pl(polish_word=x))
            df_bads['English'] = df_bads.Polski.apply(
                lambda x: self.data.get_translation_from_pl(polish_word=x))
            self.tabCorrects.setModel(TableModel(df_corrects, df_type='green'))
            self.tabBads.setModel(TableModel(df_bads, df_type='red'))
            # self.tabBads.horizontalHeader().setMinimumSectionSize(2200)
            self.tabCorrects.horizontalHeader().setSectionResizeMode(
                0, QtWidgets.QHeaderView.Stretch)
            self.tabBads.horizontalHeader().setSectionResizeMode(
                0, QtWidgets.QHeaderView.Stretch)

        print(f'value: {value}')
        print(obj)

    def start_game(self):
        self.start_time = datetime.today()
        self.button_default_stylesheet()
        self.set_start_btn(mode='start')
        print("start")

    def set_start_btn(self, mode: str = ''):
        color = "rgb(0,123,255)" if mode == 'end' else "rgb(209,245,255)"
        text = "Start" if mode == 'end' else "In game..."
        print(f"Change to: {mode} color: {color}")
        self.btnStart.setStyleSheet(
            "QPushButton""{""background-color:"+color+";color:rgb(255,255,255)""}")
        self.btnStart.setText(text)
        self.btnStart.setEnabled(mode == 'end')
        self.is_game = True
        self.random_word()

    def pix_map(self, *, label, file_path: str):
        pixmap = QPixmap(file_path)
        label.setPixmap(pixmap)
        label.setScaledContents(True)

    def result_setup(self):
        self.stackedWidget.setCurrentWidget(self.StatsPage)
        result_time = int((datetime.today() - self.start_time).total_seconds())
        self.btnTimerResult.setText(f'Competition took {result_time} seconds')

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
        self.button_default_stylesheet()
        self.start_game()

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
            self.set_status_message("Error with parsing data")


def main():
    app = QtWidgets.QApplication(sys.argv)
    myWindow = MyWindowClass()
    myWindow.show()
    app.exec_()


if __name__ == "__main__":
    main()


"""
{
  "dimensions": {
    "x": 818,
    "y": 555,
    "width": 810,
    "height": 916
  },
  "last_page_index": 0,
  "settings_page": {
    "speaker": false
  },
  "display_columns_configurations": {
    "Angielski": true,
    "Polski": true,
    "Frequency": false,
    "BadlyAnswer": false,
    "PerfectScore": false
  }
}
"""

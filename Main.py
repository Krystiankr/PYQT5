import sys
import json
import pandas as pd
import random
import re
import time
from datetime import datetime

from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import QTableWidgetItem, QPushButton

from interface.table_view import TableModel
from control import *
from operations import get_translation_from
from view.popup import PopUp


main_dialog = uic.loadUiType("interface/main.ui")[0]


class MyWindowClass(QtWidgets.QMainWindow, main_dialog):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        ############ CONFIGURATIONS ############
        self.setupUi(self)
        # Action setup
        self.actionDisplay_words.triggered.connect(
            lambda: self.interface_pages_redirecting("DisplayPage")
        )
        self.actionMain.triggered.connect(
            lambda: self.interface_pages_redirecting("MainPage")
        )
        self.actionMigrate_Words.triggered.connect(
            lambda: self.interface_pages_redirecting("MigratePage")
        )

        self.actionStatystyki.triggered.connect(
            lambda: self.interface_pages_redirecting("StatsPage")
        )
        self.actionInformation_page.triggered.connect(
            lambda: self.interface_pages_redirecting("InformationPage")
        )
        self.actionSave_cords.triggered.connect(self.save_dimensions)
        self.actionLoad_cords.triggered.connect(self.load_dimensions)
        self.actionOptions.triggered.connect(
            lambda: self.grpMenu.setVisible(self.actionOptions.isChecked())
        )
        self.actionSave_last_page.triggered.connect(self.set_last_page_index)
        # Settings
        self.spnQLabel.valueChanged.connect(lambda x: self.spin_font(x))

        # Set up checkbox
        self.checkboxs = [
            self.cbxAngielski,
            self.cbxPolski,
            self.cbxFrequency,
            self.cbxBadlyAnswer,
            self.cbxPerfectScore,
        ]
        for index, cbx in enumerate(self.checkboxs):
            cbx.setObjectName(str(index))
            cbx.clicked.connect(self.checkbox_display)
        # Set up words buttons
        self.buttons = [self.btnWord1, self.btnWord2, self.btnWord3]
        for index, btn in enumerate(self.buttons):
            btn.clicked.connect(self.btn_random_word)
            btn.setObjectName(str(index))
        self.buttons_disable_all()

        ####
        self.data = DataOperations()
        # Btn
        # self.btnStart.clicked.connect(lambda: print("Start btn"))
        self.speaker = get_json_value("settings_page")["speaker"]
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
        self.winning_row = "easy"
        self.is_game = False

        # Toggle setup
        self.toggle_settings = AnimatedToggle(
            checked_color="#FFB000", pulse_checked_color="#44FFB000"
        )
        self.toggle_settings.clicked.connect(
            lambda: self.toggle_settings_func(self.toggle_settings.isChecked())
        )
        self.verSettings.addWidget(self.toggle_settings)

        self.load_settings()
        self.setup_checkbox_display()
        self.thredapool = QThreadPool()
        self.voice = VoiceSpeech()
        self.lblSpeaker.clicked.connect(self.speaker_on)
        self.lblRequest.clicked.connect(
            lambda: self.make_request(self.txtDisplaySearch.text())
        )
        self.lblAddFromRequest.clicked.connect(self.add_new_word)
        self.lblPronunciation.clicked.connect(
            lambda: self.speaker_on(page="display_words")
        )

    def add_new_word(self):
        english_word = self.lblMainWord_2.text()
        polish_word = self.lblTranslation.text()
        if english_word == "" or polish_word == "":
            self.set_status_message("New words can't be empty!")
        else:
            mess = self.data.add_new_word(
                english_word=english_word, polish_word=polish_word
            )
            if 'new word' in mess:
                self.add_word_song()

            self.refresh_display_page()
            self.interface_pages_redirecting("DisplayPage")
            self.set_status_message(mess)

    def make_request(self, word: str):
        resp = get_translation_from(word)
        self.lblMainWord_2.setText(resp["head_word"])
        self.lblTranslation.setText(resp["translation"])
        text = "<ul>"
        for element in [element for element in resp["examples"]]:
            tmp_word = resp["head_word"]
            text += (
                "<li>"
                + re.sub(rf"{tmp_word}(\w*)", rf"<b>{tmp_word}\1</b>", element)
                + "</li>"
            )
        text += "</ul>"
        self.lblExamples.setText(text)
        print(word)

    def spin_font(self, a=""):
        self.centralwidget.setStyleSheet(f"QLabel" "{" "font : {a}pt;" "}")
        print(f"Spin changed to c: {a}")

    def display_obj_name(self):
        obj_name = self.sender().objectName()
        self.make_request(obj_name)

    def checkbox_display(self):
        obj_index = int(self.sender().objectName())
        bool_value = self.checkboxs[obj_index].isChecked()
        set_display_value(index=obj_index, bool_value=bool_value)
        print(f"obj clicked: {obj_index} = {bool_value}")

    def toggle_settings_func(self, value):
        set_json_value(name="settings_page", name2="speaker", value=value)
        self.speaker = get_json_value("settings_page")["speaker"]
        self.set_status_message(f"Change speaker status: {self.speaker}")

    # SETTINGS

    def load_settings(self):
        self.toggle_settings.setChecked(
            get_json_value("settings_page")["speaker"])

    def set_len_df_lbl(self, number_of_words: int) -> None:
        self.lblNumerWords.setText(f"Number of words: {number_of_words}")

    def set_table_model(self, _df: pd.DataFrame):

        # self.tableView.setRowCount(len(_df))
        self.tableView.setRowCount(10)
        # Two additional columns, Request, Delete
        indexes = _df.index
        df_names = self.data.get_english_poland_col_names()
        self.tableView.setColumnCount(len(df_names) + 2)

        # Columns width
        for i, col_width in enumerate([180, 500, 90, 90]):
            self.tableView.setColumnWidth(i, col_width)

        # for i in range(len(_df)):
        for i, index in enumerate(indexes):
            try:
                col_length = self.tableView.columnCount()

                for j in range(2):
                    item = QTableWidgetItem(self.data.get_item_by(index, j))
                    self.tableView.setItem(i, j, item)

                # R, request btn, D - delete btn
                for j, (btn_name, btn_func) in enumerate(zip(["R", "D"], [self.display_obj_name, self.on_delete])):
                    item_request = QTableWidgetItem("item_request")
                    self.tableView.setItem(
                        index, col_length - 2 + j, item_request)
                    button = QPushButton(btn_name)
                    button.setObjectName(self.data.get_item_by(index, 0))
                    button.clicked.connect(btn_func)
                    self.tableView.setCellWidget(
                        i, col_length - 2 + j, button)

                # for delete btn set style
                button.setStyleSheet(
                    "QPushButton" "{" "background-color : rgb(255, 128, 128);" "}"
                )

            except Exception:
                pass

        for i in range(len(indexes), 10):
            for j in range(4):
                item = QTableWidgetItem("empty")
                self.tableView.setItem(i, j, item)

        self.tableView.setHorizontalHeaderLabels(
            df_names + ["Request", "Delete"])
        self.tableView.setVerticalHeaderLabels(list(map(str, _df.index)))

    def on_delete(self):
        popup = PopUp()
        delete_word = self.sender().objectName()
        print(delete_word)
        output = popup.delete_this(delete_word)
        if output == True:
            message = self.data.delete_word_by(english_word=delete_word)
            self.set_status_message(message)
            self.refresh_display_page()

    def refresh_df(self, text: str):
        tmp_df = transform_df(self.data.get_df(), text).head(10)
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
        pages = ["MainPage", "DisplayPage", "StatsPage", "MigratePage"]
        index = get_last_page()
        self.stackedWidget.setCurrentIndex(index)
        self.set_status_message(f"Loaded Last page: {pages[index]}")

    def set_last_page_index(self) -> int:
        pages = ["MainPage", "DisplayPage", "StatsPage", "MigratePage"]
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
        random_word_1, random_word_2 = (
            self.data.get_sample_polish(),
            self.data.get_sample_polish(),
        )
        buttons = self.buttons.copy()
        self.lblMainWord.setText(english_word)
        random.shuffle(buttons)
        for word, btn in zip([polish_word, random_word_1, random_word_2], buttons):
            btn.setText(word)
        self.speaker_on()

    def worker_result(self, label):
        print("Finish project")
        self.speaker = True
        self.pix_map(label=label, file_path="icons/Speaker_black.svg")

    # Random words key pressed
    def keyPressEvent(self, e):
        if e.key() == Qt.Key_1:
            self.buttons[0].click()
        if e.key() == Qt.Key_2:
            self.buttons[1].click()
        if e.key() == Qt.Key_3:
            self.buttons[2].click()
        if e.key() == Qt.Key_4:
            self.speaker_on()
        if e.key() == Qt.Key_P:
            self.centralwidget.setStyleSheet("QLabel" "{" "font : 3pt;" "}")
        if e.key() == Qt.Key_S:
            self.start_game()
            self.button_default_stylesheet()
        if e.key() == Qt.Key_R:
            print("random word")
            self.button_default_stylesheet()
            if not self.is_game:
                self.set_status_message(f"First start the game!")
                return
            if self.winning_status:
                self.button_default_stylesheet()
                self.random_word()
                self.winning_status = False
            else:
                self.set_status_message(f"Answer the current question first")

    def setup_checkbox_display(self) -> None:
        for index, cbx in enumerate(self.checkboxs):
            cbx.setChecked(get_display_value(index))

    def speaker_on(self, page: str = "main"):
        text = (
            DataOperations.get_english_word(self.winning_row)
            if page == "main"
            else f"{self.lblMainWord_2.text()} {self.lblTranslation.text()}"
        )
        label = self.lblSpeaker if page == "main" else self.lblPronunciation
        if self.speaker:
            self.pix_map(label=label, file_path="icons/Speaker_gray.svg")
            self.worker = Worker(text=text, voice=self.voice)
            self.speaker = False
            self.worker.signals.finish.connect(
                lambda: self.worker_result(label))
            self.thredapool.start(self.worker)

    def button_default_stylesheet(self):
        for btn in self.buttons:
            btn.setEnabled(True)
            btn.setStyleSheet(
                "QPushButton" "{" "background-color : rgb(0, 123, 255);" "}"
            )

    def buttons_disable_all(self):
        for btn in self.buttons:
            btn.setEnabled(False)

    def refresh_progress_bar_stats(self):
        df_len = self.data.df_len()
        freq_val = len(
            self.data.df[self.data.df.Frequency ==
                         self.data.df.Frequency.min()]
        )
        meter = (df_len - freq_val) * 100
        denominator = df_len
        update_val = meter / denominator
        self.progStats.setValue(update_val)
        self.lblProgressBar.setText(f"{freq_val}/{denominator}")

    # Btn configurations
    def btn_random_word(self):
        # background-color: rgb(66, 189, 255);
        obj = self.sender().objectName()
        self.buttons[int(obj)].setStyleSheet(
            "QPushButton" "{" "background-color: rgb(66, 189, 255); color : white;" "}"
        )
        self.buttons[int(obj)].setEnabled(False)

        print(f"Button: {self.buttons[int(obj)].text()}")
        print(f'Win: {str(self.winning_row["Polski"])}')
        if str(self.buttons[int(obj)].text()) in str(self.winning_row["Polski"]):
            self.buttons_disable_all()
            self.buttons[int(obj)].setStyleSheet(
                "QPushButton"
                "{"
                "background-color: rgb(40, 179, 90); color : white;"
                "}"
            )
            self.tournament_dict["corrects"].append(
                str(self.buttons[int(obj)].text()))
            self.winning_status = True
            index = self.winning_row.index.values[0]
            self.data.increase_frequency(index)
        else:
            self.tournament_dict["bads"].append(
                str(self.buttons[int(obj)].text()))
            self.buttons[int(obj)].setStyleSheet(
                "QPushButton"
                "{"
                "background-color: rgb(220, 237, 255); color : black;"
                "}"
            )
        self.buttons[int(obj)].setEnabled(False)

        print(f'Winning: {self.winning_row["Polski"]}')
        value = self.progressBar.value() + 10
        self.progressBar.setValue(value)
        if value == 100:
            self.result_setup()
            self.set_start_btn(mode="end")
            self.progressBar.setValue(0)
            print(self.tournament_dict)
            self.lblResult.setText(
                f"Corrects: {len(self.tournament_dict['corrects'])}, Bads: {len(self.tournament_dict['bads'])}"
            )
            df_corrects = pd.DataFrame.from_dict(
                self.tournament_dict["corrects"])
            df_bads = pd.DataFrame.from_dict(self.tournament_dict["bads"])
            df_corrects.columns, df_bads.columns = ["Polski"], ["Polski"]
            df_corrects["English"] = df_corrects.Polski.apply(
                lambda x: self.data.get_translation_from_pl(polish_word=x)
            )
            df_bads["English"] = df_bads.Polski.apply(
                lambda x: self.data.get_translation_from_pl(polish_word=x)
            )
            self.tabCorrects.setModel(TableModel(df_corrects, df_type="green"))
            self.tabBads.setModel(TableModel(df_bads, df_type="red"))
            # self.tabBads.horizontalHeader().setMinimumSectionSize(2200)
            self.tabCorrects.horizontalHeader().setSectionResizeMode(
                0, QtWidgets.QHeaderView.Stretch
            )
            self.tabBads.horizontalHeader().setSectionResizeMode(
                0, QtWidgets.QHeaderView.Stretch
            )

        print(f"value: {value}")
        print(obj)

    def start_game(self):
        self.start_time = datetime.today()
        self.button_default_stylesheet()
        self.set_start_btn(mode="start")
        print("start")

    def set_start_btn(self, mode: str = ""):
        color = "rgb(0,123,255)" if mode == "end" else "rgb(209,245,255)"
        text = "Start" if mode == "end" else "In game..."
        print(f"Change to: {mode} color: {color}")
        self.btnStart.setStyleSheet(
            "QPushButton"
            "{"
            "background-color:" + color + ";color:rgb(255,255,255)"
            "}"
        )
        self.btnStart.setText(text)
        self.btnStart.setEnabled(mode == "end")
        self.is_game = True
        self.random_word()

    def pix_map(self, *, label, file_path: str):
        pixmap = QPixmap(file_path)
        label.setPixmap(pixmap)
        label.setScaledContents(True)

    def result_setup(self):
        self.interface_pages_redirecting("StatsPage")
        result_time = int((datetime.today() - self.start_time).total_seconds())
        self.btnTimerResult.setText(f"Competition took {result_time} seconds")

    def refresh_display_page(self):
        self.refresh_df(self.txtDisplaySearch.text())
        self.set_len_df_lbl(self.data.get_num_all_words())

    # interface pages
    def interface_pages_redirecting(self, page_name: str):
        if page_name == "DisplayPage":
            self.stackedWidget.setCurrentWidget(self.DisplayPage)
        if page_name == "SettingsPage":
            self.stackedWidget.setCurrentWidget(self.SettingsPage)
        if page_name == "StatsPage":
            self.refresh_progress_bar_stats()
            self.stackedWidget.setCurrentWidget(self.StatsPage)
        if page_name == "MigratePage":
            self.stackedWidget.setCurrentWidget(self.MigratePage)
        if page_name == "MainPage":
            self.stackedWidget.setCurrentWidget(self.MainPage)
        if page_name == "InformationPage":
            self.stackedWidget.setCurrentWidget(self.InformationPage)

    def add_word_song(self):
        self.worker = WorkerMusic(music_type=MusicType.add_word)
        self.worker.signals.finish.connect(
            lambda: print('Finish'))
        self.thredapool.start(self.worker)

    # Buttons setup

    @pyqtSlot()
    def on_btnTest_clicked(self):
        self.toggle_settings.setChecked(True)
        print(f"Btn test ")

    @pyqtSlot()
    def on_btnAddWords_clicked(self):
        for index, row in self.json_df.iterrows():
            self.data.add_new_word(
                english_word=row.English, polish_word=row.Polish)

        self.refresh_display_page()
        self.interface_pages_redirecting("DisplayPage")

        self.set_status_message(f"Added {len(self.json_df)} words.")

    @pyqtSlot()
    def on_btnAddWord_clicked(self):

        english_word, polish_word = (
            self.txtEnglishWord.text(),
            self.txtPolishWord.text(),
        )
        if english_word == "" or polish_word == "":
            self.set_status_message("New words can't be empty!")
        else:
            self.add_word_song()
            mess = self.data.add_new_word(
                english_word=english_word, polish_word=polish_word
            )
            if mess.startswith("Added new word"):
                self.refresh_display_page()
            self.interface_pages_redirecting("DisplayPage")
            self.set_status_message(mess)
        # print(f'add word clicked! {english_word} {polish_word}')

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
        self.interface_pages_redirecting("SettingsPage")

    @pyqtSlot()
    def on_btnMain_clicked(self):
        self.interface_pages_redirecting("MainPage")

    @pyqtSlot()
    def on_btnDisplay_clicked(self):
        self.interface_pages_redirecting("DisplayPage")

    @pyqtSlot()
    def on_btnMigrate_clicked(self):
        self.interface_pages_redirecting("MigratePage")

    @pyqtSlot()
    def on_btnStats_clicked(self):
        self.interface_pages_redirecting("StatsPage")

    @pyqtSlot()
    def on_btnLoadJson_clicked(self):
        print("Load JSON!")
        try:
            parsed = json.loads(self.txtJSON.toPlainText())
            self.json_df = pd.DataFrame.from_dict(
                dict(parsed), orient="index"
            ).reset_index()
            self.json_df.columns = ["English", "Polish"]
            self.json_df["Exists"] = False
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

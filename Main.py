import sys
from datetime import datetime
from random import shuffle

from interface_files.Dialog import Ui_Dialog
from interface_files.MainWindow import Ui_MainWindow
from control_files.Voice import voice_speech
from control_files.Graph import Graph

from PyQt5 import QtCore, QtWidgets
from control_files.Data import Data
from control_files.File_IO import File
from PyQt5.QtWidgets import QLabel, QAction
from PyQt5.QtGui import QIcon, QPixmap


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # using the interface made
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.add_new_word.clicked.connect(self.open_dialog_window)

        # dialog window for adding new word
        self.Dialog = QtWidgets.QDialog()
        self.dialog = Ui_Dialog()
        self.dialog.setupUi(self.Dialog)
        self.dialog.buttonBox.accepted.connect(self.new_word)

        # adding configuration of answering calls from the button
        self.ui.random_button.clicked.connect(self.change_text_main)
        self.ui.cbutton1.clicked.connect(lambda: self.polish_button_clicked(self.ui.cbutton1))
        self.ui.cbutton2.clicked.connect(lambda: self.polish_button_clicked(self.ui.cbutton2))
        self.ui.cbutton3.clicked.connect(lambda: self.polish_button_clicked(self.ui.cbutton3))
        self.ui.save_button.clicked.connect(self.save_button)
        self.ui.reset_button.clicked.connect(self.reset_button)

        # Status bar
        self.bar_label = QLabel("Welcome")
        self.statusBar().setStyleSheet(
            "QLabel{font-weight:bold;color:grey}QStatusBar{border :1px solid gray;padding-left:8px;background:rgba(0,0,0,0);color:black;font-weight:bold;}")
        self.statusBar().addPermanentWidget(self.bar_label)

        # a class that deals with pandas df
        self.df_data = Data()
        self.ui.number_of_words.setText(str(self.df_data.len_df()))
        self.update_rand()

        # voice speaker class
        self.speak = voice_speech()
        # self.ui.pronunciation_button.clicked.connect(lambda: self.speak.text(self.ui.random_word.text()))
        self.ui.pronunciation_button.clicked.connect(lambda: self.reading_word(self.ui.random_word.text()))

        self.load_scores()

        def line_edit(line, btn):
            line.setEnabled(True)
            self.new_choice = [line, btn]

        # intercepts the signal from the right pushbutton
        self.ui.cbutton1.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.cbutton1.customContextMenuRequested.connect(lambda: line_edit(self.ui.edit_c1, self.ui.cbutton1))
        self.ui.cbutton2.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.cbutton2.customContextMenuRequested.connect(lambda: line_edit(self.ui.edit_c2, self.ui.cbutton2))
        self.ui.cbutton3.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.cbutton3.customContextMenuRequested.connect(lambda: line_edit(self.ui.edit_c3, self.ui.cbutton3))
        self.ui.random_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.random_button.customContextMenuRequested.connect(self.copy_eng_word)

        # save streak
        self.ui.save_word.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.save_word.customContextMenuRequested.connect(self.test)
        self.ui.save_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.save_button.customContextMenuRequested.connect(self.to_file)

        self.new_choice = None
        self.ui.save_word.clicked.connect(self.line_edit_disable)

        # init streak
        self.tmp_file = File()
        self.strike_max = self.tmp_file.return_strike()
        print("Strike =", self.strike_max)
        self.ui.strike_main.setText(str(self.strike_max))
        self.streak_choice = "correct"
        self.tmp_file.close()
        self.record = None

        # init graph
        self.graph = None

        self.init_graph()

        # add action to menu bar
        self.ui.actionGraph.triggered.connect(self.init_graph)
        #self.ui.actionSave_Graph.triggered.connect(self.save_graph)

        # setting icons for buttons
        self.ui.save_button.setIcon(QIcon("images/disk-black.png"))
        self.ui.save_word.setIcon(QIcon("images/disk-black.png"))
        self.ui.add_new_word.setIcon(QIcon("images/plus.png"))
        self.ui.reset_button.setIcon(QIcon("images/arrow-circle.png"))
        self.ui.random_button.setIcon(QIcon("images/playing-card.png"))
        self.ui.pronunciation_button.setIcon(QIcon("images/speaker.png"))
        self.ui.actionSave_Graph.setIcon(QIcon("images/image--arrow.png"))

    # def save_graph(self):
    #     p = QPixmap.grabWindow(self.ui.verticalLayout_2.winId())
    #     p.save('123.png', 'png')
    #
    # def save_graph2(self):
    #     self.save_graph()

    def init_graph(self):
        self.graph = Graph()

        # add graph to horizontal3
        self.ui.stackedWidget.addWidget(self.graph.return_canvas())
        self.ui.stackedWidget.setCurrentWidget(self.graph.return_canvas())
      #  self.ui.horizontalLayout_3.addWidget(self.graph.return_canvas())

    def to_file(self):
        print("to file")
        f = File("a+", "control_files/Log.txt")
        now = datetime.now()
        today = now.strftime("%d/%m/%Y %H:%M:%S")
        print(f"{today}+\n+{self.strike_max}")
        f.write_end("")
        f.write_end(f"Date: {today} Number of words: {self.ui.number_of_words.text()}")
        f.write_end(f"Date: {today} Correctly:{self.ui.correctly_main.text()}")
        f.write_end(f"Date: {today} Badly:{self.ui.badly_main.text()}")
        f.write_end(f"Date: {today} Max Strike: {self.strike_max}")
        f.close()
        self.bar_change_text("update log file")

    def bar_change_text(self, text):
        self.bar_label.setText(text)

    def reading_word(self, word):
        if self.ui.pronunciation_checkbox.isChecked():
            self.speak.text(word)
        else:
            print("Pronunciation is disable")
        self.bar_change_text("clicked pronunciation")

    def copy_eng_word(self):
        print(self.ui.random_word.text())

    def new_word(self):
        add = self.df_data.add_new_word(self.dialog.angielski.text(), self.dialog.polski.text())
        print(add)
        #self.reading_word(add)
        self.reload_df()
        #self.df_data = Data()
        self.bar_change_text(add)

    def reload_df(self):
        self.ui.number_of_words.setText(str(self.df_data.len_df()))

    def open_dialog_window(self):
        self.Dialog.exec_()
        self.dialog.angielski.setText("")
        self.dialog.polski.setText("")

    def update_rand(self):
        self.ui.random_w.setText(str(self.df_data.len_random()))
        number_all = int(self.ui.number_of_words.text())
        number_need = number_all-int(self.ui.random_w.text())
        new_value = (100*number_need)//number_all
        self.ui.progressBar.setValue(new_value)

    def line_edit_disable(self):
        self.ui.edit_c1.setEnabled(False)
        self.ui.edit_c2.setEnabled(False)
        self.ui.edit_c3.setEnabled(False)
        self.update_new_word()

    def update_new_word(self):# ??need change this name
        if self.new_choice is not None:
            try:
                df = self.df_data.df_return()
                stare = df[self.df_data.ret_pol(df) == self.new_choice[1].text()].index[0]
                df.at[stare, 'Meaning'] = self.new_choice[0].text()
                self.new_choice[1].setText(self.new_choice[0].text())
                self.new_choice = None
                print("Successfully update")
                self.bar_change_text("Update word")
            except Exception:
                print("Update failed")

    def change_text_main(self):
        def change_text_in_label(btn, text):
            btn.setText(text)

        self.line_edit_disable()
        self.button_default_stylesheet()
        self.button_set_enabled(True)

        sample_row = self.df_data.sample_row()
        change_text_in_label(self.ui.random_word, self.df_data.return_english_word_from_row(sample_row))

        # create dictes and shuffle their elements
        button_dict = [self.ui.cbutton1, self.ui.cbutton2, self.ui.cbutton3]
        edit_dict = [self.ui.edit_c1, self.ui.edit_c2, self.ui.edit_c3]
        pack = list(zip(button_dict, edit_dict))
        shuffle(pack)
        button_dict, edit_dict = zip(*pack)

        # enters the randomly selected words into the pushbutton
        texts = [sample_row, self.df_data.sample_row(), self.df_data.sample_row()]
        for button, text, ed in zip(button_dict, texts, edit_dict):
            text_t = self.df_data.return_polish_word_from_row(text)
            change_text_in_label(button, text_t)
            change_text_in_label(ed, text_t)
        #self.reading_word(self.ui.random_word.text())
        self.bar_change_text("Random a word")
        self.ui.random_button.setEnabled(False)

    def polish_button_clicked(self, btn): # temporary stats
        df = self.df_data.df_random_return()
        print(self.ui.random_word.text(), " + ", df[df['Meaning'] == btn.text()]['Idiom'].any())
        if self.ui.random_word.text() in df[df['Meaning'] == btn.text()]['Idiom'].values:
            self.df_data.increase_frequency(self.ui.random_word.text())
            new_number = int(self.ui.correctly.text()) + 1
            self.ui.correctly.setText(str(new_number))
            self.button_set_enabled(False)
            btn.setStyleSheet("QPushButton""{""background-color: rgb(14, 217, 0); color : green;""}")
            self.update_rand()
            self.streak("correct")
            self.ui.random_button.setEnabled(True)
            if self.graph:
                self.graph.add_item(1)
        else:
            self.df_data.increaseBadlyAnswer(self.ui.random_word.text())
            new_number = int(self.ui.badly.text()) + 1
            self.ui.badly.setText(str(new_number))
            btn.setEnabled(False)
            btn.setStyleSheet("QPushButton""{""background-color : rgb(167, 12, 20);""}")
            self.streak("baddly")
            if self.graph:
                self.graph.add_item(-1)

    def streak(self, w_l):
        if w_l == "correct" and self.streak_choice == "correct":
            self.ui.streak_num.setText(str(int(self.ui.streak_num.text())+1))
        elif w_l == "correct" and self.streak_choice == "baddly":
            self.ui.streak_num.setText("1")
        else:
            self.ui.streak_num.setText("0")
        self.streak_choice = w_l
        if int(self.ui.streak_num.text()) > self.strike_max:
            self.strike_max = int(self.ui.streak_num.text())
            self.bar_change_text("New streak!")
        if int(self.ui.streak_num.text()) > 0:
            self.ui.streak_num.setStyleSheet("QLabel{color: darkgreen;}")
            self.ui.streak_name.setStyleSheet("QLabel{color: darkgreen;}")
        else:
            self.ui.streak_num.setStyleSheet("QLabel{color: dark;}")
            self.ui.streak_name.setStyleSheet("QLabel{color: dark;}")

    def test(self):
        print("test")

    def button_set_enabled(self, bool_tmp):
        self.ui.cbutton1.setEnabled(bool_tmp)
        self.ui.cbutton2.setEnabled(bool_tmp)
        self.ui.cbutton3.setEnabled(bool_tmp)

    def button_default_stylesheet(self):
        self.ui.cbutton1.setStyleSheet("QPushButton""{""background-color : None;""}")
        self.ui.cbutton2.setStyleSheet("QPushButton""{""background-color : None;""}")
        self.ui.cbutton3.setStyleSheet("QPushButton""{""background-color : None;""}")

    def save_button(self):
        self.df_data.df_return().to_csv('control_files/Data.csv', index=False, encoding='utf-8-sig')
        print("save")
        f = File()
        scores = f.return_lines()
        correct = int(scores[0][10:-1])+int(self.ui.correctly.text())
        bad = int(scores[1][6:])+int(self.ui.badly.text())
        strike = self.strike_max

        scores = [f"correctly: {correct}\n", f"badly: {bad}\nMax_strike: {strike}"]

        f = File("w")
        f.write_lines(scores)
        f.close()
        #self.reading_word("successfully saved")
        self.reset_button()
        self.load_scores()
        self.bar_change_text("Save changes")

    def reset_button(self):
        print("reset")
        #.reading_word("reset")
        self.df_data.reset_df()
        self.update_rand()
        self.ui.number_of_words.setText(str(self.df_data.len_df()))
        self.ui.correctly.setText(str(0))
        self.ui.badly.setText(str(0))
        self.change_text_main()
        self.ui.strike_main.setText(str(self.strike_max))
        self.ui.random_button.setEnabled(True)
        self.bar_change_text("Reset")

    def load_scores(self): # main stats
        with open("control_files/Scores.txt", "r") as f:
            scores = f.readlines()
            self.ui.correctly_main.setText(scores[0][10:-1])
            self.ui.badly_main.setText(scores[1][6:-1])
            self.ui.badly_main.setStyleSheet("QLabel""{""color: rgb(153, 29, 29); font-family : SimSun-ExtB;""}")
            self.ui.correctly_main.setStyleSheet("QLabel""{""color: rgb(60, 163, 44); font-family : SimSun-ExtB;""}")
        f.close()
        self.bar_change_text("Load scores")
        return scores


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

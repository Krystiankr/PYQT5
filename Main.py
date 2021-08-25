import sys
from random import randint, shuffle

from Dialog import Ui_Dialog
from MainWindow import Ui_MainWindow

from Voice import voice_speech
from PyQt5 import QtCore, QtWidgets
from Data import Data
from File_IO import File
#2

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

        # a class that deals with pandas df
        self.df_data = Data()
        self.ui.number_of_words.setText(str(self.df_data.len_df()))
        self.ui.random_w.setText(str(self.df_data.len_random()))

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
        self.ui.save_word.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.save_word.customContextMenuRequested.connect(self.test)

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

    def reading_word(self, word):
        if self.ui.pronunciation_checkbox.isChecked():
            self.speak.text(word)
        else:
            print("Pronunciation is disable")

    def copy_eng_word(self):
        print(self.ui.random_word.text())

    def new_word(self):
        add = self.df_data.add_new_word(self.dialog.angielski.text(), self.dialog.polski.text())
        print(add)
        self.reading_word(add)
        self.reload_df()

    def reload_df(self):
        self.ui.number_of_words.setText(str(self.df_data.len_df()))

    def open_dialog_window(self):
        self.Dialog.exec_()
        self.dialog.angielski.setText("")
        self.dialog.polski.setText("")

    def update_rand(self):
        self.ui.random_w.setText(str(self.df_data.len_random()))

    def line_edit_disable(self):
        self.ui.edit_c1.setEnabled(False)
        self.ui.edit_c2.setEnabled(False)
        self.ui.edit_c3.setEnabled(False)
        self.update_new_word()

    def update_new_word(self):
        if self.new_choice is not None:
            try:
                df = self.df_data.df_return()
                stare = df[self.df_data.ret_pol(df) == self.new_choice[1].text()].index[0]
                df.at[stare, 'Polski'] = self.new_choice[0].text()
                self.new_choice[1].setText(self.new_choice[0].text())
                self.new_choice = None
                print("Successfully update")
            except:
                print("Update failed")

    def change_text_main(self):
        def change_text_in_label(btn, text):
            btn.setText(text)

        self.line_edit_disable()
        self.button_default_stylesheet()
        self.button_set_enabled(True)

        sample_row = self.df_data.ret_ang(self.df_data.sample_row())
        random_value = sample_row.values[0]
        random_index = sample_row.index[0]
        change_text_in_label(self.ui.random_word, random_value)

        # create dictes and shuffle their elements
        button_dict = [self.ui.cbutton1, self.ui.cbutton2, self.ui.cbutton3]
        edit_dict = [self.ui.edit_c1, self.ui.edit_c2, self.ui.edit_c3]
        pack = list(zip(button_dict, edit_dict))
        shuffle(pack)
        button_dict, edit_dict = zip(*pack)

        # enters the randomly selected words into the pushbutton
        answer = [random_index, randint(0, self.df_data.len_df()), randint(0, self.df_data.len_df())]
        for button, ans, ed in zip(button_dict, answer, edit_dict):
            change_text_in_label(button, self.df_data.ret_pol(self.df_data.df_return())[ans])
            change_text_in_label(ed, self.df_data.ret_pol(self.df_data.df_return())[ans])
        self.reading_word(self.ui.random_word.text())

    def polish_button_clicked(self, btn):
        df = self.df_data.df_return()
        print(self.ui.random_word.text(), " + ", df[df['Polski'] == btn.text()]['Angielski'].any())
        if self.ui.random_word.text() in df[df['Polski'] == btn.text()]['Angielski'].values:
            self.df_data.increase_frequency(self.ui.random_word.text())
            new_number = int(self.ui.correctly.text()) + 1
            self.ui.correctly.setText(str(new_number))
            self.button_set_enabled(False)
            btn.setStyleSheet("QPushButton""{""background-color: rgb(14, 217, 0); color : green;""}")
            self.update_rand()
            self.streak("correct")
        else:
            new_number = int(self.ui.badly.text()) + 1
            self.ui.badly.setText(str(new_number))
            btn.setEnabled(False)
            btn.setStyleSheet("QPushButton""{""background-color : rgb(167, 12, 20);""}")
            self.streak("baddly")

    def streak(self, w_l):
        if w_l == "correct" and self.streak_choice == "correct":
            self.ui.streak_num.setText(str(int(self.ui.streak_num.text())+1))
        elif w_l == "correct" and self.streak_choice == "baddly":
            self.ui.streak_num.setText("1")
        else:
            self.ui.streak_num.setText("0")
        self.streak_choice = w_l
        if int(self.ui.streak_num.text()) > self.strike_max:
            print("Rekord")
        if int(self.ui.streak_num.text()) > 0:
            self.ui.streak_num.setStyleSheet("QLabel{color: darkgreen;}")
            self.ui.streak_name.setStyleSheet("QLabel{color: darkgreen;}")
        else:
            self.ui.streak_num.setStyleSheet("QLabel{color: dark;}")
            self.ui.streak_name.setStyleSheet("QLabel{color: dark;}")

    #def update_streak(self):


    def test(self):
        f = File()
        print("*", end='')
        f.print(2)
        print("*")
        f.close()

    def button_set_enabled(self, bool_tmp):
        self.ui.cbutton1.setEnabled(bool_tmp)
        self.ui.cbutton2.setEnabled(bool_tmp)
        self.ui.cbutton3.setEnabled(bool_tmp)

    def button_default_stylesheet(self):
        self.ui.cbutton1.setStyleSheet("QPushButton""{""background-color : None;""}")
        self.ui.cbutton2.setStyleSheet("QPushButton""{""background-color : None;""}")
        self.ui.cbutton3.setStyleSheet("QPushButton""{""background-color : None;""}")

    def save_button(self):
        self.df_data.df_return().to_csv('Data.csv', index=False, encoding='utf-8-sig')
        print("save")
        f = File()
        scores = f.return_lines()
        correct = int(scores[0][10:-1])+int(self.ui.correctly.text())
        bad = int(scores[1][6:])+int(self.ui.badly.text())
        strike = self.strike_max
       # f.close()
       # if self.record is not None:
        #    strike =

        scores = [f"correctly: {correct}\n", f"badly: {bad}\nMax_strike: {strike}"]

        f = File("w")
        f.write_lines(scores)
        f.close()
        self.reading_word("successfully saved")
        self.reset_button()
        self.load_scores()

    def reset_button(self):
        print("reset")
        self.reading_word("reset")
        self.df_data.reset_df()
        self.update_rand()
        self.ui.number_of_words.setText(str(self.df_data.len_df()))
        self.ui.correctly.setText(str(0))
        self.ui.badly.setText(str(0))
        self.change_text_main()
        self.ui.streak_num.setText("0")

    def load_scores(self):
        with open("Scores.txt", "r") as f:
            scores = f.readlines()
            self.ui.correctly_main.setText(scores[0][10:-1])
            self.ui.badly_main.setText(scores[1][6:])
            self.ui.badly_main.setStyleSheet("QLabel""{""color: rgb(153, 29, 29); font-family : SimSun-ExtB;""}")
            self.ui.correctly_main.setStyleSheet("QLabel""{""color: rgb(60, 163, 44); font-family : SimSun-ExtB;""}")
        f.close()
        return scores


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

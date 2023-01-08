from PyQt5.QtWidgets import QWidget, QPushButton, QMessageBox


class PopUp(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Create a delete button
        delete_button = QPushButton('Delete', self)
        delete_button.clicked.connect(self.delete_this)

    def delete_this(self, delete_word: str) -> bool:
        # Show a message box with "Yes" and "No" buttons
        reply = QMessageBox.question(
            self, 'Message', f"Are you sure you want to delete <b>{delete_word}</b>?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        return reply == QMessageBox.Yes

# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'migrate.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Migrate(object):
    def setupUi(self, Migrate):
        Migrate.setObjectName("Migrate")
        Migrate.resize(338, 239)
        self.buttonBox = QtWidgets.QDialogButtonBox(Migrate)
        self.buttonBox.setGeometry(QtCore.QRect(10, 191, 311, 31))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.textEdit = QtWidgets.QTextEdit(Migrate)
        self.textEdit.setGeometry(QtCore.QRect(10, 10, 311, 171))
        self.textEdit.setObjectName("textEdit")

        self.retranslateUi(Migrate)
        self.buttonBox.accepted.connect(Migrate.accept)
        self.buttonBox.rejected.connect(Migrate.reject)
        QtCore.QMetaObject.connectSlotsByName(Migrate)

    def retranslateUi(self, Migrate):
        _translate = QtCore.QCoreApplication.translate
        Migrate.setWindowTitle(_translate("Migrate", "Migrate Words"))


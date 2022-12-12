# coding=utf-8
import json
import sys

import requests
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QRect
from PyQt5.QtWidgets import *
from jira import JIRA
from PyQt5.QtCore import *

from ui import base, report
from util import configUtils
from util.cyUtils import cyUtils


class Ui_MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.retranslateUi(self)

    def keyPressEvent(self, event):
        if (event.key() == Qt.Key_Enter) or (event.key() == Qt.Key_Return):
            self.do_login()

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(386, 127)
        self.centralWidget = QtWidgets.QWidget(MainWindow)
        self.centralWidget.setObjectName("centralWidget")
        self.lineEdit = QtWidgets.QLineEdit(self.centralWidget)
        self.lineEdit.setGeometry(QtCore.QRect(250, 20, 100, 20))
        self.lineEdit.setText("")
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit_2 = QtWidgets.QLineEdit(self.centralWidget)
        self.lineEdit_2.setGeometry(QtCore.QRect(250, 50, 100, 20))
        self.lineEdit_2.setText("")
        self.lineEdit_2.setEchoMode(QtWidgets.QLineEdit.Password)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.label = QtWidgets.QLabel(self.centralWidget)
        self.label.setGeometry(QtCore.QRect(200, 24, 24, 12))
        self.label.setTextFormat(QtCore.Qt.AutoText)
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.centralWidget)
        self.label_2.setGeometry(QtCore.QRect(200, 54, 24, 12))
        self.label_2.setObjectName("label_2")
        self.pushButton = QtWidgets.QPushButton(self.centralWidget)
        self.pushButton.setGeometry(QtCore.QRect(190, 90, 75, 23))
        self.pushButton.setObjectName("pushButton")
        self.pushButton_2 = QtWidgets.QPushButton(self.centralWidget)
        self.pushButton_2.setGeometry(QtCore.QRect(290, 90, 75, 23))
        self.pushButton_2.setObjectName("pushButton_2")
        MainWindow.setCentralWidget(self.centralWidget)

        self.pushButton.clicked.connect(self.do_login)
        self.pushButton_2.clicked.connect(MainWindow.close)

        self.retranslateUi(MainWindow)
        self.show()

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "quickReport"))
        self.lineEdit.setPlaceholderText(_translate("MainWindow", "请输入帐号"))
        self.lineEdit_2.setPlaceholderText(_translate("MainWindow", "请输入密码"))
        self.label.setText(_translate("MainWindow", "帐号"))
        self.label_2.setText(_translate("MainWindow", "密码"))
        self.pushButton.setText(_translate("MainWindow", "确定"))
        self.pushButton_2.setText(_translate("MainWindow", "取消"))

    def do_login(self):
        user = self.lineEdit.text()
        passwd = self.lineEdit_2.text()
        jira = None
        error_msg = '登陆失败！'
        try:
            jira = JIRA(configUtils.host, max_retries=1, timeout=20, basic_auth=(user, passwd))
            configUtils.set_user(cyUtils().encrypt(user))
            configUtils.set_passwd(cyUtils().encrypt(passwd))
        except Exception as e:
            error_msg = str('登录失败! 检查jira是否能正常登录或是需要输入验证码！\n' + str(e))
        if jira is not None:
            window.close()
            ui_hello.setupUi()
            ui_hello.show()
        else:
            QMessageBox.warning(self, "警告", error_msg, QMessageBox.Yes)
            self.lineEdit.setFocus()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Ui_MainWindow()
    ui_report = report.Ui_Form()
    ui_hello = base.Ui_MainWindow()
    try:
        jira = JIRA(configUtils.host, timeout=3, basic_auth=(configUtils.user(), configUtils.passwd()))
        window.close()
        ui_hello.setupUi()
        ui_hello.show()
    except Exception as e:
        if str(e) == '\'ConnectTimeout\' object has no attribute \'headers\'':
            QMessageBox.warning(window, "警告", "登录超时，请检查网络环境与jira是否联通!", QMessageBox.Yes)
        window.show()
    sys.exit(app.exec_())

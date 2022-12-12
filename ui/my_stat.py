import os
import subprocess

import pandas as pd
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMessageBox, QComboBox, QLabel
from openpyxl import Workbook

from util import configUtils, jiraUtils
from util.dateUtils import get_diff_selected


class Ui_Form(QtWidgets.QMainWindow):

    def __init__(self):
        super(Ui_Form, self).__init__()
        try:
            self.setupUi(self)
        except Exception as e:
            QMessageBox.warning(self, "警告", str(e), QMessageBox.Yes)

    def setupUi(self, Form):
        self.he = QLabel('我的工作统计:', self)
        self.he.setStyleSheet("color:green")
        self.he.setGeometry(QtCore.QRect(13, 10, 100, 40))

        self.textEdit = QtWidgets.QTextBrowser(Form)
        self.textEdit.setGeometry(QtCore.QRect(13, 53, 600, 470))
        self.textEdit.setFocusPolicy(QtCore.Qt.NoFocus)
        self.pushButton = QtWidgets.QPushButton(Form)
        self.pushButton.setGeometry(QtCore.QRect(650, 170, 100, 23))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(lambda: self.stat(False))
        self.pushButton.setText("提交")
        # 导出
        self.exportButton = QtWidgets.QPushButton(Form)
        self.exportButton.setGeometry(QtCore.QRect(650, 200, 100, 23))
        self.exportButton.setObjectName("exportButton")
        self.exportButton.setText('导出excel')
        self.exportButton.clicked.connect(lambda: self.stat(True))
        # 实例化QComBox对象
        self.cb = QComboBox(Form)
        self.cb.setGeometry(QtCore.QRect(650, 100, 100, 23))
        self.cb.addItems(['近7天', '近30天', '本周', '本月', '本年度'])
        self.cb.setCurrentIndex(0)
        self.cb.currentIndexChanged.connect(self.change_cb)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def change_cb(self):
        self.worklogs = None

    def stat(self, export):
        if not export:
            self.textEdit.setText('')
        try:
            diff = get_diff_selected(self.cb.currentIndex())
            jql = "assignee = currentUser() and updated >=%(name)sd " % {'name': diff}
            jira = configUtils.jira_client()
            if not hasattr(self, 'worklogs') or not self.worklogs:
                issues = jira.search_issues(jql, maxResults=-1, fields=['customfield_11907', 'summary', 'created'])
                self.worklogs = jiraUtils.get_worklogs(issues, '个人', diff, None, None)
            if self.worklogs:
                df = pd.DataFrame(self.worklogs)
                self.textEdit.setHtml(df.to_html())
                if export:
                    filepath = configUtils.export
                    if os.path.exists(filepath):
                        os.remove(filepath)
                    book = Workbook()
                    writer = pd.ExcelWriter(filepath, engine='openpyxl')
                    writer.sheets = dict((ws.title, ws) for ws in book.worksheets)
                    df.to_excel(writer, "组内工作汇总")
                    writer.save()
                    QMessageBox.information(self, "文件导出成功", '文件已经导出到目录:' + filepath, QMessageBox.Yes)
                    subprocess.call(["open", filepath])

        except Exception as e:
            QMessageBox.warning(self, "警告", str(e), QMessageBox.Yes)
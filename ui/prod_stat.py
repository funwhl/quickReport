import os
import subprocess

import pandas as pd
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QDateTime
from PyQt5.QtWidgets import QMessageBox, QComboBox, QLabel, QDateTimeEdit
from openpyxl import Workbook

from util import configUtils, jiraUtils


class Ui_Form(QtWidgets.QMainWindow):

    def __init__(self):
        super(Ui_Form, self).__init__()
        try:
            self.setupUi(self)
            self.retranslateUi(self)
        except Exception as e:
            QMessageBox.warning(self, "警告", str(e), QMessageBox.Yes)

    def setupUi(self, Form):
        self.he = QLabel('产品统计:', self)
        self.he.setStyleSheet("color:green")
        self.he.setGeometry(QtCore.QRect(13, 10, 100, 40))

        self.textEdit = QtWidgets.QTextBrowser(Form)
        self.textEdit.setGeometry(QtCore.QRect(13, 53, 600, 470))
        self.textEdit.setFocusPolicy(QtCore.Qt.NoFocus)
        self.pushButton = QtWidgets.QPushButton(Form)
        self.pushButton.setGeometry(QtCore.QRect(650, 170, 100, 23))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(lambda: self.stat(False))
        # 导出
        self.exportButton = QtWidgets.QPushButton(Form)
        self.exportButton.setGeometry(QtCore.QRect(650, 200, 100, 23))
        self.exportButton.setObjectName("exportButton")
        self.exportButton.setText('导出excel')
        self.exportButton.clicked.connect(lambda: self.stat(True))
        # 选择日期from
        self.dateEdit = QDateTimeEdit(QDateTime.currentDateTime(), self)
        self.dateEdit.setDisplayFormat('yyyy-MM-dd')
        self.dateEdit.setCalendarPopup(True)
        self.dateEdit.setGeometry(QtCore.QRect(100, 20, 120, 23))

        self.he = QLabel('-', self)
        self.he.setStyleSheet("color:green")
        self.he.setGeometry(QtCore.QRect(225, 10, 20, 40))
        # 选择日期to
        self.dateEdit2 = QDateTimeEdit(QDateTime.currentDateTime(), self)
        self.dateEdit2.setDisplayFormat('yyyy-MM-dd')
        self.dateEdit2.setCalendarPopup(True)
        self.dateEdit2.setGeometry(QtCore.QRect(240, 20, 120, 23))

        # self.dp = QtWidgets.QPushButton(Form)
        # self.dp.setGeometry(QtCore.QRect(650, 230, 100, 23))
        # self.dp.setObjectName("dateButton")
        # self.dp.setText('选择日期')
        # self.dp.clicked.connect(lambda: self.stat(True))

        # 实例化QComBox对象
        # self.cb = QComboBox(Form)
        # self.cb.setGeometry(QtCore.QRect(650, 100, 100, 23))
        # self.cb.addItems(['近7天', '近30天', '本周', '本月', '本年度'])
        # self.cb.setCurrentIndex(0)
        # self.cb.currentIndexChanged.connect(self.change_cb)
        # 查询范围
        self.cb2 = QComboBox(Form)
        self.cb2.setGeometry(QtCore.QRect(650, 130, 100, 23))
        self.cb2.addItems(configUtils.prod_range)
        self.cb2.setCurrentIndex(0)
        self.cb2.currentIndexChanged.connect(lambda: configUtils.set_prod_range(self.cb2.currentIndex()))

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def change_cb(self):
        self.worklogs = None

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "项目统计"))
        self.pushButton.setText(_translate("Form", "查询"))

    def stat(self, export):
        if not export:
            self.textEdit.setText('')
        try:
            # diff = get_diff_selected(self.cb.currentIndex())
            diff = None
            fromDate = str(self.dateEdit.dateTime().date().getDate())[1:-1].replace(' ', '').replace(',', '-')
            toDate = str(self.dateEdit2.dateTime().date().getDate())[1:-1].replace(' ', '').replace(',', '-')

            jql = "worklogDate >= '%(from)s' and worklogDate <= '%(to)s' and cf[12000]" \
                  " is not EMPTY" % {'from': fromDate, 'to': toDate}
            jira = configUtils.jira_client()
            # if not hasattr(self, 'worklogs') or not self.worklogs:
            if True:
                issues = jira.search_issues(jql, maxResults=-1,
                                            fields=['customfield_12000', 'summary', 'project', 'worklog'])
                worklogs = jiraUtils.get_worklogs(issues, '产品', diff, self.dateEdit.dateTime(),
                                                  self.dateEdit2.dateTime())
                self.worklogs = worklogs
            if self.worklogs:
                df = pd.DataFrame(self.worklogs)
                gr = ['产品', '部门', '姓名', '工作事项']
                cgr = configUtils.prod_range[self.cb2.currentIndex()]
                for index, item in enumerate(gr):
                    if cgr.__contains__(item):
                        self.textEdit.setHtml(df.groupby(gr[index:]).agg('sum').to_html())
                        if export:
                            filepath = configUtils.export
                            if os.path.exists(filepath):
                                os.remove(filepath)
                            book = Workbook()
                            writer = pd.ExcelWriter(filepath, engine='openpyxl')
                            writer.sheets = dict((ws.title, ws) for ws in book.worksheets)
                            df.groupby(gr).agg('sum').to_excel(writer, "明细")
                            df.groupby(['部门']).agg('sum').to_excel(writer, "岗位汇总")
                            df.groupby(['姓名']).agg('sum').to_excel(writer, "个人汇总")
                            df.groupby(['产品']).agg('sum').to_excel(writer, "产品汇总")
                            writer.save()
                            QMessageBox.information(self, "文件导出成功", '文件已经导出到目录:' + filepath, QMessageBox.Yes)
                            subprocess.call(["open", filepath])
        except Exception as e:
            QMessageBox.warning(self, "警告", str(e), QMessageBox.Yes)

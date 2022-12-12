import os
import sys
import traceback

import bs4
import markdown
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QMetaObject, pyqtSlot, Qt
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QMessageBox, QComboBox, QFileDialog, QLabel, QApplication, QInputDialog, QAction, QMenu

import work_report
from reportError import ReportError
from util import configUtils, jiraUtils
from util.configUtils import lf


class Ui_Form(QtWidgets.QMainWindow):

    def __init__(self):
        super(Ui_Form, self).__init__()
        try:
            self.setupUi(self)
        except Exception as e:
            QMessageBox.warning(self, "警告", str(e), QMessageBox.Yes)

    def file(self):
        try:
            filename = QFileDialog.getOpenFileNames(self, '选择图像', os.path.dirname(sys.argv[0]), "Text Files(*.md)")
            if filename[0]:
                filename = filename[0][0]
                configUtils.set_path(filename)
                self.fileT.setText(filename)
                self.textEdit.setText(''.join(self.read_md()))
        except Exception as e:
            QMessageBox.warning(self, "警告", str(e), QMessageBox.Yes)

    def refresh(self):
        if configUtils.path():
            self.textEdit.setText(''.join(self.read_md()))

    def clear(self):
        configUtils.set_path('')
        self.fileT.setText('')
        self.textEdit.setText('')

    def clearSubmit(self):
        confirm = QMessageBox.question(self, '⚠', '清理提交缓存后可以重复提交！')
        if confirm == QMessageBox.Yes:
            work_report.temp = []

    # 检测键盘回车按键
    def keyPressEvent(self, event):
        if (event.key() == Qt.Key_Enter) or (event.key() == Qt.Key_Return):
            self.submit()

    def read_md(self):
        lines = open(configUtils.path(), 'r', encoding='utf-8').readlines()
        index = 0
        for i in reversed(lines):
            index = index + 1
            if i.startswith("##"):
                return lines[len(lines) - index:]

    def preview(self):
        text = self.textEdit.toPlainText()
        text = work_report.completed(text)
        self.htmlEdit.setHtml(
            str(bs4.BeautifulSoup(markdown.markdown(text).replace("\n", ''),
                                  'html.parser'))
        )

    def copyPreview(self):
        QApplication.clipboard().setText(self.textEdit.toPlainText())

    def copydd(self):
        txt = []
        for i in self.textEdit.toPlainText().splitlines():
            if i.startswith("## "):
                continue
            txt.append(i.split('/')[0])
        QApplication.clipboard().setText('\n'.join(txt))

    def set_group(self, group):
        configUtils.set_group(group)
        # todo 刷新父控件statuBar

    def submit(self):
        text = self.htmlEdit.toMarkdown()
        try:
            project = configUtils.project()
            sprints = jiraUtils.get_sprints(project)
            if not sprints:
                QMessageBox.warning(self, "警告", "未找到正在冲刺的sprint, 请联系管理员在jira上添加!!!", QMessageBox.Yes)
                return
            item, ok = QInputDialog.getItem(self, '请选择sprint', '即将提交到以下sprint', [i['name'] for i in sprints])
            if ok:
                sprint = list(filter(lambda x: x['name'] == item, sprints))[0]
            else:
                return
            confirm = QMessageBox.question(self, '⚠', '请检查预览窗口格式无误后，点击yes确认提交！')
            if confirm == QMessageBox.Yes:
                work_report.work(text, sprint['id'], project)
        except ReportError as e:
            QMessageBox.information(self, "提交状态", e.msg, QMessageBox.Yes)
        except Exception as e:
            QMessageBox.warning(self, "警告", "提交异常，请检查错误日志", QMessageBox.Yes)
            with open(lf, "w+", encoding='utf-8') as f:
                f.write(str(e))
            self.cb.setFocus()
            traceback.print_exc()

    @pyqtSlot()
    def on_edit_textChanged(self):
        self.preview()

    def create_rightmenu(self):
        self.groupBox_menu = QMenu(self)
        self.actionA = QAction(u'选择产品', self)
        self.actionA.setShortcutVisibleInContextMenu(True)
        # self.actionA.setShortcut(QKeySequence("Ctrl+S"))
        self.groupBox_menu.addAction(self.actionA)

        self.actionB = QAction(u'选择项目', self)
        self.groupBox_menu.addAction(self.actionB)

        self.actionA.triggered.connect(self.button)
        self.actionB.triggered.connect(self.button_2)

        self.groupBox_menu.popup(QCursor.pos())  # 声明当鼠标在groupBox控件上右击时，在鼠标位置显示右键菜单   ,exec_,popup两个都可以，

    def button(self):
        prods = configUtils.get_prods()
        item, ok = QInputDialog.getItem(self, '选择产品', '请在下拉列表中选择对应的产品', [i['value'] for i in prods])
        if ok:
            sprint = list(filter(lambda x: x['value'] == item, prods))[0]
            self.textEdit.textCursor().insertText(sprint['value'])
        else:
            return

    def button_2(self):
        projects = configUtils.get_prjs()
        item, ok = QInputDialog.getItem(self, '选择项目', '请在下拉列表中选择对应的项目', [i['value'] for i in projects])
        if ok:
            sprint = list(filter(lambda x: x['value'] == item, projects))[0]
            self.textEdit.textCursor().insertText('['+sprint['value']+']')
        else:
            return


    def setupUi(self, Form):
        self.selectButton = QtWidgets.QPushButton(Form)
        self.selectButton.setGeometry(QtCore.QRect(8, 1, 100, 40))
        self.selectButton.setObjectName("pushButton")
        self.selectButton.clicked.connect(self.file)

        self.clearButton = QtWidgets.QPushButton(Form)
        self.clearButton.setGeometry(QtCore.QRect(550, 1, 60, 40))
        self.clearButton.setObjectName("clearButton")
        self.clearButton.clicked.connect(self.clear)

        self.rfButton = QtWidgets.QPushButton(Form)
        self.rfButton.setGeometry(QtCore.QRect(600, 1, 60, 40))
        self.rfButton.setObjectName("clearButton")
        self.rfButton.clicked.connect(self.refresh)

        # 设置显⽰窗⼝参数
        self.fileT = QtWidgets.QPushButton(Form)
        self.fileT.setGeometry(QtCore.QRect(110, 1, 450, 40))
        self.fileT.setObjectName("file")
        self.fileT.setText(configUtils.path())
        # 主窗⼝及菜单栏标题栏设
        self.te = QLabel('内容编辑窗口:', self)
        self.te.setStyleSheet("color:red")
        self.te.setGeometry(QtCore.QRect(13, 50, 100, 40))
        self.textEdit = QtWidgets.QTextEdit(Form)
        # 设置右键菜单
        self.textEdit.setContextMenuPolicy(Qt.CustomContextMenu)
        self.textEdit.customContextMenuRequested.connect(self.create_rightmenu)  # 连接到菜单显示函数

        self.textEdit.setGeometry(QtCore.QRect(13, 80, 600, 200))
        self.textEdit.setTabStopWidth(self.textEdit.fontMetrics().width(' ') * 4)
        if configUtils.path():
            self.textEdit.setText(''.join(self.read_md()))
        self.textEdit.setObjectName("edit")
        QMetaObject.connectSlotsByName(self)

        self.he = QLabel('内容预览窗口:', self)
        self.he.setStyleSheet("color:green")
        self.he.setGeometry(QtCore.QRect(13, 290, 100, 40))
        self.htmlEdit = QtWidgets.QTextBrowser(Form)
        self.htmlEdit.setGeometry(QtCore.QRect(13, 320, 600, 200))
        self.htmlEdit.setFocusPolicy(QtCore.Qt.NoFocus)
        self.preview()

        # self.textEdit.setAutoFormatting(QTextEdit)
        self.pushButton = QtWidgets.QPushButton(Form)
        self.pushButton.setGeometry(QtCore.QRect(650, 170, 100, 23))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(lambda: self.submit())

        self.pushButton2 = QtWidgets.QPushButton(Form)
        self.pushButton2.setGeometry(QtCore.QRect(650, 200, 100, 23))
        self.pushButton2.setObjectName("pushButton2")
        self.pushButton2.clicked.connect(self.clearSubmit)

        self.copyButton = QtWidgets.QPushButton(Form)
        self.copyButton.setGeometry(QtCore.QRect(650, 370, 100, 23))
        self.copyButton.setObjectName("copyButton")
        self.copyButton.clicked.connect(self.copyPreview)

        self.copyButton2 = QtWidgets.QPushButton(Form)
        self.copyButton2.setGeometry(QtCore.QRect(650, 400, 100, 23))
        self.copyButton2.setObjectName("copyButton")
        self.copyButton2.clicked.connect(self.copydd)

        # 实例化QComBox对象
        self.cb = QComboBox(Form)
        # self.cb.move(350, 100)
        self.cb.setGeometry(QtCore.QRect(650, 100, 100, 23))

        self.cb.addItems(list(configUtils.projects.keys()))
        # if configUtils.config.has_option('General', 'myGroup') and configUtils.groups.count(
        #         configUtils.my_graoup()) == 0:
        #     self.cb.addItem(configUtils.my_graoup())
        self.cb.setCurrentIndex(configUtils.group_index())
        self.cb.currentIndexChanged.connect(lambda: self.set_group(self.cb.currentIndex()))

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "jira工作面板生成"))
        self.pushButton.setText(_translate("Form", "提交"))
        self.pushButton2.setText(_translate("Form", "清空提交缓存"))
        self.selectButton.setText(_translate("Form", "从文件读取"))
        self.clearButton.setText(_translate("Form", "❌"))
        self.rfButton.setText(_translate("Form", "刷新"))
        self.copyButton.setText(_translate("Form", "拷贝"))
        self.copyButton2.setText(_translate("Form", "简洁拷贝"))

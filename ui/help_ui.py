import requests
from PyQt5 import QtCore, QtWidgets


class Ui_Form(QtWidgets.QMainWindow):

    def __init__(self):
        super(Ui_Form, self).__init__()
        self.setupUi(self)

    def setupUi(self, Form):
        self.resize(1200, 800)
        self.textEdit = QtWidgets.QTextBrowser(Form)
        self.textEdit.setGeometry(QtCore.QRect(13, 23, 1050, 750))
        self.textEdit.setFocusPolicy(QtCore.Qt.NoFocus)
        r = requests.get('https://fisherbear.cn/imgs/README.md')
        self.textEdit.setMarkdown(r.text)
        QtCore.QMetaObject.connectSlotsByName(Form)
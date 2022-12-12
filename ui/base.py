from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QAction

from ui import report, project_stat, group_stat, my_stat, help_ui, prod_stat
from util import configUtils

menu_titles = ['周报', '项目', '产品', '组内', '个人', '关于', '帮助?']


class Ui_MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(Ui_MainWindow, self).__init__()

    def hello_(self, menu):
        if menu == 6:
            self.cw = help_ui.Ui_Form()
            self.cw.show()

        else:
            self.stackedWidget.setCurrentIndex(menu)
            self.retranslateUi()

    def setupUi(self):
        self.setObjectName("MainWindow")
        self.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")

        # 创建stackedWidget
        self.stackedWidget = QtWidgets.QStackedWidget(self.centralwidget)
        self.stackedWidget.setGeometry(QtCore.QRect(1, 1, 751, 521))
        self.setCentralWidget(self.centralwidget)

        # self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        # self.gridLayout.setObjectName("gridLayout")

        # self.stackedWidget.addWidget(label)

        # self.listView = QtWidgets.QListView(self.centralwidget)
        # self.listView.setObjectName("listView")

        # self.gridLayout.addWidget(self.listView, 0, 0, 1, 1)
        # self.gridLayout.addWidget(self.pushButton_5, 6, 0, 1, 1)

        self.setCentralWidget(self.centralwidget)
        self.bar = QtWidgets.QMenuBar(self)
        self.bar.setGeometry(1, 40, 578, 40)
        self.bar.setObjectName("menubar")

        self.m_report = QAction(self.centralwidget)
        self.m_report.triggered.connect(lambda: self.hello_(0))

        self.m_project = QAction(self.centralwidget)
        self.m_project.triggered.connect(lambda: self.hello_(1))

        self.m_prod = QAction(self.centralwidget)
        self.m_prod.triggered.connect(lambda: self.hello_(2))

        self.m_group = QAction(self.centralwidget)
        self.m_group.triggered.connect(lambda: self.hello_(3))

        self.m_my = QAction(self.centralwidget)
        self.m_my.triggered.connect(lambda: self.hello_(4))

        self.m_about = QAction(self.centralwidget)
        self.m_about.triggered.connect(lambda: self.hello_(5))

        self.m_help = QAction(self.centralwidget)
        self.m_help.triggered.connect(lambda: self.hello_(6))

        self.setMenuBar(self.bar)

        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.statusbar.showMessage("当前用户: %s    |    选择组织: %s" % (configUtils.user(),
                                                                  list(configUtils.projects.keys())[
                                                                      configUtils.group_index()]))
        self.setStatusBar(self.statusbar)

        self.bar.addAction(self.m_report)
        self.bar.addAction(self.m_project)
        self.bar.addAction(self.m_prod)
        self.bar.addAction(self.m_group)
        self.bar.addAction(self.m_my)
        self.bar.addAction(self.m_about)
        self.bar.addAction(self.m_help)
        self.bar.setStyleSheet("border :2px; solid; color: #87CEEB")
        self.bar.setNativeMenuBar(False)

        QtCore.QMetaObject.connectSlotsByName(self)

        hasPermission = configUtils.permissions()
        form = report.Ui_Form()
        self.stackedWidget.addWidget(form)
        form = project_stat.Ui_Form()
        form.type = 1
        self.stackedWidget.addWidget(QLabel("没有权限！！！") if not hasPermission else form)

        form = prod_stat.Ui_Form()
        form.type = 2
        self.stackedWidget.addWidget(QLabel("没有权限！！！") if not hasPermission else form)

        form = group_stat.Ui_Form()
        form.type = 3
        self.stackedWidget.addWidget(QLabel("没有权限！！！") if not hasPermission else form)
        form = my_stat.Ui_Form()
        form.type = 4
        self.stackedWidget.addWidget(form)
        l = QLabel("v2.0:\n"
                   "1.降低格式限制要求，对大多数格式书写错误自动补全。\n"
                   "2.增加统计功能,项目耗时统计。 \n"
                   "3.优化错误提示，提示信息及错误行数 \n"
                   "4.增加周报文件读取及解析最后一次工作内容 \n"
                   "5.大幅度优化启动速度\n"
                   "6.优化程序处理逻辑，提升操作速度\n"
                   "                                                    "
                   "                                                    "
                   , self.centralwidget)  # 创建一个标签
        l.adjustSize()  # 根据内容适应标签大小
        l.setStyleSheet("background-color: grey;")
        l.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        # 缩进和边距
        l.setIndent(100)
        # l.setMargin(50)
        # 图片自适应窗口大小
        l.setScaledContents(True)
        # 打开文本链接
        l.setOpenExternalLinks(True)
        # 单词换行
        l.setWordWrap(True)
        # pe = QPalette()
        # pe.setColor(QPalette.WindowText, Qt.black)  # 设置字体颜色
        # l.setAutoFillBackground(True)  # 设置背景充满，为设置背景颜色的必要条件
        # pe.setColor(QPalette.Window, Qt.gray)  # 设置背景颜色
        # l.setPalette(pe)
        self.stackedWidget.addWidget(l)
        self.retranslateUi()


    def retranslateUi(self):
        i = self.stackedWidget.currentIndex()
        titles = ['周报提交', '项目支持统计', '产品统计', '组内工作统计', '我的工作统计', '关于此工具']
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(titles[i])
        self.m_report.setText(menu_titles[0])
        self.m_project.setText(menu_titles[1])
        self.m_prod.setText(menu_titles[2])
        self.m_group.setText(menu_titles[3])
        self.m_my.setText(menu_titles[4])
        self.m_about.setText(menu_titles[5])
        self.m_help.setText(menu_titles[6])
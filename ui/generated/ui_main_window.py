# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
##
## Created by: Qt User Interface Compiler version 6.10.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QDoubleSpinBox, QGridLayout, QGroupBox,
    QLabel, QLineEdit, QMainWindow, QPushButton,
    QSizePolicy, QSpinBox, QStatusBar, QTabWidget,
    QTextEdit, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(463, 368)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.vboxLayout = QVBoxLayout(self.centralwidget)
        self.vboxLayout.setObjectName(u"vboxLayout")
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.gridLayout = QGridLayout(self.tab)
        self.gridLayout.setObjectName(u"gridLayout")
        self.groupBox = QGroupBox(self.tab)
        self.groupBox.setObjectName(u"groupBox")
        self.verticalLayout = QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.dsp_fly_duration = QDoubleSpinBox(self.groupBox)
        self.dsp_fly_duration.setObjectName(u"dsp_fly_duration")
        self.dsp_fly_duration.setDecimals(1)
        self.dsp_fly_duration.setSingleStep(0.100000000000000)
        self.dsp_fly_duration.setValue(2.000000000000000)

        self.gridLayout_2.addWidget(self.dsp_fly_duration, 3, 1, 1, 2)

        self.sp_fly_times = QSpinBox(self.groupBox)
        self.sp_fly_times.setObjectName(u"sp_fly_times")
        self.sp_fly_times.setValue(1)

        self.gridLayout_2.addWidget(self.sp_fly_times, 4, 1, 1, 2)

        self.label_4 = QLabel(self.groupBox)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout_2.addWidget(self.label_4, 3, 0, 1, 1)

        self.btn_bind_game = QPushButton(self.groupBox)
        self.btn_bind_game.setObjectName(u"btn_bind_game")

        self.gridLayout_2.addWidget(self.btn_bind_game, 0, 0, 1, 1)

        self.le_start_click_y = QLineEdit(self.groupBox)
        self.le_start_click_y.setObjectName(u"le_start_click_y")

        self.gridLayout_2.addWidget(self.le_start_click_y, 1, 2, 1, 1)

        self.label_5 = QLabel(self.groupBox)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout_2.addWidget(self.label_5, 4, 0, 1, 1)

        self.btn_capture_start_click = QPushButton(self.groupBox)
        self.btn_capture_start_click.setObjectName(u"btn_capture_start_click")

        self.gridLayout_2.addWidget(self.btn_capture_start_click, 1, 0, 1, 1)

        self.le_start_click_x = QLineEdit(self.groupBox)
        self.le_start_click_x.setObjectName(u"le_start_click_x")

        self.gridLayout_2.addWidget(self.le_start_click_x, 1, 1, 1, 1)

        self.le_action_click_y = QLineEdit(self.groupBox)
        self.le_action_click_y.setObjectName(u"le_action_click_y")

        self.gridLayout_2.addWidget(self.le_action_click_y, 2, 2, 1, 1)

        self.btn_capture_action_click = QPushButton(self.groupBox)
        self.btn_capture_action_click.setObjectName(u"btn_capture_action_click")

        self.gridLayout_2.addWidget(self.btn_capture_action_click, 2, 0, 1, 1)

        self.le_action_click_x = QLineEdit(self.groupBox)
        self.le_action_click_x.setObjectName(u"le_action_click_x")

        self.gridLayout_2.addWidget(self.le_action_click_x, 2, 1, 1, 1)

        self.le_window_name = QLineEdit(self.groupBox)
        self.le_window_name.setObjectName(u"le_window_name")

        self.gridLayout_2.addWidget(self.le_window_name, 0, 1, 1, 2)

        self.btn_trace_toggle = QPushButton(self.groupBox)
        self.btn_trace_toggle.setObjectName(u"btn_trace_toggle")

        self.gridLayout_2.addWidget(self.btn_trace_toggle, 5, 2, 1, 1)

        self.btn_mask_toggle = QPushButton(self.groupBox)
        self.btn_mask_toggle.setObjectName(u"btn_mask_toggle")

        self.gridLayout_2.addWidget(self.btn_mask_toggle, 5, 1, 1, 1)


        self.verticalLayout.addLayout(self.gridLayout_2)


        self.gridLayout.addWidget(self.groupBox, 1, 0, 1, 1)

        self.te_result = QTextEdit(self.tab)
        self.te_result.setObjectName(u"te_result")

        self.gridLayout.addWidget(self.te_result, 3, 0, 1, 1)

        self.groupBox_2 = QGroupBox(self.tab)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.verticalLayout_2 = QVBoxLayout(self.groupBox_2)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.gridLayout_6 = QGridLayout()
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.lbl_status = QLabel(self.groupBox_2)
        self.lbl_status.setObjectName(u"lbl_status")
        self.lbl_status.setMinimumSize(QSize(75, 0))

        self.gridLayout_6.addWidget(self.lbl_status, 1, 1, 1, 1)

        self.label = QLabel(self.groupBox_2)
        self.label.setObjectName(u"label")

        self.gridLayout_6.addWidget(self.label, 1, 0, 1, 1)

        self.label_2 = QLabel(self.groupBox_2)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout_6.addWidget(self.label_2, 2, 0, 1, 1)

        self.lbl_height = QLabel(self.groupBox_2)
        self.lbl_height.setObjectName(u"lbl_height")

        self.gridLayout_6.addWidget(self.lbl_height, 2, 1, 1, 1)

        self.lbl_timer = QLabel(self.groupBox_2)
        self.lbl_timer.setObjectName(u"lbl_timer")

        self.gridLayout_6.addWidget(self.lbl_timer, 0, 1, 1, 1)


        self.verticalLayout_2.addLayout(self.gridLayout_6)


        self.gridLayout.addWidget(self.groupBox_2, 1, 1, 1, 1)

        self.groupBox_3 = QGroupBox(self.tab)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.verticalLayout_3 = QVBoxLayout(self.groupBox_3)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.gridLayout_7 = QGridLayout()
        self.gridLayout_7.setObjectName(u"gridLayout_7")
        self.btn_action = QPushButton(self.groupBox_3)
        self.btn_action.setObjectName(u"btn_action")

        self.gridLayout_7.addWidget(self.btn_action, 0, 0, 1, 1)

        self.btn_reset = QPushButton(self.groupBox_3)
        self.btn_reset.setObjectName(u"btn_reset")

        self.gridLayout_7.addWidget(self.btn_reset, 1, 0, 1, 1)


        self.verticalLayout_3.addLayout(self.gridLayout_7)


        self.gridLayout.addWidget(self.groupBox_3, 3, 1, 1, 1)

        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.tabWidget.addTab(self.tab_2, "")

        self.vboxLayout.addWidget(self.tabWidget)

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"PetHunter", None))
        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"config", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"fly_duration", None))
        self.btn_bind_game.setText(QCoreApplication.translate("MainWindow", u"bind", None))
        self.le_start_click_y.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Y", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"fly_times", None))
        self.btn_capture_start_click.setText(QCoreApplication.translate("MainWindow", u"capture_start", None))
        self.le_start_click_x.setPlaceholderText(QCoreApplication.translate("MainWindow", u"X", None))
        self.le_action_click_y.setText("")
        self.le_action_click_y.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Y", None))
        self.btn_capture_action_click.setText(QCoreApplication.translate("MainWindow", u"capture_action", None))
        self.le_action_click_x.setText("")
        self.le_action_click_x.setPlaceholderText(QCoreApplication.translate("MainWindow", u"X", None))
        self.le_window_name.setText(QCoreApplication.translate("MainWindow", u"HTID \u4e0e \u4e2d\u95f4\u4ef6.md - Typora", None))
        self.btn_trace_toggle.setText(QCoreApplication.translate("MainWindow", u"trace", None))
        self.btn_mask_toggle.setText(QCoreApplication.translate("MainWindow", u"mask", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("MainWindow", u"status", None))
        self.lbl_status.setText("")
        self.label.setText(QCoreApplication.translate("MainWindow", u"status", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"height", None))
        self.lbl_height.setText("")
        self.lbl_timer.setText(QCoreApplication.translate("MainWindow", u"timer", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("MainWindow", u"control", None))
        self.btn_action.setText(QCoreApplication.translate("MainWindow", u"action", None))
        self.btn_reset.setText(QCoreApplication.translate("MainWindow", u"reset", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("MainWindow", u"Tab 1", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QCoreApplication.translate("MainWindow", u"Tab 2", None))
    # retranslateUi


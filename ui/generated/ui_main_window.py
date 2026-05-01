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
from PySide6.QtWidgets import (QAbstractSpinBox, QApplication, QDoubleSpinBox, QGridLayout,
    QGroupBox, QLabel, QLineEdit, QMainWindow,
    QPushButton, QSizePolicy, QSpinBox, QStatusBar,
    QTabWidget, QTextEdit, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(459, 502)
        MainWindow.setStyleSheet(u"            QMainWindow {\n"
"                background-color: #2b2d30;\n"
"            }\n"
"\n"
"            QWidget {\n"
"                background-color: #33363a;\n"
"                color: #e8eaed;                 /* \u4e3b\u6587\u5b57 */\n"
"                font-family: \"Microsoft YaHei\";\n"
"                font-size: 9pt;\n"
"            }\n"
"\n"
"            /* ================= Tab ================= */\n"
"            QTabWidget::pane {\n"
"                border: 1px solid #4a4f55;\n"
"                background-color: #2f3236;\n"
"                border-radius: 6px;\n"
"                top: -1px;\n"
"            }\n"
"\n"
"            QTabBar::tab {\n"
"                background-color: #3a3f45;\n"
"                border: 1px solid #555b62;\n"
"                border-bottom: none;\n"
"                padding: 6px 12px;\n"
"                min-width: 86px;\n"
"                color: #c7ccd1;                 /* \u6b21\u6587\u5b57 */\n"
"                border-top-left-radius: 5px;\n"
"         "
                        "       border-top-right-radius: 5px;\n"
"            }\n"
"\n"
"            QTabBar::tab:selected {\n"
"                background-color: #2f3236;\n"
"                color: #ffffff;\n"
"            }\n"
"\n"
"            /* ================= Label ================= */\n"
"            QLabel {\n"
"                background-color: transparent;\n"
"                color: #d0d6dc;                 /* \u63d0\u5347\u5bf9\u6bd4 */\n"
"            }\n"
"\n"
"            /* ================= \u8f93\u5165\u63a7\u4ef6 ================= */\n"
"            QLineEdit, QSpinBox, QDoubleSpinBox, QTextEdit {\n"
"                background-color: #1f2124;      /* \u66f4\u6df1\u80cc\u666f */\n"
"                border: 1px solid #5a6067;\n"
"                border-radius: 4px;\n"
"                color: #f2f4f6;                 /* \u63d0\u4eae\u6587\u5b57 */\n"
"                selection-background-color: #4c78a8;\n"
"                selection-color: #ffffff;\n"
"            }\n"
"\n"
"            QLineEdit {\n"
"              "
                        "  padding: 4px 6px;\n"
"            }\n"
"\n"
"            QSpinBox, QDoubleSpinBox {\n"
"                padding: 4px 24px 4px 6px;\n"
"            }\n"
"\n"
"            QSpinBox::up-button, QDoubleSpinBox::up-button {\n"
"                subcontrol-origin: border;\n"
"                subcontrol-position: top right;\n"
"                width: 18px;\n"
"                background-color: #3a3f45;\n"
"                border-left: 1px solid #5a6067;\n"
"                border-top-right-radius: 4px;\n"
"            }\n"
"\n"
"            QSpinBox::down-button, QDoubleSpinBox::down-button {\n"
"                subcontrol-origin: border;\n"
"                subcontrol-position: bottom right;\n"
"                width: 18px;\n"
"                background-color: #35393e;\n"
"                border-left: 1px solid #5a6067;\n"
"                border-bottom-right-radius: 4px;\n"
"            }\n"
"\n"
"            QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,\n"
"            QSpinBox::down-button:hover, "
                        "QDoubleSpinBox::down-button:hover {\n"
"                background-color: #4a5056;\n"
"            }\n"
"\n"
"            /* ================= \u6309\u94ae ================= */\n"
"            QPushButton {\n"
"                background-color: #3c4147;\n"
"                color: #e6e6e6;\n"
"                border: 1px solid #666c73;\n"
"                border-radius: 5px;\n"
"                padding: 5px 10px;\n"
"            }\n"
"\n"
"            QPushButton:hover {\n"
"                background-color: #4a5056;\n"
"            }\n"
"\n"
"            QPushButton:pressed {\n"
"                background-color: #2f3338;\n"
"            }\n"
"\n"
"            QPushButton:disabled {\n"
"                background-color: #3a3f45;\n"
"                color: #8b9198;\n"
"            }\n"
"\n"
"            /* ================= \u6587\u672c\u6846 ================= */\n"
"            QTextEdit {\n"
"                padding: 6px;\n"
"            }\n"
"\n"
"            /* ================= \u6eda\u52a8\u6761 ========="
                        "======== */\n"
"            QScrollBar:vertical {\n"
"                background: #2a2d31;\n"
"                width: 10px;\n"
"                margin: 0px;\n"
"            }\n"
"\n"
"            QScrollBar::handle:vertical {\n"
"                background: #5c636a;\n"
"                border-radius: 5px;\n"
"                min-height: 24px;\n"
"            }\n"
"\n"
"            QScrollBar::handle:vertical:hover {\n"
"                background: #7a828a;\n"
"            }\n"
"\n"
"            QScrollBar::add-line:vertical,\n"
"            QScrollBar::sub-line:vertical {\n"
"                height: 0px;\n"
"            }")
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
        self.gb_config = QGroupBox(self.tab)
        self.gb_config.setObjectName(u"gb_config")
        self.verticalLayout = QVBoxLayout(self.gb_config)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.gl_config = QGridLayout()
        self.gl_config.setObjectName(u"gl_config")
        self.le_action_click_x = QLineEdit(self.gb_config)
        self.le_action_click_x.setObjectName(u"le_action_click_x")

        self.gl_config.addWidget(self.le_action_click_x, 2, 1, 1, 1)

        self.btn_bind_game = QPushButton(self.gb_config)
        self.btn_bind_game.setObjectName(u"btn_bind_game")

        self.gl_config.addWidget(self.btn_bind_game, 0, 0, 1, 1)

        self.le_start_click_x = QLineEdit(self.gb_config)
        self.le_start_click_x.setObjectName(u"le_start_click_x")

        self.gl_config.addWidget(self.le_start_click_x, 1, 1, 1, 1)

        self.le_action_click_y = QLineEdit(self.gb_config)
        self.le_action_click_y.setObjectName(u"le_action_click_y")

        self.gl_config.addWidget(self.le_action_click_y, 2, 2, 1, 1)

        self.btn_mask_toggle = QPushButton(self.gb_config)
        self.btn_mask_toggle.setObjectName(u"btn_mask_toggle")

        self.gl_config.addWidget(self.btn_mask_toggle, 6, 1, 1, 1)

        self.le_start_click_y = QLineEdit(self.gb_config)
        self.le_start_click_y.setObjectName(u"le_start_click_y")

        self.gl_config.addWidget(self.le_start_click_y, 1, 2, 1, 1)

        self.btn_topmost = QPushButton(self.gb_config)
        self.btn_topmost.setObjectName(u"btn_topmost")

        self.gl_config.addWidget(self.btn_topmost, 6, 0, 1, 1)

        self.sp_fly_times = QSpinBox(self.gb_config)
        self.sp_fly_times.setObjectName(u"sp_fly_times")
        self.sp_fly_times.setMaximum(1000000)
        self.sp_fly_times.setValue(1)

        self.gl_config.addWidget(self.sp_fly_times, 4, 1, 1, 2)

        self.lbl_fly_times_caption = QLabel(self.gb_config)
        self.lbl_fly_times_caption.setObjectName(u"lbl_fly_times_caption")

        self.gl_config.addWidget(self.lbl_fly_times_caption, 4, 0, 1, 1)

        self.btn_capture_start_click = QPushButton(self.gb_config)
        self.btn_capture_start_click.setObjectName(u"btn_capture_start_click")

        self.gl_config.addWidget(self.btn_capture_start_click, 1, 0, 1, 1)

        self.btn_capture_action_click = QPushButton(self.gb_config)
        self.btn_capture_action_click.setObjectName(u"btn_capture_action_click")

        self.gl_config.addWidget(self.btn_capture_action_click, 2, 0, 1, 1)

        self.btn_trace_toggle = QPushButton(self.gb_config)
        self.btn_trace_toggle.setObjectName(u"btn_trace_toggle")

        self.gl_config.addWidget(self.btn_trace_toggle, 6, 2, 1, 1)

        self.lbl_fly_duration_caption = QLabel(self.gb_config)
        self.lbl_fly_duration_caption.setObjectName(u"lbl_fly_duration_caption")

        self.gl_config.addWidget(self.lbl_fly_duration_caption, 3, 0, 1, 1)

        self.le_window_name = QLineEdit(self.gb_config)
        self.le_window_name.setObjectName(u"le_window_name")

        self.gl_config.addWidget(self.le_window_name, 0, 1, 1, 2)

        self.dsp_fly_duration = QDoubleSpinBox(self.gb_config)
        self.dsp_fly_duration.setObjectName(u"dsp_fly_duration")
        self.dsp_fly_duration.setDecimals(4)
        self.dsp_fly_duration.setMaximum(1000000.000000000000000)
        self.dsp_fly_duration.setSingleStep(0.100000000000000)
        self.dsp_fly_duration.setValue(1.000000000000000)

        self.gl_config.addWidget(self.dsp_fly_duration, 3, 1, 1, 2)

        self.dsb_fall_speed = QDoubleSpinBox(self.gb_config)
        self.dsb_fall_speed.setObjectName(u"dsb_fall_speed")
        self.dsb_fall_speed.setDecimals(3)
        self.dsb_fall_speed.setMaximum(1000000.000000000000000)
        self.dsb_fall_speed.setSingleStep(0.100000000000000)
        self.dsb_fall_speed.setStepType(QAbstractSpinBox.DefaultStepType)

        self.gl_config.addWidget(self.dsb_fall_speed, 5, 1, 1, 2)

        self.lbl_fall_speed = QLabel(self.gb_config)
        self.lbl_fall_speed.setObjectName(u"lbl_fall_speed")

        self.gl_config.addWidget(self.lbl_fall_speed, 5, 0, 1, 1)


        self.verticalLayout.addLayout(self.gl_config)


        self.gridLayout.addWidget(self.gb_config, 1, 0, 1, 1)

        self.te_log = QTextEdit(self.tab)
        self.te_log.setObjectName(u"te_log")

        self.gridLayout.addWidget(self.te_log, 3, 0, 1, 1)

        self.gb_status = QGroupBox(self.tab)
        self.gb_status.setObjectName(u"gb_status")
        self.verticalLayout_2 = QVBoxLayout(self.gb_status)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.glstatus = QGridLayout()
        self.glstatus.setObjectName(u"glstatus")
        self.lbl_status = QLabel(self.gb_status)
        self.lbl_status.setObjectName(u"lbl_status")
        self.lbl_status.setMinimumSize(QSize(75, 0))

        self.glstatus.addWidget(self.lbl_status, 1, 1, 1, 1)

        self.lbl_status_caption = QLabel(self.gb_status)
        self.lbl_status_caption.setObjectName(u"lbl_status_caption")

        self.glstatus.addWidget(self.lbl_status_caption, 1, 0, 1, 1)

        self.lbl_height_caption = QLabel(self.gb_status)
        self.lbl_height_caption.setObjectName(u"lbl_height_caption")

        self.glstatus.addWidget(self.lbl_height_caption, 2, 0, 1, 1)

        self.lbl_height = QLabel(self.gb_status)
        self.lbl_height.setObjectName(u"lbl_height")

        self.glstatus.addWidget(self.lbl_height, 2, 1, 1, 1)

        self.lbl_timer = QLabel(self.gb_status)
        self.lbl_timer.setObjectName(u"lbl_timer")

        self.glstatus.addWidget(self.lbl_timer, 0, 1, 1, 1)


        self.verticalLayout_2.addLayout(self.glstatus)


        self.gridLayout.addWidget(self.gb_status, 1, 1, 1, 1)

        self.gb_control = QGroupBox(self.tab)
        self.gb_control.setObjectName(u"gb_control")
        self.verticalLayout_3 = QVBoxLayout(self.gb_control)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.gl_control = QGridLayout()
        self.gl_control.setObjectName(u"gl_control")
        self.btn_action = QPushButton(self.gb_control)
        self.btn_action.setObjectName(u"btn_action")

        self.gl_control.addWidget(self.btn_action, 0, 0, 1, 1)

        self.btn_reset = QPushButton(self.gb_control)
        self.btn_reset.setObjectName(u"btn_reset")

        self.gl_control.addWidget(self.btn_reset, 1, 0, 1, 1)


        self.verticalLayout_3.addLayout(self.gl_control)


        self.gridLayout.addWidget(self.gb_control, 3, 1, 1, 1)

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
        self.gb_config.setTitle(QCoreApplication.translate("MainWindow", u"\u914d\u7f6e", None))
        self.le_action_click_x.setText("")
        self.le_action_click_x.setPlaceholderText(QCoreApplication.translate("MainWindow", u"X", None))
        self.btn_bind_game.setText(QCoreApplication.translate("MainWindow", u"\u7ed1\u5b9a\u7a97\u53e3", None))
        self.le_start_click_x.setPlaceholderText(QCoreApplication.translate("MainWindow", u"X", None))
        self.le_action_click_y.setText("")
        self.le_action_click_y.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Y", None))
        self.btn_mask_toggle.setText(QCoreApplication.translate("MainWindow", u"\u5173\u95ed\u8499\u5c42", None))
        self.le_start_click_y.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Y", None))
        self.btn_topmost.setText(QCoreApplication.translate("MainWindow", u"\u7f6e\u9876", None))
        self.lbl_fly_times_caption.setText(QCoreApplication.translate("MainWindow", u"\u98de\u884c\u6b21\u6570", None))
        self.btn_capture_start_click.setText(QCoreApplication.translate("MainWindow", u"\u6355\u83b7\u8d77\u98de\u70b9", None))
        self.btn_capture_action_click.setText(QCoreApplication.translate("MainWindow", u"\u6355\u83b7\u76ee\u6807\u70b9", None))
        self.btn_trace_toggle.setText(QCoreApplication.translate("MainWindow", u"\u5173\u95ed\u8f68\u8ff9", None))
        self.lbl_fly_duration_caption.setText(QCoreApplication.translate("MainWindow", u"\u5355\u6b21\u98de\u884c\u65f6\u957f(s)", None))
        self.le_window_name.setText("")
        self.le_window_name.setPlaceholderText(QCoreApplication.translate("MainWindow", u"window", None))
        self.lbl_fall_speed.setText(QCoreApplication.translate("MainWindow", u"\u4e0b\u843d\u901f\u5ea6(m/s)", None))
        self.gb_status.setTitle(QCoreApplication.translate("MainWindow", u"\u72b6\u6001", None))
        self.lbl_status.setText("")
        self.lbl_status_caption.setText(QCoreApplication.translate("MainWindow", u"\u5f53\u524d\u72b6\u6001", None))
        self.lbl_height_caption.setText(QCoreApplication.translate("MainWindow", u"\u5b9e\u65f6\u9ad8\u5ea6", None))
        self.lbl_height.setText("")
        self.lbl_timer.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.gb_control.setTitle(QCoreApplication.translate("MainWindow", u"\u63a7\u5236", None))
        self.btn_action.setText(QCoreApplication.translate("MainWindow", u"\u5f00\u59cb\u6d4b\u91cf", None))
        self.btn_reset.setText(QCoreApplication.translate("MainWindow", u"\u91cd\u7f6e", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("MainWindow", u"\u6d4b\u91cf", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QCoreApplication.translate("MainWindow", u"\u9884\u7559", None))
    # retranslateUi


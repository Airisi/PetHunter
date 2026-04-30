from datetime import datetime
import re
from PySide6.QtCore import Qt
from PySide6.QtGui import (
    QTextCursor, QTextCharFormat, QColor,
    QAction
)
from PySide6.QtWidgets import QApplication, QStyle


class LogManager:
    """
    统一日志管理：
    - 追加日志（错误 / 警告 / 调试）
    - 合并重复日志
    - 右键菜单（清空）
    """

    COLOR_ERROR   = "#a85c53"   # 红：错误/失败
    COLOR_WARN    = "#C6A776"   # 橙：警告/可疑
    COLOR_SUCCESS = "#63a77f"   # 绿：成功/通过
    COLOR_INFO    = "#BABABA"   # 黑：普通信息
    COLOR_DEBUG   = "#BABABA"   # 深蓝：调试信息

    def __init__(self, text_browser):
        self.tb_log = text_browser

        self._last_log_tpl = None
        self._last_log_pos = None

        self._init_context_menu()

        self.debug_enabled = False        # 是否显示调试信息
        self.show_time = True             # 是否显示时间戳
        self.show_us = True               # 是否显示微秒
        self.merge_repeat_enabled = False # 是否合并重复

    # ================== 右键菜单 ==================
    def _init_context_menu(self):
        self.tb_log.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tb_log.customContextMenuRequested.connect(
            self._show_context_menu
        )

    def _show_context_menu(self, point):
        menu = self.tb_log.createStandardContextMenu()

        trash_icon = QApplication.style().standardIcon(
            QStyle.SP_DialogResetButton
        )

        clear_action = QAction(trash_icon, "Clear All", self.tb_log)
        clear_action.triggered.connect(self.clear)

        menu.addSeparator()
        menu.addAction(clear_action)
        menu.exec(self.tb_log.mapToGlobal(point))

    def clear(self):
        self.tb_log.clear()
        self._last_log_tpl = None
        self._last_log_pos = None

    # ================== 核心日志 ==================
    def _append(self, text: str, color: str):
        """
        向 QTextBrowser 添加日志，并根据时间控制选项显示时间戳
        """
        # 时间戳
        if self.show_time:
            if self.show_us:
                timestamp = datetime.now().strftime("[%H:%M:%S.%f] ")
            else:
                timestamp = datetime.now().strftime("[%H:%M:%S] ")
            text_to_insert = timestamp + text
        else:
            text_to_insert = text

        cursor = self.tb_log.textCursor()

        if self.merge_repeat_enabled:
            tpl = re.sub(r'\d+', '#', text_to_insert)

            if tpl == self._last_log_tpl and self._last_log_pos is not None:
                cursor.setPosition(self._last_log_pos)
                cursor.select(QTextCursor.LineUnderCursor)
                cursor.removeSelectedText()
                cursor.deleteChar()
            else:
                cursor.movePosition(QTextCursor.End)
                self._last_log_pos = cursor.position()
                self._last_log_tpl = tpl
                self.tb_log.moveCursor(QTextCursor.End)
        else:
            cursor.movePosition(QTextCursor.End)
            self._last_log_pos = None
            self._last_log_tpl = None
            self.tb_log.moveCursor(QTextCursor.End)

        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color))
        cursor.insertText(text_to_insert + "\n", fmt)

    # ================== 对外接口 ==================
    def error(self, text):
        self._append(text, self.COLOR_ERROR)

    def warning(self, text):
        self._append(text, self.COLOR_WARN)

    def debug(self, text):
        if self.debug_enabled:
            self._append(text, self.COLOR_DEBUG)

    def info(self, text):
        self._append(text, self.COLOR_INFO)

    def success(self, text):
        self._append(text, self.COLOR_SUCCESS)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QHBoxLayout, QLabel, QSizePolicy, QVBoxLayout, QWidget

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils import WindowTool


class GameMaskOverlay(QWidget):
    """Transparent overlay bound to the target game window."""

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.hide()

        self.game_hwnd = 0

        self.follow_timer = QTimer()
        self.follow_timer.setInterval(50)
        self.follow_timer.timeout.connect(self.follow_game_window)
        self.follow_timer.start()

        self._init_ui()

    def _init_ui(self):
        font = QFont("Microsoft YaHei", 9)

        self.lbl_height = QLabel("高度 0.00 m")
        self.lbl_height.setFont(font)
        self._configure_pill_label(self.lbl_height, "#ffffff")

        self.lbl_status = QLabel("状态 待命")
        self.lbl_status.setFont(font)
        self._configure_pill_label(self.lbl_status, "#ffffff")

        self.lbl_timer = QLabel("倒计时 0.000 s")
        self.lbl_timer.setFont(font)
        self._configure_pill_label(self.lbl_timer, "#ffffff")

        self.lbl_msg = QLabel("")
        self.lbl_msg.setFont(font)
        self.lbl_msg.setAlignment(Qt.AlignCenter)
        self._configure_pill_label(self.lbl_msg, "#ffffff")
        self.lbl_msg.hide()

        top_layout = QVBoxLayout()
        top_layout.setContentsMargins(15, 15, 15, 0)
        top_layout.setSpacing(8)
        top_layout.addLayout(self._wrap_left(self.lbl_height))
        top_layout.addLayout(self._wrap_left(self.lbl_status))
        top_layout.addLayout(self._wrap_left(self.lbl_timer))
        top_layout.addLayout(self._wrap_left(self.lbl_msg))
        top_layout.addStretch()

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addLayout(top_layout)
        self.setLayout(main_layout)

        self.msg_timer = QTimer()
        self.msg_timer.setSingleShot(True)
        self.msg_timer.timeout.connect(lambda: self._set_message_text(""))

    def _configure_pill_label(self, label: QLabel, color: str):
        label.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        label.setStyleSheet(
            "padding: 6px 10px;"
            "border-radius: 6px;"
            "background-color: rgba(29, 37, 45, 132);"
            f"color: {color};"
        )

    def _wrap_left(self, label: QLabel):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(label, 0, Qt.AlignLeft)
        layout.addStretch()
        return layout

    def _set_message_text(self, msg: str):
        text = msg.strip()
        self.lbl_msg.setText(text)
        self.lbl_msg.setVisible(bool(text))

    def bind_game_hwnd(self, hwnd: int):
        self.game_hwnd = hwnd

    def follow_game_window(self):
        if self.game_hwnd == 0:
            return

        try:
            x, y, width, height = WindowTool.get_window_rect_scaled(self.game_hwnd, client_area=True)
            if width > 0 and height > 0:
                self.setGeometry(x, y, width, height)
        except Exception as exc:
            print(f"follow_game_window failed: {exc}")
            self.game_hwnd = 0
            self.hide()

    def update_info(self, height: float, status: str):
        self.lbl_height.setText(f"高度 {height:.2f} m")
        self.lbl_status.setText(f"状态 {status}")

    def update_timer(self, remaining_ms: int):
        if remaining_ms <= 0:
            self.lbl_timer.setText("倒计时 0.000 s")
        else:
            seconds = remaining_ms / 1000.0
            self.lbl_timer.setText(f"倒计时 {seconds:.3f} s")

    def show_message(self, msg: str, duration_ms=2000):
        self._set_message_text(msg)
        if msg.strip():
            self.msg_timer.start(duration_ms)
        else:
            self.msg_timer.stop()

    def clear_trace(self):
        pass

    def add_trace(self, msg: str):
        self.show_message(msg, 2000)

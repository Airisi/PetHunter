from PySide6.QtCore import QPoint, Qt, QTimer
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from utils import WindowTool


class MouseTraceOverlay(QWidget):
    """Transparent overlay used to render automated mouse paths."""

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.hide()

        self.game_hwnd = 0
        self.trace_enabled = True
        self.items = []

        self.follow_timer = QTimer()
        self.follow_timer.setInterval(50)
        self.follow_timer.timeout.connect(self.follow_game_window)
        self.follow_timer.start()

    def bind_game_hwnd(self, hwnd: int):
        self.game_hwnd = hwnd

    def follow_game_window(self):
        if self.game_hwnd == 0:
            return

        try:
            x, y, width, height = WindowTool.get_window_rect_scaled(self.game_hwnd, client_area=True)
            if width > 0 and height > 0:
                self.setGeometry(x, y, width, height)
        except Exception:
            self.game_hwnd = 0
            self.hide()

    def add_click_point(self, point: QPoint):
        if not self.trace_enabled:
            return
        self.items.append({"type": "click", "point": QPoint(point)})
        self.update()

    def add_path(self, points: list[QPoint]):
        if not self.trace_enabled or len(points) < 2:
            return
        self.items.append({"type": "drag", "points": points[:]})
        self.update()

    def set_trace_enabled(self, state: bool):
        self.trace_enabled = state
        if not state:
            self.clear_paths()
            self.hide()
            return

        if self.game_hwnd != 0:
            self.follow_game_window()
            self.show()
        self.update()

    def clear_paths(self):
        self.items.clear()
        self.update()

    def paintEvent(self, event):
        if not self.trace_enabled or not self.items:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        for item in self.items:
            if item["type"] == "click":
                point = item["point"]
                painter.setPen(QPen(QColor(76, 160, 255, 235), 2))
                painter.setBrush(QColor(76, 160, 255, 200))
                radius = 9
                painter.drawEllipse(point, radius, radius)
                continue

            points = item["points"]
            painter.setPen(QPen(QColor(76, 160, 255, 220), 3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            for index in range(len(points) - 1):
                painter.drawLine(points[index], points[index + 1])

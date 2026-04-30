import win32api
import win32con
import win32gui
import win32process
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))
from behavior import Behavior


class WindowTool:
    _capture_timer = None
    _capture_hwnd = 0
    _capture_callback = None
    _capture_last_down = False

    @staticmethod
    def find_window_by_title(title: str) -> int:
        hwnd_list = []

        def callback(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                win_title = win32gui.GetWindowText(hwnd)
                if title.lower() in win_title.lower():
                    hwnd_list.append(hwnd)

        win32gui.EnumWindows(callback, None)
        return hwnd_list[0] if hwnd_list else 0

    @staticmethod
    def get_window_title(hwnd: int) -> str:
        if not hwnd or not win32gui.IsWindow(hwnd):
            return ""
        try:
            return win32gui.GetWindowText(hwnd)
        except Exception:
            return ""

    @staticmethod
    def get_window_rect(hwnd: int, client_area=False) -> tuple[int, int, int, int]:
        if not hwnd or not win32gui.IsWindow(hwnd):
            return 0, 0, 0, 0

        try:
            if client_area:
                rect = win32gui.GetClientRect(hwnd)
                left, top = win32gui.ClientToScreen(hwnd, (rect[0], rect[1]))
                right = left + rect[2]
                bottom = top + rect[3]
            else:
                left, top, right, bottom = win32gui.GetWindowRect(hwnd)

            width = right - left
            height = bottom - top
            if width <= 0 or height <= 0:
                return 0, 0, 0, 0

            return left, top, width, height
        except Exception:
            return 0, 0, 0, 0

    @staticmethod
    def get_window_rect_scaled(hwnd: int, client_area=False) -> tuple[int, int, int, int]:
        left, top, width, height = WindowTool.get_window_rect(hwnd, client_area)
        if width == 0:
            return 0, 0, 0, 0

        dpi_ratio = WindowTool.get_dpi_ratio()
        left = int(left / dpi_ratio)
        top = int(top / dpi_ratio)
        width = int(width / dpi_ratio)
        height = int(height / dpi_ratio)
        return left, top, width, height

    @staticmethod
    def get_dpi_ratio():
        screen = QApplication.primaryScreen()
        return screen.devicePixelRatio() if screen else 1.0

    @staticmethod
    def click_at(hwnd: int, x: int, y: int):
        """
        点击指定窗口的指定位置

        x, y 为窗口客户区坐标 (client 坐标，非屏幕坐标)
        """

        # 进行坐标抖动
        x, y = Behavior.jitter_point(x, y)

        # 将客户端坐标转换为屏幕坐标，并考虑 DPI 缩放
        dpi_ratio = WindowTool.get_dpi_ratio()
        screen_x = int(round(x * dpi_ratio))
        screen_y = int(round(y * dpi_ratio))
        client_left, client_top = win32gui.ClientToScreen(hwnd, (0, 0))
        screen_x = client_left + screen_x
        screen_y = client_top + screen_y
        # start_x, start_y = win32api.GetCursorPos()

        # 如果目标窗口不是当前前台窗口，尝试将其置于前台
        if not WindowTool.is_foreground(hwnd):
            WindowTool._bring_window_to_front(hwnd)

        # 移动鼠标到目标位置并点击
        win32api.SetCursorPos((screen_x, screen_y))
        # 等待一点时间
        Behavior.sleep()

        # 按下鼠标
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
       # 等待一点时间
        Behavior.sleep()

        # 抬起鼠标
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

        # 返回点击信息，包括起始位置、目标位置和路径点（用于绘制轨迹）
        return {
            # "start_screen": (start_x, start_y),
            "click_point": (x, y),
            # "path_points": WindowTool._interpolate_points(
            #     int(round((start_x - client_left) / dpi_ratio)),
            #     int(round((start_y - client_top) / dpi_ratio)),
            #     x,
            #     y,
            # ),
        }

    @staticmethod
    def start_capture_click(hwnd: int, callback, interval_ms=20):
        if not hwnd or not win32gui.IsWindow(hwnd):
            raise RuntimeError("invalid target window")

        WindowTool.stop_capture_click()
        WindowTool._capture_hwnd = hwnd
        WindowTool._capture_callback = callback
        WindowTool._capture_last_down = bool(win32api.GetAsyncKeyState(win32con.VK_LBUTTON) & 0x8000)
        WindowTool._capture_timer = QTimer()
        WindowTool._capture_timer.setInterval(interval_ms)
        WindowTool._capture_timer.timeout.connect(WindowTool._poll_capture_click)
        WindowTool._capture_timer.start()

    @staticmethod
    def is_capture_active():
        return WindowTool._capture_timer is not None and WindowTool._capture_timer.isActive()

    @staticmethod
    def stop_capture_click():
        if WindowTool._capture_timer is not None:
            WindowTool._capture_timer.stop()
            WindowTool._capture_timer.deleteLater()
            WindowTool._capture_timer = None
        WindowTool._capture_hwnd = 0
        WindowTool._capture_callback = None
        WindowTool._capture_last_down = False

    @staticmethod
    def _poll_capture_click():
        is_down = bool(win32api.GetAsyncKeyState(win32con.VK_LBUTTON) & 0x8000)
        if not is_down or WindowTool._capture_last_down:
            WindowTool._capture_last_down = is_down
            return

        WindowTool._capture_last_down = True
        hwnd = WindowTool._capture_hwnd
        callback = WindowTool._capture_callback
        if not hwnd or callback is None or not win32gui.IsWindow(hwnd):
            WindowTool.stop_capture_click()
            return

        screen_x, screen_y = win32api.GetCursorPos()
        if not WindowTool._is_point_in_window_client(hwnd, screen_x, screen_y):
            return

        client_x, client_y = win32gui.ScreenToClient(hwnd, (screen_x, screen_y))
        dpi_ratio = WindowTool.get_dpi_ratio()
        WindowTool.stop_capture_click()
        callback(
            int(round(client_x / dpi_ratio)),
            int(round(client_y / dpi_ratio)),
        )

    @staticmethod
    def _is_point_in_window_client(hwnd: int, screen_x: int, screen_y: int) -> bool:
        try:
            client_x, client_y = win32gui.ScreenToClient(hwnd, (screen_x, screen_y))
            _, _, width, height = WindowTool.get_window_rect(hwnd, client_area=True)
            return 0 <= client_x < width and 0 <= client_y < height
        except Exception:
            return False

    @staticmethod
    def is_foreground(hwnd: int) -> bool:
        try:
            fg = win32gui.GetForegroundWindow()
            return fg == hwnd or win32gui.GetAncestor(fg, win32con.GA_ROOT) == hwnd
        except Exception:
            return False

    @staticmethod
    def _bring_window_to_front(hwnd: int):
        try:
            win32gui.SetForegroundWindow(hwnd)
            return
        except Exception:
            pass

        try:
            thread_id, _ = win32process.GetWindowThreadProcessId(hwnd)
            current_thread_id = win32api.GetCurrentThreadId()
            win32process.AttachThreadInput(current_thread_id, thread_id, True)
            try:
                win32gui.SetForegroundWindow(hwnd)
            finally:
                win32process.AttachThreadInput(current_thread_id, thread_id, False)
        except Exception:
            pass

    @staticmethod
    def _interpolate_points(x1: int, y1: int, x2: int, y2: int, step=8):
        dx = x2 - x1
        dy = y2 - y1
        distance = max(abs(dx), abs(dy))
        segments = max(1, distance // step)
        points = []
        for index in range(segments + 1):
            ratio = index / segments
            px = int(round(x1 + dx * ratio))
            py = int(round(y1 + dy * ratio))
            points.append((px, py))
        return points

    @staticmethod
    def enum_windows():
        results = []

        def callback(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title:
                    results.append((hwnd, title))
                    print(f"{hwnd} - {title}")

        win32gui.EnumWindows(callback, None)
        return results

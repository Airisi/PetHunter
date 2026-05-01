import win32api
import win32con
import win32gui
import win32process
import time
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))
from behavior import Behavior


class WindowTool:
    _capture_image_timer = None
    _capture_image_hwnd = 0
    _capture_image_callback = None

    _capture_timer = None
    _capture_hwnd = 0
    _capture_callback = None
    _capture_last_down = False

    _capture_key_timer = None
    _capture_key_callback = None
    _capture_last_state = {}

    @staticmethod
    def capture_window(hwnd: int):
        """
        截图指定窗口客户区

        :param hwnd: 窗口句柄
        :return: (width, height, raw_bytes) 或 None
        """

        if not hwnd or not win32gui.IsWindow(hwnd):
            return None

        try:
            # 获取客户区大小
            left, top, right, bottom = win32gui.GetClientRect(hwnd)
            width = right - left
            height = bottom - top

            if width <= 0 or height <= 0:
                return None

            # 获取窗口 DC
            hwnd_dc = win32gui.GetWindowDC(hwnd)
            mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
            save_dc = mfc_dc.CreateCompatibleDC()

            # 创建位图
            save_bitmap = win32ui.CreateBitmap()
            save_bitmap.CreateCompatibleBitmap(mfc_dc, width, height)
            save_dc.SelectObject(save_bitmap)

            # 拷贝图像
            save_dc.BitBlt(
                (0, 0),
                (width, height),
                mfc_dc,
                (0, 0),
                win32con.SRCCOPY
            )

            # 获取数据
            bmpinfo = save_bitmap.GetInfo()
            bmpstr = save_bitmap.GetBitmapBits(True)

            # 释放资源
            win32gui.DeleteObject(save_bitmap.GetHandle())
            save_dc.DeleteDC()
            mfc_dc.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwnd_dc)

            return bmpinfo["bmWidth"], bmpinfo["bmHeight"], bmpstr

        except Exception:
            return None

    @staticmethod
    def start_capture_image(hwnd: int, callback, interval_ms=500):
        """
        开启定时截图

        :param hwnd: 目标窗口
        :param callback: 回调 callback(width, height, raw_bytes)
        :param interval_ms: 截图间隔(ms)
        """

        WindowTool.stop_capture_image()

        if not hwnd or not win32gui.IsWindow(hwnd):
            raise RuntimeError("invalid hwnd")

        WindowTool._capture_image_hwnd = hwnd
        WindowTool._capture_image_callback = callback

        timer = QTimer()
        timer.setInterval(interval_ms)
        timer.timeout.connect(WindowTool._poll_capture_image)
        timer.start()

        WindowTool._capture_image_timer = timer

    @staticmethod
    def stop_capture_image():
        """
        停止截图
        """

        if WindowTool._capture_image_timer:
            WindowTool._capture_image_timer.stop()
            WindowTool._capture_image_timer.deleteLater()
            WindowTool._capture_image_timer = None

        WindowTool._capture_image_hwnd = 0
        WindowTool._capture_image_callback = None

    @staticmethod
    def _poll_capture_image():
        """
        定时截图轮询
        """

        hwnd = WindowTool._capture_image_hwnd
        callback = WindowTool._capture_image_callback

        if not hwnd or callback is None or not win32gui.IsWindow(hwnd) or not WindowTool.is_foreground(hwnd):
            WindowTool.stop_capture_image()
            return

        result = WindowTool.capture_window(hwnd)
        if result:
            callback(*result)

    @staticmethod
    def find_window_by_title(title: str) -> int:
        hwnd_list = []
        minimized_list = []

        def callback(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                win_title = win32gui.GetWindowText(hwnd)
                if title.lower() in win_title.lower():
                    if win32gui.IsIconic(hwnd):
                        minimized_list.append(hwnd)   # 最小化的
                    else:
                        hwnd_list.append(hwnd)       # 未最小化的

        win32gui.EnumWindows(callback, None)

        # 优先返回未最小化窗口
        if hwnd_list:
            return hwnd_list[0]

        # 否则返回最小化窗口
        if minimized_list:
            return minimized_list[0]

        return 0

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

        # 如果目标窗口不是当前前台窗口，尝试将其置于前台
        if not WindowTool.is_foreground(hwnd):
            WindowTool._bring_window_to_front(hwnd)

        # 移动鼠标到目标位置并点击
        win32api.SetCursorPos((screen_x, screen_y))
        Behavior.sleep()

        # 按下鼠标
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        Behavior.sleep()

        # 抬起鼠标
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

        return {
            "click_point": (x, y),
        }

    @staticmethod
    def key_press(hwnd: int, vk_code: int):
        """
        向指定窗口发送一次按键（按下 + 抬起）

        :param hwnd: 目标窗口句柄
        :param vk_code: 虚拟键值 win32con.VK_*
        :return: dict
        """

        if not hwnd or not win32gui.IsWindow(hwnd):
            return None

        # 如果不是前台窗口，尝试切换
        if not WindowTool.is_foreground(hwnd):
            WindowTool._bring_window_to_front(hwnd)

        # 按下
        win32api.keybd_event(vk_code, 0, 0, 0)
        Behavior.sleep()

        # 抬起
        win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP, 0)

        return {
            "vk_code": vk_code
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
    def drag_view(dx: int, dy: int, duration=0.1, steps=10):
        """
        通过鼠标相对移动调整视角（不需要按键）

        :param dx: 水平移动
        :param dy: 垂直移动（正数=向下）
        :param duration: 持续时间
        """

        step_dx = int(dx / steps)
        step_dy = int(dy / steps)

        for _ in range(steps):
            # 相对移动（关键）
            win32api.mouse_event(
                win32con.MOUSEEVENTF_MOVE,
                step_dx,
                step_dy
            )
            if duration > 0 and steps > 0:
                time.sleep(duration / steps)

    @staticmethod
    def set_top_view():
        """
        拉到俯视最大角度
        """
        # 连续多次向下移动（直到极限）
        WindowTool.drag_view(0, 10000, 1, 10)

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

    @staticmethod
    def start_capture_key(callback, vk_list=None, interval_ms=20):
        """
        捕获键盘按键（按下瞬间触发）

        :param callback: 回调函数 callback(vk_code)
        :param vk_list: 监听键列表
        :param interval_ms: 轮询间隔
        """

        WindowTool.stop_capture_key()

        if vk_list is None:
            vk_list = [
                win32con.VK_RETURN,
                win32con.VK_SPACE,
                win32con.VK_ESCAPE,
                win32con.VK_LEFT,
                win32con.VK_RIGHT,
                win32con.VK_UP,
                win32con.VK_DOWN,
            ]

        WindowTool._capture_key_callback = callback
        WindowTool._capture_last_state = {
            vk: bool(win32api.GetAsyncKeyState(vk) & 0x8000)
            for vk in vk_list
        }

        timer = QTimer()
        timer.setInterval(interval_ms)
        timer.timeout.connect(lambda: WindowTool._poll_capture_key(vk_list))
        timer.start()

        WindowTool._capture_key_timer = timer

    @staticmethod
    def stop_capture_key():
        if WindowTool._capture_key_timer:
            WindowTool._capture_key_timer.stop()
            WindowTool._capture_key_timer.deleteLater()
            WindowTool._capture_key_timer = None

        WindowTool._capture_key_callback = None
        WindowTool._capture_last_state = {}

    @staticmethod
    def _poll_capture_key(vk_list):
        callback = WindowTool._capture_key_callback
        if callback is None:
            WindowTool.stop_capture_key()
            return

        for vk in vk_list:
            is_down = bool(win32api.GetAsyncKeyState(vk) & 0x8000)
            last = WindowTool._capture_last_state.get(vk, False)

            # 只在按下瞬间触发
            if is_down and not last:
                callback(vk)

            WindowTool._capture_last_state[vk] = is_down
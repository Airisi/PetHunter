import csv
import time
import ctypes
import win32api
import win32con
import win32gui
import win32process
from datetime import datetime

from PySide6.QtCore import QPoint, Qt
from PySide6.QtWidgets import QAbstractSpinBox, QMainWindow, QApplication

from core.mask_overlay import GameMaskOverlay
from core.mouse_trace_overlay import MouseTraceOverlay
from ui.generated.ui_main_window import Ui_MainWindow
from config.paths import screenshots_dir

import sys
from pathlib import Path 
sys.path.append(str(Path(__file__).parent.parent))
from utils import FlightMeasureTool, LogManager, WindowTool
from config.paths import measurement_results_csv_path
from config.flight_config import load_flight_config_dict, update_flight_config_dict
from utils.behavior import Behavior

RESULTS_CSV_PATH = measurement_results_csv_path()


class MainWindow(QMainWindow, Ui_MainWindow):
    """Main tool window."""

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # self.showMinimized()
        # self.setGeometry(950, 324, 500, 500)
        self.move(1300, 400)

        self.game_hwnd = None
        self.measure = FlightMeasureTool()
        self.is_measuring = False
        self.game_mask = GameMaskOverlay()
        self.mouse_trace_mask = MouseTraceOverlay()
        self._capture_target_kind = None
        self._loading_config = True
        self._cfg_mask_enabled = True
        self._cfg_trace_enabled = True
        self._cfg_topmost_enabled = True
        self.screenshots_dir = screenshots_dir()
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        self.screenshots_index = 0
        # 飞行按键状态机
        self.fly_key_state = 0      # 0=W,1=D,2=S,3=A
        self.fly_count = 0
        self.fly_current_vk = None


        self._apply_theme()
        self._configure_widgets()

        self.log = LogManager(self.te_log)

        self.measure.height_changed.connect(self.update_height)
        self.measure.state_changed.connect(self.update_status)
        self.measure.time_remaining_changed.connect(self.on_time_remaining)
        self.measure.fly_finished.connect(self.on_fly_once_finished)
        self.measure.falling_started.connect(self.on_falling_started)

        # UI 参数变更时同步到配置文件
        self.dsp_fly_duration.valueChanged.connect(self.on_fly_duration_changed)
        self.sp_fly_times.valueChanged.connect(self.on_fly_times_changed)

        self.btn_action.clicked.connect(self.on_action)
        self.btn_reset.clicked.connect(self.on_reset)
        self.btn_mask_toggle.clicked.connect(self.toggle_mask)
        self.btn_trace_toggle.clicked.connect(self.toggle_trace)
        self.btn_bind_game.clicked.connect(self.bind_game_window)
        self.btn_capture_start_click.clicked.connect(self.on_capture_start_click_once)
        self.btn_capture_action_click.clicked.connect(self.on_capture_action_click_once)
        self.btn_topmost.clicked.connect(self.toggle_topmost)

        self._apply_config_on_startup()
        self._set_idle_view()
        self.bind_game_window()
        self._apply_settings_from_config()
        self._loading_config = False

        # WindowTool.enum_windows()

    def _apply_theme(self):
        DWMWA_USE_IMMERSIVE_DARK_MODE = 20

        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            int(self.winId()),
            DWMWA_USE_IMMERSIVE_DARK_MODE,
            ctypes.byref(ctypes.c_int(1)),
            ctypes.sizeof(ctypes.c_int)
        )

    def _configure_widgets(self):
        self.te_log.setReadOnly(True)
        self.dsp_fly_duration.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.UpDownArrows)
        self.sp_fly_times.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.UpDownArrows)
        self.dsb_fall_speed.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.UpDownArrows)
        self.dsp_fly_duration.setMinimum(0.0)
        self.dsp_fly_duration.setMaximum(1000000.0)
        self.sp_fly_times.setMinimum(1)
        self.sp_fly_times.setMaximum(1000000)
        self.dsb_fall_speed.setMinimum(0.0)
        self.dsb_fall_speed.setMaximum(1000000.0)

    def _load_config(self) -> dict:
        return load_flight_config_dict()

    def _save_config(self, updates: dict) -> None:
        update_flight_config_dict(updates)

    def _get_int_from_line_edit(self, line_edit, default=None):
        text = line_edit.text().strip()
        if not text:
            return default
        try:
            return int(text)
        except Exception:
            return default

    def _apply_config_on_startup(self) -> None:
        """从配置文件初始化 UI（窗口名、飞行参数、按钮开关等）。"""
        config = self._load_config()

        self.dsp_fly_duration.setValue(float(config.get("fly_duration", self.dsp_fly_duration.value())))
        self.sp_fly_times.setValue(int(config.get("fly_times", self.sp_fly_times.value())))

        window_name = config.get("window_name", "")
        self.le_window_name.setText(window_name)

        start_click = config.get("start_click", {}) if isinstance(config.get("start_click", {}), dict) else {}
        action_click = config.get("action_click", {}) if isinstance(config.get("action_click", {}), dict) else {}
        self.le_start_click_x.setText(str(start_click.get("x", "")))
        self.le_start_click_y.setText(str(start_click.get("y", "")))
        self.le_action_click_x.setText(str(action_click.get("x", "")))
        self.le_action_click_y.setText(str(action_click.get("y", "")))

        self._cfg_mask_enabled = bool(config.get("mask_enabled", True))
        self._cfg_trace_enabled = bool(config.get("trace_enabled", True))
        self._cfg_topmost_enabled = bool(config.get("topmost_enabled", True))

    def _apply_settings_from_config(self) -> None:
        # 轨迹层蒙板配置
        if self._cfg_trace_enabled and self.mouse_trace_mask.game_hwnd != 0:
            self.mouse_trace_mask.set_trace_enabled(self._cfg_trace_enabled)
            self.btn_trace_toggle.setText("关闭轨迹")
        else:
            self.mouse_trace_mask.hide()
            self.btn_trace_toggle.setText("开启轨迹")

        # 数据层蒙板配置
        if self._cfg_mask_enabled and self.game_mask.game_hwnd != 0:
            self.game_mask.follow_game_window()
            self.game_mask.show()
            self.game_mask.raise_()#
            self.btn_mask_toggle.setText("关闭蒙层")
        else:
            self.game_mask.hide()
            self.btn_mask_toggle.setText("开启蒙层")

        # 置顶
        self.toggle_topmost(self._cfg_topmost_enabled)

    def _set_idle_view(self):
        self.lbl_status.setText("待命")
        self.lbl_height.setText("0.00 m")
        self.lbl_timer.setText("0.000 s")
        self.log.info(
            "PetHunter 辅助测量台\n"
            "等待开始测量...\n\n"
            "结果将汇总显示：\n"
            "- 总上升高度\n"
            "- 平均上升速度\n"
            "- 下落高度\n"
            "- 下落耗时\n"
            "- 下落速度\n\n"
        )
        self.game_mask.update_info(0.0, "待命")
        self.game_mask.update_timer(0)

    def _set_trace_enabled(self, enabled: bool) -> None:
        self.mouse_trace_mask.set_trace_enabled(enabled)
        self.btn_trace_toggle.setText("关闭轨迹" if enabled else "开启轨迹")

    def _get_time_str(self):
        return datetime.now().strftime("%H:%M:%S.%f")[:-3]

    def _format_result(self, data):
        return (
            "测量完成\n"
            f"单次飞行高度: {data['single_height']:.2f} m\n"
            f"飞行次数: {data['fly_times']}\n"
            f"总上升高度: {data['total_rise']:.2f} m\n"
            f"平均上升速度: {data['rise_speed']:.2f} m/s\n"
            f"预计总飞行时长: {data['total_fly_time']:.3f} s\n"
            f"下落高度: {data['fall_height']:.2f} m\n"
            f"下落耗时: {data['fall_time']:.3f} s\n"
            f"下落速度: {data['fall_speed']:.2f} m/s\n\n"
        )

    def bind_game_window(self):
        window_name = self.le_window_name.text().strip()
        if not window_name:
            self.log.warning("请先输入目标窗口标题。\n")
            return

        hwnd = WindowTool.find_window_by_title(window_name)
        if hwnd == 0:
            self.log.warning(f"未找到窗口: {window_name}")
            return

        self.game_hwnd = hwnd
        self.game_mask.bind_game_hwnd(hwnd)
        self.mouse_trace_mask.bind_game_hwnd(hwnd)
        self.mouse_trace_mask.follow_game_window()
        self.game_mask.follow_game_window()
        self.log.success(f"窗口已绑定: {window_name}")
        self.game_mask.show_message("窗口绑定成功", 1800)
        self._save_config({"window_name": window_name})

    def toggle_mask(self):
        if self.game_mask.isVisible():
            self.game_mask.hide()
            self.btn_mask_toggle.setText("开启蒙层")
            self.log.info("蒙层显示已关闭。\n")
            self._save_config({"mask_enabled": False})
            return

        if self.game_mask.game_hwnd == 0:
            self.log.warning("请先绑定目标窗口，再开启蒙层。")
            return

        self.game_mask.follow_game_window()
        self.game_mask.show()
        self.game_mask.raise_()
        self.btn_mask_toggle.setText("关闭蒙层")
        self.log.info("蒙层显示已开启。\n")
        self._save_config({"mask_enabled": True})

    def toggle_trace(self):
        state = not self.mouse_trace_mask.trace_enabled
        self.mouse_trace_mask.set_trace_enabled(state)
        self.btn_trace_toggle.setText("关闭轨迹" if state else "开启轨迹")
        self.log.info("Trace display enabled.\n" if state else "Trace display disabled.\n")
        self._save_config({"trace_enabled": state})

    def toggle_topmost(self, enable: bool | None = None):
        state = enable

        if state is None:
            is_top = self.windowFlags() & Qt.WindowStaysOnTopHint
            state = not bool(is_top)
            self._save_config({"topmost_enabled": state})

        self.setWindowFlag(Qt.WindowStaysOnTopHint, state)
        self.show()

    def update_height(self, height):
        self.lbl_height.setText(f"{height:.2f} m")
        self.game_mask.update_info(height, self.lbl_status.text())

    def update_status(self, status):
        self.lbl_status.setText(status)
        self.game_mask.update_info(self.measure.current_height, status)
        self.game_mask.add_trace(f"[{self._get_time_str()}] {status}")

    def on_time_remaining(self, ms):
        seconds = max(0.0, ms / 1000.0)
        self.lbl_timer.setText(f"{seconds:.3f} s")
        self.game_mask.update_timer(ms)

    def on_action(self):
        self.btn_action.setEnabled(False)
        if self.is_measuring:
            self.on_land()
        else:
            self.on_start()

    def _toggle_capture_button(self, target_kind: str, enabled: bool):
        if target_kind == "start":
            self.btn_capture_start_click.setEnabled(enabled)
            return
        self.btn_capture_action_click.setEnabled(enabled)

    def _capture_button_name(self, target_kind: str):
        return "start" if target_kind == "start" else "action"

    def on_capture_start_click_once(self):
        self._start_capture_click_once("start")

    def on_capture_action_click_once(self):
        self._start_capture_click_once("action")

    def _start_capture_click_once(self, target_kind: str):
        if not self.game_hwnd:
            self.log.warning("Please bind the target window first.\n")
            return

        if WindowTool.is_capture_active():
            WindowTool.stop_capture_click()
            if self._capture_target_kind is not None:
                self._toggle_capture_button(self._capture_target_kind, True)
            self._capture_target_kind = None
            self.game_mask.show_message("Click capture cancelled", 1500)
            self.log.info("Click capture cancelled.\n")
            return

        try:
            WindowTool.start_capture_click(self.game_hwnd, self._apply_captured_click_position)
        except Exception as exc:
            self.log.warning(f"Start capture failed: {exc}\n")
            return

        self._capture_target_kind = target_kind
        self._toggle_capture_button(target_kind, False)
        self.game_mask.show_message("Click once inside the target window", 2500)
        self.log.info(
            f"Capture armed for {self._capture_button_name(target_kind)} click: "
            "waiting for one click inside target window.\n"
        )

    def _apply_captured_click_position(self, x: int, y: int):
        target_kind = self._capture_target_kind or "action"
        if target_kind == "start":
            self.le_start_click_x.setText(str(x))
            self.le_start_click_y.setText(str(y))
        else:
            self.le_action_click_x.setText(str(x))
            self.le_action_click_y.setText(str(y))

        self._toggle_capture_button(target_kind, True)
        self._capture_target_kind = None
        self.game_mask.show_message(
            f"Captured {self._capture_button_name(target_kind)} click position ({x}, {y})",
            2000,
        )
        self.log.info(
            f"Captured {self._capture_button_name(target_kind)} click position ({x}, {y})\n"
        )

        if target_kind == "start":
            self._save_config({"start_click": {"x": int(x), "y": int(y)}})
        else:
            self._save_config({"action_click": {"x": int(x), "y": int(y)}})

    def _resolve_click_target(self, target_kind="action"):
        '''
        获取指定点击目标在游戏窗口中的坐标
        '''
        if not self.game_hwnd:
            raise RuntimeError("game window not bound")

        if target_kind == "start":
            x_text = self.le_start_click_x.text().strip()
            y_text = self.le_start_click_y.text().strip()
        else:
            x_text = self.le_action_click_x.text().strip()
            y_text = self.le_action_click_y.text().strip()

        # 获取游戏窗口的尺寸
        _, _, width, height = WindowTool.get_window_rect_scaled(self.game_hwnd, client_area=True)
        if width <= 0 or height <= 0:
            raise RuntimeError("invalid game client rect")

        x = int(x_text) if x_text else width // 2
        y = int(y_text) if y_text else height - 50
        return x, y

    def _draw_auto_click_point(self, point):
        if not point:
            return

        self.mouse_trace_mask.follow_game_window()
        point_x, point_y = point
        self.mouse_trace_mask.add_click_point(QPoint(point_x, point_y))

    def _log_auto_click(self, x, y):
        '''
        记录鼠标点击到日志标签
        '''
        self.game_mask.show_message(f"Clicked trigger point ({x}, {y})", 2000)
        self.game_mask.add_trace(f"[{self._get_time_str()}] Clicked trigger point ({x}, {y})")
        self.log.info(f"Sent trigger click ({x}, {y})\n")

    def _send_auto_click(self, target_kind="action"):
        '''
        向游戏窗口发送自动点击（包含轨迹绘制与鼠标位置恢复）
        '''
        x, y = self._resolve_click_target(target_kind)
        # try:
        #     import win32api

        #     # 获取当前鼠标位置
        #     original_pos = win32api.GetCursorPos()
        # except Exception:
        #     original_pos = None

        # 执行鼠标点击
        click_info = WindowTool.click_at(self.game_hwnd, x, y)
        # 绘制轨迹
        self._draw_auto_click_point(click_info.get("click_point", (0, 0)))
        # if original_pos is not None:
        #     try:
        #         win32api.SetCursorPos(original_pos)
        #     except Exception:
        #         pass
        self._log_auto_click(x, y)

    def _log_auto_key_press(self, vk_code: int):
        '''
        记录鼠标点击到日志标签
        '''
        self.game_mask.show_message(f"Send trigger key press ({vk_code})", 2000)
        self.log.info(f"Sent trigger key press ({vk_code})\n")

    def _send_auto_key_press(self, vk_code: int):
        '''
        向游戏窗口发送自动按键后鼠标位置恢复
        '''
        # try:
        #     import win32api

        #     # 获取当前鼠标位置
        #     original_pos = win32api.GetCursorPos()
        # except Exception:
        #     original_pos = None

        # 执行鼠标点击
        WindowTool.key_press(self.game_hwnd, vk_code)
        # if original_pos is not None:
        #     try:
        #         win32api.SetCursorPos(original_pos)
        #     except Exception:
        #         pass
        self._log_auto_key_press(vk_code)

    def _fly_key_control(self, fly_limit: int):
        VK_W, VK_D, VK_S, VK_A = ord('W'), ord('D'), ord('S'), ord('A')
        key_map = [VK_W, VK_D, VK_S, VK_A]

        next_vk = key_map[self.fly_key_state]

        # 第一次按下
        if self.fly_current_vk is None:
            self.fly_current_vk = next_vk
            win32api.keybd_event(next_vk, 0, 0, 0)
        else:
            self.fly_count += 1

        if self.fly_count >= fly_limit:
            # 松开当前键
            win32api.keybd_event(self.fly_current_vk, 0, win32con.KEYEVENTF_KEYUP, 0)

            # 切换状态
            self.fly_key_state = (self.fly_key_state + 1) % 4
            self.fly_current_vk = key_map[self.fly_key_state]

            self.fly_count = 0

            time.sleep(0.1)

            # 按下新键
            win32api.keybd_event(self.fly_current_vk, 0, 0, 0)

    def on_start(self):
        try:
            duration = float(self.dsp_fly_duration.value())
            times = int(self.sp_fly_times.value())
        except Exception:
            self.log.warning("飞行参数无效，请检查时长和次数。\n")
            return

        self.measure.fly_duration = duration
        self.measure.save_config()
        self._save_config({"fly_duration": duration, "fly_times": times})
        import traceback

        if self.game_hwnd:
            try:
                # self._send_auto_click("start")
                # time.sleep(0.2)
                # self._send_auto_click("action")

                # 如果不是前台窗口，尝试切换
                # if not WindowTool.is_foreground(self.game_hwnd):
                WindowTool._bring_window_to_front(self.game_hwnd)
                # WindowTool.key_press(self.game_hwnd, win32con.VK_SPACE)
                # self._send_auto_click("start")
                # time.sleep(1)
                # # 拉到俯视角

                # WindowTool.set_top_view()
                time.sleep(0.5)
                WindowTool.key_press(self.game_hwnd, win32con.VK_SPACE)
                time.sleep(0.2)
                # 上升 6 次高度
                for _ in range(6):
                    WindowTool.key_press(self.game_hwnd, win32con.VK_SPACE)
                    time.sleep(1.25)
                    QApplication.processEvents()

                # WindowTool.start_capture_image(
                #     self.game_hwnd,
                #     self.on_capture_frame,
                #     interval_ms=5000
                # )

            except Exception:
                self.log.warning("触发点击失败:\n" + traceback.format_exc())
        else:
            self.log.warning("尚未绑定目标窗口，无法发送点击。\n")

        self.is_measuring = True
        self.btn_action.setEnabled(False)
        self.btn_action.setText("标记落地")
        self.lbl_status.setText("准备起飞")
        self.log.info(
            "测量进行中\n"
            f"单次飞行时长: {duration:.1f} s\n"
            f"飞行次数: {times}\n"
            "等待落地标记...\n\n"
        )
        self.measure.start_measure(times)

    def on_capture_frame(self, width, height, raw_bytes):
        """
        截图回调（保存到 run/captures）

        :param width: 宽
        :param height: 高
        :param raw_bytes: 原始图像数据(BGR)
        """

        # 时间戳命名
        # timestamp = int(time.time() * 1000)
        # file_path = self.capture_dir / f"frame_{timestamp}.png"

        # 递增编号
        file_path = self.screenshots_dir / f"frame_{self.screenshots_index:05d}.png"
        self.screenshots_index += 1

        image = QImage(raw_bytes, width, height, QImage.Format_BGR888)
        image.save(str(file_path))

    def on_fly_once_finished(self, done, total):
        if not self.is_measuring or done >= total or not self.game_hwnd:
            if self.fly_current_vk is not None:
                win32api.keybd_event(self.fly_current_vk, 0, win32con.KEYEVENTF_KEYUP, 0)
            WindowTool.stop_capture_image()
            return

        try:
            # self._send_auto_click("action")
            self._send_auto_key_press(win32con.VK_SPACE)
            time.sleep(0.1)
            self._fly_key_control(1)
            # WindowTool.drag_view(500, 0, 0.2, 2)

        except Exception as exc:
            self.log.warning(f"Trigger click failed: {exc}\n")

    def on_land(self):
        data = self.measure.mark_land(0.0)
        if not data:
            self.btn_action.setEnabled(True)
            return

        WindowTool.stop_capture_image()
        self.log.info(self._format_result(data))
        self.btn_action.setText("开始测量")
        self.is_measuring = False
        self.btn_action.setEnabled(True)
        self.lbl_status.setText("测量完成")
        self.lbl_timer.setText("0.000 s")
        self.game_mask.show_message("测量已完成", 2200)
        self._append_result_to_csv(data)

    def on_falling_started(self):
        """全部上升完成、进入等待标记落地阶段时启用按钮。"""
        if self.is_measuring:
            self.btn_action.setEnabled(True)

    def on_reset(self):
        if self.fly_current_vk is not None:
            win32api.keybd_event(self.fly_current_vk, 0, win32con.KEYEVENTF_KEYUP, 0)
        self.fly_key_state = 0      # 0=W,1=D,2=S,3=A
        self.fly_count = 0
        self.fly_current_vk = None
        WindowTool.stop_capture_image()
        WindowTool.stop_capture_click()
        self.measure.reset()
        self.btn_action.setText("开始测量")
        self.btn_action.setEnabled(True)
        self.is_measuring = False
        self.game_mask.clear_trace()
        self.mouse_trace_mask.clear_paths()
        self.btn_capture_start_click.setEnabled(True)
        self.btn_capture_action_click.setEnabled(True)
        self._capture_target_kind = None
        # 保持当前配置的蒙层/轨迹状态，不强制关闭；只恢复面板显示
        self._set_idle_view()
        self.log.info("测量状态已重置。\n")

    def on_fly_duration_changed(self, _value):
        if self._loading_config:
            return
        self._save_config({"fly_duration": float(self.dsp_fly_duration.value())})

    def on_fly_times_changed(self, _value):
        if self._loading_config:
            return
        self._save_config({"fly_times": int(self.sp_fly_times.value())})

    def _append_result_to_csv(self, data: dict) -> None:
        RESULTS_CSV_PATH.parent.mkdir(parents=True, exist_ok=True)

        header = [
            "timestamp",
            "window_name",
            "fly_duration",
            "fly_times",
            "start_click_x",
            "start_click_y",
            "action_click_x",
            "action_click_y",
            "mask_enabled",
            "trace_enabled",
            "single_height",
            "total_rise",
            "rise_speed",
            "total_fly_time",
            "fall_height",
            "fall_time",
            "fall_speed",
        ]

        row = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "window_name": self.le_window_name.text().strip(),
            "fly_duration": float(self.dsp_fly_duration.value()),
            "fly_times": int(self.sp_fly_times.value()),
            "start_click_x": self._get_int_from_line_edit(self.le_start_click_x, None),
            "start_click_y": self._get_int_from_line_edit(self.le_start_click_y, None),
            "action_click_x": self._get_int_from_line_edit(self.le_action_click_x, None),
            "action_click_y": self._get_int_from_line_edit(self.le_action_click_y, None),
            "mask_enabled": bool(self.game_mask.isVisible()),
            "trace_enabled": bool(self.mouse_trace_mask.trace_enabled),
        }
        row.update(data)

        file_exists = RESULTS_CSV_PATH.exists() and RESULTS_CSV_PATH.stat().st_size > 0
        with open(RESULTS_CSV_PATH, "a", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=header)
            if not file_exists:
                writer.writeheader()
            writer.writerow({k: ("" if row.get(k, None) is None else row.get(k, "")) for k in header})

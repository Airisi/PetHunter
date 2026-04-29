import ctypes
import csv
import json
from datetime import datetime

from PySide6.QtCore import QPoint, Qt
from PySide6.QtWidgets import QAbstractSpinBox, QMainWindow

from core.mask_overlay import GameMaskOverlay
from core.mouse_trace_overlay import MouseTraceOverlay
from ui.generated.ui_main_window import Ui_MainWindow

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils import FlightMeasureTool, LogManager, WindowTool, CONFIG_PATH

RESULTS_CSV_PATH = CONFIG_PATH.parent / "measurement_results.csv"


class MainWindow(QMainWindow, Ui_MainWindow):
    """Main tool window."""

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # self.showMinimized()
        # self.setGeometry(950, 324, 500, 500)
        self.move(950, 324)

        self.game_hwnd = None
        self.measure = FlightMeasureTool()
        self.is_measuring = False
        self.game_mask = GameMaskOverlay()
        self.mouse_trace_mask = MouseTraceOverlay()
        self._capture_target_kind = None
        self._loading_config = True
        self._cfg_mask_enabled = True
        self._cfg_trace_enabled = True

        self._apply_theme()
        self._configure_widgets()
        self._apply_ui_text()

        self.log = LogManager(self.te_result)

        self.measure.height_changed.connect(self.update_height)
        self.measure.state_changed.connect(self.update_status)
        self.measure.time_remaining_changed.connect(self.on_time_remaining)
        self.measure.fly_finished.connect(self.on_fly_finished)
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

        self._apply_config_on_startup()
        self._set_idle_view()
        self.bind_game_window()
        self._apply_overlay_settings_from_config()
        self._loading_config = False

    def _apply_theme(self):
        DWMWA_USE_IMMERSIVE_DARK_MODE = 20

        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            int(self.winId()),
            DWMWA_USE_IMMERSIVE_DARK_MODE,
            ctypes.byref(ctypes.c_int(1)),
            ctypes.sizeof(ctypes.c_int)
        )

    def _configure_widgets(self):
        self.te_result.setReadOnly(True)
        self.dsp_fly_duration.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.UpDownArrows)
        self.sp_fly_times.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.UpDownArrows)
        self.dsp_fly_duration.setMinimum(0.1)
        self.dsp_fly_duration.setMaximum(60.0)
        self.sp_fly_times.setMinimum(1)
        self.sp_fly_times.setMaximum(99)

    def _apply_ui_text(self):
        self.setWindowTitle("PetHunter 辅助测量台")
        self.label.setText("当前状态")
        self.label_2.setText("实时高度")
        self.label_4.setText("单次飞行时长")
        self.label_5.setText("飞行次数")
        self.btn_action.setText("开始测量")
        self.btn_reset.setText("重置")
        self.btn_mask_toggle.setText("关闭蒙层")
        self.btn_trace_toggle.setText("关闭轨迹")
        self.btn_bind_game.setText("重新绑定窗口")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), "测量面板")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), "预留")

    def _load_config(self) -> dict:
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as file:
                loaded = json.load(file)
                return loaded if isinstance(loaded, dict) else {}
        except Exception:
            return {}

    def _save_config(self, updates: dict) -> None:
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        config = self._load_config()
        config.update(updates)
        with open(CONFIG_PATH, "w", encoding="utf-8") as file:
            json.dump(config, file, ensure_ascii=False, indent=4)

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

    def _apply_overlay_settings_from_config(self) -> None:
        # Trace 独立于蒙层开关
        self._set_trace_enabled(self._cfg_trace_enabled)
        # 蒙层需要已绑定窗口后才能显示
        if self._cfg_mask_enabled and self.game_mask.game_hwnd != 0:
            self.game_mask.follow_game_window()
            self.game_mask.show()
            self.game_mask.raise_()
            self.btn_mask_toggle.setText("关闭蒙层")
        else:
            self.game_mask.hide()
            self.btn_mask_toggle.setText("开启蒙层")

    def _set_idle_view(self):
        self.lbl_status.setText("待命")
        self.lbl_height.setText("0.00 m")
        self.lbl_timer.setText("0.000 s")
        self.te_result.setPlainText(
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
        if not self.game_hwnd:
            raise RuntimeError("game window not bound")

        if target_kind == "start":
            x_text = self.le_start_click_x.text().strip()
            y_text = self.le_start_click_y.text().strip()
        else:
            x_text = self.le_action_click_x.text().strip()
            y_text = self.le_action_click_y.text().strip()
        _, _, width, height = WindowTool.get_window_rect_scaled(self.game_hwnd, client_area=True)
        if width <= 0 or height <= 0:
            raise RuntimeError("invalid game client rect")

        x = int(x_text) if x_text else width // 2
        y = int(y_text) if y_text else height - 50
        return x, y

    def _draw_auto_click_path(self, path_points):
        if not path_points:
            return

        self.mouse_trace_mask.follow_game_window()
        point_x, point_y = path_points[-1]
        self.mouse_trace_mask.add_click_point(QPoint(point_x, point_y))

    def _log_auto_click(self, x, y):
        self.game_mask.show_message(f"Clicked trigger point ({x}, {y})", 2000)
        self.game_mask.add_trace(f"[{self._get_time_str()}] Clicked trigger point ({x}, {y})")
        self.log.info(f"Sent trigger click ({x}, {y})\n")

    def _send_auto_click(self, target_kind="action"):
        x, y = self._resolve_click_target(target_kind)
        try:
            import win32api

            original_pos = win32api.GetCursorPos()
        except Exception:
            original_pos = None
        click_info = WindowTool.click_at(self.game_hwnd, x, y)
        self._draw_auto_click_path(click_info.get("path_points", []))
        if original_pos is not None:
            try:
                win32api.SetCursorPos(original_pos)
            except Exception:
                pass
        self._log_auto_click(x, y)

    def on_fly_finished(self, done, total):
        if not self.is_measuring or done >= total or not self.game_hwnd:
            return

        try:
            self._send_auto_click("action")
        except Exception as exc:
            self.log.warning(f"Trigger click failed: {exc}\n")

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

        try:
            import win32api

            original_pos = win32api.GetCursorPos()
        except Exception:
            original_pos = None

        if self.game_hwnd:
            try:
                self._send_auto_click("start")
            except Exception as exc:
                self.log.warning(f"触发点击失败: {exc}\n")
        else:
            self.log.warning("尚未绑定目标窗口，无法发送点击。\n")

        if original_pos is not None:
            try:
                import win32api

                win32api.SetCursorPos(original_pos)
            except Exception:
                pass

        self.btn_action.setText("标记落地")
        self.is_measuring = True
        # 先禁用，等待上升全部结束后才启用标记落地按钮
        self.btn_action.setEnabled(False)
        self.lbl_status.setText("准备起飞")
        self.te_result.setPlainText(
            "测量进行中\n"
            f"单次飞行时长: {duration:.1f} s\n"
            f"飞行次数: {times}\n"
            "等待落地标记...\n"
        )
        self.log.info(f"开始测量: {times} 次飞行, 单次 {duration:.1f} s\n")
        self.measure.start_measure(times)

    def on_land(self):
        data = self.measure.mark_land(0.0)
        if not data:
            # 理论上按钮在上升阶段会被禁用，这里避免误触造成用户卡住
            self.btn_action.setEnabled(True)
            return

        self.te_result.setPlainText(self._format_result(data))
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

    def on_topmost(self):
        is_top = self.windowFlags() & Qt.WindowStaysOnTopHint
        self.setWindowFlag(Qt.WindowStaysOnTopHint, not bool(is_top))
        self.show()

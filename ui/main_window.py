import ctypes
from datetime import datetime

from PySide6.QtCore import QPoint, Qt
from PySide6.QtWidgets import QAbstractSpinBox, QMainWindow

from core.mask_overlay import GameMaskOverlay
from core.mouse_trace_overlay import MouseTraceOverlay
from ui.generated.ui_main_window import Ui_MainWindow

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils import FlightMeasureTool, LogManager, WindowTool


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

        self._apply_theme()
        self._configure_widgets()
        self._apply_ui_text()

        self.log = LogManager(self.te_result)

        self.measure.height_changed.connect(self.update_height)
        self.measure.state_changed.connect(self.update_status)
        self.measure.time_remaining_changed.connect(self.on_time_remaining)
        self.measure.fly_finished.connect(self.on_fly_finished)

        self.btn_action.clicked.connect(self.on_action)
        self.btn_reset.clicked.connect(self.on_reset)
        self.btn_mask_toggle.clicked.connect(self.toggle_mask)
        self.btn_trace_toggle.clicked.connect(self.toggle_trace)
        self.btn_bind_game.clicked.connect(self.bind_game_window)
        self.btn_capture_start_click.clicked.connect(self.on_capture_start_click_once)
        self.btn_capture_action_click.clicked.connect(self.on_capture_action_click_once)

        self._set_idle_view()
        self.bind_game_window()
        self.toggle_mask()

    def _apply_theme(self):
        DWMWA_USE_IMMERSIVE_DARK_MODE = 20

        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            int(self.winId()),
            DWMWA_USE_IMMERSIVE_DARK_MODE,
            ctypes.byref(ctypes.c_int(1)),
            ctypes.sizeof(ctypes.c_int)
        )
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #2b2d30;
            }

            QWidget {
                background-color: #33363a;
                color: #e8eaed;                 /* 主文字 */
                font-family: "Microsoft YaHei";
                font-size: 9pt;
            }

            /* ================= Tab ================= */
            QTabWidget::pane {
                border: 1px solid #4a4f55;
                background-color: #2f3236;
                border-radius: 6px;
                top: -1px;
            }

            QTabBar::tab {
                background-color: #3a3f45;
                border: 1px solid #555b62;
                border-bottom: none;
                padding: 6px 12px;
                min-width: 86px;
                color: #c7ccd1;                 /* 次文字 */
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }

            QTabBar::tab:selected {
                background-color: #2f3236;
                color: #ffffff;
            }

            /* ================= Label ================= */
            QLabel {
                background-color: transparent;
                color: #d0d6dc;                 /* 提升对比 */
            }

            /* ================= 输入控件 ================= */
            QLineEdit, QSpinBox, QDoubleSpinBox, QTextEdit {
                background-color: #1f2124;      /* 更深背景 */
                border: 1px solid #5a6067;
                border-radius: 4px;
                color: #f2f4f6;                 /* 提亮文字 */
                selection-background-color: #4c78a8;
                selection-color: #ffffff;
            }

            QLineEdit {
                padding: 4px 6px;
            }

            QSpinBox, QDoubleSpinBox {
                padding: 4px 24px 4px 6px;
            }

            QSpinBox::up-button, QDoubleSpinBox::up-button {
                subcontrol-origin: border;
                subcontrol-position: top right;
                width: 18px;
                background-color: #3a3f45;
                border-left: 1px solid #5a6067;
                border-top-right-radius: 4px;
            }

            QSpinBox::down-button, QDoubleSpinBox::down-button {
                subcontrol-origin: border;
                subcontrol-position: bottom right;
                width: 18px;
                background-color: #35393e;
                border-left: 1px solid #5a6067;
                border-bottom-right-radius: 4px;
            }

            QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
            QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {
                background-color: #4a5056;
            }

            /* ================= 按钮 ================= */
            QPushButton {
                background-color: #3c4147;
                color: #e6e6e6;
                border: 1px solid #666c73;
                border-radius: 5px;
                padding: 5px 10px;
            }

            QPushButton:hover {
                background-color: #4a5056;
            }

            QPushButton:pressed {
                background-color: #2f3338;
            }

            QPushButton:disabled {
                background-color: #3a3f45;
                color: #8b9198;
            }

            /* ================= 文本框 ================= */
            QTextEdit {
                padding: 6px;
            }

            /* ================= 滚动条 ================= */
            QScrollBar:vertical {
                background: #2a2d31;
                width: 10px;
                margin: 0px;
            }

            QScrollBar::handle:vertical {
                background: #5c636a;
                border-radius: 5px;
                min-height: 24px;
            }

            QScrollBar::handle:vertical:hover {
                background: #7a828a;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
            """
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

    def toggle_mask(self):
        if self.game_mask.isVisible():
            self.game_mask.hide()
            self.mouse_trace_mask.hide()
            self.btn_mask_toggle.setText("开启蒙层")
            self.log.info("蒙层显示已关闭。\n")
            return

        if self.game_mask.game_hwnd == 0:
            self.log.warning("请先绑定目标窗口，再开启蒙层。")
            return

        self.mouse_trace_mask.follow_game_window()
        self.mouse_trace_mask.show()
        self.game_mask.follow_game_window()
        self.game_mask.show()
        self.game_mask.raise_()
        self.btn_mask_toggle.setText("关闭蒙层")
        self.log.info("蒙层显示已开启。\n")

    def toggle_trace(self):
        state = not self.mouse_trace_mask.trace_enabled
        self.mouse_trace_mask.set_trace_enabled(state)
        self.btn_trace_toggle.setText("Hide Trace" if state else "Show Trace")
        self.log.info("Trace display enabled.\n" if state else "Trace display disabled.\n")

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
            self.log.warning("当前还未进入下落阶段，无法标记落地。\n")
            return

        self.te_result.setPlainText(self._format_result(data))
        self.btn_action.setText("开始测量")
        self.is_measuring = False
        self.lbl_status.setText("测量完成")
        self.lbl_timer.setText("0.000 s")
        self.game_mask.show_message("测量已完成", 2200)

    def on_reset(self):
        WindowTool.stop_capture_click()
        self.measure.reset()
        self.btn_action.setText("开始测量")
        self.is_measuring = False
        self.game_mask.clear_trace()
        self.mouse_trace_mask.clear_paths()
        self.btn_capture_action_click.setEnabled(True)
        self._set_idle_view()
        self.log.info("测量状态已重置。\n")

    def on_topmost(self):
        is_top = self.windowFlags() & Qt.WindowStaysOnTopHint
        self.setWindowFlag(Qt.WindowStaysOnTopHint, not bool(is_top))
        self.show()

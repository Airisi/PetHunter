import json
import time

from PySide6.QtCore import QObject, QTimer, Signal


import sys
from pathlib import Path

def get_base_path():
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent.parent
    return Path(__file__).resolve().parent.parent

CONFIG_PATH = get_base_path() / "runs" / "flight_config.json"


class FlightMeasureTool(QObject):
    """Flight measurement helper with realtime height and countdown updates."""

    height_changed = Signal(float)
    state_changed = Signal(str)
    time_remaining_changed = Signal(int)
    fly_finished = Signal(int, int)
    # 全部上升结束，进入“等待标记落地”阶段时触发
    falling_started = Signal()

    def __init__(self):
        super().__init__()
        self.fly_duration = 2.0
        self.SINGLE_FLY_HEIGHT = 2.0

        self.current_height = 0.0
        self.is_flying = False
        self.is_falling = False
        self.fly_count_total = 0
        self.fly_count_done = 0

        self.start_height = 0.0
        self.peak_height = 0.0

        self._fly_start_time = 0.0
        self._fall_start_time = 0.0
        self._last_emitted_height = 0.0
        self._timer = QTimer()
        self._timer.setInterval(10)
        self._timer.timeout.connect(self._update_countdown)

        self.load_config()

    def load_config(self):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as file:
                config = json.load(file)
                self.fly_duration = config.get("fly_duration", 1.0)
        except Exception:
            self.fly_duration = 1.0
            self.save_config()

    def save_config(self):
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        config = {}
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as file:
                loaded = json.load(file)
                if isinstance(loaded, dict):
                    config = loaded
        except Exception:
            config = {}

        config["fly_duration"] = self.fly_duration
        with open(CONFIG_PATH, "w", encoding="utf-8") as file:
            json.dump(config, file, ensure_ascii=False, indent=4)

    def start_measure(self, fly_times):
        self.current_height = 0.0
        self.start_height = 0.0
        self.peak_height = 0.0
        self._last_emitted_height = 0.0
        self.height_changed.emit(0.0)

        self.fly_count_total = fly_times
        self.fly_count_done = 0
        self._fall_start_time = 0.0
        self._trigger_fly()

    def _trigger_fly(self):
        if self.fly_count_done >= self.fly_count_total:
            self.peak_height = self.current_height
            self.state_changed.emit("全部上升完成，等待标记落地")
            self.is_falling = True
            self.falling_started.emit()
            self._fall_start_time = time.perf_counter()
            self._timer.stop()
            self.time_remaining_changed.emit(0)
            return

        self.is_flying = True
        self.fly_count_done += 1
        self.state_changed.emit(f"第 {self.fly_count_done}/{self.fly_count_total} 次上升中")
        self._fly_start_time = time.perf_counter()
        self._timer.start()

    def _update_countdown(self):
        if not self.is_flying:
            return

        elapsed_seconds = time.perf_counter() - self._fly_start_time
        remaining = max(0, int(self.fly_duration * 1000 - elapsed_seconds * 1000))
        self.time_remaining_changed.emit(remaining)

        progress = 1.0 if self.fly_duration <= 0 else min(1.0, elapsed_seconds / self.fly_duration)
        base_height = max(0, self.fly_count_done - 1) * self.SINGLE_FLY_HEIGHT
        preview_height = round(base_height + self.SINGLE_FLY_HEIGHT * progress, 2)
        if preview_height != self._last_emitted_height:
            self._last_emitted_height = preview_height
            self.height_changed.emit(preview_height)

        if remaining == 0:
            self._end_fly()

    def _end_fly(self):
        if not self.is_flying:
            return

        self._timer.stop()
        self.is_flying = False

        actual_duration = time.perf_counter() - self._fly_start_time
        self.current_height += self.SINGLE_FLY_HEIGHT
        self._last_emitted_height = round(self.current_height, 2)
        self.height_changed.emit(self._last_emitted_height)
        self.fly_finished.emit(self.fly_count_done, self.fly_count_total)

        rise_speed = self.SINGLE_FLY_HEIGHT / actual_duration if actual_duration > 0 else 0.0
        self.state_changed.emit(f"本次上升完成，速度 {rise_speed:.2f} m/s")
        self._trigger_fly()

    def mark_land(self, land_height=0.0):
        if not self.is_falling:
            return None

        now = time.perf_counter()
        self.is_falling = False
        total_rise = self.peak_height - self.start_height
        fall_height = self.peak_height - land_height

        if fall_height <= 0:
            fall_height = 0.0
            fall_time = 0.0
            fall_speed = 0.0
        else:
            fall_time = max(0.0, now - self._fall_start_time)
            fall_speed = fall_height / fall_time if fall_time > 0 else 0.0

        result = {
            "single_height": round(self.SINGLE_FLY_HEIGHT, 2),
            "fly_times": self.fly_count_total,
            "total_fly_time": round(self.fly_duration * self.fly_count_total, 3),
            "total_rise": round(total_rise, 2),
            "rise_speed": round(self.SINGLE_FLY_HEIGHT / self.fly_duration, 2) if self.fly_duration > 0 else 0.0,
            "fall_height": round(fall_height, 2),
            "fall_time": round(fall_time, 3),
            "fall_speed": round(fall_speed, 2),
        }

        self.current_height = 0.0
        self.start_height = 0.0
        self.peak_height = 0.0
        self._fall_start_time = 0.0
        self._last_emitted_height = 0.0
        self.height_changed.emit(0.0)

        return result

    def reset(self):
        self.current_height = 0.0
        self.is_flying = False
        self.is_falling = False
        self._last_emitted_height = 0.0
        self._timer.stop()
        self.time_remaining_changed.emit(0)
        self.height_changed.emit(0.0)
        self.state_changed.emit("待命")

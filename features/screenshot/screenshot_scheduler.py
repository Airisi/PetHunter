from dataclasses import dataclass


@dataclass
class ScreenshotSchedulePolicy:
    min_interval_ms: int = 1500
    target_height_m: float = 0.0
    height_tolerance_m: float = 0.2


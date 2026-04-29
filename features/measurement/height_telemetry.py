from dataclasses import dataclass


@dataclass
class MeasurementResult:
    single_height: float
    fly_times: int
    total_fly_time: float
    total_rise: float
    rise_speed: float
    fall_height: float
    fall_time: float
    fall_speed: float


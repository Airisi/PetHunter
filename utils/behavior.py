import time
import random
import threading


class Behavior:
    """
    行为控制器（时间 + 空间 + 节奏控制）
    """

    # =========================================================
    # 基础控制
    # =========================================================
    _lock = threading.Lock()

    ENABLE = True

    MODE_OFF = 0
    MODE_FIXED = 1
    MODE_RANDOM = 2

    MODE = MODE_RANDOM

    # =========================================================
    # 时间参数
    # =========================================================
    FIXED_DELAY = 0.02
    RANDOM_RANGE = (0.01, 0.05) # (min_s, max_s)

    # =========================================================
    # 坐标扰动
    # =========================================================
    COORD_JITTER_ENABLE = True

    # 扰动范围（半径概念：±range）
    COORD_JITTER_RANGE_X = 10
    COORD_JITTER_RANGE_Y = 10

    # =========================================================
    # 外部控制接口
    # =========================================================

    @staticmethod
    def set_enable(flag: bool):
        with Behavior._lock:
            Behavior.ENABLE = bool(flag)

    @staticmethod
    def enable():
        Behavior.set_enable(True)

    @staticmethod
    def disable():
        Behavior.set_enable(False)

    @staticmethod
    def set_mode(mode: int):
        with Behavior._lock:
            Behavior.MODE = mode

    @staticmethod
    def set_fixed_delay(delay: float):
        with Behavior._lock:
            Behavior.FIXED_DELAY = float(delay)

    @staticmethod
    def set_random_range(min_s: float, max_s: float):
        with Behavior._lock:
            Behavior.RANDOM_RANGE = (float(min_s), float(max_s))

    @staticmethod
    def configure(enable=None, mode=None, fixed=None, rand_range=None):
        with Behavior._lock:
            if enable is not None:
                Behavior.ENABLE = bool(enable)

            if mode is not None:
                Behavior.MODE = mode

            if fixed is not None:
                Behavior.FIXED_DELAY = float(fixed)

            if rand_range is not None:
                Behavior.RANDOM_RANGE = tuple(rand_range)

    @staticmethod
    def reset():
        with Behavior._lock:
            Behavior.ENABLE = True
            Behavior.MODE = Behavior.MODE_RANDOM
            Behavior.FIXED_DELAY = 0.02
            Behavior.RANDOM_RANGE = (0.01, 0.05)

            Behavior.COORD_JITTER_ENABLE = True
            Behavior.COORD_JITTER_RANGE_X = 2
            Behavior.COORD_JITTER_RANGE_Y = 2

    @staticmethod
    def status():
        return {
            "ENABLE": Behavior.ENABLE,
            "MODE": Behavior.MODE,
            "FIXED_DELAY": Behavior.FIXED_DELAY,
            "RANDOM_RANGE": Behavior.RANDOM_RANGE,
            "COORD_JITTER_ENABLE": Behavior.COORD_JITTER_ENABLE,
            "COORD_JITTER_RANGE_X": Behavior.COORD_JITTER_RANGE_X,
            "COORD_JITTER_RANGE_Y": Behavior.COORD_JITTER_RANGE_Y,
        }

    # =========================================================
    # 时间控制
    # =========================================================

    @staticmethod
    def sleep():
        if not Behavior.ENABLE:
            return

        if Behavior.MODE == Behavior.MODE_OFF:
            return

        elif Behavior.MODE == Behavior.MODE_FIXED:
            time.sleep(Behavior.FIXED_DELAY)

        else:
            time.sleep(random.uniform(*Behavior.RANDOM_RANGE))

    @staticmethod
    def click_pause():
        Behavior.sleep()

    # =========================================================
    # 坐标扰动（核心修正）
    # =========================================================

    @staticmethod
    def set_coord_jitter(enable: bool):
        Behavior.COORD_JITTER_ENABLE = bool(enable)

    @staticmethod
    def set_coord_jitter_range(x_range: int, y_range: int = None):
        """
        设置坐标扰动范围
        - x_range: X方向±范围
        - y_range: Y方向±范围（不传则等于x_range）
        """
        Behavior.COORD_JITTER_RANGE_X = int(x_range)
        Behavior.COORD_JITTER_RANGE_Y = int(y_range if y_range is not None else x_range)

    @staticmethod
    def jitter_point(x: int, y: int):
        """
        在设定范围内随机扰动坐标（关键修正）
        """
        if not Behavior.COORD_JITTER_ENABLE:
            return x, y

        dx = random.randint(
            -Behavior.COORD_JITTER_RANGE_X,
             Behavior.COORD_JITTER_RANGE_X
        )

        dy = random.randint(
            -Behavior.COORD_JITTER_RANGE_Y,
             Behavior.COORD_JITTER_RANGE_Y
        )

        return x + dx, y + dy
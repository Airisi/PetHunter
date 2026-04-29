import sys
from pathlib import Path


def get_project_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent.parent
    return Path(__file__).resolve().parent.parent


def runs_dir() -> Path:
    return get_project_root() / "runs"


def flight_config_path() -> Path:
    return runs_dir() / "configs" / "flight_config.json"


def measurement_results_csv_path() -> Path:
    return runs_dir() / "measurements" / "measurement_results.csv"


def screenshots_dir() -> Path:
    return runs_dir() / "screenshots"


def ensure_parent_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


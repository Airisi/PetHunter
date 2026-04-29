from __future__ import annotations

import json

from .paths import flight_config_path, ensure_parent_dir


def load_flight_config_dict() -> dict:
    path = flight_config_path()
    if not path.exists():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            loaded = json.load(f)
        return loaded if isinstance(loaded, dict) else {}
    except Exception:
        return {}


def update_flight_config_dict(updates: dict) -> None:
    if not isinstance(updates, dict):
        return
    path = flight_config_path()
    ensure_parent_dir(path)
    config = load_flight_config_dict()
    config.update(updates)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=4)


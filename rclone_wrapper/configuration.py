"""Utilities for reading the configuration file."""

from typing import Any, Dict

import yaml

CONFIG_FILE = "rclone_wrapper/config.yaml"


def read_config() -> Dict[str, Any]:
    """Read the configuration file and return its contents as a dictionary."""
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data if isinstance(data, dict) else {}

"""Utilities for reading the configuration file."""

from types import SimpleNamespace

import yaml

CONFIG_FILE = "rclone_wrapper/config.yaml"


def read_config() -> SimpleNamespace:
    """Read the configuration file and return its contents as a SimpleNamespace."""
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return SimpleNamespace(**data) if isinstance(data, dict) else SimpleNamespace()

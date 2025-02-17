#!/usr/bin/env python3
"""Main module for the rclone wrapper."""

import argparse
import os
import sys
from types import SimpleNamespace
from typing import Sequence

from logger_wrapper.logger_wrapper import setup_logger
from rclone_wrapper.configuration import read_config
from rclone_wrapper.navigation import navigate_gdrive

logger = setup_logger(name_appendix=__name__)


def _main_navigate(_: argparse.Namespace, config: SimpleNamespace) -> None:
    navigate_gdrive(config.remote)


def _parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="rclone wrapper operations")
    subparsers = parser.add_subparsers(dest="command", required=True)
    navigate_parser = subparsers.add_parser("navigate", help="Interactively navigate Google Drive")
    navigate_parser.set_defaults(func=_main_navigate)
    return parser.parse_args(argv)


def main(argv: Sequence[str]) -> int:
    """Main entry point for the rclone wrapper."""
    args = _parse_args(argv)
    config = read_config()
    args.func(args, config)
    return os.EX_OK


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

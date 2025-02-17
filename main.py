#!/usr/bin/env python3
"""Main module for the rclone wrapper."""

import argparse
import os
import sys
from datetime import datetime
from types import SimpleNamespace
from typing import Sequence

from logger_wrapper.logger_wrapper import setup_logger
from rclone_wrapper.comparison import compare_folders
from rclone_wrapper.configuration import read_config
from rclone_wrapper.mounting import mount, unmount
from rclone_wrapper.navigation import navigate

logger = setup_logger(name_appendix=__name__)


def _main_navigate(_: argparse.Namespace, config: SimpleNamespace) -> None:
    navigate(config.remote)


def _main_mount(args: argparse.Namespace, config: SimpleNamespace) -> None:
    mount(args.remote_folder, args.mount_point, config.remote)


def _main_unmount(args: argparse.Namespace, _: SimpleNamespace) -> None:
    unmount(args.mount_point)


def _main_compare(args: argparse.Namespace, config: SimpleNamespace) -> None:
    current_time = datetime.now().strftime("%Y%m%dT%H%M%S")
    diff_file = f"results/{current_time}_comparison.txt"
    compare_folders(args.local_folder, f"{config.remote}:{args.remote_folder}", diff_file)


def _parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="rclone wrapper operations")
    subparsers = parser.add_subparsers(dest="command", required=True)

    navigate_parser = subparsers.add_parser("navigate", help="Interactively navigate Google Drive")
    navigate_parser.set_defaults(func=_main_navigate)

    mount_parser = subparsers.add_parser("mount", help="Mount a remote folder")
    mount_parser.set_defaults(func=_main_mount)
    mount_parser.add_argument("--remote-folder", help="Remote folder to mount")
    mount_parser.add_argument("--mount-point", help="Local mount point")

    unmount_parser = subparsers.add_parser("unmount", help="Unmount a mount point")
    unmount_parser.set_defaults(func=_main_unmount)
    unmount_parser.add_argument("--mount-point", help="Local mount point to unmount")

    compare_parser = subparsers.add_parser("compare", help="Compare folders (see results/ folder)")
    compare_parser.set_defaults(func=_main_compare)
    compare_parser.add_argument("--remote-folder", help="Remote folder")
    compare_parser.add_argument("--local-folder", help="Local folder")

    return parser.parse_args(argv)


def main(argv: Sequence[str]) -> int:
    """Main entry point for the rclone wrapper."""
    args = _parse_args(argv)
    config = read_config()
    args.func(args, config)
    return os.EX_OK


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

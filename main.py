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
from rclone_wrapper.transferring import download, upload

logger = setup_logger(name_appendix=__name__)


def _main_navigate(_: argparse.Namespace, config: SimpleNamespace) -> None:
    navigate(config.remote)


def _main_mount(args: argparse.Namespace, config: SimpleNamespace) -> None:
    mount(args.remote_path, args.mount_point, config.remote)


def _main_unmount(args: argparse.Namespace, _: SimpleNamespace) -> None:
    unmount(args.mount_point)


def _main_compare(args: argparse.Namespace, config: SimpleNamespace) -> None:
    current_time = datetime.now().strftime("%Y%m%dT%H%M%S")
    diff_file = f"results/{current_time}_comparison.txt"
    compare_folders(args.local_path, f"{config.remote}:{args.remote_path}", diff_file)


def _main_upload(args: argparse.Namespace, config: SimpleNamespace) -> None:
    upload(args.remote_path, args.local_path, config.remote)


def _main_download(args: argparse.Namespace, config: SimpleNamespace) -> None:
    download(args.remote_path, args.local_path, config.remote)


def _parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="rclone wrapper operations")
    subparsers = parser.add_subparsers(dest="command", required=True)

    navigate_parser = subparsers.add_parser("navigate", help="Interactively navigate remote")
    navigate_parser.set_defaults(func=_main_navigate)

    mount_parser = subparsers.add_parser("mount", help="Mount a remote path")
    mount_parser.set_defaults(func=_main_mount)
    mount_parser.add_argument("-r", "--remote-path", help="Remote path to mount")
    mount_parser.add_argument("-m", "--mount-point", help="Local mount point")

    unmount_parser = subparsers.add_parser("unmount", help="Unmount a mount point")
    unmount_parser.set_defaults(func=_main_unmount)
    unmount_parser.add_argument("-m", "--mount-point", help="Local mount point to unmount")

    compare_parser = subparsers.add_parser("compare", help="Compare paths (diffs in results/)")
    compare_parser.set_defaults(func=_main_compare)
    compare_parser.add_argument("-r", "--remote-path", help="Remote path")
    compare_parser.add_argument("-l", "--local-path", help="Local path")

    upload_parser = subparsers.add_parser("upload", help="Upload local file/dir")
    upload_parser.set_defaults(func=_main_upload)
    upload_parser.add_argument("-r", "--remote-path", help="Remote path to upload to")
    upload_parser.add_argument("-l", "--local-path", help="Path to local file/dir to upload")

    download_parser = subparsers.add_parser("download", help="Download remote file/dir")
    download_parser.set_defaults(func=_main_download)
    download_parser.add_argument("-r", "--remote-path", help="Path to remote file/dir to download")
    download_parser.add_argument("-l", "--local-path", help="Local path to download to")

    return parser.parse_args(argv)


def main(argv: Sequence[str]) -> int:
    """Main entry point for the rclone wrapper."""
    args = _parse_args(argv)
    config = read_config()
    args.func(args, config)
    return os.EX_OK


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

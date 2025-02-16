#!/usr/bin/env python3
"""Main module for the rclone wrapper."""

import argparse
import os
import sys
from typing import Sequence

from rclone_wrapper.configuration import read_config
from rclone_wrapper.navigation import navigate_gdrive


def _parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="rclone wrapper operations")
    subparsers = parser.add_subparsers(dest="command", required=True)
    navigate_parser = subparsers.add_parser("navigate", help="Interactively navigate Google Drive")
    navigate_parser.add_argument(
        "--remote",
        type=str,
        help="Remote name (if not provided, read from config file)",
    )
    navigate_parser.add_argument(
        "--path",
        type=str,
        default="",
        help="Initial remote path (default is root)",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str]) -> int:  # pragma: no cover
    """Main entry point for the rclone wrapper."""
    args = _parse_args(argv)
    if args.command == "navigate":
        remote = args.remote
        if not remote:
            config = read_config()
            remote = config.get("remote")
            if not remote:
                print("Remote not specified and not found in config.", file=sys.stderr)
                return os.EX_CONFIG
        navigate_gdrive(remote, args.path)
    return os.EX_OK


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

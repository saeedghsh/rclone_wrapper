"""utilities for mounting remote directories using rclone"""

import logging
import os
import subprocess

logger = logging.getLogger(__name__)


def is_mounted(mount_point: str) -> bool:
    """Check if a directory is a valid mount point."""

    if not os.path.exists(mount_point):
        logger.warning("Path '%s' does not exist.", mount_point)
        return False  # Explicitly log and return False

    try:
        subprocess.run(["mountpoint", "-q", mount_point], check=True)
        return True  # exists and is a mount point

    except subprocess.CalledProcessError as exc:
        if exc.returncode == 32:
            return False  # exists and not a mount point, safe to ignore
        logger.error("Unexpected error checking mount point '%s': %s", mount_point, exc)
        raise

    except (FileNotFoundError, PermissionError) as exc:
        logger.error("Error accessing mount point '%s': %s", mount_point, exc)
        raise


def mount(remote_path: str, mount_point: str, remote: str) -> None:
    """Mount a remote folder to a local directory using rclone."""

    if is_mounted(mount_point):
        logger.error("'%s' is already mounted.", mount_point)
        return

    if not os.path.exists(mount_point):
        logger.info("Creating mount point directory: '%s'", mount_point)
        os.makedirs(mount_point, exist_ok=True)  # Ensure the directory exists

    logger.info("Mounting '%s:%s' to '%s'...", remote, remote_path, mount_point)
    try:
        # Popen only needs `with` if we plan to `wait()` or `communicate()`
        # Using `with` is not appropriate for long-running processes like `rclone mount`.
        subprocess.Popen(  # pylint: disable=consider-using-with
            [
                "nohup",
                "rclone",
                "mount",
                f"{remote}:{remote_path}",
                mount_point,
                "--vfs-cache-mode",
                "writes",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            start_new_session=True,
        )
        logger.info("Mounted '%s' to '%s'", remote_path, mount_point)
    except subprocess.SubprocessError as exc:
        logger.error("Failed to mount '%s' to '%s': %s", remote_path, mount_point, exc)
        raise


def unmount(mount_point: str) -> None:
    """Unmount a local mount point."""

    if not os.path.exists(mount_point):
        logger.error("Mount point '%s' does not exist. Cannot unmount.", mount_point)
        return

    if not is_mounted(mount_point):
        logger.info("'%s' is not a mount point. Nothing to unmount.", mount_point)
        return

    logger.info("Unmounting '%s'...", mount_point)
    try:
        subprocess.run(["fusermount", "-uz", mount_point], check=True)
        logger.info("Unmounted '%s'", mount_point)
    except subprocess.CalledProcessError as exc:
        logger.error("Failed to unmount '%s': %s", mount_point, exc)
        raise

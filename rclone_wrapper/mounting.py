"""utilities for mounting remote directories using rclone"""

import logging
import os
import subprocess

logger = logging.getLogger(__name__)


def is_mounted(mount_point: str) -> bool:
    """Return True if the specified mount point is already mounted."""
    try:
        subprocess.run(["mountpoint", "-q", mount_point], check=True)
        return True  # If we reach here, return code was 0 (mounted)
    except subprocess.CalledProcessError as e:
        if e.returncode == 1:
            return False  # Expected "not mounted" case
        raise  # Other `CalledProcessError`s should propagate # pragma: no cover
    except (FileNotFoundError, PermissionError) as exc:
        logger.error("checking mount point '%s': %s", mount_point, exc)
        raise  # Re-raise to ensure a clear failure message


def mount(remote_folder: str, mount_point: str, remote: str) -> None:
    """Mount a remote folder to a specified local mount point using rclone."""
    if is_mounted(mount_point):
        logger.error("'%s' is already mounted.", mount_point)
        return

    os.makedirs(mount_point, exist_ok=True)

    command = [
        "nohup",
        "rclone",
        "mount",
        f"{remote}:{remote_folder}",
        mount_point,
        "--vfs-cache-mode",
        "writes",
    ]
    # Popen only needs `with` if we plan to `wait()` or `communicate()`
    # Using `with` is not appropriate for long-running processes like `rclone mount`.
    subprocess.Popen(  # pylint: disable=consider-using-with
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL,
        start_new_session=True,
    )
    logger.info("Mounted '%s' to '%s", remote_folder, mount_point)


def unmount(mount_point: str) -> None:
    """Unmount a local mount point."""
    if not is_mounted(mount_point):
        logger.error("'%s' is not a mount point.", mount_point)
        return
    try:
        subprocess.run(["fusermount", "-uz", mount_point], check=True)
        logger.info("Unmounted '%s'", mount_point)
    except subprocess.CalledProcessError as e:
        if e.returncode == 1:  # Expected "not mounted" case
            logger.error("'%s' is already unmounted or not a valid mount point.", mount_point)
        else:  # pragma: no cover
            logger.error("Failed to unmount '%s': %s", mount_point, e)
            raise
    except (FileNotFoundError, PermissionError) as exc:  # pragma: no cover
        logger.error("Error unmounting '%s': %s", mount_point, exc)
        raise

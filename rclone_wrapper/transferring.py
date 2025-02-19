"""utilities for transferring files/dirs between local and remote using rclone"""

import logging
import os
import subprocess

logger = logging.getLogger(__name__)


def _remote_path_exists(remote_path: str, mode: str) -> bool:
    """Return True if `remote_path` exists on the remote

    If mode is 'dir', check if the path exists as a directory.
    If mode is 'file_or_dir', check if the path exists as a file or directory.
    """
    try:
        command = ["rclone", "lsd" if mode == "dir" else "lsf", remote_path]
        result = subprocess.run(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True
        )
        return True if mode == "dir" else bool(result.stdout.strip())

    except subprocess.CalledProcessError as exc:
        stderr = exc.stderr.lower() if exc.stderr else ""
        if "not found" in stderr:
            return False
        logger.error("Error checking remote path: %s", stderr)
        raise

    except (FileNotFoundError, PermissionError) as exc:
        logger.error("Error accessing remote path '%s': %s", remote_path, exc)
        raise


def _validate_remote_destination(remote_path: str, local_path: str, remote: str) -> bool:
    """Return True if the remote destination is valid for uploading."""
    if not _remote_path_exists(f"{remote}:{remote_path}", mode="dir"):
        logger.error("Destination '%s:%s' does not exist.", remote, remote_path)
        return False

    local_path_base = os.path.basename(os.path.normpath(local_path))
    target_path = f"{remote_path.rstrip('/')}/{local_path_base}"

    if _remote_path_exists(f"{remote}:{target_path}", mode="file_or_dir"):
        logger.error(
            "A file/dir named '%s' already exists under destination '%s:%s'.",
            local_path_base,
            remote,
            remote_path,
        )
        return False

    return True


def upload(remote_path: str, local_path: str, remote: str) -> None:
    """Uploads a local file/dir to a remote destination.

    It makes a copy of the local_path file/dir under the remote_path.

    Abort if:
    * a dir as remote_path does not exist.
    * remote_path already contains a dir/file with the same basename as local_path.
    """
    if not _validate_remote_destination(remote_path, local_path, remote):
        return

    local_path_base = os.path.basename(os.path.normpath(local_path))
    target_path = f"{remote_path.rstrip('/')}/{local_path_base}"

    logger.info("Uploading '%s' to '%s:%s'...", local_path, remote, target_path)
    try:
        subprocess.run(
            ["rclone", "copy", "--progress", "--checksum", local_path, f"{remote}:{target_path}"],
            check=True,
            stderr=subprocess.PIPE,
            text=True,
        )
        logger.info("Upload completed successfully.")

    except subprocess.CalledProcessError as exc:
        logger.error(
            "Failed to upload local dir '%s' to remote '%s:%s': %s",
            local_path,
            remote,
            target_path,
            exc.stderr.strip() if exc.stderr else "Unknown error",
        )
        raise


def _validate_local_destination(remote_path: str, local_path: str) -> bool:
    """Return True if the local destination is valid for downloading."""
    if not os.path.isdir(local_path):
        logger.error("Destination '%s' does not exist or is not a directory.", local_path)
        return False

    remote_path_base = os.path.basename(os.path.normpath(remote_path))
    target_path = os.path.join(local_path, remote_path_base)

    if os.path.exists(target_path):
        logger.error(
            "A file/dir named '%s' already exists under '%s'.", remote_path_base, local_path
        )
        return False

    return True


def download(remote_path: str, local_path: str, remote: str) -> None:
    """Download a remote file/dir to a local destination.

    It makes a copy of the remote_path file/dir under the local_path.

    Abort if:
    * a dir as local_path does not exist.
    * local_path already contains a file/dir with the same basename as remote_path.
    """
    if not _validate_local_destination(remote_path, local_path):
        return

    remote_path_base = os.path.basename(os.path.normpath(remote_path))
    target_path = os.path.join(local_path, remote_path_base)

    logger.info("Downloading '%s:%s' to '%s'...", remote, remote_path, target_path)
    try:
        subprocess.run(
            ["rclone", "copy", "--progress", "--checksum", f"{remote}:{remote_path}", target_path],
            check=True,
            stderr=subprocess.PIPE,
            text=True,
        )
        logger.info("Download completed successfully.")

    except subprocess.CalledProcessError as exc:
        logger.error(
            "Failed to download '%s:%s' to '%s': %s",
            remote,
            remote_path,
            target_path,
            exc.stderr.strip() if exc.stderr else "Unknown error",
        )
        raise

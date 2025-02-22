"""utilities for comparing folders using rclone"""

import logging
import subprocess
from datetime import datetime

logger = logging.getLogger(__name__)


def compare_folders(folder1: str, folder2: str) -> bool:
    """
    Compare two folders (local or remote) using rclone check with --checksum.
    Returns True if the folders are identical, False if differences are detected.
    If differences are detected and diff_file is provided, the output is stored in that file.
    """
    current_time = datetime.now().strftime("%Y%m%dT%H%M%S")
    diff_file = f"results/{current_time}_comparison.txt"
    command = ["rclone", "check", folder1, folder2, "--checksum"]
    try:
        result = subprocess.run(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False
        )

        # no diff branch
        if result.returncode == 0:
            logger.info("Folders '%s' and '%s' are identical.", folder1, folder2)
            return True

        # diff branch
        logger.info("Differences detected between folders '%s' and '%s'.", folder1, folder2)
        with open(diff_file, "w", encoding="utf-8") as f:
            f.write("Differences detected between folders:\n")
            f.write(f"Folder 1: {folder1}\n")
            f.write(f"Folder 2: {folder2}\n")
            f.write("STDOUT:\n")
            f.write(result.stdout)
            f.write("\nSTDERR:\n")
            f.write(result.stderr)
        logger.info("Differences stored in '%s'.", diff_file)
        return False

    except Exception as exc:
        logger.error("Error comparing folders '%s' and '%s': %s", folder1, folder2, exc)
        raise

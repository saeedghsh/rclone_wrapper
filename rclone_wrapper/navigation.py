"""utilities for navigating remote directories using rclone"""

import subprocess
from typing import List


def _list_dirs(current_path: str, remote: str) -> List[str]:
    command = ["rclone", "lsf", f"{remote}:{current_path}", "--dirs-only"]
    try:
        result = subprocess.run(
            command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        return [line.rstrip("/ \n\r") for line in result.stdout.splitlines()]
    except subprocess.CalledProcessError:
        return []


def navigate_gdrive(remote: str, start_path: str) -> None:
    """
    Interactively navigate the remote directories using rclone.
    The remote and initial path are provided by the caller.
    """
    current_path = start_path
    while True:
        display_path = "/" if current_path == "" else f"/{current_path}/"
        print(f"Current remote path: {display_path}")
        dirs = _list_dirs(current_path, remote)
        if not dirs:
            print("No sub-directories found.")
        else:
            print("Sub-directories:")
            for idx, d in enumerate(dirs):
                print(f"  [{idx}] {d}")
        print('Select a number ("." go to root, ".." go up, "q" quit) >', end=" ")
        choice = input().strip()
        if choice == "q":
            break

        if choice == ".":
            current_path = ""
        elif choice == "..":
            current_path = "/".join(current_path.split("/")[:-1])
        elif choice.isdigit():
            index = int(choice)
            if 0 <= index < len(dirs):
                subdir = dirs[index]
                current_path = subdir if current_path == "" else f"{current_path}/{subdir}"
            else:
                print("Invalid selection: index out of range.")
        else:
            print("Invalid input. Please enter a number, '.', '..', or 'q'.")
        print()
    final_path = "/" if current_path == "" else f"/{current_path}/"
    print(f"Final remote path: {final_path}")

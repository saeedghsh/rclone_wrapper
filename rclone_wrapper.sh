#!/bin/bash

# Mount a remote folder from saeedghsh_gdrive to a specified local mount point.
gmount() {
  if [ "$#" -ne 2 ]; then
    echo "Usage: gmount <remote_folder> <local_mount_point>"
    echo "Example: gmount \"media\" \"~/gdrive\""
    return 1
  fi

  local remote_folder="$1"
  local mount_point="$2"

  # Check if the mount point is already in use.
  if mountpoint -q "$mount_point"; then
    echo "Error: '$mount_point' is already mounted."
    return 1
  fi

  # Ensure the local mount point exists.
  mkdir -p "$mount_point"

  # Mount the remote folder in the background, so it persists after the terminal is closed.
  nohup rclone mount saeedghsh_gdrive:"$remote_folder" "$mount_point" --vfs-cache-mode writes >/dev/null 2>&1 & disown
  echo "Mounted '$remote_folder' to '$mount_point'"
}

# Unmount a local mount point.
gumount() {
  if [ "$#" -ne 1 ]; then
    echo "Usage: gumount <local_mount_point>"
    echo "Example: gumount \"~/gdrive\""
    return 1
  fi

  local mount_point="$1"

  if mountpoint -q "$mount_point"; then
    fusermount -uz "$mount_point"
    echo "Unmounted '$mount_point'"
  else
    echo "Error: '$mount_point' is not a mount point."
    return 1
  fi
}


# Checks if a remote folder (on Google Drive) and a local folder have identical
# content (recursively), using rclone’s built-in `check` command with the
# `--checksum` flag.
is_the_same() {
  if [ "$#" -ne 2 ]; then
    echo "Usage: is_the_same <remote_folder> <local_folder>"
    return 1
  fi

  local remote_folder="$1"
  local local_folder="$2"

  echo "Comparing local '$local_folder' with remote 'saeedghsh_gdrive:$remote_folder'..."
  rclone check "$local_folder" saeedghsh_gdrive:"$remote_folder" --checksum
  if [ $? -eq 0 ]; then
    echo "Local and remote folders are identical."
  else
    echo "Differences detected between local and remote folders."
  fi
}

# Copies/uploads a local directory to a remote folder on Google Drive, but won’t
# overwrite if the remote folder already exists.
copy_to_gdrive() {
  if [ "$#" -ne 2 ]; then
    echo "Usage: copy_to_gdrive <remote_folder> <local_folder>"
    return 1
  fi

  local remote_folder="$1"
  local local_folder="$2"

  # Check if remote folder exists (even if empty)
  if rclone lsd saeedghsh_gdrive:"$remote_folder" >/dev/null 2>&1; then
    echo "Error: Remote folder '$remote_folder' already exists. Aborting."
    return 1
  fi

  echo "Copying local folder '$local_folder' to remote 'saeedghsh_gdrive:$remote_folder'..."
  rclone copy "$local_folder" saeedghsh_gdrive:"$remote_folder"
  echo "Copy completed."
}

# Copies/downloads a remote folder from Google Drive to a local directory, but
# won’t overwrite if the local folder already exists.
copy_from_gdrive() {
  if [ "$#" -ne 2 ]; then
    echo "Usage: copy_from_gdrive <remote_folder> <local_folder>"
    return 1
  fi

  local remote_folder="$1"
  local local_folder="$2"

  if [ -d "$local_folder" ]; then
    echo "Error: Local folder '$local_folder' already exists. Aborting."
    return 1
  fi

  echo "Copying remote folder 'saeedghsh_gdrive:$remote_folder' to local '$local_folder'..."
  rclone copy saeedghsh_gdrive:"$remote_folder" "$local_folder"
  echo "Copy completed."
}


# Description: A bash script function (nav_gdrive) that using rclone (similar to
# what we have so far) that lists the content of the path (only directories)
# from the remote. It should be interactive in the way that at each step after
# listing the latest paths content content, the user can select one of the
# sub-directories (via index/number assigned to them and shown at the terminal)
# and then the function would update the path with that choice, and list the
# content of that directory, and so on. When leaving the function, it should
# print out the full path to the latest path the user interactively ended up at.
# This is for ability to navigate through the directories on remote from command
# line.
#
# At each step, there should be additional options beyond the choice of
# sub-directories at that path:
# * option . will reset the path to the root of remote, i.e. an empty string.
# * option .. will go one level up to the parent directory
# * option q will quite the function and print the final path.
nav_gdrive() {
  # Start at the root (empty string represents "My Drive")
  currentPath=""

  while true; do
    # Format the display path
    if [ -z "$currentPath" ]; then
      displayPath="/"
    else
      displayPath="/${currentPath}/"
    fi
    echo "Current remote path: ${displayPath}"
    
    # List subdirectories in the current path using rclone lsf --dirs-only.
    # Remove trailing slashes from each directory name.
    mapfile -t dirs < <(rclone lsf saeedghsh_gdrive:"$currentPath" --dirs-only | sed 's:/*$::')
    
    if [ ${#dirs[@]} -eq 0 ]; then
      echo "No sub-directories found."
    else
      echo "Sub-directories:"
      for i in "${!dirs[@]}"; do
        echo "  [$i] ${dirs[$i]}"
      done
    fi

    # Print the interactive prompt with special options.
    echo 'Select a number ("." go to root, ".." go up, "q" quit) >'
    read -r choice

    case "$choice" in
      q)
        break
        ;;
      ".")
        # Reset to the root.
        currentPath=""
        ;;
      "..")
        # Go up one level unless we're at the root.
        if [ -z "$currentPath" ]; then
          echo "Already at root."
        else
          # Remove any trailing slash and then remove the last component.
          currentPath="${currentPath%/}"
          currentPath="${currentPath%/*}"
        fi
        ;;
      *)
        # Check if input is a valid number.
        if [[ "$choice" =~ ^[0-9]+$ ]]; then
          if [ "$choice" -ge 0 ] && [ "$choice" -lt "${#dirs[@]}" ]; then
            # Remove trailing slash from the chosen subdirectory.
            subdir="${dirs[$choice]%%/}"
            if [ -z "$currentPath" ]; then
              currentPath="${subdir}"
            else
              currentPath="${currentPath}/${subdir}"
            fi
          else
            echo "Invalid selection: index out of range."
          fi
        else
          echo "Invalid input. Please enter a number, '.', '..', or 'q'."
        fi
        ;;
    esac

    echo # Blank line for readability.
  done

  # Print the final remote path.
  if [ -z "$currentPath" ]; then
    echo "Final remote path: /"
  else
    echo "Final remote path: /${currentPath}/"
  fi
}


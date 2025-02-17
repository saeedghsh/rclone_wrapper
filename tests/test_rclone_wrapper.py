# pylint: disable=missing-module-docstring, missing-function-docstring
import subprocess
from types import SimpleNamespace
from typing import List
from unittest.mock import MagicMock, mock_open, patch

import pytest

from rclone_wrapper.comparison import compare_folders
from rclone_wrapper.configuration import read_config
from rclone_wrapper.mounting import is_mounted, mount, unmount
from rclone_wrapper.navigation import _list_dirs, navigate


@pytest.fixture(autouse=True)
def clear_list_dirs_cache() -> None:
    """Automatically clear `_list_dirs` cache before each test."""
    _list_dirs.cache_clear()


@pytest.mark.parametrize(
    "current_path, remote, mock_output, expected",
    [
        ("", "gdrive", "folder1/\nfolder2/\n", ["folder1", "folder2"]),
        ("parent", "gdrive", "sub1/\nsub2/\n", ["sub1", "sub2"]),
        ("empty", "gdrive", "", []),
    ],
)
def test_list_dirs(current_path: str, remote: str, mock_output: str, expected: List[str]) -> None:
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout=mock_output, returncode=0)
        result = _list_dirs(current_path, remote)
        assert result == expected


def test_list_dirs_failure() -> None:
    with patch(
        "subprocess.run",
        side_effect=subprocess.CalledProcessError(1, "rclone", stderr="Some error"),
    ):
        assert _list_dirs("", "gdrive") == []  # Ensure it gracefully returns an empty list


def test_list_dirs_file_not_found() -> None:
    with patch("subprocess.run", side_effect=FileNotFoundError("rclone not found")):
        try:
            _list_dirs("", "gdrive")
        except FileNotFoundError as e:
            assert str(e) == "rclone not found"
        else:
            assert False, "Expected FileNotFoundError but did not get one"


def test_list_dirs_permission_error() -> None:
    with patch("subprocess.run", side_effect=PermissionError("Permission denied")):
        try:
            _list_dirs("", "gdrive")
        except PermissionError as e:
            assert str(e) == "Permission denied"
        else:
            assert False, "Expected PermissionError but did not get one"


def test_navigate(monkeypatch: pytest.MonkeyPatch) -> None:
    inputs = iter(["0", "..", "q"])
    monkeypatch.setattr("builtins.input", lambda: next(inputs))
    with patch("rclone_wrapper.navigation._list_dirs", return_value=["subdir"]):
        with patch("builtins.print") as mock_print:
            navigate("gdrive", "")
        # Ensure that print was called at least once
        assert mock_print.call_args_list, "Expected print statements were not called."
        # Extract printed lines
        printed_lines = [call[0][0] for call in mock_print.call_args_list if call[0]]
        assert any("Current remote path: /" in line for line in printed_lines)
        assert any("Sub-directories:" in line for line in printed_lines)
        assert any("[0] subdir" in line for line in printed_lines)
        assert any("Final remote path: /" in line for line in printed_lines)


def test_navigate_no_subdirs(monkeypatch: pytest.MonkeyPatch) -> None:
    inputs = iter(["q"])
    monkeypatch.setattr("builtins.input", lambda: next(inputs))
    with patch("rclone_wrapper.navigation._list_dirs", return_value=[]):
        with patch("builtins.print") as mock_print:
            navigate("gdrive", "")

    printed_lines = [call.args[0] for call in mock_print.call_args_list if call.args]
    assert "No sub-directories found." in printed_lines


def test_navigate_root_path(monkeypatch: pytest.MonkeyPatch) -> None:
    inputs = iter([".", "q"])
    monkeypatch.setattr("builtins.input", lambda: next(inputs))
    with patch("rclone_wrapper.navigation._list_dirs", return_value=["subdir"]):
        with patch("builtins.print") as mock_print:
            navigate("gdrive", "some/path")

    printed_lines = [call.args[0] for call in mock_print.call_args_list if call.args]
    assert "Final remote path: /" in printed_lines


def test_navigate_invalid_index(monkeypatch: pytest.MonkeyPatch) -> None:
    inputs = iter(["10", "q"])
    monkeypatch.setattr("builtins.input", lambda: next(inputs))
    with patch("rclone_wrapper.navigation._list_dirs", return_value=["subdir"]):
        with patch("builtins.print") as mock_print:
            navigate("gdrive", "")

    printed_lines = [call.args[0] for call in mock_print.call_args_list if call.args]
    assert "Invalid selection: index out of range." in printed_lines


def test_navigate_invalid_input(monkeypatch: pytest.MonkeyPatch) -> None:
    inputs = iter(["invalid", "q"])
    monkeypatch.setattr("builtins.input", lambda: next(inputs))
    with patch("rclone_wrapper.navigation._list_dirs", return_value=["subdir"]):
        with patch("builtins.print") as mock_print:
            navigate("gdrive", "")

    printed_lines = [call.args[0] for call in mock_print.call_args_list if call.args]
    assert "Invalid input. Please enter a number, '.', '..', or 'q'." in printed_lines


def test_read_config() -> None:
    mock_yaml_content = "key1: value1\nkey2: value2"
    expected_result = SimpleNamespace(key1="value1", key2="value2")
    with patch("builtins.open", mock_open(read_data=mock_yaml_content)):
        with patch("yaml.safe_load", return_value={"key1": "value1", "key2": "value2"}):
            result = read_config()
    assert vars(result) == vars(expected_result)


def test_read_config_empty_file() -> None:
    with patch("builtins.open", mock_open(read_data="")):
        with patch("yaml.safe_load", return_value=None):
            result = read_config()
    assert isinstance(result, SimpleNamespace)
    assert vars(result) == {}


def test_read_config_invalid_format() -> None:
    with patch("builtins.open", mock_open(read_data="invalid: [data, no_colon]")):
        with patch("yaml.safe_load", return_value=None):
            result = read_config()
    assert isinstance(result, SimpleNamespace)
    assert vars(result) == {}


@pytest.mark.parametrize(
    "returncode, expected",
    [(0, True), (1, False)],
)
def test_is_mounted(returncode: int, expected: bool) -> None:
    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = (
            subprocess.CalledProcessError(returncode, "mountpoint") if returncode else None
        )
        result = is_mounted("/mnt/test")
        assert result == expected


def test_is_mounted_error() -> None:
    with patch("subprocess.run", side_effect=FileNotFoundError("mountpoint not found")):
        with pytest.raises(FileNotFoundError):
            is_mounted("/mnt/test")


def test_mount_already_mounted() -> None:
    with patch("rclone_wrapper.mounting.is_mounted", return_value=True):
        with patch("rclone_wrapper.mounting.logger.error") as mock_logger:
            mount("remote_folder", "/mnt/test", "gdrive")
            assert mock_logger.call_args[0][0] == "'%s' is already mounted."
            assert mock_logger.call_args[0][1] == "/mnt/test"


def test_mount_success() -> None:
    with patch("rclone_wrapper.mounting.is_mounted", return_value=False):
        with (
            patch("os.makedirs") as mock_makedirs,
            patch("subprocess.Popen") as mock_popen,
            patch("rclone_wrapper.mounting.logger.info") as mock_logger,
        ):
            mount("remote_folder", "/mnt/test", "gdrive")
            mock_makedirs.assert_called_with("/mnt/test", exist_ok=True)
            mock_popen.assert_called()
            mock_logger.assert_called_with("Mounted '%s' to '%s", "remote_folder", "/mnt/test")


def test_unmount_not_mounted() -> None:
    with patch("rclone_wrapper.mounting.is_mounted", return_value=False):
        with patch("rclone_wrapper.mounting.logger.error") as mock_logger:
            unmount("/mnt/test")
            mock_logger.assert_called_with("'%s' is not a mount point.", "/mnt/test")


def test_unmount_success() -> None:
    with patch("rclone_wrapper.mounting.is_mounted", return_value=True):
        with (
            patch("subprocess.run") as mock_run,
            patch("rclone_wrapper.mounting.logger.info") as mock_logger,
        ):
            mock_run.return_value = MagicMock(returncode=0)
            unmount("/mnt/test")
            mock_run.assert_called_with(["fusermount", "-uz", "/mnt/test"], check=True)
            mock_logger.assert_called_with("Unmounted '%s'", "/mnt/test")


def test_unmount_error() -> None:
    with patch("rclone_wrapper.mounting.is_mounted", return_value=True):
        with (
            patch(
                "subprocess.run", side_effect=subprocess.CalledProcessError(1, "fusermount")
            ) as mock_run,
            patch("rclone_wrapper.mounting.logger.error") as mock_logger,
        ):
            unmount("/mnt/test")
            mock_run.assert_called_with(["fusermount", "-uz", "/mnt/test"], check=True)
            mock_logger.assert_called_with(
                "'%s' is already unmounted or not a valid mount point.", "/mnt/test"
            )


@pytest.mark.parametrize(
    "returncode, stdout, stderr, expected, expect_diff_file",
    [
        (0, "", "", True, False),  # No differences, no file written
        (1, "Differences found", "Error log", False, True),  # Differences found, file written
    ],
)
def test_compare_folders(
    returncode: int, stdout: str, stderr: str, expected: bool, expect_diff_file: bool
) -> None:
    with (
        patch(
            "subprocess.run",
            return_value=MagicMock(returncode=returncode, stdout=stdout, stderr=stderr),
        ),
        patch("rclone_wrapper.comparison.logger.info") as mock_logger,
        patch("builtins.open", mock_open()) as mock_file,
    ):
        result = compare_folders("folder1", "folder2", "diff.txt")
        assert result == expected
        mock_logger.assert_called()  # Ensure logging happened

        # Ensure the diff file was only written if differences were detected
        if expect_diff_file:
            mock_file.assert_called_once_with("diff.txt", "w", encoding="utf-8")
        else:
            mock_file.assert_not_called()


def test_compare_folders_exception() -> None:
    with (
        patch("subprocess.run", side_effect=OSError("mock error")),
        patch("rclone_wrapper.comparison.logger.error") as mock_logger,
    ):
        with pytest.raises(OSError):
            compare_folders("folder1", "folder2", "diff.txt")
        mock_logger.assert_called()  # Ensure an error was logged

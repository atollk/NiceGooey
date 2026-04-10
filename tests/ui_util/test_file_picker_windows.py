"""
FilePicker Tests - Windows-Specific

Tests for Windows-specific code paths: _is_windows(), _get_windows_drives(),
_path_is_hidden() (FILE_ATTRIBUTE_HIDDEN branch), drives panel UI, and
breadcrumb drive letter display.

All tests in this file are skipped on non-Windows hosts.
"""

import platform
import re
import tempfile
from pathlib import Path

import pytest
from nicegui import ui
from nicegui.testing import User

from nicegooey.ui_util.file_picker import FilePicker

pytestmark = pytest.mark.skipif(platform.system() != "Windows", reason="Windows-specific tests")


def create_temp_structure() -> Path:
    temp_dir = Path(tempfile.mkdtemp())
    (temp_dir / "file1.txt").write_text("content1")
    (temp_dir / "folder1").mkdir()
    return temp_dir


# ==================== _is_windows() ====================


def test_is_windows_returns_true() -> None:
    """_is_windows() must return True when running on Windows."""
    assert FilePicker._is_windows() is True


# ==================== _get_windows_drives() ====================


@pytest.mark.nicegui_main_file(__file__)
async def test_get_windows_drives_returns_non_empty_list(user: User) -> None:
    """At least one drive (e.g. C:\\) must be present."""
    await user.open("/")
    picker = user.find(FilePicker).elements.pop()

    drives = picker._get_windows_drives()

    assert isinstance(drives, list)
    assert len(drives) > 0


@pytest.mark.nicegui_main_file(__file__)
async def test_get_windows_drives_format(user: User) -> None:
    """Each drive string must match the pattern 'X:\\'."""
    await user.open("/")
    picker = user.find(FilePicker).elements.pop()

    drives = picker._get_windows_drives()
    pattern = re.compile(r"^[A-Z]:\\$")

    for drive in drives:
        assert pattern.match(drive), f"Drive '{drive}' does not match expected format"


@pytest.mark.nicegui_main_file(__file__)
async def test_get_windows_drives_only_existing(user: User) -> None:
    """_get_windows_drives() must only return drives that actually exist."""
    await user.open("/")
    picker = user.find(FilePicker).elements.pop()

    drives = picker._get_windows_drives()

    for drive in drives:
        assert Path(drive).exists(), f"Drive '{drive}' was returned but does not exist"


# ==================== _path_is_hidden() ====================


@pytest.mark.nicegui_main_file(__file__)
async def test_path_is_hidden_dot_prefix(user: User) -> None:
    """Files starting with '.' are hidden regardless of platform."""
    await user.open("/")
    picker = user.find(FilePicker).elements.pop()
    temp_dir = picker.current_directory

    hidden = temp_dir / ".dotfile"
    hidden.write_text("x")

    assert picker._path_is_hidden(hidden) is True


@pytest.mark.nicegui_main_file(__file__)
async def test_path_is_hidden_windows_attribute(user: User) -> None:
    """Files with FILE_ATTRIBUTE_HIDDEN set are reported as hidden on Windows."""
    import ctypes

    await user.open("/")
    picker = user.find(FilePicker).elements.pop()
    temp_dir = picker.current_directory

    hidden_file = temp_dir / "win_hidden.txt"
    hidden_file.write_text("hidden")

    FILE_ATTRIBUTE_HIDDEN = 0x02
    ctypes.windll.kernel32.SetFileAttributesW(str(hidden_file), FILE_ATTRIBUTE_HIDDEN)

    assert picker._path_is_hidden(hidden_file) is True


@pytest.mark.nicegui_main_file(__file__)
async def test_path_is_hidden_normal_file_not_hidden(user: User) -> None:
    """A normal file without the hidden attribute is not reported as hidden."""
    await user.open("/")
    picker = user.find(FilePicker).elements.pop()
    temp_dir = picker.current_directory

    normal_file = temp_dir / "file1.txt"

    assert picker._path_is_hidden(normal_file) is False


# ==================== Drives Panel UI Tests ====================


@pytest.mark.nicegui_main_file(__file__)
async def test_drives_panel_exists_on_windows(user: User) -> None:
    """On Windows the drives panel must not be None."""
    await user.open("/")
    picker = user.find(FilePicker).elements.pop()

    assert picker._inner_elements.drives_panel is not None


@pytest.mark.nicegui_main_file(__file__)
async def test_drives_panel_shows_c_drive(user: User) -> None:
    """C:\\ should appear in the drives panel (virtually all Windows machines have C:)."""
    await user.open("/")

    await user.should_see("C:\\")


# ==================== Breadcrumb Tests ====================


@pytest.mark.nicegui_main_file(__file__)
async def test_breadcrumb_shows_drive_letter(user: User) -> None:
    """The breadcrumb path bar shows the drive root (e.g. C:\\) on Windows."""
    await user.open("/")

    # temp dirs on Windows live under C:\ (or whichever system drive)
    picker = user.find(FilePicker).elements.pop()
    drive_root = picker.current_directory.parts[0]  # e.g. "C:\\"

    await user.should_see(drive_root)


# Main page
@ui.page("/")
def main() -> None:
    temp_dir = create_temp_structure()
    FilePicker(starting_directory=str(temp_dir), mode="read")


if __name__ in {"__main__", "__mp_main__"}:
    ui.run()

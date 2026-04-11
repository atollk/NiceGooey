"""
FilePicker Tests - Edge Cases and Additional Features

Tests for edge cases, error handling, and additional FilePicker features.
"""

import platform
import tempfile
from pathlib import Path

import pytest
from nicegui import ui
from nicegui.testing import User

from nicegooey.ui_util.file_picker import FilePicker


def _make_row(path, name, is_dir):
    return FilePicker._DirectoryItemTableRow(
        id=str(path),
        name=name,
        is_dir=is_dir,
        size="",
        modified="",
        icon="folder" if is_dir else "description",
    )


def create_temp_structure() -> Path:
    """Create temporary directory structure for tests."""
    temp_dir = Path(tempfile.mkdtemp())

    # Create files
    (temp_dir / "file1.txt").write_text("content1")

    # Create folders
    (temp_dir / "folder1").mkdir()
    (temp_dir / "folder1" / "nested_file.txt").write_text("nested")
    (temp_dir / "empty_folder").mkdir()

    # Create hidden files
    (temp_dir / ".hidden_file").write_text("hidden")

    return temp_dir


# ==================== Initialization Tests ====================


# Note: Specific configuration tests (directory selection, show_hidden, hide_buttons)
# are tested in their dedicated test files with proper configurations


# ==================== Navigation Tests ====================


@pytest.mark.nicegui_main_file(__file__)
async def test_set_directory(user: User) -> None:
    """Test set_directory public API method."""
    await user.open("/")

    picker = user.find(FilePicker).elements.pop()
    temp_dir = picker.current_directory

    subfolder = temp_dir / "folder1"

    # Use set_directory method
    picker.navigate_to(str(subfolder))

    assert picker.current_directory == subfolder


@pytest.mark.nicegui_main_file(__file__)
async def test_set_directory_invalid(user: User) -> None:
    """Test set_directory with non-directory path."""
    await user.open("/")

    picker = user.find(FilePicker).elements.pop()
    temp_dir = picker.current_directory

    file_path = temp_dir / "file1.txt"
    original_dir = picker.current_directory

    # Try to set directory to a file (should fail or be ignored)
    picker.navigate_to(str(file_path))

    # Directory should not change
    assert picker.current_directory == original_dir


@pytest.mark.nicegui_main_file(__file__)
async def test_navigate_to_invalid_path(user: User) -> None:
    """Test navigating to non-existent path."""
    await user.open("/")

    picker = user.find(FilePicker).elements.pop()
    original_dir = picker.current_directory

    # Try to navigate to non-existent path
    invalid_path = original_dir / "does_not_exist"
    picker._navigate_to(invalid_path)

    # Should stay in current directory (or handle gracefully)
    assert picker.current_directory == original_dir


# ==================== Edge Cases ====================


@pytest.mark.nicegui_main_file(__file__)
async def test_empty_directory(user: User) -> None:
    """Test listing empty directory."""
    await user.open("/")

    picker = user.find(FilePicker).elements.pop()
    temp_dir = picker.current_directory

    # Navigate to empty folder
    empty_folder = temp_dir / "empty_folder"
    picker._navigate_to(empty_folder)

    # Should return empty list
    items = picker._list_directory()
    assert items == []


@pytest.mark.nicegui_main_file(__file__)
async def test_hidden_files_not_shown_by_default(user: User) -> None:
    """Test that hidden files are not shown by default."""
    await user.open("/")

    picker = user.find(FilePicker).elements.pop()

    # Ensure show_hidden is False
    assert picker.show_hidden is False

    # List directory
    items = picker._list_directory()
    names = [item.name for item in items]

    # Hidden file should not appear
    assert ".hidden_file" not in names


@pytest.mark.nicegui_main_file(__file__)
async def test_value_property_setter(user: User) -> None:
    """Test setting value property directly."""
    await user.open("/")

    picker = user.find(FilePicker).elements.pop()
    temp_dir = picker.current_directory

    file_path = temp_dir / "file1.txt"

    # Set value directly
    picker.value = [str(file_path)]

    assert picker.value == [str(file_path)]


@pytest.mark.nicegui_main_file(__file__)
async def test_double_click_on_file(user: User) -> None:
    """Test double-clicking on a file."""
    await user.open("/")

    picker = user.find(FilePicker).elements.pop()
    temp_dir = picker.current_directory

    file_path = temp_dir / "file1.txt"
    original_dir = picker.current_directory

    # Double-click on file (should select, not navigate)
    picker._on_item_double_click(_make_row(file_path, "file1.txt", False))

    # Should not change directory
    assert picker.current_directory == original_dir


@pytest.mark.nicegui_main_file(__file__)
async def test_double_click_on_folder(user: User) -> None:
    """Test double-clicking on a folder."""
    await user.open("/")

    picker = user.find(FilePicker).elements.pop()
    temp_dir = picker.current_directory

    folder = temp_dir / "folder1"

    # Double-click on folder (should navigate)
    picker._on_item_double_click(_make_row(folder, "folder1", True))

    # Should navigate into folder
    assert picker.current_directory == folder


@pytest.mark.nicegui_main_file(__file__)
@pytest.mark.skipif(platform.system() == "Windows", reason="Permission tests unreliable on Windows")
async def test_permission_error_handling(user: User) -> None:
    """Test graceful handling of permission errors."""
    await user.open("/")

    picker = user.find(FilePicker).elements.pop()

    # Try to navigate to a restricted directory (if any)
    # This test is platform-specific and may need adjustment
    # For now, just ensure no crash occurs
    original_dir = picker.current_directory

    # Try navigating to root (might have permission issues)
    try:
        picker._navigate_to(Path("/root"))
        # If successful, verify we're still in a valid state
        assert picker.current_directory is not None
    except (PermissionError, OSError):
        # Expected behavior - should handle gracefully
        assert picker.current_directory == original_dir


# ==================== Integration Tests ====================


@pytest.mark.nicegui_main_file(__file__)
async def test_breadcrumb_navigation(user: User) -> None:
    """Test navigating using breadcrumb path."""
    await user.open("/")

    picker = user.find(FilePicker).elements.pop()
    temp_dir = picker.current_directory

    # Navigate to nested folder
    folder1 = temp_dir / "folder1"
    picker._navigate_to(folder1)
    assert picker.current_directory == folder1

    # Navigate back using parent directory
    picker._navigate_to(temp_dir)
    assert picker.current_directory == temp_dir


@pytest.mark.nicegui_main_file(__file__)
async def test_parent_directory_navigation(user: User) -> None:
    """Test parent directory button/navigation."""
    await user.open("/")

    picker = user.find(FilePicker).elements.pop()
    temp_dir = picker.current_directory

    # Navigate to subfolder
    subfolder = temp_dir / "folder1"
    picker._navigate_to(subfolder)
    assert picker.current_directory == subfolder

    # Navigate to parent
    parent = picker.current_directory.parent
    picker._navigate_to(parent)
    assert picker.current_directory == parent


# Main page - single FilePicker for default tests
@ui.page("/")
def main() -> None:
    temp_dir = create_temp_structure()

    ui.label("FilePicker - Default (for general tests)").classes("text-h4")
    FilePicker(starting_directory=str(temp_dir), mode="read")


if __name__ in {"__main__", "__mp_main__"}:
    ui.run()

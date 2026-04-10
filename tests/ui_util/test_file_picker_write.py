"""
FilePicker Tests - Write Mode

Tests for FilePicker in write mode (save file dialog).
"""

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
    (temp_dir / "file2.pdf").write_text("content2")
    (temp_dir / "file3.doc").write_text("content3")

    # Create folders
    (temp_dir / "folder1").mkdir()
    (temp_dir / "folder1" / "file_in_folder.txt").write_text("nested content")
    (temp_dir / "folder2").mkdir()

    return temp_dir


# ==================== Initialization Tests ====================


@pytest.mark.nicegui_main_file(__file__)
async def test_init_write_mode(user: User) -> None:
    """Test initialization in write mode."""
    await user.open("/")
    await user.should_see("FilePicker - Write Mode")

    picker = user.find(FilePicker).elements.pop()

    assert picker.value == []
    assert picker._filename_input_value == ""
    assert picker.allow_multiple is False  # Write mode doesn't allow multiple


@pytest.mark.nicegui_main_file(__file__)
async def test_write_mode_has_filename_input(user: User) -> None:
    """Test that filename input field exists in write mode."""
    await user.open("/")

    picker = user.find(FilePicker).elements.pop()

    # Check that filename input exists
    assert hasattr(picker._inner_elements, "filename_input")
    assert picker._inner_elements.filename_input is not None


# ==================== Write Mode Specific Tests ====================


@pytest.mark.nicegui_main_file(__file__)
async def test_write_mode_selection_sets_filename(user: User) -> None:
    """Test clicking file populates filename input in write mode."""
    await user.open("/")

    picker = user.find(FilePicker).elements.pop()
    temp_dir = picker.current_directory

    file_path = temp_dir / "file1.txt"

    # Click on a file
    picker._on_item_click(_make_row(file_path, "file1.txt", False))

    # Filename input should be populated
    assert picker._filename_input_value == "file1.txt"
    # Value should also contain the selected file
    assert picker.value == [str(file_path)]


@pytest.mark.nicegui_main_file(__file__)
async def test_write_mode_filename_input_clears_selection(user: User) -> None:
    """Test that typing in filename input clears file selection."""
    await user.open("/")

    picker = user.find(FilePicker).elements.pop()
    temp_dir = picker.current_directory

    file_path = temp_dir / "file1.txt"

    # First, select a file
    picker._on_item_click(_make_row(file_path, "file1.txt", False))
    assert picker.value == [str(file_path)]
    assert picker._filename_input_value == "file1.txt"

    # Now simulate typing in the filename input
    class MockEvent:
        def __init__(self, value):
            self.args = value

    picker._on_filename_input_change(MockEvent("my_custom_file.txt"))

    # Selection should be cleared
    assert picker.value == []
    assert picker._filename_input_value == "my_custom_file.txt"


@pytest.mark.nicegui_main_file(__file__)
async def test_write_mode_has_new_folder_dialog(user: User) -> None:
    """Test that new folder dialog method exists in write mode."""
    await user.open("/")

    picker = user.find(FilePicker).elements.pop()

    # Check that the method exists
    assert hasattr(picker, "_create_new_folder_dialog")
    assert callable(picker._create_new_folder_dialog)


@pytest.mark.nicegui_main_file(__file__)
async def test_write_mode_directory_click_navigates(user: User) -> None:
    """Test that clicking directory navigates in write mode."""
    await user.open("/")

    picker = user.find(FilePicker).elements.pop()
    temp_dir = picker.current_directory
    folder = temp_dir / "folder1"

    # Click on directory
    picker._on_item_click(_make_row(folder, "folder1", True))

    # Should navigate, not select
    assert picker.current_directory == folder
    # Filename should not be set to folder name
    assert picker._filename_input_value != "folder1"


# ==================== Integration Tests ====================


@pytest.mark.nicegui_main_file(__file__)
async def test_complete_save_file_workflow(user: User) -> None:
    """Test full workflow in write mode."""
    await user.open("/")

    picker = user.find(FilePicker).elements.pop()
    temp_dir = picker.current_directory

    # Navigate into folder1
    folder1 = temp_dir / "folder1"
    picker._navigate_to(folder1)
    assert picker.current_directory == folder1

    # Type a filename
    class MockEvent:
        def __init__(self, value):
            self.args = value

    picker._on_filename_input_change(MockEvent("my_new_file.txt"))
    assert picker._filename_input_value == "my_new_file.txt"

    # Value should be empty since we typed manually
    assert picker.value == []

    # Alternative: select existing file
    file_in_folder = folder1 / "file_in_folder.txt"
    picker._on_item_click(_make_row(file_in_folder, "file_in_folder.txt", False))

    # Filename should be populated
    assert picker._filename_input_value == "file_in_folder.txt"
    assert picker.value == [str(file_in_folder)]


@pytest.mark.nicegui_main_file(__file__)
async def test_write_mode_multiple_selection_disabled(user: User) -> None:
    """Test that multiple selection is disabled in write mode."""
    await user.open("/")

    picker = user.find(FilePicker).elements.pop()

    # Write mode should always have allow_multiple = False
    assert picker.allow_multiple is False


# Main page
@ui.page("/")
def main() -> None:
    temp_dir = create_temp_structure()

    ui.label("FilePicker - Write Mode").classes("text-h4")

    FilePicker(starting_directory=str(temp_dir), mode="write")


if __name__ in {"__main__", "__mp_main__"}:
    ui.run()

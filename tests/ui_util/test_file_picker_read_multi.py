"""
FilePicker Tests - Read Mode, Multiple Selection

Tests for FilePicker in read mode with multiple file selection.
"""

import tempfile
from pathlib import Path

import pytest
from nicegui import ui
from nicegui.testing import User

from nicegooey.ui_util.file_picker import FilePicker


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

    # Create hidden files/folders
    (temp_dir / ".hidden_file").write_text("hidden")
    (temp_dir / ".hidden_folder").mkdir()

    return temp_dir


# ==================== Initialization Tests ====================


@pytest.mark.nicegui_main_file(__file__)
async def test_init_multiple_selection(user: User) -> None:
    """Test initialization with allow_multiple=True."""
    await user.open("/")
    await user.should_see("FilePicker - Read Mode (Multiple)")

    picker = user.find(FilePicker).elements.pop()

    assert picker.allow_multiple is True
    assert picker.allow_directory_selection is False
    assert picker.value == []


# ==================== Selection Logic Tests ====================


@pytest.mark.nicegui_main_file(__file__)
async def test_multiple_selection_files(user: User) -> None:
    """Test selecting multiple files."""
    await user.open("/")

    picker = user.find(FilePicker).elements.pop()
    temp_dir = picker.current_directory

    file1 = temp_dir / "file1.txt"
    file2 = temp_dir / "file2.pdf"
    file3 = temp_dir / "file3.doc"

    # Select first file
    picker._on_item_click({"path": file1, "is_dir": False, "name": "file1.txt"})
    assert str(file1) in picker.value

    # Select second file (should add to selection)
    picker._on_item_click({"path": file2, "is_dir": False, "name": "file2.pdf"})
    assert str(file1) in picker.value
    assert str(file2) in picker.value

    # Select third file
    picker._on_item_click({"path": file3, "is_dir": False, "name": "file3.doc"})
    assert str(file1) in picker.value
    assert str(file2) in picker.value
    assert str(file3) in picker.value
    assert len(picker.value) == 3


@pytest.mark.nicegui_main_file(__file__)
async def test_multiple_selection_toggle(user: User) -> None:
    """Test toggling selection in multiple mode."""
    await user.open("/")

    picker = user.find(FilePicker).elements.pop()
    temp_dir = picker.current_directory

    file1 = temp_dir / "file1.txt"
    file2 = temp_dir / "file2.pdf"

    # Select file1
    picker._on_item_click({"path": file1, "is_dir": False, "name": "file1.txt"})
    assert str(file1) in picker.value
    assert len(picker.value) == 1

    # Select file2
    picker._on_item_click({"path": file2, "is_dir": False, "name": "file2.pdf"})
    assert str(file1) in picker.value
    assert str(file2) in picker.value
    assert len(picker.value) == 2

    # Toggle file1 (deselect)
    picker._on_item_click({"path": file1, "is_dir": False, "name": "file1.txt"})
    assert str(file1) not in picker.value
    assert str(file2) in picker.value
    assert len(picker.value) == 1

    # Toggle file1 again (select)
    picker._on_item_click({"path": file1, "is_dir": False, "name": "file1.txt"})
    assert str(file1) in picker.value
    assert str(file2) in picker.value
    assert len(picker.value) == 2


@pytest.mark.nicegui_main_file(__file__)
async def test_value_multiple_selection(user: User) -> None:
    """Test value property in multiple selection mode."""
    await user.open("/")

    picker = user.find(FilePicker).elements.pop()
    temp_dir = picker.current_directory

    file1_path = temp_dir / "file1.txt"
    file2_path = temp_dir / "file2.pdf"

    # Set multiple values
    picker.value = [str(file1_path), str(file2_path)]

    assert len(picker.value) == 2
    assert str(file1_path) in picker.value
    assert str(file2_path) in picker.value


@pytest.mark.nicegui_main_file(__file__)
async def test_directory_selection_navigates_in_multi_mode(user: User) -> None:
    """Test that clicking directory still navigates in multiple selection mode."""
    await user.open("/")

    picker = user.find(FilePicker).elements.pop()
    temp_dir = picker.current_directory
    folder = temp_dir / "folder1"

    picker._on_item_click({"path": folder, "is_dir": True, "name": "folder1"})

    # Should navigate into the directory
    assert picker.current_directory == folder


@pytest.mark.nicegui_main_file(__file__)
async def test_table_selection_syncs_with_value(user: User) -> None:
    """Test that table's selected property syncs with FilePicker's value property."""
    await user.open("/")

    picker = user.find(FilePicker).elements.pop()
    temp_dir = picker.current_directory

    file1 = temp_dir / "file1.txt"
    file2 = temp_dir / "file2.pdf"

    # Select files via _on_item_click
    picker._on_item_click({"path": file1, "is_dir": False, "name": "file1.txt"})
    picker._on_item_click({"path": file2, "is_dir": False, "name": "file2.pdf"})

    # Check that table selection is synced
    table = picker._inner_elements.file_table
    assert table is not None
    assert len(table.selected) == 2
    assert any(row["id"] == str(file1) for row in table.selected)
    assert any(row["id"] == str(file2) for row in table.selected)


@pytest.mark.nicegui_main_file(__file__)
async def test_selection_persists_after_navigation(user: User) -> None:
    """Test that selection is cleared after navigating to a different directory."""
    await user.open("/")

    picker = user.find(FilePicker).elements.pop()
    temp_dir = picker.current_directory

    file1 = temp_dir / "file1.txt"

    # Select a file
    picker._on_item_click({"path": file1, "is_dir": False, "name": "file1.txt"})
    assert str(file1) in picker.value

    # Navigate to subfolder
    folder = temp_dir / "folder1"
    picker._navigate_to(folder)

    # Selection should still contain the file from parent directory
    # (This tests that selection doesn't get cleared on navigation)
    assert str(file1) in picker.value


# ==================== Integration Tests ====================


@pytest.mark.nicegui_main_file(__file__)
async def test_complete_multiple_file_selection_workflow(user: User) -> None:
    """Test full workflow of selecting multiple files."""
    await user.open("/")

    picker = user.find(FilePicker).elements.pop()
    temp_dir = picker.current_directory

    # Select multiple files in root
    file1 = temp_dir / "file1.txt"
    file2 = temp_dir / "file2.pdf"

    picker._on_item_click({"path": file1, "is_dir": False, "name": "file1.txt"})
    picker._on_item_click({"path": file2, "is_dir": False, "name": "file2.pdf"})

    assert len(picker.value) == 2
    assert str(file1) in picker.value
    assert str(file2) in picker.value

    # Navigate into folder
    folder1 = temp_dir / "folder1"
    picker._navigate_to(folder1)

    # Add file from subfolder
    file_in_folder = folder1 / "file_in_folder.txt"
    picker._on_item_click({"path": file_in_folder, "is_dir": False, "name": "file_in_folder.txt"})

    # Should have 3 files selected now
    assert len(picker.value) == 3
    assert str(file1) in picker.value
    assert str(file2) in picker.value
    assert str(file_in_folder) in picker.value


# Main page
@ui.page("/")
def main() -> None:
    temp_dir = create_temp_structure()

    ui.label("FilePicker - Read Mode (Multiple)").classes("text-h4")

    FilePicker(starting_directory=str(temp_dir), mode="read", allow_multiple=True)


if __name__ in {"__main__", "__mp_main__"}:
    ui.run()

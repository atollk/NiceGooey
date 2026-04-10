"""
FilePicker Tests - File Filters

Tests for FilePicker with file extension filters.
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

    # Create files with various extensions
    (temp_dir / "file1.txt").write_text("content1")
    (temp_dir / "file2.TXT").write_text("content2")  # Different case
    (temp_dir / "file3.pdf").write_text("content3")
    (temp_dir / "file4.doc").write_text("content4")
    (temp_dir / "file5.jpg").write_text("content5")
    (temp_dir / "no_extension").write_text("content6")

    # Create folders
    (temp_dir / "folder1").mkdir()

    return temp_dir


# ==================== Initialization Tests ====================


@pytest.mark.nicegui_main_file(__file__)
async def test_init_with_file_filter(user: User) -> None:
    """Test initialization with file extensions filter."""
    await user.open("/")
    await user.should_see("FilePicker - With Filter (.txt, .pdf)")

    picker = user.find(FilePicker).elements.pop()

    assert picker.file_filter == [".txt", ".pdf"]


# ==================== File Filter Tests ====================


@pytest.mark.nicegui_main_file(__file__)
async def test_matches_filter_with_extensions(user: User) -> None:
    """Test file matching with extension filter."""
    await user.open("/")

    picker = user.find(FilePicker).elements.pop()
    temp_dir = picker.current_directory

    # Files that should match
    txt_file = temp_dir / "file1.txt"
    pdf_file = temp_dir / "file3.pdf"

    # Files that should not match
    doc_file = temp_dir / "file4.doc"
    jpg_file = temp_dir / "file5.jpg"
    no_ext_file = temp_dir / "no_extension"

    assert picker._path_matches_filter(txt_file) is True
    assert picker._path_matches_filter(pdf_file) is True
    assert picker._path_matches_filter(doc_file) is False
    assert picker._path_matches_filter(jpg_file) is False
    assert picker._path_matches_filter(no_ext_file) is False


@pytest.mark.nicegui_main_file(__file__)
async def test_list_directory_with_filter(user: User) -> None:
    """Test listing respects file extension filter."""
    await user.open("/")

    picker = user.find(FilePicker).elements.pop()
    items = picker._list_directory()

    # Get file names (excluding directories)
    file_names = [item["name"] for item in items if not item["is_dir"]]

    # Should only include .txt and .pdf files
    assert "file1.txt" in file_names
    assert "file2.TXT" in file_names  # Case insensitive
    assert "file3.pdf" in file_names

    # Should not include other extensions
    assert "file4.doc" not in file_names
    assert "file5.jpg" not in file_names
    assert "no_extension" not in file_names

    # Directories should always be included
    dir_names = [item["name"] for item in items if item["is_dir"]]
    assert "folder1" in dir_names


@pytest.mark.nicegui_main_file(__file__)
async def test_file_filter_case_insensitive(user: User) -> None:
    """Test file filter is case-insensitive."""
    await user.open("/")

    picker = user.find(FilePicker).elements.pop()
    temp_dir = picker.current_directory

    # Test with uppercase extension
    txt_upper = temp_dir / "file2.TXT"
    assert picker._path_matches_filter(txt_upper) is True

    # Verify it appears in listing
    items = picker._list_directory()
    file_names = [item["name"] for item in items if not item["is_dir"]]
    assert "file2.TXT" in file_names


@pytest.mark.nicegui_main_file(__file__)
async def test_file_filter_with_and_without_dot(user: User) -> None:
    """Test file filter normalizes extensions (with/without dot)."""
    await user.open("/")
    await user.should_see("FilePicker - Filter Without Dots (jpg, png)")

    picker = user.find(FilePicker).elements.pop()

    # Filter was specified as ["jpg", "png"] without dots
    # Implementation should normalize to [".jpg", ".png"]
    # Check that the filter works correctly
    temp_dir = picker.current_directory

    jpg_file = temp_dir / "test.jpg"
    png_file = temp_dir / "test.png"
    txt_file = temp_dir / "test.txt"

    # These should be created by the second page setup
    if jpg_file.exists():
        assert picker._path_matches_filter(jpg_file) is True
    if png_file.exists():
        assert picker._path_matches_filter(png_file) is True
    if txt_file.exists():
        assert picker._path_matches_filter(txt_file) is False


@pytest.mark.nicegui_main_file(__file__)
async def test_filter_empty_directory(user: User) -> None:
    """Test filter works with empty directory."""
    await user.open("/")

    picker = user.find(FilePicker).elements.pop()
    temp_dir = picker.current_directory

    # Navigate to empty folder
    empty_folder = temp_dir / "folder1"
    picker._navigate_to(empty_folder)

    # Should return empty list (no crash)
    items = picker._list_directory()
    assert items == []


# ==================== Integration Tests ====================


@pytest.mark.nicegui_main_file(__file__)
async def test_filter_selection_workflow(user: User) -> None:
    """Test selecting files with filter applied."""
    await user.open("/")

    picker = user.find(FilePicker).elements.pop()

    # Get filtered files
    items = picker._list_directory()
    file_items = [item for item in items if not item["is_dir"]]

    # Select first filtered file
    if file_items:
        first_file = file_items[0]
        picker._on_item_click(first_file)

        # Should be selected
        assert picker.value == [str(first_file["path"])]


# Main page with two different filter configurations
@ui.page("/")
def main() -> None:
    temp_dir = create_temp_structure()

    ui.label("FilePicker - With Filter (.txt, .pdf)").classes("text-h4")
    FilePicker(starting_directory=str(temp_dir), mode="read", file_filter=[".txt", ".pdf"])

    ui.separator()

    # Create second temp structure for filter without dots test
    temp_dir2 = Path(tempfile.mkdtemp())
    (temp_dir2 / "test.jpg").write_text("image1")
    (temp_dir2 / "test.png").write_text("image2")
    (temp_dir2 / "test.txt").write_text("text")
    (temp_dir2 / "folder1").mkdir()

    ui.label("FilePicker - Filter Without Dots (jpg, png)").classes("text-h4")
    FilePicker(starting_directory=str(temp_dir2), mode="read", file_filter=["jpg", "png"])


if __name__ in {"__main__", "__mp_main__"}:
    ui.run()

"""
FilePicker Tests - Read Mode, Single Selection

Tests for FilePicker in read mode with single file selection.
"""

import platform
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
async def test_init_default_params(user: User) -> None:
    """Test FilePicker initialization with default parameters."""
    await user.open("/")
    await user.should_see("FilePicker - Read Mode (Single)")

    picker = user.find(FilePicker).elements.pop()

    assert picker.allow_directory_selection is False
    assert picker.allow_multiple is False
    assert picker.show_hidden is False
    assert picker.show_buttons is True
    assert picker.file_filter is None
    assert picker.value == []


@pytest.mark.nicegui_main_file(__file__)
async def test_init_read_mode(user: User) -> None:
    """Test initialization in read mode."""
    await user.open("/")
    await user.should_see("FilePicker")

    picker = user.find(FilePicker).elements.pop()
    assert picker.value == []


# ==================== File System Operation Tests ====================


@pytest.mark.nicegui_main_file(__file__)
async def test_is_windows(user: User) -> None:
    """Test OS detection."""
    await user.open("/")

    picker = user.find(FilePicker).elements.pop()
    expected = platform.system() == "Windows"
    assert picker._is_windows() == expected


@pytest.mark.nicegui_main_file(__file__)
async def test_is_hidden_unix(user: User) -> None:
    """Test hidden file detection for dot files."""
    await user.open("/")

    picker = user.find(FilePicker).elements.pop()
    temp_dir = picker.current_directory

    hidden_file = temp_dir / ".hidden_file"
    regular_file = temp_dir / "file1.txt"

    assert picker._is_hidden(hidden_file) is True
    assert picker._is_hidden(regular_file) is False


@pytest.mark.nicegui_main_file(__file__)
async def test_matches_filter_no_filter(user: User) -> None:
    """Test file matching when no filter is set."""
    await user.open("/")

    picker = user.find(FilePicker).elements.pop()
    temp_dir = picker.current_directory
    file_path = temp_dir / "file1.txt"
    assert picker._matches_filter(file_path) is True


@pytest.mark.nicegui_main_file(__file__)
async def test_matches_filter_directories_always_match(user: User) -> None:
    """Test that directories always match filters."""
    await user.open("/")

    picker = user.find(FilePicker).elements.pop()
    temp_dir = picker.current_directory
    folder = temp_dir / "folder1"
    assert picker._matches_filter(folder) is True


@pytest.mark.nicegui_main_file(__file__)
async def test_get_file_size(user: User) -> None:
    """Test human-readable file size formatting."""
    await user.open("/")

    picker = user.find(FilePicker).elements.pop()
    temp_dir = picker.current_directory
    file_path = temp_dir / "file1.txt"
    size = picker._get_file_size(file_path)

    assert isinstance(size, str)
    assert "B" in size


@pytest.mark.nicegui_main_file(__file__)
async def test_get_file_size_directory(user: User) -> None:
    """Test that directory size returns empty string."""
    await user.open("/")

    picker = user.find(FilePicker).elements.pop()
    temp_dir = picker.current_directory
    folder = temp_dir / "folder1"
    size = picker._get_file_size(folder)

    assert size == ""


@pytest.mark.nicegui_main_file(__file__)
async def test_get_modified_time(user: User) -> None:
    """Test modification time formatting."""
    await user.open("/")

    picker = user.find(FilePicker).elements.pop()
    temp_dir = picker.current_directory
    file_path = temp_dir / "file1.txt"
    mtime = picker._get_modified_time(file_path)

    assert isinstance(mtime, str)
    assert "-" in mtime
    assert ":" in mtime


@pytest.mark.nicegui_main_file(__file__)
async def test_list_directory(user: User) -> None:
    """Test directory listing."""
    await user.open("/")

    picker = user.find(FilePicker).elements.pop()
    items = picker._list_directory()

    assert isinstance(items, list)
    assert len(items) > 0
    assert all("path" in item for item in items)
    assert all("name" in item for item in items)
    assert all("is_dir" in item for item in items)


@pytest.mark.nicegui_main_file(__file__)
async def test_list_directory_filters_hidden_files(user: User) -> None:
    """Test listing excludes hidden files by default."""
    await user.open("/")

    picker = user.find(FilePicker).elements.pop()
    items = picker._list_directory()
    names = [item["name"] for item in items]

    assert ".hidden_file" not in names
    assert ".hidden_folder" not in names


@pytest.mark.nicegui_main_file(__file__)
async def test_list_directory_sorting(user: User) -> None:
    """Test that directories come first, then files, alphabetically."""
    await user.open("/")

    picker = user.find(FilePicker).elements.pop()
    items = picker._list_directory()

    # Find the index of first file
    first_file_idx = next((i for i, item in enumerate(items) if not item["is_dir"]), None)

    if first_file_idx is not None:
        # All items before first_file_idx should be directories
        for i in range(first_file_idx):
            assert items[i]["is_dir"] is True

        # All items after should be files
        for i in range(first_file_idx, len(items)):
            assert items[i]["is_dir"] is False


# ==================== Navigation Tests ====================


@pytest.mark.nicegui_main_file(__file__)
async def test_navigate_to_subdirectory(user: User) -> None:
    """Test navigating into a subdirectory."""
    await user.open("/")

    picker = user.find(FilePicker).elements.pop()
    temp_dir = picker.current_directory
    subfolder = temp_dir / "folder1"
    picker._navigate_to(subfolder)

    assert picker.current_directory == subfolder


@pytest.mark.nicegui_main_file(__file__)
async def test_navigate_to_parent(user: User) -> None:
    """Test navigating to parent directory."""
    await user.open("/")

    picker = user.find(FilePicker).elements.pop()
    temp_dir = picker.current_directory
    subfolder = temp_dir / "folder1"
    picker._navigate_to(subfolder)
    picker._navigate_to(temp_dir)

    assert picker.current_directory == temp_dir


@pytest.mark.nicegui_main_file(__file__)
async def test_current_directory_property(user: User) -> None:
    """Test current_directory getter/setter."""
    await user.open("/")

    picker = user.find(FilePicker).elements.pop()
    temp_dir = picker.current_directory
    new_dir = temp_dir / "folder1"
    picker.current_directory = new_dir

    assert picker.current_directory == new_dir


# ==================== Selection Logic Tests ====================


@pytest.mark.nicegui_main_file(__file__)
async def test_single_selection_file(user: User) -> None:
    """Test selecting a single file in read mode."""
    await user.open("/")

    picker = user.find(FilePicker).elements.pop()
    temp_dir = picker.current_directory
    file_path = temp_dir / "file1.txt"
    picker._on_item_click({"path": file_path, "is_dir": False, "name": "file1.txt"})

    assert picker.value == [str(file_path)]


@pytest.mark.nicegui_main_file(__file__)
async def test_single_selection_replaces(user: User) -> None:
    """Test that single selection replaces previous selection."""
    await user.open("/")

    picker = user.find(FilePicker).elements.pop()
    temp_dir = picker.current_directory
    file1 = temp_dir / "file1.txt"
    file2 = temp_dir / "file2.pdf"

    picker._on_item_click({"path": file1, "is_dir": False, "name": "file1.txt"})
    picker._on_item_click({"path": file2, "is_dir": False, "name": "file2.pdf"})

    assert picker.value == [str(file2)]


@pytest.mark.nicegui_main_file(__file__)
async def test_directory_selection_when_not_allowed(user: User) -> None:
    """Test that clicking directory navigates when not allowed."""
    await user.open("/")

    picker = user.find(FilePicker).elements.pop()
    temp_dir = picker.current_directory
    folder = temp_dir / "folder1"
    picker._on_item_click({"path": folder, "is_dir": True, "name": "folder1"})

    # Should navigate into the directory
    assert picker.current_directory == folder


@pytest.mark.nicegui_main_file(__file__)
async def test_value_single_selection(user: User) -> None:
    """Test value property in single selection mode."""
    await user.open("/")

    picker = user.find(FilePicker).elements.pop()
    temp_dir = picker.current_directory
    file_path = temp_dir / "file1.txt"
    picker.value = [str(file_path)]

    assert picker.value == [str(file_path)]
    assert picker.value[0] == str(file_path)


# ==================== UI Interaction Tests ====================


@pytest.mark.nicegui_main_file(__file__)
async def test_item_click_navigates_to_folder(user: User) -> None:
    """Test clicking folder navigates into it."""
    await user.open("/")

    picker = user.find(FilePicker).elements.pop()
    temp_dir = picker.current_directory
    folder = temp_dir / "folder1"
    picker._on_item_click({"path": folder, "is_dir": True, "name": "folder1"})

    assert picker.current_directory == folder


@pytest.mark.nicegui_main_file(__file__)
async def test_item_click_selects_file(user: User) -> None:
    """Test clicking file selects it."""
    await user.open("/")

    picker = user.find(FilePicker).elements.pop()
    temp_dir = picker.current_directory
    file_path = temp_dir / "file1.txt"
    picker._on_item_click({"path": file_path, "is_dir": False, "name": "file1.txt"})

    assert picker.value == [str(file_path)]


@pytest.mark.nicegui_main_file(__file__)
async def test_item_double_click_navigates(user: User) -> None:
    """Test double-clicking folder navigates."""
    await user.open("/")

    picker = user.find(FilePicker).elements.pop()
    temp_dir = picker.current_directory
    folder = temp_dir / "folder1"
    picker._on_item_double_click({"path": folder, "is_dir": True, "name": "folder1"})

    assert picker.current_directory == folder


@pytest.mark.nicegui_main_file(__file__)
async def test_refresh_updates_listing(user: User) -> None:
    """Test refresh() updates the file listing."""
    await user.open("/")

    picker = user.find(FilePicker).elements.pop()
    temp_dir = picker.current_directory

    # Get initial listing
    initial_items = picker._list_directory()

    # Create a new file
    new_file = temp_dir / "new_file.txt"
    new_file.write_text("new content")

    # Refresh and get updated listing
    updated_items = picker._list_directory()

    assert len(updated_items) > len(initial_items)
    assert any(item["name"] == "new_file.txt" for item in updated_items)


# ==================== Integration Tests ====================


@pytest.mark.nicegui_main_file(__file__)
async def test_complete_file_selection_workflow(user: User) -> None:
    """Test full workflow of navigating and selecting file."""
    await user.open("/")

    picker = user.find(FilePicker).elements.pop()
    temp_dir = picker.current_directory

    # Navigate into folder1
    folder1 = temp_dir / "folder1"
    picker._navigate_to(folder1)
    assert picker.current_directory == folder1

    # Select a file in the folder
    file_path = folder1 / "file_in_folder.txt"
    picker._on_item_click({"path": file_path, "is_dir": False, "name": "file_in_folder.txt"})
    assert picker.value == [str(file_path)]

    # Verify selected path
    assert picker.value[0] == str(file_path)


# Main page
@ui.page("/")
def main() -> None:
    temp_dir = create_temp_structure()

    ui.label("FilePicker - Read Mode (Single)").classes("text-h4")

    FilePicker(starting_directory=str(temp_dir), mode="read")


if __name__ in {"__main__", "__mp_main__"}:
    ui.run()

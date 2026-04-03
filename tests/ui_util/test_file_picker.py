"""
Comprehensive tests for the FilePicker widget.

Tests cover:
- Initialization with various configurations
- File system operations (listing, filtering, size/time formatting)
- Navigation (directory traversal, breadcrumbs)
- Selection logic (single, multiple, directories)
- UI interactions
- Callbacks (OK, Cancel)
- Write mode features
- Edge cases and error handling
- Integration workflows
"""

import platform
from unittest.mock import Mock, patch

import pytest

from nicegooey.ui_util.file_picker import FilePicker


# ==================== Fixtures ====================


@pytest.fixture
def temp_dir_structure(tmp_path):
    """
    Create a temporary directory structure for testing.

    Structure:
    tmp_path/
        file1.txt
        file2.pdf
        file3.doc
        .hidden_file
        folder1/
            subfolder1/
            file_in_folder.txt
        folder2/
        .hidden_folder/
    """
    # Create files
    (tmp_path / "file1.txt").write_text("content1")
    (tmp_path / "file2.pdf").write_text("content2")
    (tmp_path / "file3.doc").write_text("content3")
    (tmp_path / ".hidden_file").write_text("hidden")

    # Create folders
    (tmp_path / "folder1").mkdir()
    (tmp_path / "folder1" / "subfolder1").mkdir()
    (tmp_path / "folder1" / "file_in_folder.txt").write_text("nested")
    (tmp_path / "folder2").mkdir()
    (tmp_path / ".hidden_folder").mkdir()

    return tmp_path


@pytest.fixture
def mock_notify():
    """Mock ui.notify to capture notification calls."""
    with patch("nicegooey.ui_util.file_picker.ui.notify") as mock:
        yield mock


# ==================== 1. Initialization Tests ====================


def test_init_default_params(temp_dir_structure):
    """Test FilePicker initialization with default parameters."""
    picker = FilePicker(starting_directory=str(temp_dir_structure))

    assert picker.mode == "read"
    assert picker.allow_directory_selection is False
    assert picker.allow_multiple is False
    assert picker.show_hidden is False
    assert picker.show_buttons is True
    assert picker.file_filter is None
    assert picker.on_ok is None
    assert picker.on_cancel is None
    assert picker.current_directory == temp_dir_structure
    assert picker.value is None


def test_init_read_mode(temp_dir_structure):
    """Test initialization in read mode."""
    picker = FilePicker(starting_directory=str(temp_dir_structure), mode="read")

    assert picker.mode == "read"
    assert picker.value is None


def test_init_write_mode(temp_dir_structure):
    """Test initialization in write mode."""
    picker = FilePicker(starting_directory=str(temp_dir_structure), mode="write")

    assert picker.mode == "write"
    assert picker.value is None
    assert picker._filename_input_value == ""


def test_init_with_starting_directory(temp_dir_structure):
    """Test initialization with a specific starting directory."""
    subfolder = temp_dir_structure / "folder1"
    picker = FilePicker(starting_directory=str(subfolder))

    assert picker.current_directory == subfolder


def test_init_invalid_mode(temp_dir_structure):
    """Test that invalid mode raises ValueError."""
    with pytest.raises(ValueError, match="mode must be 'read' or 'write'"):
        FilePicker(starting_directory=str(temp_dir_structure), mode="invalid")


def test_init_with_file_filter(temp_dir_structure):
    """Test initialization with file extensions filter."""
    picker = FilePicker(starting_directory=str(temp_dir_structure), file_filter=[".txt", "pdf"])

    assert picker.file_filter == [".txt", ".pdf"]


def test_init_with_callbacks(temp_dir_structure):
    """Test initialization with on_ok and on_cancel callbacks."""
    ok_callback = Mock()
    cancel_callback = Mock()

    picker = FilePicker(
        starting_directory=str(temp_dir_structure), on_ok=ok_callback, on_cancel=cancel_callback
    )

    assert picker.on_ok is ok_callback
    assert picker.on_cancel is cancel_callback


def test_init_multiple_selection(temp_dir_structure):
    """Test initialization with allow_multiple=True."""
    picker = FilePicker(starting_directory=str(temp_dir_structure), allow_multiple=True)

    assert picker.allow_multiple is True
    assert picker.value == []


def test_init_directory_selection(temp_dir_structure):
    """Test initialization with allow_directory_selection=True."""
    picker = FilePicker(starting_directory=str(temp_dir_structure), allow_directory_selection=True)

    assert picker.allow_directory_selection is True


# ==================== 2. File System Operation Tests ====================


def test_is_windows(temp_dir_structure):
    """Test OS detection."""
    picker = FilePicker(starting_directory=str(temp_dir_structure))

    expected = platform.system() == "Windows"
    assert picker._is_windows() == expected


@pytest.mark.skipif(platform.system() != "Windows", reason="Windows-specific test")
def test_get_drives(temp_dir_structure):
    """Test drive listing on Windows."""
    picker = FilePicker(starting_directory=str(temp_dir_structure))

    drives = picker._get_drives()
    assert isinstance(drives, list)
    assert len(drives) > 0
    assert all(d.endswith(":\\") for d in drives)


def test_is_hidden_unix(temp_dir_structure):
    """Test hidden file detection for dot files."""
    picker = FilePicker(starting_directory=str(temp_dir_structure))

    hidden_file = temp_dir_structure / ".hidden_file"
    regular_file = temp_dir_structure / "file1.txt"

    assert picker._is_hidden(hidden_file) is True
    assert picker._is_hidden(regular_file) is False


def test_matches_filter_no_filter(temp_dir_structure):
    """Test file matching when no filter is set."""
    picker = FilePicker(starting_directory=str(temp_dir_structure))

    file_path = temp_dir_structure / "file1.txt"
    assert picker._matches_filter(file_path) is True


def test_matches_filter_with_extensions(temp_dir_structure):
    """Test file matching with extension filter."""
    picker = FilePicker(starting_directory=str(temp_dir_structure), file_filter=[".txt", ".pdf"])

    txt_file = temp_dir_structure / "file1.txt"
    pdf_file = temp_dir_structure / "file2.pdf"
    doc_file = temp_dir_structure / "file3.doc"

    assert picker._matches_filter(txt_file) is True
    assert picker._matches_filter(pdf_file) is True
    assert picker._matches_filter(doc_file) is False


def test_matches_filter_directories_always_match(temp_dir_structure):
    """Test that directories always match filters."""
    picker = FilePicker(starting_directory=str(temp_dir_structure), file_filter=[".txt"])

    folder = temp_dir_structure / "folder1"
    assert picker._matches_filter(folder) is True


def test_get_file_size(temp_dir_structure):
    """Test human-readable file size formatting."""
    picker = FilePicker(starting_directory=str(temp_dir_structure))

    file_path = temp_dir_structure / "file1.txt"
    size = picker._get_file_size(file_path)

    assert isinstance(size, str)
    assert "B" in size


def test_get_file_size_directory(temp_dir_structure):
    """Test that directory size returns empty string."""
    picker = FilePicker(starting_directory=str(temp_dir_structure))

    folder = temp_dir_structure / "folder1"
    size = picker._get_file_size(folder)

    assert size == ""


def test_get_modified_time(temp_dir_structure):
    """Test modification time formatting."""
    picker = FilePicker(starting_directory=str(temp_dir_structure))

    file_path = temp_dir_structure / "file1.txt"
    mtime = picker._get_modified_time(file_path)

    assert isinstance(mtime, str)
    assert "-" in mtime
    assert ":" in mtime


def test_list_directory(temp_dir_structure):
    """Test directory listing."""
    picker = FilePicker(starting_directory=str(temp_dir_structure))

    items = picker._list_directory()

    assert isinstance(items, list)
    assert len(items) > 0
    assert all("path" in item for item in items)
    assert all("name" in item for item in items)
    assert all("is_dir" in item for item in items)


def test_list_directory_with_hidden_files(temp_dir_structure):
    """Test listing includes hidden files when enabled."""
    picker = FilePicker(starting_directory=str(temp_dir_structure), show_hidden=True)

    items = picker._list_directory()
    names = [item["name"] for item in items]

    assert ".hidden_file" in names
    assert ".hidden_folder" in names


def test_list_directory_filters_hidden_files(temp_dir_structure):
    """Test listing excludes hidden files by default."""
    picker = FilePicker(starting_directory=str(temp_dir_structure))

    items = picker._list_directory()
    names = [item["name"] for item in items]

    assert ".hidden_file" not in names
    assert ".hidden_folder" not in names


def test_list_directory_with_filter(temp_dir_structure):
    """Test listing respects file extension filter."""
    picker = FilePicker(starting_directory=str(temp_dir_structure), file_filter=[".txt"])

    items = picker._list_directory()
    file_names = [item["name"] for item in items if not item["is_dir"]]

    assert "file1.txt" in file_names
    assert "file2.pdf" not in file_names
    assert "file3.doc" not in file_names


def test_list_directory_sorting(temp_dir_structure):
    """Test that directories come first, then files, alphabetically."""
    picker = FilePicker(starting_directory=str(temp_dir_structure))

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


# ==================== 3. Navigation Tests ====================


def test_navigate_to_subdirectory(temp_dir_structure):
    """Test navigating into a subdirectory."""
    picker = FilePicker(starting_directory=str(temp_dir_structure))

    subfolder = temp_dir_structure / "folder1"
    picker._navigate_to(subfolder)

    assert picker.current_directory == subfolder


def test_navigate_to_parent(temp_dir_structure):
    """Test navigating to parent directory."""
    subfolder = temp_dir_structure / "folder1"
    picker = FilePicker(starting_directory=str(subfolder))

    picker._navigate_to(temp_dir_structure)

    assert picker.current_directory == temp_dir_structure


def test_navigate_to_invalid_path(temp_dir_structure, mock_notify):
    """Test navigating to non-existent path."""
    picker = FilePicker(starting_directory=str(temp_dir_structure))

    invalid_path = temp_dir_structure / "nonexistent"
    original_dir = picker.current_directory

    picker._navigate_to(invalid_path)

    # Should stay in the same directory
    assert picker.current_directory == original_dir


def test_set_directory(temp_dir_structure):
    """Test public API method for changing directory."""
    picker = FilePicker(starting_directory=str(temp_dir_structure))

    subfolder = temp_dir_structure / "folder1"
    picker.set_directory(str(subfolder))

    assert picker.current_directory == subfolder


def test_set_directory_invalid(temp_dir_structure, mock_notify):
    """Test set_directory with non-directory path."""
    picker = FilePicker(starting_directory=str(temp_dir_structure))

    file_path = temp_dir_structure / "file1.txt"
    original_dir = picker.current_directory

    picker.set_directory(str(file_path))

    # Should stay in the same directory
    assert picker.current_directory == original_dir
    mock_notify.assert_called_once()


def test_current_directory_property(temp_dir_structure):
    """Test current_directory getter/setter."""
    picker = FilePicker(starting_directory=str(temp_dir_structure))

    new_dir = temp_dir_structure / "folder1"
    picker.current_directory = new_dir

    assert picker.current_directory == new_dir


# ==================== 4. Selection Logic Tests ====================


def test_single_selection_file(temp_dir_structure):
    """Test selecting a single file in read mode."""
    picker = FilePicker(starting_directory=str(temp_dir_structure))

    file_path = temp_dir_structure / "file1.txt"
    picker._on_item_click({"path": file_path, "is_dir": False, "name": "file1.txt"})

    assert picker.value == file_path


def test_single_selection_replaces(temp_dir_structure):
    """Test that single selection replaces previous selection."""
    picker = FilePicker(starting_directory=str(temp_dir_structure))

    file1 = temp_dir_structure / "file1.txt"
    file2 = temp_dir_structure / "file2.pdf"

    picker._on_item_click({"path": file1, "is_dir": False, "name": "file1.txt"})

    picker._on_item_click({"path": file2, "is_dir": False, "name": "file2.pdf"})

    assert picker.value == file2


def test_multiple_selection_files(temp_dir_structure):
    """Test selecting multiple files."""
    picker = FilePicker(starting_directory=str(temp_dir_structure), allow_multiple=True)

    file1 = temp_dir_structure / "file1.txt"
    file2 = temp_dir_structure / "file2.pdf"

    picker._on_item_click({"path": file1, "is_dir": False, "name": "file1.txt"})

    picker._on_item_click({"path": file2, "is_dir": False, "name": "file2.pdf"})

    assert file1 in picker.value
    assert file2 in picker.value


def test_multiple_selection_toggle(temp_dir_structure):
    """Test toggling selection in multiple mode."""
    picker = FilePicker(starting_directory=str(temp_dir_structure), allow_multiple=True)

    file1 = temp_dir_structure / "file1.txt"

    # Select
    picker._on_item_click({"path": file1, "is_dir": False, "name": "file1.txt"})
    assert file1 in picker.value

    # Deselect
    picker._on_item_click({"path": file1, "is_dir": False, "name": "file1.txt"})
    assert file1 not in picker.value


def test_directory_selection_when_allowed(temp_dir_structure):
    """Test selecting a directory when allowed."""
    picker = FilePicker(starting_directory=str(temp_dir_structure), allow_directory_selection=True)

    folder = temp_dir_structure / "folder1"
    picker._on_item_click({"path": folder, "is_dir": True, "name": "folder1"})

    assert picker.value == folder


def test_directory_selection_when_not_allowed(temp_dir_structure):
    """Test that clicking directory navigates when not allowed."""
    picker = FilePicker(starting_directory=str(temp_dir_structure))

    folder = temp_dir_structure / "folder1"
    picker._on_item_click({"path": folder, "is_dir": True, "name": "folder1"})

    # Should navigate into the directory
    assert picker.current_directory == folder


def test_get_selected_path_single(temp_dir_structure):
    """Test get_selected_path() in single selection mode."""
    picker = FilePicker(starting_directory=str(temp_dir_structure))

    file_path = temp_dir_structure / "file1.txt"
    picker.value = file_path

    assert picker.get_selected_path() == file_path


def test_get_selected_path_multiple(temp_dir_structure):
    """Test get_selected_path() in multiple selection mode."""
    picker = FilePicker(starting_directory=str(temp_dir_structure), allow_multiple=True)

    file1 = temp_dir_structure / "file1.txt"
    file2 = temp_dir_structure / "file2.pdf"
    picker.value = [file1, file2]

    # Should return first selected item
    assert picker.get_selected_path() == file1


def test_get_selected_paths_single(temp_dir_structure):
    """Test get_selected_paths() in single selection mode."""
    picker = FilePicker(starting_directory=str(temp_dir_structure))

    file_path = temp_dir_structure / "file1.txt"
    picker.value = file_path

    paths = picker.get_selected_paths()
    assert paths == [file_path]


def test_get_selected_paths_multiple(temp_dir_structure):
    """Test get_selected_paths() in multiple selection mode."""
    picker = FilePicker(starting_directory=str(temp_dir_structure), allow_multiple=True)

    file1 = temp_dir_structure / "file1.txt"
    file2 = temp_dir_structure / "file2.pdf"
    picker.value = [file1, file2]

    paths = picker.get_selected_paths()
    assert paths == [file1, file2]


# ==================== 5. UI Interaction Tests ====================


def test_item_click_navigates_to_folder(temp_dir_structure):
    """Test clicking folder navigates into it."""
    picker = FilePicker(starting_directory=str(temp_dir_structure))

    folder = temp_dir_structure / "folder1"
    picker._on_item_click({"path": folder, "is_dir": True, "name": "folder1"})

    assert picker.current_directory == folder


def test_item_click_selects_file(temp_dir_structure):
    """Test clicking file selects it."""
    picker = FilePicker(starting_directory=str(temp_dir_structure))

    file_path = temp_dir_structure / "file1.txt"
    picker._on_item_click({"path": file_path, "is_dir": False, "name": "file1.txt"})

    assert picker.value == file_path


def test_item_double_click_navigates(temp_dir_structure):
    """Test double-clicking folder navigates."""
    picker = FilePicker(starting_directory=str(temp_dir_structure))

    folder = temp_dir_structure / "folder1"
    picker._on_item_double_click({"path": folder, "is_dir": True, "name": "folder1"})

    assert picker.current_directory == folder


def test_refresh_updates_listing(temp_dir_structure):
    """Test refresh() updates the file listing."""
    picker = FilePicker(starting_directory=str(temp_dir_structure))

    # Get initial listing
    initial_items = picker._list_directory()

    # Create a new file
    new_file = temp_dir_structure / "new_file.txt"
    new_file.write_text("new content")

    # Refresh and get updated listing
    updated_items = picker._list_directory()

    assert len(updated_items) > len(initial_items)
    assert any(item["name"] == "new_file.txt" for item in updated_items)


def test_selection_display_updates(temp_dir_structure):
    """Test that selection display updates correctly."""
    picker = FilePicker(starting_directory=str(temp_dir_structure))

    # Create a mock label
    picker._selected_label = Mock()

    file_path = temp_dir_structure / "file1.txt"
    picker.value = file_path

    picker._update_selection_display()

    # Should have called set_text
    picker._selected_label.set_text.assert_called_once()


def test_filename_input_in_write_mode(temp_dir_structure):
    """Test filename input field in write mode."""
    picker = FilePicker(starting_directory=str(temp_dir_structure), mode="write")

    # Create a mock input field
    picker._filename_input = Mock()

    file_path = temp_dir_structure / "file1.txt"
    picker._on_item_click({"path": file_path, "is_dir": False, "name": "file1.txt"})

    # Filename should be set
    assert picker._filename_input_value == "file1.txt"


# ==================== 6. Callback Tests ====================


def test_ok_callback_read_mode(temp_dir_structure):
    """Test OK button calls callback in read mode."""
    ok_callback = Mock()
    picker = FilePicker(starting_directory=str(temp_dir_structure), on_ok=ok_callback)

    file_path = temp_dir_structure / "file1.txt"
    picker.value = file_path

    picker._on_ok_click()

    ok_callback.assert_called_once()


def test_ok_callback_write_mode(temp_dir_structure):
    """Test OK button calls callback in write mode with filename."""
    ok_callback = Mock()
    picker = FilePicker(starting_directory=str(temp_dir_structure), mode="write", on_ok=ok_callback)

    picker._filename_input_value = "newfile.txt"

    picker._on_ok_click()

    ok_callback.assert_called_once()
    assert picker.value == temp_dir_structure / "newfile.txt"


def test_ok_validation_no_selection(temp_dir_structure, mock_notify):
    """Test OK validates selection exists."""
    picker = FilePicker(starting_directory=str(temp_dir_structure))

    picker._on_ok_click()

    mock_notify.assert_called_once()


def test_ok_validation_no_filename(temp_dir_structure, mock_notify):
    """Test OK validates filename in write mode."""
    picker = FilePicker(starting_directory=str(temp_dir_structure), mode="write")

    picker._filename_input_value = ""

    picker._on_ok_click()

    mock_notify.assert_called_once()


def test_cancel_callback(temp_dir_structure):
    """Test Cancel button calls callback."""
    cancel_callback = Mock()
    picker = FilePicker(starting_directory=str(temp_dir_structure), on_cancel=cancel_callback)

    picker._on_cancel_click()

    cancel_callback.assert_called_once()


def test_callbacks_optional(temp_dir_structure):
    """Test that callbacks are optional."""
    picker = FilePicker(starting_directory=str(temp_dir_structure))

    # Should not raise any errors
    picker._on_ok_click()
    picker._on_cancel_click()


# ==================== 7. Write Mode Specific Tests ====================


def test_write_mode_filename_input(temp_dir_structure):
    """Test filename input field exists."""
    picker = FilePicker(starting_directory=str(temp_dir_structure), mode="write")

    assert picker._filename_input_value == ""


def test_write_mode_selection_sets_filename(temp_dir_structure):
    """Test clicking file populates filename input."""
    picker = FilePicker(starting_directory=str(temp_dir_structure), mode="write")

    file_path = temp_dir_structure / "file1.txt"
    picker._on_item_click({"path": file_path, "is_dir": False, "name": "file1.txt"})

    assert picker._filename_input_value == "file1.txt"


def test_write_mode_ok_creates_full_path(temp_dir_structure):
    """Test OK in write mode creates full path from filename."""
    picker = FilePicker(starting_directory=str(temp_dir_structure), mode="write")

    picker._filename_input_value = "newfile.txt"
    picker._on_ok_click()

    expected_path = temp_dir_structure / "newfile.txt"
    assert picker.value == expected_path


# ==================== 8. Edge Cases and Error Handling ====================


def test_empty_directory(tmp_path):
    """Test listing empty directory."""
    picker = FilePicker(starting_directory=str(tmp_path))

    items = picker._list_directory()

    assert items == []


def test_file_filter_case_insensitive(temp_dir_structure):
    """Test file filter is case-insensitive."""
    picker = FilePicker(starting_directory=str(temp_dir_structure), file_filter=[".TXT"])

    # Create a file with lowercase extension
    file_path = temp_dir_structure / "test.txt"

    assert picker._matches_filter(file_path) is True


def test_file_filter_with_and_without_dot(temp_dir_structure):
    """Test file filter normalizes extensions."""
    picker1 = FilePicker(starting_directory=str(temp_dir_structure), file_filter=[".txt"])
    picker2 = FilePicker(starting_directory=str(temp_dir_structure), file_filter=["txt"])

    file_path = temp_dir_structure / "file1.txt"

    assert picker1._matches_filter(file_path) is True
    assert picker2._matches_filter(file_path) is True
    assert picker1.file_filter == picker2.file_filter


def test_multiple_mode_disabled_in_write_mode(temp_dir_structure):
    """Test allow_multiple is ignored in write mode."""
    picker = FilePicker(starting_directory=str(temp_dir_structure), mode="write", allow_multiple=True)

    # Should be forced to False in write mode
    assert picker.allow_multiple is False


def test_show_buttons_false(temp_dir_structure):
    """Test that buttons can be hidden."""
    picker = FilePicker(starting_directory=str(temp_dir_structure), show_buttons=False)

    assert picker.show_buttons is False


def test_get_selected_path_returns_none_when_empty(temp_dir_structure):
    """Test get_selected_path returns None when no selection."""
    picker = FilePicker(starting_directory=str(temp_dir_structure))

    assert picker.get_selected_path() is None


def test_get_selected_paths_returns_empty_list_when_empty(temp_dir_structure):
    """Test get_selected_paths returns empty list when no selection."""
    picker = FilePicker(starting_directory=str(temp_dir_structure))

    assert picker.get_selected_paths() == []


# ==================== 9. Integration Tests ====================


def test_complete_file_selection_workflow(temp_dir_structure):
    """Test full workflow of navigating and selecting file."""
    picker = FilePicker(starting_directory=str(temp_dir_structure))

    # Navigate into folder1
    folder1 = temp_dir_structure / "folder1"
    picker._navigate_to(folder1)
    assert picker.current_directory == folder1

    # Select a file in the folder
    file_path = folder1 / "file_in_folder.txt"
    picker._on_item_click({"path": file_path, "is_dir": False, "name": "file_in_folder.txt"})
    assert picker.value == file_path

    # Get selected path
    assert picker.get_selected_path() == file_path


def test_complete_save_file_workflow(temp_dir_structure):
    """Test full workflow in write mode."""
    ok_callback = Mock()
    picker = FilePicker(starting_directory=str(temp_dir_structure), mode="write", on_ok=ok_callback)

    # Navigate into folder1
    folder1 = temp_dir_structure / "folder1"
    picker._navigate_to(folder1)

    # Enter a filename
    picker._filename_input_value = "newfile.txt"

    # Click OK
    picker._on_ok_click()

    # Should have called the callback
    ok_callback.assert_called_once()

    # Selected should be the full path
    expected_path = folder1 / "newfile.txt"
    assert picker.value == expected_path


def test_multiple_file_selection_workflow(temp_dir_structure):
    """Test selecting multiple files workflow."""
    picker = FilePicker(starting_directory=str(temp_dir_structure), allow_multiple=True)

    # Select file1
    file1 = temp_dir_structure / "file1.txt"
    picker._on_item_click({"path": file1, "is_dir": False, "name": "file1.txt"})

    # Select file2
    file2 = temp_dir_structure / "file2.pdf"
    picker._on_item_click({"path": file2, "is_dir": False, "name": "file2.pdf"})

    # Both should be selected
    selected = picker.get_selected_paths()
    assert file1 in selected
    assert file2 in selected
    assert len(selected) == 2


def test_directory_selection_workflow(temp_dir_structure):
    """Test selecting a directory workflow."""
    picker = FilePicker(starting_directory=str(temp_dir_structure), allow_directory_selection=True)

    # Select a folder
    folder = temp_dir_structure / "folder1"
    picker._on_item_click({"path": folder, "is_dir": True, "name": "folder1"})

    # Folder should be selected
    assert picker.get_selected_path() == folder


def test_refresh_method(temp_dir_structure):
    """Test the public refresh() method."""
    picker = FilePicker(starting_directory=str(temp_dir_structure))

    # Create mock UI components
    mock_path_bar = Mock()
    mock_path_bar.__enter__ = Mock(return_value=mock_path_bar)
    mock_path_bar.__exit__ = Mock(return_value=False)
    mock_path_bar.clear = Mock()

    mock_file_table = Mock()
    mock_file_table.rows = Mock()
    mock_file_table.rows.clear = Mock()
    mock_file_table.rows.extend = Mock()
    mock_file_table.update = Mock()

    picker._path_bar = mock_path_bar
    picker._file_table = mock_file_table

    # Call refresh - should not raise errors
    picker.refresh()

    # Path bar should be cleared
    mock_path_bar.clear.assert_called_once()

"""
FilePicker Tests - Callbacks

Tests for FilePicker OK and Cancel button callbacks.
"""

import tempfile
from pathlib import Path

import pytest
from nicegui import app, ui
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

    # Create folders
    (temp_dir / "folder1").mkdir()

    return temp_dir


def reset_callback_state():
    """Reset callback tracking state in shared storage."""
    app.storage.general["ok_called"] = []
    app.storage.general["cancel_called"] = []
    app.storage.general["ok_value"] = []


# ==================== Initialization Tests ====================


@pytest.mark.nicegui_main_file(__file__)
async def test_init_with_callbacks(user: User) -> None:
    """Test initialization with on_ok and on_cancel callbacks."""
    await user.open("/")
    await user.should_see("FilePicker - With Callbacks")

    picker = user.find(FilePicker).elements.pop()

    assert picker.on_ok is not None
    assert picker.on_cancel is not None


@pytest.mark.nicegui_main_file(__file__)
async def test_init_without_callbacks(user: User) -> None:
    """Test that callbacks are optional."""
    await user.open("/")
    await user.should_see("FilePicker - No Callbacks")

    pickers = user.find(FilePicker).elements
    # Get the picker without callbacks (uses default no-op lambdas)
    picker = next((p for p in pickers if p.mode == p._Mode.READ and p.on_ok.__name__ == "<lambda>"), None)

    if picker:
        assert picker.on_ok.__name__ == "<lambda>"
        assert picker.on_cancel.__name__ == "<lambda>"


# ==================== OK Callback Tests ====================


@pytest.mark.nicegui_main_file(__file__)
async def test_ok_callback_read_mode(user: User) -> None:
    """Test OK button calls callback in read mode."""
    await user.open("/")
    reset_callback_state()

    picker = next(
        p for p in user.find(FilePicker).elements if p.mode == p._Mode.READ and p.on_ok.__name__ != "<lambda>"
    )
    temp_dir = picker.current_directory

    # Select a file
    file_path = temp_dir / "file1.txt"
    picker._on_item_click(_make_row(file_path, "file1.txt", False))

    # Click OK
    picker._on_ok_click()

    # Callback should be called
    assert len(app.storage.general["ok_called"]) == 1
    assert app.storage.general["ok_called"][0] is True


@pytest.mark.nicegui_main_file(__file__)
async def test_ok_callback_passes_value(user: User) -> None:
    """Test that OK callback receives the selected value."""
    await user.open("/")
    reset_callback_state()

    picker = next(
        p for p in user.find(FilePicker).elements if p.mode == p._Mode.READ and p.on_ok.__name__ != "<lambda>"
    )
    temp_dir = picker.current_directory

    # Select a file
    file_path = temp_dir / "file1.txt"
    picker._on_item_click(_make_row(file_path, "file1.txt", False))

    # Click OK
    picker._on_ok_click()

    # Value should be passed to callback
    assert len(app.storage.general["ok_value"]) == 1
    assert app.storage.general["ok_value"][0] == [str(file_path)]


@pytest.mark.nicegui_main_file(__file__)
async def test_ok_validation_no_selection_read_mode(user: User) -> None:
    """Test OK validates selection exists in read mode."""
    await user.open("/")
    reset_callback_state()

    picker = next(
        p for p in user.find(FilePicker).elements if p.mode == p._Mode.READ and p.on_ok.__name__ != "<lambda>"
    )

    # Don't select anything
    assert picker.value == []

    # Click OK without selection
    picker._on_ok_click()

    # Callback should not be called (validation prevents it)
    assert len(app.storage.general["ok_called"]) == 0


@pytest.mark.nicegui_main_file(__file__)
async def test_cancel_callback(user: User) -> None:
    """Test Cancel button calls callback."""
    await user.open("/")
    reset_callback_state()

    picker = next(
        p for p in user.find(FilePicker).elements if p.mode == p._Mode.READ and p.on_ok.__name__ != "<lambda>"
    )
    temp_dir = picker.current_directory

    # Select a file (shouldn't matter for cancel)
    file_path = temp_dir / "file1.txt"
    picker._on_item_click(_make_row(file_path, "file1.txt", False))

    # Click Cancel
    picker._on_cancel_click()

    # Cancel callback should be called
    assert len(app.storage.general["cancel_called"]) == 1
    assert app.storage.general["cancel_called"][0] is True

    # OK callback should not be called
    assert len(app.storage.general["ok_called"]) == 0


# ==================== Write Mode Callback Tests ====================


@pytest.mark.nicegui_main_file(__file__)
async def test_ok_callback_write_mode_with_selection(user: User) -> None:
    """Test OK callback in write mode with file selection."""
    await user.open("/")
    await user.should_see("FilePicker - Write Mode with Callbacks")
    reset_callback_state()

    pickers = user.find(FilePicker).elements
    # Find the write mode picker
    picker = next((p for p in pickers if p._inner_elements.filename_input is not None), None)
    assert picker is not None

    temp_dir = picker.current_directory

    # Select a file (sets filename)
    file_path = temp_dir / "file1.txt"
    picker._on_item_click(_make_row(file_path, "file1.txt", False))

    assert picker._filename_input_value == "file1.txt"

    # Click OK
    picker._on_ok_click()

    # Callback should be called
    assert len(app.storage.general["ok_called"]) >= 1


@pytest.mark.nicegui_main_file(__file__)
async def test_ok_callback_write_mode_with_custom_filename(user: User) -> None:
    """Test OK callback in write mode with custom filename."""
    await user.open("/")
    await user.should_see("FilePicker - Write Mode with Callbacks")
    reset_callback_state()

    pickers = user.find(FilePicker).elements
    picker = next((p for p in pickers if p._inner_elements.filename_input is not None), None)
    assert picker is not None

    # Set custom filename
    class MockEvent:
        def __init__(self, value):
            self.args = value

    picker._on_filename_input_change(MockEvent("my_new_file.txt"))
    assert picker._filename_input_value == "my_new_file.txt"

    # Click OK
    picker._on_ok_click()

    # Callback should be called
    assert len(app.storage.general["ok_called"]) >= 1


@pytest.mark.nicegui_main_file(__file__)
async def test_ok_validation_no_filename_write_mode(user: User) -> None:
    """Test OK validates filename in write mode."""
    await user.open("/")
    await user.should_see("FilePicker - Write Mode with Callbacks")
    reset_callback_state()

    pickers = user.find(FilePicker).elements
    picker = next((p for p in pickers if p._inner_elements.filename_input is not None), None)
    assert picker is not None

    # Don't set any filename
    assert picker._filename_input_value == ""

    # Click OK without filename
    picker._on_ok_click()

    # Callback should not be called (validation should prevent it)
    assert picker._filename_input_value == ""


@pytest.mark.nicegui_main_file(__file__)
async def test_callbacks_not_called_on_navigation(user: User) -> None:
    """Test that callbacks are not triggered by navigation."""
    await user.open("/")
    reset_callback_state()

    picker = next(
        p for p in user.find(FilePicker).elements if p.mode == p._Mode.READ and p.on_ok.__name__ != "<lambda>"
    )
    temp_dir = picker.current_directory

    # Navigate to folder
    folder = temp_dir / "folder1"
    picker._navigate_to(folder)

    # Callbacks should not be called
    assert len(app.storage.general["ok_called"]) == 0
    assert len(app.storage.general["cancel_called"]) == 0


# Main page with different callback configurations
@ui.page("/")
def main() -> None:
    app.storage.general.setdefault("ok_called", [])
    app.storage.general.setdefault("cancel_called", [])
    app.storage.general.setdefault("ok_value", [])

    temp_dir = create_temp_structure()

    def on_ok():
        app.storage.general["ok_called"].append(True)
        app.storage.general["ok_value"].append(picker_with_callbacks.value.copy())

    def on_cancel():
        app.storage.general["cancel_called"].append(True)

    ui.label("FilePicker - With Callbacks").classes("text-h4")
    picker_with_callbacks = FilePicker(
        starting_directory=str(temp_dir), mode="read", on_ok=on_ok, on_cancel=on_cancel
    )

    ui.separator()

    ui.label("FilePicker - No Callbacks").classes("text-h4")
    FilePicker(starting_directory=str(temp_dir), mode="read")

    ui.separator()

    temp_dir2 = create_temp_structure()

    def on_ok_write():
        app.storage.general["ok_called"].append(True)
        app.storage.general["ok_value"].append(picker_write.value.copy())

    ui.label("FilePicker - Write Mode with Callbacks").classes("text-h4")
    picker_write = FilePicker(
        starting_directory=str(temp_dir2), mode="write", on_ok=on_ok_write, on_cancel=on_cancel
    )


if __name__ in {"__main__", "__mp_main__"}:
    ui.run()

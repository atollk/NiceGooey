"""
FilePicker Tests - Table Events

Tests for on_row_click, on_row_double_click.
"""

import tempfile
from dataclasses import asdict
from pathlib import Path
from types import SimpleNamespace

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
    temp_dir = Path(tempfile.mkdtemp())
    (temp_dir / "file1.txt").write_text("content1")
    (temp_dir / "folder1").mkdir()
    return temp_dir


def _get_listener(table, event_type: str):
    """Return the first EventListener for the given camelCase event type."""
    return next(listener for listener in table._event_listeners.values() if listener.type == event_type)


def _fire(table, event_type: str, args):
    """Invoke the registered handler for event_type with the given args."""
    listener = _get_listener(table, event_type)
    mock_event = SimpleNamespace(args=args, sender=table, client=None)
    listener.handler(mock_event)


# ==================== Event Registration Tests ====================


@pytest.mark.nicegui_main_file(__file__)
async def test_row_click_registered(user: User) -> None:
    """Test that the row-click event listener is registered on the table."""
    await user.open("/")
    picker = user.find(FilePicker).elements.pop()
    table = picker._inner_elements.file_table

    types = {listener.type for listener in table._event_listeners.values()}
    assert "rowClick" in types


@pytest.mark.nicegui_main_file(__file__)
async def test_row_dblclick_registered(user: User) -> None:
    """Test that the row-dblclick event listener is registered on the table."""
    await user.open("/")
    picker = user.find(FilePicker).elements.pop()
    table = picker._inner_elements.file_table

    types = {listener.type for listener in table._event_listeners.values()}
    assert "rowDblclick" in types


# ==================== on_row_click Arg Parsing Tests ====================


@pytest.mark.nicegui_main_file(__file__)
async def test_on_row_click_quasar_format_uses_args1(user: User) -> None:
    """When args has 3 elements (Quasar format), row data is taken from args[1]."""
    await user.open("/")
    picker = user.find(FilePicker).elements.pop()
    temp_dir = picker.current_directory

    file_path = temp_dir / "file1.txt"
    row = _make_row(file_path, "file1.txt", False)
    row_dict = asdict(row)

    received = []
    original = picker._on_item_click
    picker._on_item_click = lambda r: received.append(r)

    try:
        _fire(picker._inner_elements.file_table, "rowClick", [True, row_dict, 0])
    finally:
        picker._on_item_click = original

    assert len(received) == 1
    assert received[0] == row


@pytest.mark.nicegui_main_file(__file__)
async def test_on_row_click_single_arg_format_uses_args0(user: User) -> None:
    """When args has 1 element, row data is taken from args[0]."""
    await user.open("/")
    picker = user.find(FilePicker).elements.pop()
    temp_dir = picker.current_directory

    file_path = temp_dir / "file1.txt"
    row = _make_row(file_path, "file1.txt", False)
    row_dict = asdict(row)

    received = []
    picker._on_item_click = lambda r: received.append(r)

    _fire(picker._inner_elements.file_table, "rowClick", [row_dict])

    assert len(received) == 1
    assert received[0] == row


@pytest.mark.nicegui_main_file(__file__)
async def test_on_row_click_navigates_on_directory(user: User) -> None:
    """Firing row-click on a directory row navigates into that directory."""
    await user.open("/")
    picker = user.find(FilePicker).elements.pop()
    temp_dir = picker.current_directory

    folder = temp_dir / "folder1"
    row = _make_row(folder, "folder1", True)

    _fire(picker._inner_elements.file_table, "rowClick", [True, asdict(row), 0])

    assert picker.current_directory == folder


@pytest.mark.nicegui_main_file(__file__)
async def test_on_row_click_selects_file(user: User) -> None:
    """Firing row-click on a file row selects it (updates picker.value)."""
    await user.open("/")
    picker = user.find(FilePicker).elements.pop()
    temp_dir = picker.current_directory

    file_path = temp_dir / "file1.txt"
    row = _make_row(file_path, "file1.txt", False)

    _fire(picker._inner_elements.file_table, "rowClick", [True, asdict(row), 0])

    assert str(file_path) in picker.value


# ==================== on_row_double_click Tests ====================


@pytest.mark.nicegui_main_file(__file__)
async def test_on_row_dblclick_navigates_on_directory(user: User) -> None:
    """Firing row-dblclick on a directory row navigates into it."""
    await user.open("/")
    picker = user.find(FilePicker).elements.pop()
    temp_dir = picker.current_directory

    folder = temp_dir / "folder1"
    row = _make_row(folder, "folder1", True)

    _fire(picker._inner_elements.file_table, "rowDblclick", [True, asdict(row), 0])

    assert picker.current_directory == folder


@pytest.mark.nicegui_main_file(__file__)
async def test_on_row_dblclick_no_nav_on_file(user: User) -> None:
    """Firing row-dblclick on a file row does not change directory."""
    await user.open("/")
    picker = user.find(FilePicker).elements.pop()
    temp_dir = picker.current_directory

    file_path = temp_dir / "file1.txt"
    row = _make_row(file_path, "file1.txt", False)

    _fire(picker._inner_elements.file_table, "rowDblclick", [True, asdict(row), 0])

    assert picker.current_directory == temp_dir


# ==================== on_table_selection_change Tests ====================


def _fire_selection(picker, args):
    """Call _on_table_selection_change directly with the given args."""
    mock_event = SimpleNamespace(args=args)
    picker._on_table_selection_change(mock_event)


@pytest.mark.nicegui_main_file(__file__)
async def test_selection_event_registered(user: User) -> None:
    """Test that the selection event listener is registered on the table."""
    await user.open("/")
    picker = user.find(FilePicker).elements.pop()
    table = picker._inner_elements.file_table

    handlers = {
        listener.handler for listener in table._event_listeners.values() if listener.type == "selection"
    }
    assert picker._on_table_selection_change in handlers


@pytest.mark.nicegui_main_file(__file__)
async def test_on_table_selection_change_file_row_updates_value(user: User) -> None:
    """A list of row dicts passed to _on_table_selection_change updates picker.value."""
    await user.open("/")
    picker = user.find(FilePicker).elements.pop()
    temp_dir = picker.current_directory

    file_path = temp_dir / "file1.txt"
    row = _make_row(file_path, "file1.txt", False)

    _fire_selection(picker, [asdict(row)])

    assert picker.value == [str(file_path)]


@pytest.mark.nicegui_main_file(__file__)
async def test_on_table_selection_change_non_list_args_clears_value(user: User) -> None:
    """Non-list args passed to _on_table_selection_change results in empty value."""
    await user.open("/")
    picker = user.find(FilePicker).elements.pop()
    picker.value = ["something"]

    _fire_selection(picker, None)

    assert picker.value == []


# Main page
@ui.page("/")
def main() -> None:
    temp_dir = create_temp_structure()
    FilePicker(starting_directory=str(temp_dir), mode="read")


if __name__ in {"__main__", "__mp_main__"}:
    ui.run()

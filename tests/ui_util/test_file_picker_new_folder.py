"""
FilePicker Tests - New Folder Dialog

Tests for _create_new_folder_dialog in write mode.
"""

import tempfile
from pathlib import Path

import pytest
from nicegui import ui
from nicegui.testing import User

from nicegooey.ui_util.file_picker import FilePicker


def create_temp_structure() -> Path:
    temp_dir = Path(tempfile.mkdtemp())
    (temp_dir / "existing_folder").mkdir()
    (temp_dir / "file1.txt").write_text("content1")
    return temp_dir


def _open_dialog(user: User, picker: FilePicker) -> None:
    """Call _create_new_folder_dialog() within the NiceGUI slot context."""
    with user:
        picker._create_new_folder_dialog()


def _get_folder_input(user: User) -> ui.input:
    return next(el for el in user.find(ui.input).elements if el.label == "Folder name")


# ==================== Dialog Open/Close Tests ====================


@pytest.mark.nicegui_main_file(__file__)
async def test_new_folder_dialog_opens(user: User) -> None:
    """Calling _create_new_folder_dialog() shows the dialog label."""
    await user.open("/")
    picker = user.find(FilePicker).elements.pop()

    _open_dialog(user, picker)

    await user.should_see("Create New Folder")


@pytest.mark.nicegui_main_file(__file__)
async def test_new_folder_dialog_cancel_does_not_create(user: User) -> None:
    """Clicking Cancel does not create any folder."""
    await user.open("/")
    picker = user.find(FilePicker).elements.pop()
    temp_dir = picker.current_directory

    dir_count_before = sum(1 for p in temp_dir.iterdir() if p.is_dir())

    _open_dialog(user, picker)
    user.find(content="Cancel", kind=ui.button).click()

    dir_count_after = sum(1 for p in temp_dir.iterdir() if p.is_dir())
    assert dir_count_after == dir_count_before


# ==================== Folder Creation Tests ====================


@pytest.mark.nicegui_main_file(__file__)
async def test_new_folder_dialog_creates_folder_on_disk(user: User) -> None:
    """Entering a valid name and clicking Create creates the folder on disk."""
    await user.open("/")
    picker = user.find(FilePicker).elements.pop()
    temp_dir = picker.current_directory

    _open_dialog(user, picker)
    _get_folder_input(user).set_value("brand_new_dir")
    user.find(content="Create", kind=ui.button).click()

    assert (temp_dir / "brand_new_dir").is_dir()


@pytest.mark.nicegui_main_file(__file__)
async def test_new_folder_dialog_refreshes_listing(user: User) -> None:
    """After creation the new folder appears in _list_directory()."""
    await user.open("/")
    picker = user.find(FilePicker).elements.pop()

    _open_dialog(user, picker)
    _get_folder_input(user).set_value("refreshed_dir")
    user.find(content="Create", kind=ui.button).click()

    names = [item.name for item in picker._list_directory()]
    assert "refreshed_dir" in names


# ==================== Validation Tests ====================


@pytest.mark.nicegui_main_file(__file__)
async def test_new_folder_dialog_empty_name_no_create(user: User) -> None:
    """Clicking Create with an empty folder name does not create anything."""
    await user.open("/")
    picker = user.find(FilePicker).elements.pop()
    temp_dir = picker.current_directory

    dir_count_before = sum(1 for p in temp_dir.iterdir() if p.is_dir())

    _open_dialog(user, picker)
    # Do not type anything — input is empty by default
    user.find(content="Create", kind=ui.button).click()

    dir_count_after = sum(1 for p in temp_dir.iterdir() if p.is_dir())
    assert dir_count_after == dir_count_before


@pytest.mark.nicegui_main_file(__file__)
async def test_new_folder_dialog_duplicate_name_no_create(user: User) -> None:
    """Trying to create a folder that already exists does not change the count."""
    await user.open("/")
    picker = user.find(FilePicker).elements.pop()
    temp_dir = picker.current_directory

    # "existing_folder" was created in create_temp_structure()
    dir_count_before = sum(1 for p in temp_dir.iterdir() if p.is_dir())

    _open_dialog(user, picker)
    _get_folder_input(user).set_value("existing_folder")
    user.find(content="Create", kind=ui.button).click()

    dir_count_after = sum(1 for p in temp_dir.iterdir() if p.is_dir())
    assert dir_count_after == dir_count_before


@pytest.mark.nicegui_main_file(__file__)
async def test_new_folder_dialog_whitespace_name_no_create(user: User) -> None:
    """A name consisting only of whitespace is treated as empty — no folder created."""
    await user.open("/")
    picker = user.find(FilePicker).elements.pop()
    temp_dir = picker.current_directory

    dir_count_before = sum(1 for p in temp_dir.iterdir() if p.is_dir())

    _open_dialog(user, picker)
    _get_folder_input(user).set_value("   ")
    user.find(content="Create", kind=ui.button).click()

    dir_count_after = sum(1 for p in temp_dir.iterdir() if p.is_dir())
    assert dir_count_after == dir_count_before


# Main page — write mode so the "New folder" button is shown in the path bar
@ui.page("/")
def main() -> None:
    temp_dir = create_temp_structure()
    FilePicker(starting_directory=str(temp_dir), mode="write")


if __name__ in {"__main__", "__mp_main__"}:
    ui.run()

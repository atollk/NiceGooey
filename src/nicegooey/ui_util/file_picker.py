"""
FilePicker: A cross-platform file picker widget for NiceGUI.

This module provides a FilePicker class that creates a file selection interface
similar to native file pickers, with support for both read and write modes.
"""

import enum
import os
import platform
import string
from collections.abc import Callable
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import stat
from typing import Literal

from nicegui import ui, events
from nicegui.elements.mixins.validation_element import ValidationElement


class FilePicker(ValidationElement):
    """
    A file picker widget for NiceGUI applications.

    This widget provides a native file picker-like interface with support for:
    - Read and write modes
    - Single and multiple file selection
    - Directory selection
    - Hidden file visibility
    - File type filtering
    - Cross-platform support (Windows drives, Unix paths)

    Args:
        starting_directory: Initial directory to display (default: current directory)
        mode: Either "read" or "write" (default: "read")
        allow_directory_selection: Allow selecting directories in read mode (default: False)
        allow_multiple: Allow multiple file selection in read mode (default: False)
        show_hidden: Show hidden files and folders (default: False)
        show_buttons: Show OK and Cancel buttons (default: True)
        file_filter: A list of file extensions to show, e.g., ['.txt', '.pdf']. If None, all files are shown.
        on_ok: Callback function called when OK is clicked (default: None)
        on_cancel: Callback function called when Cancel is clicked (default: None)
    """

    class _Mode(enum.Enum):
        READ = "read"
        WRITE = "write"

        @classmethod
        def from_value(cls, value: str) -> "FilePicker._Mode":
            if value == "read":
                return cls.READ
            elif value == "write":
                return cls.WRITE
            else:
                raise ValueError("mode must be 'read' or 'write'")

    @dataclass
    class _InnerElements:
        container: ui.element
        path_bar: ui.element
        drives_panel: ui.element | None
        file_table: ui.table
        filename_input: ui.input | None
        selected_label: ui.label | None

    mode: _Mode
    allow_directory_selection: bool
    allow_multiple: bool
    show_hidden: bool
    show_buttons: bool
    file_filter: list[str] | None
    on_ok: Callable[[], None]
    on_cancel: Callable[[], None]

    current_directory: Path
    _filename_input_value: str
    _inner_elements: _InnerElements
    value: list[str]  # pyrefly: ignore[bad-override]

    def __init__(
        self,
        starting_directory: str = ".",
        mode: Literal["read", "write"] = "read",
        allow_directory_selection: bool = False,
        allow_multiple: bool = False,
        show_hidden: bool = False,
        show_buttons: bool = True,
        file_filter: list[str] | None = None,
        on_ok: Callable[[], None] = lambda: None,
        on_cancel: Callable[[], None] = lambda: None,
    ):
        super().__init__(value=[], validation={})

        # Store configuration
        self.mode = self._Mode.from_value(mode)
        self.allow_directory_selection = allow_directory_selection
        self.allow_multiple = allow_multiple and mode == "read"
        self.show_hidden = show_hidden
        self.show_buttons = show_buttons
        self.file_filter = (
            [f.lower() if f.startswith(".") else "." + f.lower() for f in file_filter]
            if file_filter
            else None
        )
        self.on_ok = on_ok
        self.on_cancel = on_cancel

        # Initialize state
        self.current_directory = Path(starting_directory).resolve()
        self._filename_input_value = ""

        # Render the UI
        self._inner_elements = self._render()

    # ---------- Public Functions ----------

    def navigate_to(self, path: str) -> None:
        """Programmatically change the current directory."""
        new_path = Path(path).resolve()
        if new_path.is_dir():
            self._navigate_to(new_path)
        else:
            ui.notify(f"Not a directory: {path}", type="warning")

    def reload_from_disk(self):
        """Refresh the current directory listing from the files on disk."""
        self._refresh_ui()

    # ---------- Non-Modifying Internal Utility Functions ----------

    @staticmethod
    def _is_windows() -> bool:
        return platform.system() == "Windows"

    def _get_windows_drives(self) -> list[str]:
        if not self._is_windows():
            return []

        return [drive for letter in string.ascii_uppercase if os.path.exists(drive := f"{letter}:\\")]

    def _path_is_hidden(self, path: Path) -> bool:
        if path.name.startswith("."):
            return True

        if self._is_windows():
            try:
                attrs = os.stat(path).st_file_attributes  # pyrefly: ignore[missing-attribute]
                return bool(attrs & stat.FILE_ATTRIBUTE_HIDDEN)
            except (AttributeError, OSError):
                return False

        return False

    def _path_matches_filter(self, path: Path) -> bool:
        if path.is_dir():
            return True

        if self.file_filter is None:
            return True

        return path.suffix.lower() in self.file_filter

    def _get_formatted_file_size(self, path: Path) -> str:
        """Get human-readable file size."""
        if path.is_dir():
            return ""

        try:
            size = path.stat().st_size
        except OSError:
            return ""

        for unit in ["B", "KiB", "MiB", "GiB", "TiB"]:
            if size >= 1024.0:
                size /= 1024.0
            else:
                break
        else:
            unit = "PiB"
        return f"{size:.1f} {unit}"

    def _get_formatted_modtime(self, path: Path) -> str:
        """Get human-readable modification time."""
        try:
            mtime = path.stat().st_mtime
        except OSError:
            return ""
        return datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")

    @dataclass(frozen=True)
    class _DirectoryItemTableRow:
        id: str
        name: str
        is_dir: bool
        size: str
        modified: str
        icon: Literal["folder", "description"]

        @property
        def path(self) -> Path:
            return Path(self.id)

    def _list_directory(self) -> list[_DirectoryItemTableRow]:
        """List contents of current directory, to be then used as rows for the table widget."""
        items = []

        try:
            for path in self.current_directory.iterdir():
                if not self.show_hidden and self._path_is_hidden(path):
                    continue

                if not self._path_matches_filter(path):
                    continue

                row = self._DirectoryItemTableRow(
                    id=str(path),
                    name=path.name,
                    is_dir=path.is_dir(),
                    size=self._get_formatted_file_size(path),
                    modified=self._get_formatted_modtime(path),
                    icon="folder" if path.is_dir() else "description",
                )
                items.append(row)
        except PermissionError:
            self._display_error(f"Permission denied: {self.current_directory}")
        except OSError as e:
            self._display_error(f"Error reading directory: {e}")

        # Sort: directories first, then files, alphabetically
        items.sort(key=lambda x: (not x.is_dir, x.name.lower()))
        return items

    def _navigate_to(self, path: Path) -> None:
        if not path.is_dir():
            return

        try:
            # Test if we can access the directory
            list(path.iterdir())
            self.current_directory = path.resolve()
            self._refresh_ui()
        except PermissionError:
            self._display_error(f"Permission denied: {path}")
        except OSError as e:
            self._display_error(f"Cannot access directory: {e}")

    # ---------- Internal Functions for UI Callbacks ----------

    def _on_item_click(self, row: _DirectoryItemTableRow) -> None:
        if row["is_dir"]:
            self._navigate_to(row.path)
            return

        if self.allow_multiple:
            # Toggle the checkbox selection
            current_selected = self._get_selected_rows()
            if row in current_selected:
                # Remove from selection
                self._set_selected_rows([r for r in current_selected if r != row])
            else:
                # Add to selection
                self._set_selected_rows(current_selected + [row])
        else:
            if self.mode == self._Mode.WRITE:
                self._filename_input_value = row.name
                if self._inner_elements.filename_input:
                    self._inner_elements.filename_input.set_value(self._filename_input_value)

            # row_to_select = next(
            #     (row for row in self._inner_elements.file_table.rows if row["id"] == str(row["path"])),
            #     None,
            # )
            # TODO: what happens if we are in write mode and type in a non-existent file?
            row_to_select = row
            if row_to_select:
                self._set_selected_rows([row_to_select])

        # Sync value property
        self.value = [row.id for row in self._get_selected_rows()]
        self._update_selection_display()

    def _on_item_double_click(self, item: _DirectoryItemTableRow) -> None:
        if item["is_dir"]:
            self._navigate_to(Path(item["id"]))

    # TODO specify type
    def _on_table_selection_change(self, e: events.GenericEventArguments) -> None:
        """Handle table selection changes (from checkbox clicks)."""
        # e.args contains the selection event data
        # Extract selected rows from the event
        selected_rows = e.args if isinstance(e.args, list) else []

        # Update FilePicker value property
        self.value = [row["id"] for row in selected_rows if isinstance(row, dict)]

        # Update the custom selection display
        self._update_selection_display()

    def _on_ok_click(self):
        # Get the final selection
        if self.mode == self._Mode.WRITE:
            # In write mode, use the filename input
            filename = self._filename_input_value.strip()
            if not filename:
                ui.notify("Please enter a filename", type="warning")
                return

            self.value = [str(self.current_directory / filename)]

        # Validate selection
        if self.mode == self._Mode.READ:
            if not self.value:
                err = "Please select at least one file" if self.allow_multiple else "Please select a file"
                self._display_error(err)
                return

        # Call the callback
        if self.on_ok:
            self.on_ok()

    def _on_cancel_click(self):
        if self.on_cancel:
            self.on_cancel()

    def _on_filename_input_change(self, e):
        """Handle filename input changes in write mode."""
        # Update the internal filename value
        self._filename_input_value = e.args

        # Clear any file selection when user manually types
        self.value = []

        # Clear table selection
        if self._inner_elements.file_table:
            self._set_selected_rows([])

    # ---------- Internal Functions for UI Logic ----------

    def _get_selected_rows(self) -> list[_DirectoryItemTableRow]:
        return [self._DirectoryItemTableRow(**row) for row in self._inner_elements.file_table.selected]

    def _set_selected_rows(self, rows: list[_DirectoryItemTableRow]) -> None:
        self._inner_elements.file_table.selected = [asdict(row) for row in rows]
        self._inner_elements.file_table.update()  # TODO: ?

    def _display_error(self, message: str) -> None:
        ui.notify(message, type="negative")

    def _update_selection_display(self):
        """Update the selection display in the bottom bar."""
        if self._inner_elements.selected_label is None:
            return

        if self.allow_multiple:
            match len(self.value):
                case 0:
                    text = "No files selected"
                case 1:
                    text = f"1 file selected: {Path(self.value[0]).name}"
                case n:
                    text = f"{n} files selected"
        elif self.value:
            text = f"Selected: {Path(self.value[0]).name}"
        else:
            text = "No file selected"

        self._inner_elements.selected_label.set_text(text)

    def _create_breadcrumbs(self):
        """Create breadcrumb navigation for current path."""
        parts = self.current_directory.parts

        with ui.row().classes("items-center gap-1"):
            # Home/root button
            if self._is_windows():
                # On Windows, show drive letter
                path = Path(parts[0])
                ui.button(parts[0], on_click=lambda _, p=path: self._navigate_to(p)).props("flat dense")
            else:
                ui.button("/", on_click=lambda: self._navigate_to(Path("/"))).props("flat dense")

            # Breadcrumb parts
            for i, part in enumerate(parts[1:], 1):
                ui.label("/").classes("text-gray-500")
                path = Path(*parts[: i + 1])
                ui.button(part, on_click=lambda _, p=path: self._navigate_to(p)).props("flat dense")

    def _create_new_folder_dialog(self):
        """Show dialog to create a new folder."""
        with ui.dialog() as dialog, ui.card():
            ui.label("Create New Folder").classes("text-lg font-bold")

            folder_input = ui.input("Folder name").classes("w-64")

            with ui.row().classes("w-full justify-end gap-2"):
                ui.button("Cancel", on_click=dialog.close).props("flat")

                def create_folder():
                    name = folder_input.value.strip()
                    if not name:
                        self._display_error("Please enter a folder name")
                        return

                    new_folder = self.current_directory / name
                    if new_folder.exists():
                        self._display_error("Folder already exists")
                        return

                    try:
                        new_folder.mkdir()
                        dialog.close()
                        self._refresh_ui()
                    except OSError as e:
                        self._display_error(f"Error creating folder: {e}")

                ui.button("Create", on_click=create_folder).props("color=primary")

        dialog.open()

    def _refresh_ui(self):
        """Refresh all UI components."""
        if (path_bar := self._inner_elements.path_bar) is not None:
            path_bar.clear()
            with path_bar:
                self._create_breadcrumbs()

                ui.space()

                # Refresh button
                ui.button(icon="refresh", on_click=lambda: self._refresh_ui()).props("flat dense").tooltip(
                    "Refresh"
                )

                # Parent directory button
                if self.current_directory.parent != self.current_directory:
                    ui.button(
                        icon="arrow_upward", on_click=lambda: self._navigate_to(self.current_directory.parent)
                    ).props("flat dense").tooltip("Parent directory")

                # New folder button (write mode only)
                if self.mode == self._Mode.WRITE:
                    ui.button(icon="create_new_folder", on_click=self._create_new_folder_dialog).props(
                        "flat dense"
                    ).tooltip("New folder")

        self._update_file_table()
        self._update_drives_panel()

    def _update_drives_panel(self):
        """Update the drives panel (Windows only)."""
        drives_panel = self._inner_elements.drives_panel
        if drives_panel is None:
            return

        drives_panel.clear()
        with drives_panel:
            ui.label("Drives").classes("font-bold text-sm mb-2")
            for drive in self._get_windows_drives():
                ui.button(drive, on_click=lambda _, d=drive: self._navigate_to(Path(d))).props(
                    "flat dense"
                ).classes("w-full justify-start")

    def _update_file_table(self):
        """Update the file table with current directory contents."""
        if self._inner_elements.file_table is None:
            return
        self._set_selected_rows(self._list_directory())

        # Restore selection after updating rows
        if self.value:
            self._set_selected_rows([row for row in self._get_selected_rows() if row.id in self.value])

    def _render(self) -> _InnerElements:
        """Render the file picker UI."""
        with ui.column().classes("w-full h-full gap-2") as container:
            # Path bar
            with ui.row().classes("w-full items-center gap-2") as path_bar:
                self._create_breadcrumbs()

                ui.space()

                # Refresh button
                ui.button(icon="refresh", on_click=lambda: self._refresh_ui()).props("flat dense").tooltip(
                    "Refresh"
                )

                # Parent directory button
                if self.current_directory.parent != self.current_directory:
                    ui.button(
                        icon="arrow_upward", on_click=lambda: self._navigate_to(self.current_directory.parent)
                    ).props("flat dense").tooltip("Parent directory")

                # New folder button (write mode only)
                if self.mode == self._Mode.WRITE:
                    ui.button(icon="create_new_folder", on_click=self._create_new_folder_dialog).props(
                        "flat dense"
                    ).tooltip("New folder")

            # Main content area
            with ui.row().classes("w-full flex-grow gap-2"):
                # Left panel: Drives (Windows only)
                if self._is_windows():
                    with ui.column().classes("w-32 gap-1") as drives_panel:
                        ui.label("Drives").classes("font-bold text-sm mb-2")
                        for drive in self._get_windows_drives():
                            ui.button(drive, on_click=lambda _, d=drive: self._navigate_to(Path(d))).props(
                                "flat dense"
                            ).classes("w-full justify-start")
                else:
                    drives_panel = None

                # Right panel: File table
                with ui.column().classes("flex-grow"):
                    columns = [
                        {"name": "name", "label": "Name", "field": "name", "align": "left", "sortable": True},
                        {
                            "name": "size",
                            "label": "Size",
                            "field": "size",
                            "align": "right",
                            "sortable": True,
                        },
                        {
                            "name": "modified",
                            "label": "Modified",
                            "field": "modified",
                            "align": "left",
                            "sortable": True,
                        },
                    ]

                    file_table = (
                        ui.table(
                            columns=columns,
                            rows=[asdict(row) for row in self._list_directory()],
                            row_key="id",
                            selection="multiple" if self.allow_multiple else "single",
                        )
                        .classes("w-full")
                        .props("hide-selected-banner")
                    )

                    # Add selection change listener
                    file_table.on("selection", self._on_table_selection_change)

                    # Add click handlers
                    def on_row_click(e):
                        # e.args is a list; the row data is typically in args[1] for Quasar events
                        if len(e.args) > 1:
                            row_data = e.args[1]
                        else:
                            row_data = e.args[0] if e.args else {}

                        item_dict = {
                            "path": Path(row_data["id"]),
                            "is_dir": row_data["is_dir"],
                            "name": row_data["name"],
                        }
                        self._on_item_click(item_dict)

                    def on_row_double_click(e):
                        # e.args is a list; the row data is typically in args[1] for Quasar events
                        if len(e.args) > 1:
                            row_data = e.args[1]
                        else:
                            row_data = e.args[0] if e.args else {}

                        self._on_item_double_click(row_data)

                    file_table.on("row-click", on_row_click)
                    file_table.on("row-dblclick", on_row_double_click)

                    # Add icon column rendering
                    file_table.add_slot(
                        "body-cell-name",
                        """
                        <q-td :props="props">
                            <q-icon :name="props.row.icon" size="sm" class="q-mr-sm" />
                            {{ props.row.name }}
                        </q-td>
                    """,
                    )

            # Bottom bar
            with ui.row().classes("w-full items-center gap-2"):
                if self.mode == self._Mode.WRITE:
                    # Filename input in write mode
                    ui.label("File name:").classes("text-sm")
                    filename_input = ui.input().classes("flex-grow")
                    filename_input.on("update:model-value", self._on_filename_input_change)
                    selected_label = None
                else:
                    # Selection display in read mode
                    filename_input = None
                    selected_label = ui.label("No file selected").classes("text-sm flex-grow")
                    selected_label = selected_label

                ui.space()

                # OK and Cancel buttons
                if self.show_buttons:
                    ui.button("Cancel", on_click=self._on_cancel_click).props("flat")
                    ui.button("OK", on_click=self._on_ok_click).props("color=primary")

        return self._InnerElements(
            container=container,
            path_bar=path_bar,
            drives_panel=drives_panel,
            file_table=file_table,
            filename_input=filename_input,
            selected_label=selected_label,
        )

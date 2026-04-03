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
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import stat

from nicegui import ui
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
        file_filter: List of file extensions to show, e.g., ['.txt', '.pdf'] (default: None, shows all)
        on_ok: Callback function called when OK is clicked (default: None)
        on_cancel: Callback function called when Cancel is clicked (default: None)
    """

    class _Mode(enum.Enum):
        READ = "read"
        WRITE = "write"

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
    value: list[Path]

    def __init__(
        self,
        starting_directory: str = ".",
        mode: str = "read",
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
        if mode == "read":
            self.mode = self._Mode.READ
        elif mode == "write":
            self.mode = self._Mode.WRITE
        else:
            raise ValueError("mode must be 'read' or 'write'")
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

    @staticmethod
    def _is_windows() -> bool:
        """Check if running on Windows."""
        return platform.system() == "Windows"

    def _get_drives(self) -> list[str]:
        """Get list of available drives on Windows."""
        if not self._is_windows():
            return []

        drives = []
        for letter in string.ascii_uppercase:
            drive = f"{letter}:\\"
            if os.path.exists(drive):
                drives.append(drive)
        return drives

    def _is_hidden(self, path: Path) -> bool:
        """Check if a file or directory is hidden."""
        if path.name.startswith("."):
            return True

        if self._is_windows():
            try:
                attrs = os.stat(path).st_file_attributes  # pyrefly: ignore[missing-attribute]
                return bool(attrs & stat.FILE_ATTRIBUTE_HIDDEN)
            except (AttributeError, OSError):
                return False

        return False

    def _matches_filter(self, path: Path) -> bool:
        """Check if a file matches the current filter."""
        if path.is_dir():
            return True

        if self.file_filter is None:
            return True

        return path.suffix.lower() in self.file_filter

    def _get_file_size(self, path: Path) -> str:
        """Get human-readable file size."""
        if path.is_dir():
            return ""

        try:
            size = path.stat().st_size
            for unit in ["B", "KB", "MB", "GB", "TB"]:
                if size < 1024.0:
                    return f"{size:.1f} {unit}"
                size /= 1024.0
            return f"{size:.1f} PB"
        except OSError:
            return ""

    def _get_modified_time(self, path: Path) -> str:
        """Get human-readable modification time."""
        try:
            mtime = path.stat().st_mtime
            dt = datetime.fromtimestamp(mtime)
            return dt.strftime("%Y-%m-%d %H:%M")
        except OSError:
            return ""

    def _list_directory(self) -> list[dict]:
        """List contents of current directory."""
        items = []

        try:
            for item in self.current_directory.iterdir():
                # Skip hidden files if not showing them
                if not self.show_hidden and self._is_hidden(item):
                    continue

                # Skip files that don't match filter
                if not self._matches_filter(item):
                    continue

                items.append(
                    {
                        "path": item,
                        "name": item.name,
                        "is_dir": item.is_dir(),
                        "size": self._get_file_size(item),
                        "modified": self._get_modified_time(item),
                        "icon": "folder" if item.is_dir() else "description",
                    }
                )
        except PermissionError:
            ui.notify(f"Permission denied: {self.current_directory}", type="negative")
        except OSError as e:
            ui.notify(f"Error reading directory: {e}", type="negative")

        # Sort: directories first, then files, alphabetically
        items.sort(key=lambda x: (not x["is_dir"], x["name"].lower()))

        return items

    def _navigate_to(self, path: Path):
        """Navigate to a new directory."""
        if not path.is_dir():
            return

        try:
            # Test if we can access the directory
            list(path.iterdir())
            self.current_directory = path.resolve()
            self._refresh_ui()
        except PermissionError:
            ui.notify(f"Permission denied: {path}", type="negative")
        except OSError as e:
            ui.notify(f"Cannot access directory: {e}", type="negative")

    def _on_item_click(self, item: dict):
        """Handle clicking on a file or directory."""
        if item["is_dir"] and not self.allow_directory_selection:
            # Navigate into directory
            self._navigate_to(item["path"])
        else:
            # Select the item
            if self.allow_multiple:
                # Toggle selection in multiple mode
                if item["path"] in self.value:
                    self.value.remove(item["path"])
                else:
                    self.value.append(item["path"])
            else:
                # Set selection in single mode
                self.value = item["path"]
                if self.mode == "write":
                    self._filename_input_value = item["name"]
                    if self._filename_input:
                        self._filename_input.set_value(self._filename_input_value)

            self._update_selection_display()

    def _on_item_double_click(self, item: dict):
        """Handle double-clicking on a file or directory."""
        if item["is_dir"]:
            self._navigate_to(item["path"])

    def _update_selection_display(self):
        """Update the selection display in the bottom bar."""
        if self._inner_elements.selected_label is None:
            return

        if self.allow_multiple:
            match len(self.value):
                case 0:
                    text = "No files selected"
                case 1:
                    text = f"1 file selected: {str(self.value[0])}"
                case n:
                    text = f"{n} files selected"
        elif self.value:
            text = f"Selected: {str(self.value[0])}"
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
                ui.button(parts[0], on_click=lambda p=Path(parts[0]): self._navigate_to(p)).props(
                    "flat dense"
                )
            else:
                ui.button("/", on_click=lambda: self._navigate_to(Path("/"))).props("flat dense")

            # Breadcrumb parts
            for i, part in enumerate(parts[1:], 1):
                ui.label("/").classes("text-gray-500")
                path = Path(*parts[: i + 1])
                ui.button(part, on_click=lambda p=path: self._navigate_to(p)).props("flat dense")

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
                        ui.notify("Please enter a folder name", type="warning")
                        return

                    new_folder = self.current_directory / name
                    if new_folder.exists():
                        ui.notify("Folder already exists", type="warning")
                        return

                    try:
                        new_folder.mkdir()
                        ui.notify(f"Created folder: {name}", type="positive")
                        dialog.close()
                        self._refresh_ui()
                    except OSError as e:
                        ui.notify(f"Error creating folder: {e}", type="negative")

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
                if self.mode == "write":
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
            for drive in self._get_drives():
                ui.button(drive, on_click=lambda d=drive: self._navigate_to(Path(d))).props(
                    "flat dense"
                ).classes("w-full justify-start")

    def _update_file_table(self):
        """Update the file table with current directory contents."""
        file_table = self._inner_elements.file_table
        if file_table is None:
            return

        file_table.rows = [
            {
                "id": str(item["path"]),
                "name": item["name"],
                "size": item["size"],
                "modified": item["modified"],
                "icon": item["icon"],
                "is_dir": item["is_dir"],
            }
            for item in self._list_directory()
        ]
        file_table.update()

    def _on_ok_click(self):
        """Handle OK button click."""
        # Get the final selection
        if self.mode == "write":
            # In write mode, use the filename input
            filename = self._filename_input_value.strip()
            if not filename:
                ui.notify("Please enter a filename", type="warning")
                return

            self.value = [self.current_directory / filename]

        # Validate selection
        if self.mode == "read":
            if self.allow_multiple:
                if not self.value:
                    ui.notify("Please select at least one file", type="warning")
                    return
            else:
                if not self.value:
                    ui.notify("Please select a file", type="warning")
                    return

        # Call the callback
        if self.on_ok:
            self.on_ok()

    def _on_cancel_click(self):
        """Handle Cancel button click."""
        if self.on_cancel:
            self.on_cancel()

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
                if self.mode == "write":
                    ui.button(icon="create_new_folder", on_click=self._create_new_folder_dialog).props(
                        "flat dense"
                    ).tooltip("New folder")

            # Main content area
            with ui.row().classes("w-full flex-grow gap-2"):
                # Left panel: Drives (Windows only)
                if self._is_windows():
                    with ui.column().classes("w-32 gap-1") as drives_panel:
                        ui.label("Drives").classes("font-bold text-sm mb-2")
                        for drive in self._get_drives():
                            ui.button(drive, on_click=lambda d=drive: self._navigate_to(Path(d))).props(
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

                    items = self._list_directory()
                    rows = []
                    for item in items:
                        rows.append(
                            {
                                "id": str(item["path"]),
                                "name": item["name"],
                                "size": item["size"],
                                "modified": item["modified"],
                                "icon": item["icon"],
                                "is_dir": item["is_dir"],
                            }
                        )

                    file_table = ui.table(
                        columns=columns,
                        rows=rows,
                        row_key="id",
                        selection="multiple" if self.allow_multiple else "single",
                    ).classes("w-full")

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

                        item_dict = {
                            "path": Path(row_data["id"]),
                            "is_dir": row_data["is_dir"],
                            "name": row_data["name"],
                        }
                        self._on_item_double_click(item_dict)

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
                if self.mode == "write":
                    # Filename input in write mode
                    ui.label("File name:").classes("text-sm")
                    filename_input = ui.input().classes("flex-grow")
                    filename_input.on(
                        "update:model-value", lambda e: setattr(self, "_filename_input_value", e.args)
                    )
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

    def set_directory(self, path: str) -> None:
        """Programmatically change the current directory."""
        new_path = Path(path).resolve()
        if new_path.is_dir():
            self._navigate_to(new_path)
        else:
            ui.notify(f"Not a directory: {path}", type="warning")

    def refresh(self):
        """Refresh the current directory listing."""
        self._refresh_ui()

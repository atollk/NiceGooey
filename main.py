# type: ignore


from nicegui import ui

from file_picker import FilePicker


def main():
    # Read mode - single file selection
    picker = FilePicker(
        starting_directory=".",
        mode="read",
        file_filter=[".txt", ".pdf"],
        on_ok=lambda: print(f"Selected: {picker.get_selected_path()}"),
        on_cancel=lambda: print("Cancelled"),
    )

    # Write mode - save file
    picker = FilePicker(
        starting_directory=".",
        mode="write",
        show_hidden=True,
        on_ok=lambda: print(f"Save to: {picker.get_selected_path()}"),
    )

    # Read mode - multiple selection
    picker = FilePicker(
        mode="read",
        allow_multiple=True,
        on_ok=lambda: print(f"Selected files: {picker.get_selected_paths()}"),
    )

    ui.run()


if __name__ in {"__main__", "__mp_main__"}:
    main()

from nicegui import ui

from nicegooey.ui_util.file_picker import FilePicker


def main():
    # Read mode - single file selection
    picker1 = FilePicker(
        starting_directory=".",
        mode="read",
        file_filter=[".txt", ".pdf"],
        on_ok=lambda: print(f"Selected: {picker1.value}"),
        on_cancel=lambda: print("Cancelled"),
    )

    # Write mode - save file
    picker2 = FilePicker(
        starting_directory=".",
        mode="write",
        show_hidden=True,
        on_ok=lambda: print(f"Save to: {picker2.value}"),
    )

    # Read mode - multiple selection
    picker3 = FilePicker(
        mode="read",
        allow_multiple=True,
        on_ok=lambda: print(f"Selected files: {picker3.value}"),
    )

    ui.run()


if __name__ in {"__main__", "__mp_main__"}:
    main()

from nicegui import ui


class MaxWidthSelect(ui.select):
    """A select element that is as wide as its longest option, but no wider."""

    def __init__(self, options: list[str], **kwargs):
        super().__init__(options, **kwargs)

        # Reparent: wrap self in an inline-block div after creation
        longest = max((str(opt) for opt in options), key=len)
        assert self.parent_slot is not None
        with self.parent_slot.parent:
            with ui.element("div").classes("relative inline-block") as wrapper:
                # Hidden sizer with only the longest label
                with ui.element("div").classes(
                    "flex flex-col invisible h-0 overflow-hidden text-base whitespace-nowrap pl-3 pr-10"
                ):
                    ui.label(longest).classes("block")

        self.move(wrapper)
        self.classes("w-full")

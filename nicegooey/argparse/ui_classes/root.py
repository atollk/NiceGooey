from typing import TYPE_CHECKING, override

import nicegui.html
from nicegui import ui

from .groupings.parser_ui import ParserUi
from .util.ui_wrapper import UiWrapper

if TYPE_CHECKING:
    from ..main import NiceGooeyMain


class RootUi(UiWrapper):
    parser: ParserUi

    def __init__(self, parent: "NiceGooeyMain") -> None:
        super().__init__(parent)
        assert self.parent.parent_parser is not None
        self.parser = ParserUi(parent, self.parent.parent_parser)

    @override
    def render(self) -> ui.element:
        with ui.column(align_items="center").mark("ng-root") as root:
            with ui.column(align_items="center"):
                # TODO: dark mode to save my eyes
                dark = ui.dark_mode(True)
                with ui.row():
                    ui.label("Switch mode:")
                    ui.button("Dark", on_click=dark.enable)
                    ui.button("Light", on_click=dark.disable)

                width = (
                    self.parser_config.argument_vp_width
                    if isinstance(self.parser_config.argument_vp_width, str)
                    else f"w-{self.parser_config.argument_vp_width}"
                )
                with ui.card():
                    # Use a form to enable submit keyboard controls, but prevent page redirect on Submit.
                    with nicegui.html.form().props("onsubmit='return false;'"):
                        with ui.element().classes(width):
                            self.parser.render()

                        # Submit button
                        on_submit = self.parent.submit
                        ui.button("Submit").on_click(on_submit).props("type=submit")

            with ui.column(align_items="end"):
                ui.link("License", "/license")
        return root

    @override
    def validate(self) -> bool:
        return self.parser.validate()

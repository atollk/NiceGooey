from typing import TYPE_CHECKING, override

import nicegui.html
from nicegui import ui
from nicegui.elements.mixins.text_element import TextElement

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
        with ui.element().classes("absolute right-16"):
            dark = ui.dark_mode()
            with ui.row():
                ui.button(icon="light_mode", on_click=dark.disable)
                ui.button(icon="dark_mode", on_click=dark.enable)

        with ui.column(align_items="center").mark("ng-root") as root:
            TextElement(text=self.parent.parent_parser.prog, tag="h1").classes("text-h2")
            TextElement(text=self.parent.parent_parser.description, tag="h2").classes("text-subtitle1")

            with ui.card():
                # Use a form to enable submit keyboard controls, but prevent page redirect on Submit.
                with nicegui.html.form().props("onsubmit='return false;'"):
                    with ui.element().classes(self.parser_config.root_card_class):
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

from typing import TYPE_CHECKING

from nicegui import ui

from nicegooey.argparse import NiceGooeyConfig

if TYPE_CHECKING:
    from nicegooey.argparse.main import NiceGooeyMain


class UiWrapper:
    """Generic base class for most UI elements."""

    parent: "NiceGooeyMain"

    def __init__(self, parent: "NiceGooeyMain") -> None:
        self.parent = parent

    @property
    def parser_config(self) -> NiceGooeyConfig:
        return self.parent.config

    def render(self) -> ui.element:
        return ui.element()

    def validate(self) -> bool:
        return True

import argparse
import typing

from nicegui import ui

from .action_input_base import ActionInputBaseElement
from .action_ui_element import ActionUiElement


class CountActionUiElement(ActionUiElement[argparse._CountAction]):
    @typing.override
    def _input_element_init(self, default: typing.Any) -> ActionInputBaseElement:
        # TODO
        return ui.number(default, format="%d")

    @typing.override
    def _action_type(self) -> typing.Callable[[str], typing.Any]:
        return int

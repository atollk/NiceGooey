import argparse
import typing

from nicegui import ui
from nicegui.elements.mixins import value_element

from .action_ui_element import ActionUiElement


class CountActionUiElement(ActionUiElement[argparse._CountAction]):
    @typing.override
    def _input_element_init(self, default: typing.Any) -> value_element.ValueElement:
        return ui.number(default, format="%d")

    @typing.override
    def _action_type(self) -> typing.Callable[[str], typing.Any]:
        return int

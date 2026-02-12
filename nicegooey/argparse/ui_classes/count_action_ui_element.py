import argparse
import typing

from nicegui import ui
from nicegui.elements.mixins import value_element

from .action_ui_element import ActionUiElement


class CountActionUiElement(ActionUiElement[argparse._CountAction]):
    @typing.override
    def _create_input_element(self) -> value_element.ValueElement:
        return self._create_input_element_generic(lambda v: ui.number(v, format="%d"))

    @typing.override
    def _action_type(self) -> typing.Callable[[str], typing.Any]:
        return int

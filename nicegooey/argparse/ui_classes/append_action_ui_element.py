import argparse
import typing

from nicegui import ui
from nicegui.elements.mixins import value_element
from nicegui.elements.mixins.validation_element import ValidationElement

from .list_action_ui_element import ListActionUiElement


class AppendActionUiElement(ListActionUiElement[argparse._AppendAction]):
    @typing.override
    def render(self) -> ui.element:
        c = ui.column()
        with c:
            self.render_action_name()
            with ui.row(align_items="center"):
                value_el = self._create_add_element()
                self._create_add_button(value_el).set_icon("south")
            self._create_input_element()
        return c

    def _create_add_element(self) -> value_element.ValueElement:
        value_el = self._action_type_input()
        if isinstance(value_el, ValidationElement):
            value_el.validation = {"Must enter a value": lambda v: v is not None}
            value_el.without_auto_validation()
            value_el.error = None
        self.add_element_default_value = value_el.value
        return value_el

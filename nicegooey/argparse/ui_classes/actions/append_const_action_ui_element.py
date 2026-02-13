import argparse
import typing

from nicegui import ui
from nicegui.elements.mixins import value_element

from .list_action_ui_element import ListActionUiElement


class AppendConstActionUiElement(ListActionUiElement[argparse._AppendConstAction]):
    @typing.override
    def _input_element_default(self) -> None:
        return None

    @typing.override
    def render(self) -> ui.element:
        c = ui.column()
        with c:
            self._render_action_name()
            with ui.row(align_items="center"):
                self._create_input_element().props("use-input=false")
                value_el = value_element.ValueElement(value=None)
                self._create_add_button(value_el).set_icon("add")
        return c

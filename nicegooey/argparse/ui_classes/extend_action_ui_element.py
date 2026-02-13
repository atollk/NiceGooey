import argparse
import typing

from nicegui import ui
from nicegui.elements.mixins import value_element, validation_element
from nicegui.elements.mixins.validation_element import ValidationElement

from .list_action_ui_element import ListActionUiElement


class ExtendActionUiElement(ListActionUiElement[argparse._ExtendAction]):
    @typing.override
    def render(self) -> ui.element:
        c = ui.column()
        with c:
            self._render_action_name()
            with ui.row(align_items="center"):
                value_el = self._create_add_element()
                self._create_add_button(value_el).set_icon("south")
            self._create_input_element()
        return c

    def _create_add_element(self) -> value_element.ValueElement:
        self._action_type_input()
        value_el = self.element
        if isinstance(value_el, ValidationElement):
            value_el.validation = {"Must enter a value": lambda v: v is not None}
            value_el.without_auto_validation()
            value_el.error = None
        self.add_element_default_value = value_el.value
        return value_el

    @typing.override
    def _on_add_button_click(self, value_el: value_element.ValueElement) -> None:
        if isinstance(value_el, validation_element.ValidationElement):
            if not value_el.validate():
                return
        ns = argparse.Namespace()
        assert self.parent.parent_parser is not None
        assert self.element is not None
        self.action(self.parent.parent_parser, ns, [value_el.value])
        new = (self.element.value or []) + getattr(ns, self.action.dest)
        self.element.set_value(new)
        value_el.set_value(self.add_element_default_value)

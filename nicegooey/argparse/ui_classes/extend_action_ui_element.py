import argparse
import typing

from nicegui.elements.mixins import value_element, validation_element

from .append_action_ui_element import AppendActionUiElement


class ExtendActionUiElement(AppendActionUiElement):
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

import abc
import argparse
import typing

from nicegui import ui
from nicegui.elements.mixins import value_element, validation_element

from .action_ui_element import ActionUiElement


class ListActionUiElement[ActionT: argparse.Action](ActionUiElement[ActionT], abc.ABC):
    add_element_default_value: typing.Any = None

    @typing.override
    def _create_input_element(self) -> value_element.ValueElement:
        def forward_transform(vs: list[typing.Any] | None) -> list[typing.Any] | None:
            ns = argparse.Namespace()
            ns.__setattr__(self.action.dest, getattr(self.parent.namespace, self.action.dest))
            try:
                cast = [self._action_type()(v) for v in (vs or [])]
            except TypeError:
                return getattr(ns, self.action.dest)
            else:
                return cast

        el = self._create_input_element_generic(ui.input_chips, forward_transform=forward_transform)
        el.classes("w-xl")
        return el

    def _on_add_button_click(self, value_el: value_element.ValueElement) -> None:
        if isinstance(value_el, validation_element.ValidationElement):
            if not value_el.validate():
                return
        ns = argparse.Namespace()
        assert self.parent.parent_parser is not None
        assert self.element is not None
        self.action(self.parent.parent_parser, ns, value_el.value)
        new = (self.element.value or []) + getattr(ns, self.action.dest)
        self.element.set_value(new)
        value_el.set_value(self.add_element_default_value)

    def _create_add_button(self, value_el: value_element.ValueElement) -> ui.button:
        return (
            ui.button(on_click=lambda: self._on_add_button_click(value_el))
            .props("square padding=xs")
            .mark("ng-action-add-button")
        )

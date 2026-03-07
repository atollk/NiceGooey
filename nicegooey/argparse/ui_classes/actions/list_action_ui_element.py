import abc
import argparse
import typing

from nicegui import ui
from nicegui.elements.mixins import value_element, validation_element

from .action_ui_element import ActionUiElement
from .action_input_base import ActionInputBaseElement, DisableableValidationElement


class ListActionInputBaseElement(ActionInputBaseElement):
    @typing.override
    def _action_type_input_nargs_wrapper(
        self, basic_element: typing.Callable[[], value_element.ValueElement]
    ) -> DisableableValidationElement:
        return super()._action_type_input_nargs_wrapper(basic_element)

    @typing.override
    def _action_type_input_required_wrapper(
        self, nargs_wrapper_element: typing.Callable[[], DisableableValidationElement]
    ) -> ui.element:
        if self.action.required:
            raise NotImplementedError("Required list actions are not supported yet")  # TODO
        else:
            with ui.element() as required_wrapper:
                required_wrapper.mark(self.REQUIRED_WRAPPER_MARKER)
                return self._list_element(nargs_wrapper_element)


class ListActionUiElement[ActionT: argparse.Action](ActionUiElement[ActionT], abc.ABC):
    add_element_default_value: typing.Any = None

    @typing.override
    def _create_input_element(self) -> value_element.ValueElement:
        return super()._create_input_element().classes("w-xl")

    @typing.override
    def _input_element_init(self, default: typing.Any) -> ActionInputBaseElement:
        assert self.parent.parent_parser is not None
        input_base = ListActionInputBaseElement(
            action=self.action, parser=self.parent.parent_parser, init_value=default
        )
        return input_base

    @typing.override
    def _input_element_forward_transform(self, v: typing.Any) -> list[typing.Any] | None:
        # assert isinstance(vs, list) or vs is None  TODO
        ns = argparse.Namespace()
        ns.__setattr__(self.action.dest, getattr(self.parent.namespace, self.action.dest))
        try:
            cast = [self._action_type()(u) for u in (v or [])]
        except TypeError:
            return getattr(ns, self.action.dest)
        else:
            return cast

    def _create_add_button(self, value_el: value_element.ValueElement) -> ui.button:
        return (
            ui.button(on_click=lambda: self._on_add_button_click(value_el))
            .props("square padding=xs")
            .mark("ng-action-add-button")
        )

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

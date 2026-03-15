import abc
import argparse
import typing

from nicegui import ui
from nicegui.elements.mixins import value_element, validation_element

from .action_ui_element import ActionUiElement
from .action_sync_element import ActionSyncElement


class ListActionInputBaseElement(ActionSyncElement):
    @typing.override
    def _action_type_input_required_wrapper(
        self, nargs_wrapper_element: typing.Callable[[], value_element.ValueElement]
    ) -> ui.element:
        if self.action.required:
            raise NotImplementedError("Required list actions are not supported yet")  # TODO
        else:

            def on_add_button_click(
                list_element: value_element.ValueElement,
                inner_element: value_element.ValueElement,
                inner_element_default_value: typing.Any,
            ) -> None:
                """Override the on_click function to call the action instead of just appending to the list."""
                if isinstance(inner_element, validation_element.ValidationElement):
                    if not inner_element.validate():
                        return
                ns = argparse.Namespace()
                ns.__setattr__(self.action.dest, list_element.value)
                self.action(self.parser, ns, inner_element.value)
                list_element.value = getattr(ns, self.action.dest)
                inner_element.set_value(inner_element_default_value)

            with ui.element() as required_wrapper:
                required_wrapper.mark(self.REQUIRED_WRAPPER_MARKER)
                return self._list_element(nargs_wrapper_element, on_add_button_click=on_add_button_click)


class ListActionUiElement[ActionT: argparse.Action](ActionUiElement[ActionT], abc.ABC):
    add_element_default_value: typing.Any = None

    @typing.override
    def _render_input_element(self) -> value_element.ValueElement:
        return super()._render_input_element().classes("w-xl")

    @typing.override
    def _input_element_init(self, default: typing.Any) -> ActionSyncElement:
        assert self.parent.parent_parser is not None
        input_base = ListActionInputBaseElement(
            action=self.action, parser=self.parent.parent_parser, init_value=default
        )
        return input_base

    @typing.override
    def _input_element_forward_transform(self, v: typing.Any) -> list[typing.Any] | None:
        assert isinstance(v, list) or v is None
        return [self._action_type()(u) for u in (v or [])]

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

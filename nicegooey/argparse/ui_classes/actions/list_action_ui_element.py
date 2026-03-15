import abc
import argparse
from typing import override, Callable, Any, Type

from nicegui import ui
from nicegui.elements.mixins import value_element, validation_element
from nicegui.elements.mixins.value_element import ValueElement

from .action_info_helper import ActionInfoHelper
from .action_ui_element import ActionUiElement
from .action_sync_element import ActionSyncElement


class ListActionUiElement[ActionT: argparse.Action](ActionUiElement[ActionT], abc.ABC):
    class _ActionSyncElement(ActionSyncElement):
        @override
        @classmethod
        def _action_type_input_required_wrapper(
            cls, action_info: ActionInfoHelper, nargs_wrapper_element: Callable[[], ValueElement]
        ) -> ui.element:
            if action_info.action.required:
                # TODO
                raise NotImplementedError("Required list actions are not supported yet")
            else:

                def on_add_button_click(
                    list_element: value_element.ValueElement,
                    inner_element: value_element.ValueElement,
                    inner_element_default_value: Any,
                ) -> None:
                    """Override the on_click function to call the action instead of just appending to the list."""
                    if isinstance(inner_element, validation_element.ValidationElement):
                        if not inner_element.validate():
                            return
                    ns = argparse.Namespace()
                    ns.__setattr__(action_info.action.dest, list_element.value)
                    action_info.action(action_info.parser, ns, inner_element.value)
                    list_element.value = getattr(ns, action_info.action.dest)
                    inner_element.set_value(inner_element_default_value)

                with ui.element() as required_wrapper:
                    required_wrapper.mark(cls.REQUIRED_WRAPPER_MARKER)
                    return cls._list_element(nargs_wrapper_element, on_add_button_click=on_add_button_click)

        def _ui_state_to_value(self) -> Any:
            v = self.inner_elements.nargs_wrapper_element.value
            assert isinstance(v, list) or v is None
            action_info = ActionInfoHelper(action=self.action, parser=self.parser)
            return [action_info.action_type()[1](u) for u in (v or [])]

    add_element_default_value: Any = None

    @override
    def _render_input_element(self) -> ActionSyncElement:
        super()._render_input_element()
        self.element.inner_elements.nargs_wrapper_element.classes("w-xl")
        return self.element

    @classmethod
    def _action_sync_element(cls) -> Type[ActionSyncElement]:
        return cls._ActionSyncElement

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

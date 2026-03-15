import abc
import argparse
from typing import Any, override, Type, Callable

from nicegui import ui
from nicegui.elements.mixins.validation_element import ValidationElement
from nicegui.elements.mixins.value_element import ValueElement

from nicegooey.argparse.ui_classes.actions.action_info_helper import ActionInfoHelper
from nicegooey.argparse.ui_classes.actions.action_sync_element import ActionSyncElement
from nicegooey.argparse.ui_classes.actions.action_ui_element import ActionUiElement


class StoreActionUiElement(ActionUiElement[argparse._StoreAction]):
    class _ActionSyncElement(ActionSyncElement):
        @override
        def _ui_state_to_value(self) -> Any:
            v = self.inner_elements.nargs_wrapper_element.value
            ns = argparse.Namespace()
            ns.__setattr__(self.action.dest, getattr(self.namespace, self.action.dest, None))
            try:
                action_info = ActionInfoHelper(action=self.action, parser=self.parser)
                t = action_info.action_type_with_nargs()
                cast = t(v)
            except (TypeError, ValueError):
                pass
            else:
                assert self.parser is not None
                self.action(self.parser, ns, cast)
            return getattr(ns, self.action.dest)

    @classmethod
    def _action_sync_element(cls) -> Type[ActionSyncElement]:
        return cls._ActionSyncElement


class StoreConstActionUiElement(ActionUiElement[argparse._StoreConstAction]):
    class _ActionSyncElement(ActionSyncElement):
        @override
        def _ui_state_from_value(self, value: Any) -> None:
            el = self.inner_elements.enable_box_element
            if el is None:
                # The element is required, so we can't do anything.
                return
            # This logic doesn't matter because the value isn't actually used, but it's fun to have here :)
            if value == self.action.const:
                el.value = True
            elif value == ActionInfoHelper(action=self.action, parser=self.parser).action_default():
                el.value = False
            else:
                el.value = None

        @override
        def _ui_state_to_value(self) -> Any:
            if self.inner_elements.enable_box_element is None or self.inner_elements.enable_box_element.value:
                ns = argparse.Namespace()
                assert self.parser is not None
                self.action(self.parser, ns, None)
                return getattr(ns, self.action.dest)
            else:
                return ActionInfoHelper(action=self.action, parser=self.parser).action_default()

    @classmethod
    @override
    def _action_sync_element(cls) -> Type[ActionSyncElement]:
        return cls._ActionSyncElement


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
                    list_element: ValueElement,
                    inner_element: ValueElement,
                    inner_element_default_value: Any,
                ) -> None:
                    """Override the on_click function to call the action instead of just appending to the list."""
                    if isinstance(inner_element, ValidationElement):
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


class ExtendActionUiElement(ActionUiElement[argparse._AppendAction]):
    pass


class AppendActionUiElement(ListActionUiElement[argparse._AppendAction]):
    pass


class AppendConstActionUiElement(ListActionUiElement[argparse._AppendConstAction]):
    pass


class CountActionUiElement(ActionUiElement[argparse._CountAction]):
    """Count actions are a special case because they differ very much between UI and CLI usage. In the UI, they are just a number widget."""

    class _ActionSyncElement(ActionSyncElement):
        @override
        def __init__(self, action: argparse.Action, parser: argparse.ArgumentParser):
            super().__init__(self._create_pseudo_action(action), parser)

        @staticmethod
        def _create_pseudo_action(action: argparse.Action) -> argparse.Action:
            """Create a pseudo action that behaves like the count action but can be used to initialize the input element."""
            # TODO: if the original is required, the min count should be 1
            return argparse._StoreAction(
                option_strings=action.option_strings,
                dest=action.dest,
                nargs=None,
                default=0,
                type=int,
                required=True,
                help=action.help,
                metavar=action.metavar,
                deprecated=action.deprecated if hasattr(action, "deprecated") else False,
            )

    @override
    @classmethod
    def _action_sync_element(cls) -> Type[ActionSyncElement]:
        return cls._ActionSyncElement

import abc
import argparse
from typing import Any, Callable, override

from nicegui import ui
from nicegui.elements.mixins.validation_element import ValidationElement

from nicegooey.argparse.main import NiceGooeyMain
from nicegooey.argparse.ui_classes.actions.action_info_helper import ActionInfoHelper
from nicegooey.argparse.ui_classes.actions.action_ui_element import ActionUiElement
from nicegooey.argparse.ui_classes.util.misc import add_validation, q_field

# TODO: make some method names clearer


class StoreActionUiElement(ActionUiElement[argparse._StoreAction]):
    @override
    def _ui_state_to_value(self) -> Any:
        assert self.inner_elements is not None
        if not self.is_enabled():
            return ActionInfoHelper(action=self.action, parser=self._parser).action_default()
        v = self.inner_elements.nargs_wrapper_element.value
        ns = argparse.Namespace()
        ns.__setattr__(self.action.dest, getattr(self.namespace, self.action.dest, None))
        try:
            action_info = ActionInfoHelper(action=self.action, parser=self._parser)
            t = action_info.action_type_with_nargs()
            cast = t(v)
        except (TypeError, ValueError):
            pass
        else:
            assert self._parser is not None
            self.action(self._parser, ns, cast)
        return getattr(ns, self.action.dest)


class StoreConstActionUiElement(ActionUiElement[argparse._StoreConstAction]):
    @override
    def _ui_state_from_value(self, value: Any) -> None:
        assert self.inner_elements is not None
        el = self.inner_elements.enable_box_element
        if el is None:
            # The element is required, so we can't do anything.
            return
        # This logic doesn't matter because the value isn't actually used, but it's fun to have here :)
        if value == self.action.const:
            el.value = True
        elif value == ActionInfoHelper(action=self.action, parser=self._parser).action_default():
            el.value = False
        else:
            el.value = None

    @override
    def _ui_state_to_value(self) -> Any:
        if not self.is_enabled():
            return ActionInfoHelper(action=self.action, parser=self._parser).action_default()
        ns = argparse.Namespace()
        assert self._parser is not None
        self.action(self._parser, ns, None)
        return getattr(ns, self.action.dest)


class ListActionUiElement[ActionT: argparse.Action](ActionUiElement[ActionT], abc.ABC):
    add_element_default_value: Any = None

    @override
    def _render_input_element(self) -> None:
        super()._render_input_element()
        assert self.inner_elements is not None
        self.inner_elements.nargs_wrapper_element.classes("w-xl")

    @override
    @classmethod
    def _action_type_input_required_wrapper(
        cls, action_info: ActionInfoHelper, nargs_wrapper_element: Callable[[], ValidationElement]
    ) -> ui.element:
        def on_add_button_click(
            list_element: ValidationElement,
            inner_element: ValidationElement,
            inner_element_default_value: Any,
        ) -> None:
            """Override the on_click function to call the action instead of just appending to the list."""
            if not inner_element.validate():
                return
            ns = argparse.Namespace()
            ns.__setattr__(action_info.action.dest, list_element.value)
            action_info.action(action_info.parser, ns, inner_element.value)
            list_element.value = getattr(ns, action_info.action.dest)
            inner_element.set_value(inner_element_default_value)

        with q_field() as required_wrapper:
            required_wrapper.mark(cls.REQUIRED_WRAPPER_MARKER)
            list_element = cls._list_element(nargs_wrapper_element, on_add_button_click=on_add_button_click)

        if action_info.action.required:
            list_element.without_auto_validation()
            add_validation(
                list_element,
                {"At least one element is required": lambda v: isinstance(v, list) and len(v) > 0},
            )

        return required_wrapper

    def _ui_state_to_value(self) -> Any:
        assert self.inner_elements is not None
        if not self.is_enabled():
            return ActionInfoHelper(action=self.action, parser=self._parser).action_default()
        v = self.inner_elements.nargs_wrapper_element.value
        assert isinstance(v, list) or v is None
        action_info = ActionInfoHelper(action=self.action, parser=self._parser)
        return [action_info.action_type()[1](u) for u in (v or [])]


class ExtendActionUiElement(ActionUiElement[argparse._AppendAction]):
    pass


class AppendActionUiElement(ListActionUiElement[argparse._AppendAction]):
    pass


class AppendConstActionUiElement(ListActionUiElement[argparse._AppendConstAction]):
    @override
    @classmethod
    def _action_type_input_nargs_wrapper(
        cls, action_info: ActionInfoHelper, basic_element: Callable[[], ValidationElement]
    ) -> ValidationElement:
        return q_field().mark(cls.BASIC_ELEMENT_MARKER, cls.NARGS_WRAPPER_MARKER)


class CountActionUiElement(ActionUiElement[argparse._CountAction]):
    """Count actions are a special case because they differ very much between UI and CLI usage. In the UI, they are just a number widget."""

    _original_action: argparse.Action

    @override
    def __init__(self, parent: NiceGooeyMain, action: argparse._CountAction) -> None:
        self._original_action = action
        super().__init__(parent, self._create_pseudo_action(action))

    @staticmethod
    def _create_pseudo_action(action: argparse.Action) -> argparse.Action:
        """Create a pseudo action that behaves like the count action but can be used to initialize the input element."""
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
    def validate(self) -> bool:
        if not super().validate():
            return False
        if self._original_action.required:
            # if the original is required, the min count should be 1
            if self._ui_state_to_value() < 1:
                self.inner_elements.required_wrapper_element.error = "Value needs to be at least 1"
                return False
        return True

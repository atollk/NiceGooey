import abc
import argparse
from typing import Any, Callable, override, Final

from nicegui import ui, ElementFilter
from nicegui.elements.mixins.validation_element import ValidationElement

from nicegooey.argparse.main import NiceGooeyMain
from nicegooey.argparse.ui_classes.actions.action_info_helper import ActionInfoHelper
from nicegooey.argparse.ui_classes.actions.action_ui_element import ActionUiElement, find_exactly_one_element
from nicegooey.argparse.ui_classes.util.misc import add_validation, q_field, clear_value_element


class StoreActionUiElement(ActionUiElement[argparse._StoreAction]):
    @override
    def _ui_state_to_value(self) -> Any:
        assert self.inner_elements is not None
        if not self.is_enabled():
            return ActionInfoHelper(action=self.action, parser=self._parser).default()
        v = self.inner_elements.nargs_wrapper_element.value
        ns = argparse.Namespace()
        ns.__setattr__(self.action.dest, getattr(self.namespace, self.action.dest, None))
        try:
            action_info = ActionInfoHelper(action=self.action, parser=self._parser)
            t = action_info.type_with_nargs()
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
        if value == self.action.const:
            el.value = True
        elif value == ActionInfoHelper(action=self.action, parser=self._parser).default():
            el.value = False
        else:
            el.value = None

    @override
    def _ui_state_to_value(self) -> Any:
        if not self.is_enabled():
            return ActionInfoHelper(action=self.action, parser=self._parser).default()
        ns = argparse.Namespace()
        assert self._parser is not None
        self.action(self._parser, ns, None)
        return getattr(ns, self.action.dest)

    @classmethod
    def _should_render_enable_box(cls, action_info: ActionInfoHelper) -> bool:
        # Since a store-const action is basically useless if it cannot be en-/disabled, we only don't do that if it is explicitly asked for.
        return action_info.ng_config().override_required or action_info.action.required


class ListActionUiElement[ActionT: argparse.Action](ActionUiElement[ActionT], abc.ABC):
    LIST_ELEMENT_MARKER: Final[str] = "ng-action-listelement"
    LIST_ADD_BUTTON_MARKER: Final[str] = "ng-action-listbutton"

    add_element_default_value: Any = None
    list_input_element: ui.input_chips | None = None

    @override
    def _render_inner_elements(self) -> None:
        super()._render_inner_elements()
        assert self.inner_elements is not None
        self.inner_elements.nargs_wrapper_element.classes("w-xl")
        self.list_input_element = find_exactly_one_element(
            ElementFilter(marker=self.LIST_ELEMENT_MARKER, kind=ui.input_chips).within(
                instance=self.inner_elements.outmost
            ),
        )

    @override
    def _render_input_element(self) -> None:
        super()._render_input_element()
        assert self.list_input_element is not None
        self.list_input_element.on_value_change(lambda ev: self.sync_to_namespace())

    @override
    @classmethod
    def _render_action_required(
        cls, action_info: ActionInfoHelper, nargs_wrapper_element: Callable[[], ValidationElement]
    ) -> ValidationElement:
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
            list_element, inner_element, add_button = cls._render_action_list(
                nargs_wrapper_element, on_add_button_click=on_add_button_click
            )
            list_element.mark(cls.LIST_ELEMENT_MARKER)
            add_button.mark(cls.LIST_ADD_BUTTON_MARKER)

        if action_info.action.required:
            list_element.without_auto_validation()
            add_validation(
                list_element,
                {"At least one element is required": lambda v: isinstance(v, list) and len(v) > 0},
            )

        return required_wrapper

    @override
    def _ui_state_to_value(self) -> Any:
        if self.list_input_element is None:
            return []
        assert self.inner_elements is not None
        if not self.is_enabled():
            return ActionInfoHelper(action=self.action, parser=self._parser).default()
        v = self.list_input_element.value
        assert isinstance(v, list) or v is None
        action_info = ActionInfoHelper(action=self.action, parser=self._parser)
        return [action_info.type_with_nargs()(u) for u in (v or [])]

    # TODO: this override is almost entirely duplicate code; can we make this nicer?
    @override
    def _ui_state_from_value(self, value: Any) -> None:
        assert self.inner_elements is not None

        # TODO: this assertion is False if the namespace value is already set
        assert self.list_input_element is not None

        # Evaluate whether the element should be disabled or enabled (if non-required).
        typ = self._action_info.type()
        try:
            typ(value)
        except Exception:
            value_is_valid = False
        else:
            value_is_valid = True
        disable = value is None or not value_is_valid or value == self._action_info.default()

        # Set the values of the UI elements.
        if self.inner_elements.enable_box_element is not None:
            self.inner_elements.enable_box_element.value = not disable
        if value_is_valid and value is not None:
            self.list_input_element.value = value
        else:
            clear_value_element(self.list_input_element)

    @override
    def validate(self) -> bool:
        assert self.list_input_element is not None
        return super().validate() and self.list_input_element.validate()


class ExtendActionUiElement(ActionUiElement[argparse._AppendAction]):
    pass


class AppendActionUiElement(ListActionUiElement[argparse._AppendAction]):
    pass


class AppendConstActionUiElement(ListActionUiElement[argparse._AppendConstAction]):
    @override
    @classmethod
    def _render_action_nargs(
        cls, action_info: ActionInfoHelper, basic_element: Callable[[], ValidationElement]
    ) -> ValidationElement:
        return q_field().mark(cls.BASIC_ELEMENT_MARKER, cls.NARGS_WRAPPER_MARKER)


class CountActionUiElement(ActionUiElement[argparse.Action]):
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
        )

    @override
    def validate(self) -> bool:
        assert self.inner_elements is not None
        if not super().validate():
            return False
        if self._original_action.required:
            # if the original is required, the min count should be 1
            if self._ui_state_to_value() < 1:
                self.inner_elements.required_wrapper_element.error = "Value needs to be at least 1"
                return False
        return True

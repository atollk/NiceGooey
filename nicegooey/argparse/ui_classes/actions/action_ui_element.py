import abc
import argparse
import typing

from nicegui import ui
from nicegui.elements.mixins import value_element, validation_element

from .action_info_helper import ActionInfoHelper
from .action_input_base import ActionInputBaseElement
from ...main import NiceGooeyMain
from nicegooey.argparse.ui_classes.util import UiWrapper, Nargs


class ActionUiElement[ActionT: argparse.Action](UiWrapper, abc.ABC):
    _UNSET = object()

    action: ActionT
    element: value_element.ValueElement | None = None

    @staticmethod
    def from_action(parent: NiceGooeyMain, action: argparse.Action) -> "ActionUiElement | None":
        from .store_action_ui_element import StoreActionUiElement
        from .store_const_action_ui_element import StoreConstActionUiElement
        from .extend_action_ui_element import ExtendActionUiElement
        from .append_action_ui_element import AppendActionUiElement
        from .append_const_action_ui_element import AppendConstActionUiElement
        from .count_action_ui_element import CountActionUiElement

        match action:
            case argparse._StoreAction():
                return StoreActionUiElement(parent=parent, action=action)
            case argparse._StoreConstAction():
                return StoreConstActionUiElement(parent=parent, action=action)
            case argparse._ExtendAction():
                return ExtendActionUiElement(parent=parent, action=action)
            case argparse._AppendAction():
                return AppendActionUiElement(parent=parent, action=action)
            case argparse._AppendConstAction():
                return AppendConstActionUiElement(parent=parent, action=action)
            case argparse._CountAction():
                return CountActionUiElement(parent=parent, action=action)
            case argparse._HelpAction() | argparse._VersionAction() | argparse._SubParsersAction():
                # handled differently
                return None
            case _:
                raise NotImplementedError(f"UI for action type {type(action)} not implemented")

    def __init__(self, parent: NiceGooeyMain, action: ActionT) -> None:
        super().__init__(parent)
        self.action = action

    @typing.override
    def render(self) -> ui.element:
        c = ui.column()
        with c:
            self._render_action_name()
            self._create_input_element()
        return c

    @typing.override
    def validate(self) -> bool:
        """Validates all child elements."""
        if isinstance(self.element, validation_element.ValidationElement):
            return self.element.validate()
        return True

    @property
    def _action_info(self) -> ActionInfoHelper:
        assert self.parent.parent_parser is not None
        return ActionInfoHelper(self.action, self.parent.parent_parser)

    def _render_action_name(self):
        """Renders the name of this action (i.e. the metavar or dest) and a tooltip with the help text if it exists."""
        with ui.row(align_items="center").mark("ng-action-name"):
            if isinstance(self.action.metavar, str):
                name = self.action.metavar
            elif isinstance(self.action.metavar, tuple):
                name = self.action.metavar[0]
            else:
                name = self.action.dest
            ui.label(name).classes("font-bold")
            if self.action.help:
                with ui.button(icon="question_mark").props("round padding=xs size=xs"):
                    ui.tooltip(self.action.help)

    def _action_type(self) -> typing.Callable[[str], typing.Any]:
        return self._action_info.action_type()

    def _action_default(self) -> typing.Any:
        return self._action_info.action_default()

    def _action_nargs(self) -> int | Nargs:
        return self._action_info.action_nargs()

    def _input_element_forward_transform(self, v: typing.Any) -> typing.Any:
        """Used by `_create_input_element_generic` to transform the value from the input element before storing it in the namespace."""
        return v

    def _input_element_backward_transform(self, v: typing.Any) -> typing.Any:
        """Used by `_create_input_element_generic` to transform the value from the namespace before storing it in the input element."""
        return v

    def _input_element_validate(self, value: typing.Any) -> str | None:
        """Used by `_create_input_element_generic` as the validation function for the input element. Validates the value by trying to cast it to the action's type by default."""
        if self._action_nargs() == Nargs.OPTIONAL and value is None:
            return "Value is required"
        try:
            self._action_type()(value)
            return None
        except Exception as e:
            return str(e)

    def _input_element_default(self) -> typing.Any:
        return self._action_default()

    def _input_element_init(self, default: typing.Any) -> value_element.ValueElement:
        assert self.parent.parent_parser is not None
        input_base = ActionInputBaseElement(
            action=self.action, parser=self.parent.parent_parser, init_value=default
        )
        return input_base.basic_element

    def _create_input_element(self) -> value_element.ValueElement:
        """
        Creates/Renders the input element for this action and stores it in `self.element`.
        :return `self.element`
        """
        el = self._input_element_init(self._input_element_default())
        if isinstance(el, validation_element.ValidationElement):
            el.without_auto_validation()
            el.validation = self._input_element_validate
            el.error = None
        if not hasattr(self.parent.namespace, self.action.dest):
            setattr(self.parent.namespace, self.action.dest, self._action_default())
        el.bind_value(
            target_object=self.parent.namespace,
            target_name=self.action.dest,
            forward=self._input_element_forward_transform,
            backward=self._input_element_backward_transform,
        )
        self.element = el
        return self.element

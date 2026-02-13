import abc
import argparse
import builtins
import typing

from nicegui import ui
from nicegui.elements.mixins import value_element, validation_element

from ..main import NiceGooeyMain
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
        """Returns the type of this action, or a reasonable default if no type is set."""
        match self.action.type:
            case None:
                return str
            case argparse.FileType:
                raise NotImplementedError("argparse.FileType is deprecated and not supported.")
            case str():
                assert self.parent.parent_parser is not None
                return self.parent.parent_parser._registry_get("type", self.action.type)
            case _:
                return self.action.type

    def _action_default(self) -> typing.Any:
        """Returns the default value for this action, or a reasonable default if no default is set."""
        if self.action.default is not None:
            return self.action.default
        if self.action.choices is not None:
            return []
        else:
            match self._action_type():
                case builtins.bool:
                    return False
                case builtins.int | builtins.float:
                    return 0
                case _:
                    return ""

    def _action_nargs(self) -> int | Nargs:
        """Returns the nargs of this action, or a reasonable default if no nargs is set."""
        if isinstance(self.action.nargs, int):
            return self.action.nargs

        if self.action.nargs is not None:
            if self.action.nargs in ("?", "*", "+"):
                return Nargs(self.action.nargs)
            elif self.action.nargs in ("...", "A...", "==SUPPRESS=="):
                raise NotImplementedError(f"nargs value {self.action.nargs} not supported")
            else:
                raise ValueError(f"Unrecognized nargs value: {self.action.nargs}")

        return Nargs.SINGLE_ELEMENT

    def _action_type_input(self, *args, **kwargs) -> value_element.ValueElement:
        """Creates a ValueElement that represents the input of a single item matching the type of this action."""
        # Set up the basic element for entering a value.
        basic_element: value_element.ValueElement
        if self.action.choices is not None:
            # TODO: make the size consistent
            choices = list(self.action.choices)
            # pyrefly: ignore[bad-keyword-argument]
            basic_element = ui.select(options=choices, *args, **kwargs)
        else:
            match self._action_type():
                case builtins.bool:
                    basic_element = ui.checkbox(*args, **kwargs)
                case builtins.int:
                    basic_element = ui.number(format="%d", *args, **kwargs).props("dense")
                case builtins.float:
                    basic_element = ui.number(format="%f", *args, **kwargs).props("dense")
                case builtins.str:
                    basic_element = ui.input(*args, **kwargs).props("dense")
                case _:
                    basic_element = ui.input(*args, **kwargs).props("dense")
        basic_element.mark("ng-action-type-input-basic")

        # Set up any surrounding elements that might be necessary based on nargs.
        nargs_wrapper_element: value_element.ValueElement
        nargs = self._action_nargs()
        match nargs:
            case Nargs.SINGLE_ELEMENT:
                nargs_wrapper_element = basic_element
            case Nargs.OPTIONAL:
                # TODO
                raise NotImplementedError("nargs value ? is not supported in _action_type_input")
            case Nargs.ZERO_OR_MORE | Nargs.ONE_OR_MORE:
                # TODO
                raise NotImplementedError("nargs values * and + are not supported in _action_type_input")
            case Nargs.PARSER | Nargs.REMAINDER | Nargs.SUPPRESS:
                raise NotImplementedError(f"nargs value {nargs} are not supported in _action_type_input")
            case int(n):
                if n != 1:
                    raise NotImplementedError("Only nargs=1 is supported in _action_type_input")
        nargs_wrapper_element.mark("ng-action-type-input-nargs-wrapper")

        return nargs_wrapper_element

    def _validate_input_value(self, value: typing.Any) -> str | None:
        """Used by `_create_input_element_generic` as the validation function for the input element. Validates the value by trying to cast it to the action's type by default."""
        try:
            self._action_type()(value)
            return None
        except Exception as e:
            return str(e)

    def _input_element_forward_transform(self, v: typing.Any) -> typing.Any:
        """Used by `_create_input_element_generic` to transform the value from the input element before storing it in the namespace."""
        return v

    def _input_element_backward_transform(self, v: typing.Any) -> typing.Any:
        """Used by `_create_input_element_generic` to transform the value from the namespace before storing it in the input element."""
        return v

    def _input_element_default(self) -> typing.Any:
        return self._action_default()

    def _input_element_init(self, default: typing.Any) -> value_element.ValueElement:
        return self._action_type_input(value=default)

    def _create_input_element(self) -> value_element.ValueElement:
        """
        Creates/Renders the input element for this action and stores it in `self.element`.
        :param init: The type/constructor to use for the input element.
        :param default: Optional default value for the input element. If not provided, the action's default or a type-based default will be used.
        :return `self.element`
        """
        el = self._input_element_init(self._input_element_default())
        if isinstance(el, validation_element.ValidationElement):
            el.without_auto_validation()
            el.validation = self._validate_input_value
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

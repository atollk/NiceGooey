import abc
import argparse
import builtins
import dataclasses
import typing

from nicegui import ui, ElementFilter
from nicegui.elements.mixins import value_element, validation_element
from nicegui.elements.mixins.disableable_element import DisableableElement

from ...main import NiceGooeyMain
from nicegooey.argparse.ui_classes.util import UiWrapper, Nargs, MaxWidthSelect


@dataclasses.dataclass
class ActionInfoHelper:
    action: argparse.Action
    parser: argparse.ArgumentParser

    def action_type(self) -> typing.Callable[[str], typing.Any]:
        """Returns the type of this action, or a reasonable default if no type is set."""
        match self.action.type:
            case None:
                return str
            case argparse.FileType:
                raise NotImplementedError("argparse.FileType is deprecated and not supported.")
            case str():
                return self.parser._registry_get("type", self.action.type)
            case _:
                return self.action.type

    def action_default(self) -> typing.Any:
        """Returns the default value for this action, or a reasonable default if no default is set."""
        if self.action.default is not None:
            return self.action.default
        if self.action.choices is not None:
            return []
        else:
            match self.action_type():
                case builtins.bool:
                    return False
                case builtins.int | builtins.float:
                    return 0
                case _:
                    return ""

    def action_nargs(self) -> int | Nargs:
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


class ActionInputBaseElement:
    action: argparse.Action
    parser: argparse.ArgumentParser

    basic_element: value_element.ValueElement
    nargs_wrapper_element: DisableableElement
    required_wrapper_element: ui.element

    BASIC_ELEMENT_MARKER: typing.Final[str] = "ng-action-type-input-basic"
    NARGS_WRAPPER_MARKER: typing.Final[str] = "ng-action-type-input-nargs-wrapper"
    REQUIRED_WRAPPER_MARKER: typing.Final[str] = "ng-action-type-input-required-wrapper"

    def __init__(
        self, action: argparse.Action, parser: argparse.ArgumentParser, init_value: typing.Any = None
    ) -> None:
        self.action = action
        self.parser = parser
        self._render(init_value)

    def _action_type_input_basic_element(self, value: typing.Any) -> value_element.ValueElement:
        basic_element: value_element.ValueElement
        if self.action.choices is not None:
            choices = list(self.action.choices)
            basic_element = MaxWidthSelect(options=choices, value=value)
        else:
            match ActionInfoHelper(action=self.action, parser=self.parser).action_type():
                case builtins.bool:
                    basic_element = ui.checkbox(value=value)
                case builtins.int:
                    basic_element = ui.number(format="%d", value=value).props("dense")
                case builtins.float:
                    basic_element = ui.number(format="%f", value=value).props("dense")
                case builtins.str:
                    basic_element = ui.input(value=value).props("dense")
                case _:
                    basic_element = ui.input(value=value).props("dense")
        basic_element.mark(self.BASIC_ELEMENT_MARKER)
        return basic_element

    def _action_type_input_nargs_wrapper(
        self, basic_element: typing.Callable[[], value_element.ValueElement]
    ) -> DisableableElement:
        nargs = ActionInfoHelper(action=self.action, parser=self.parser).action_nargs()
        with DisableableElement() as nargs_wrapper_element:
            match nargs:
                case Nargs.SINGLE_ELEMENT | Nargs.OPTIONAL:
                    basic_element()
                case Nargs.ZERO_OR_MORE | Nargs.ONE_OR_MORE:
                    # TODO
                    raise NotImplementedError("nargs values * and + are not supported in _action_type_input")
                case Nargs.PARSER | Nargs.REMAINDER | Nargs.SUPPRESS:
                    raise NotImplementedError(f"nargs value {nargs} are not supported in _action_type_input")
                case int(n):
                    if n == 0:
                        value_element.ValueElement(value=None).mark(self.BASIC_ELEMENT_MARKER)
                    elif n == 1:
                        basic_element()
                    else:
                        raise NotImplementedError("Only nargs 0 or 1 is supported in _action_type_input")
        nargs_wrapper_element.mark(self.NARGS_WRAPPER_MARKER)
        return nargs_wrapper_element

    def _action_type_input_required_wrapper(
        self, nargs_wrapper_element: typing.Callable[[], DisableableElement]
    ) -> ui.element:
        with ui.element() as required_wrapper:
            if self.action.required:
                nargs_wrapper_element()
            else:
                with ui.row():
                    with ui.checkbox() as enable_box:
                        ui.tooltip("Enable")
                    nargs_wrapper_element().bind_enabled(enable_box, "value")
        required_wrapper.mark("ng-action-type-input-required-wrapper")
        return required_wrapper

    def _render(self, value: typing.Any) -> None:
        """Creates a ValueElement that represents the input of a single item matching the type of this action."""

        def basic_element_f():
            return self._action_type_input_basic_element(value)

        def nargs_wrapper_element_f():
            return self._action_type_input_nargs_wrapper(basic_element_f)

        def required_wrapper_element_f():
            return self._action_type_input_required_wrapper(nargs_wrapper_element_f)

        required_wrapper_element = required_wrapper_element_f()

        basic_elements = list(
            ElementFilter(marker=self.BASIC_ELEMENT_MARKER).within(instance=required_wrapper_element)
        )
        assert len(basic_elements) == 1
        basic_element = basic_elements[0]
        assert isinstance(basic_element, value_element.ValueElement)

        nargs_wrapper_element = list(
            ElementFilter(marker=self.NARGS_WRAPPER_MARKER).within(instance=required_wrapper_element)
        )
        assert len(nargs_wrapper_element) == 1
        nargs_wrapper_element = nargs_wrapper_element[0]
        assert isinstance(nargs_wrapper_element, DisableableElement)

        self.basic_element = basic_element
        self.nargs_wrapper_element = nargs_wrapper_element
        self.required_wrapper_element = required_wrapper_element


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

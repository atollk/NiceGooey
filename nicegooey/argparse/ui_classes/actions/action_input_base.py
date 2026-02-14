import argparse
import builtins
import typing

from nicegui import ui, ElementFilter
from nicegui.elements.mixins import value_element, validation_element
from nicegui.elements.mixins.disableable_element import DisableableElement

from nicegooey.argparse.ui_classes.actions.action_info_helper import ActionInfoHelper
from nicegooey.argparse.ui_classes.util import MaxWidthSelect, Nargs


class DisableableValidationElement(validation_element.ValidationElement, DisableableElement):
    pass


class ActionInputBaseElement:
    action: argparse.Action
    parser: argparse.ArgumentParser

    basic_element: value_element.ValueElement
    nargs_wrapper_element: validation_element.ValidationElement
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
    ) -> DisableableValidationElement:
        nargs = ActionInfoHelper(action=self.action, parser=self.parser).action_nargs()
        with DisableableValidationElement(value=None, validation={}) as nargs_wrapper_element:
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

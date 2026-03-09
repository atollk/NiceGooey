import argparse
import builtins
import typing
import warnings

from nicegui import ui, ElementFilter
from nicegui.elements.mixins.value_element import ValueElement
from nicegui.elements.mixins.validation_element import ValidationElement

from nicegooey.argparse.ui_classes.actions.action_info_helper import ActionInfoHelper
from nicegooey.argparse.ui_classes.util import MaxWidthSelect, Nargs, DisableableDiv


class ActionInputBaseElement:
    action: argparse.Action
    parser: argparse.ArgumentParser

    basic_element: ValueElement
    nargs_wrapper_element: ValueElement
    enable_box_element: ui.checkbox | None
    required_wrapper_element: ui.element

    LIST_INNER_ELEMENT_MARKER_SUFFIX: typing.Final[str] = "-inner"
    BASIC_ELEMENT_MARKER: typing.Final[str] = "ng-action-type-input-basic"
    NARGS_WRAPPER_MARKER: typing.Final[str] = "ng-action-type-input-nargs-wrapper"
    ENABLE_PARAMETER_BOX_MARKER: typing.Final[str] = "ng-action-type-input-enable-parameter-box"
    ENABLE_VALUE_BOX_MARKER: typing.Final[str] = "ng-action-type-input-enable-value-box"
    REQUIRED_WRAPPER_MARKER: typing.Final[str] = "ng-action-type-input-required-wrapper"
    ADD_BUTTON_MARKER: typing.Final[str] = "ng-action-add-button"

    def __init__(
        self, action: argparse.Action, parser: argparse.ArgumentParser, init_value: typing.Any = None
    ) -> None:
        self.action = action
        self.parser = parser
        self._render(init_value)

    def _action_type_input_basic_element(self) -> ValueElement:
        """Creates and returns an input element depending on just the type of this action."""
        basic_element: ValueElement
        if self.action.choices is not None:
            choices = list(self.action.choices)
            basic_element = MaxWidthSelect(options=choices)
        else:
            _, action_type = ActionInfoHelper(action=self.action, parser=self.parser).action_type()
            match action_type:
                case builtins.bool:
                    basic_element = ui.checkbox()
                case builtins.int:
                    basic_element = ui.number(format="%d").props("dense")
                case builtins.float:
                    basic_element = ui.number(
                        format="%f",
                    ).props("dense")
                case builtins.str:
                    basic_element = ui.input().props("dense")
                case _:
                    basic_element = ui.input().props("dense")
        basic_element.mark(self.BASIC_ELEMENT_MARKER)
        return basic_element

    def _list_element(
        self,
        inner_element_f: typing.Callable[[], ValueElement],
        on_add_button_click: typing.Callable[[ValueElement, ValueElement, typing.Any], None] | None = None,
    ) -> ValueElement:
        """Creates and returns an element for inputting multiple items of the given inner element."""

        def on_add_button_click_default(
            list_element: ValueElement,
            inner_element: ValueElement,
            inner_element_default_value: typing.Any,
        ) -> None:
            if isinstance(inner_element, ValidationElement):
                if not inner_element.validate():
                    return
            list_element.set_value(list_element.value + [inner_element.value])
            inner_element.set_value(inner_element_default_value)

        with ui.column():
            with ui.row(align_items="center"):
                # Create single-item add element
                inner_element = inner_element_f()
                inner_element_markers = inner_element._markers
                inner_element.mark(
                    *(m + self.LIST_INNER_ELEMENT_MARKER_SUFFIX for m in inner_element_markers)
                )
                if isinstance(inner_element, ValidationElement):
                    inner_element.validation = {"Must enter a value": lambda v: v is not None}
                    inner_element.without_auto_validation()
                    inner_element.error = None
                inner_element_default_value = inner_element.value

                # Create add button
                on_click = (
                    (lambda: on_add_button_click(list_element, inner_element, inner_element_default_value))
                    if on_add_button_click is not None
                    else (
                        lambda: on_add_button_click_default(
                            list_element, inner_element, inner_element_default_value
                        )
                    )
                )
                add_button = (
                    ui.button(on_click=on_click).props("square padding=xs").mark(self.ADD_BUTTON_MARKER)
                )
                add_button.set_icon("south")
            list_element = ui.input_chips(value=[])
            list_element.mark(*inner_element_markers)
        return list_element

    def _action_type_input_nargs_wrapper(
        self, basic_element: typing.Callable[[], ValueElement]
    ) -> ValueElement:
        """Creates and returns an element that wraps the basic element depending on the nargs of this action."""
        nargs = ActionInfoHelper(action=self.action, parser=self.parser).action_nargs()
        nargs_value_element: ValueElement
        match nargs:
            case Nargs.SINGLE_ELEMENT:
                nargs_value_element = basic_element()
            case Nargs.OPTIONAL:
                nargs_value_element = basic_element()
                warnings.warn(
                    "nargs=? is not well supported by nicegooey at the moment and will behave like nargs=None."
                )
                # TODO: this doesn't work and I don't know why :(
                #  nargs_value_element = OptionalValueElement(inner=basic_element)
            case Nargs.ZERO_OR_MORE | Nargs.ONE_OR_MORE:
                nargs_value_element = self._list_element(basic_element)
            case Nargs.PARSER | Nargs.REMAINDER | Nargs.SUPPRESS:
                raise NotImplementedError(f"nargs value {nargs} are not supported in _action_type_input")
            case int(n):
                if n == 0:
                    nargs_value_element = ValueElement(value=None).mark(self.BASIC_ELEMENT_MARKER)
                elif n == 1:
                    nargs_value_element = basic_element()
                else:
                    raise NotImplementedError("Only nargs 0 or 1 is supported in _action_type_input")
            case _:
                raise ValueError(f"Invalid nargs value: {nargs}")
        nargs_value_element.mark(self.NARGS_WRAPPER_MARKER, *nargs_value_element._markers)
        return nargs_value_element

    def _action_type_input_required_wrapper(
        self, nargs_wrapper_element: typing.Callable[[], ValueElement]
    ) -> ui.element:
        """Creates and returns an element that wraps the nargs wrapper element depending on whether this action is required or optional."""
        with ui.element() as required_wrapper:
            if self.action.required:
                nargs_wrapper_element()
            else:
                with ui.row():
                    with ui.checkbox() as enable_box:
                        ui.tooltip("Enable")
                    enable_box.mark(self.ENABLE_PARAMETER_BOX_MARKER)
                    with DisableableDiv() as nargs_wrapper:
                        nargs_wrapper_element()
                    nargs_wrapper.bind_enabled(enable_box, "value")

        required_wrapper.mark(self.REQUIRED_WRAPPER_MARKER)
        return required_wrapper

    def _render(self, value: typing.Any) -> None:
        """Creates a ValueElement that represents the input of a single item matching the type of this action."""

        def basic_element_f():
            return self._action_type_input_basic_element()

        def nargs_wrapper_element_f():
            return self._action_type_input_nargs_wrapper(basic_element_f)

        def required_wrapper_element_f():
            return self._action_type_input_required_wrapper(nargs_wrapper_element_f)

        with ui.element() as outmost:
            required_wrapper_element = required_wrapper_element_f()

        basic_elements = list(ElementFilter(marker=self.BASIC_ELEMENT_MARKER).within(instance=outmost))
        assert len(basic_elements) == 1
        basic_element = basic_elements[0]
        assert isinstance(basic_element, ValueElement)

        nargs_wrapper_element = list(ElementFilter(marker=self.NARGS_WRAPPER_MARKER).within(instance=outmost))
        assert len(nargs_wrapper_element) == 1
        nargs_wrapper_element = nargs_wrapper_element[0]
        assert isinstance(nargs_wrapper_element, ValueElement)

        enable_box_elements = list(
            ElementFilter(marker=self.ENABLE_PARAMETER_BOX_MARKER).within(instance=outmost)
        )
        if len(enable_box_elements) > 0:
            assert len(enable_box_elements) == 1
            enable_box_element = enable_box_elements[0]
            assert isinstance(enable_box_element, ui.checkbox)
        else:
            enable_box_element = None

        nargs_wrapper_element.set_value(value)

        self.basic_element = basic_element
        self.nargs_wrapper_element = nargs_wrapper_element
        self.enable_box_element = enable_box_element
        self.required_wrapper_element = required_wrapper_element

import argparse
import builtins
import dataclasses
import typing
import warnings
from typing import Type, Any

from nicegui import ui, ElementFilter
from nicegui.elements.mixins.value_element import ValueElement
from nicegui.elements.mixins.validation_element import ValidationElement

from nicegooey.argparse.main import main_instance, NiceGooeyNamespace
from nicegooey.argparse.ui_classes.actions.action_info_helper import ActionInfoHelper
from nicegooey.argparse.ui_classes.util import clear_value_element
from nicegooey.argparse.ui_classes.util.disableable_div import DisableableDiv
from nicegooey.argparse.ui_classes.util.max_width_select import MaxWidthSelect
from nicegooey.argparse.ui_classes.util.nargs import Nargs


def _find_exactly_one_element[T](filter: ElementFilter, typ: Type[T]) -> T | None:
    elements = list(filter)
    if not elements:
        return None
    assert len(elements) == 1
    e = elements[0]
    assert isinstance(e, typ)
    return e


class ActionSyncElement:
    """
    A group of UI elements that represent a single value of the argparse namespace.

    Offers functionality to automatically sync the element values to and from the namespace attribute.
    """

    action: argparse.Action
    parser: argparse.ArgumentParser

    @dataclasses.dataclass
    class InnerElements:
        basic_element: ValueElement
        nargs_wrapper_element: ValueElement
        enable_box_element: ui.checkbox | None
        required_wrapper_element: ui.element

    inner_elements: InnerElements | None

    LIST_INNER_ELEMENT_MARKER_SUFFIX: typing.Final[str] = "-inner"
    BASIC_ELEMENT_MARKER: typing.Final[str] = "ng-action-type-input-basic"
    NARGS_WRAPPER_MARKER: typing.Final[str] = "ng-action-type-input-nargs-wrapper"
    ENABLE_PARAMETER_BOX_MARKER: typing.Final[str] = "ng-action-type-input-enable-parameter-box"
    ENABLE_VALUE_BOX_MARKER: typing.Final[str] = "ng-action-type-input-enable-value-box"
    REQUIRED_WRAPPER_MARKER: typing.Final[str] = "ng-action-type-input-required-wrapper"
    ADD_BUTTON_MARKER: typing.Final[str] = "ng-action-add-button"

    def __init__(self, action: argparse.Action, parser: argparse.ArgumentParser):
        self.action = action
        self.parser = parser
        self.inner_elements = None

    @property
    def namespace(self) -> NiceGooeyNamespace:
        return main_instance.namespace

    def sync_from_namespace(self) -> None:
        assert self.inner_elements is not None
        value = getattr(self.namespace, self.action.dest, None)
        self._ui_state_from_value(value)

    def _ui_state_from_value(self, value: Any) -> None:
        if self.inner_elements.enable_box_element is not None:
            self.inner_elements.enable_box_element.value = value is not None

        if value is None:
            clear_value_element(self.inner_elements.nargs_wrapper_element)
        else:
            # TODO: special cases for "default" and "const"
            self.inner_elements.nargs_wrapper_element.value = value

    def sync_to_namespace(self) -> None:
        assert self.inner_elements is not None
        value = self._ui_state_to_value()
        setattr(self.namespace, self.action.dest, value)

    def _ui_state_to_value(self) -> Any:
        is_enabled = (
            self.inner_elements.enable_box_element is None or self.inner_elements.enable_box_element.value
        )
        if not is_enabled:
            value = ActionInfoHelper(action=self.action, parser=self.parser).action_default()
        else:
            value = self.inner_elements.nargs_wrapper_element.value
        return value

    def validate(self) -> bool:
        # TODO implement validation
        return True

    def render(self) -> None:
        """Creates a ValueElement that represents the input of a single item matching the type of this action."""
        assert self.inner_elements is None
        self.inner_elements = self._render_inner_elements()
        # self.inner_elements.nargs_wrapper_element.set_value(value) TODO: needed or not?

        self.inner_elements.basic_element.on_value_change(self.sync_to_namespace)
        self.inner_elements.nargs_wrapper_element.on_value_change(self.sync_to_namespace)
        if self.inner_elements.enable_box_element is not None:
            self.inner_elements.enable_box_element.on_value_change(self.sync_to_namespace)

    def configure(self) -> None:
        """a"""
        assert self.inner_elements is not None
        action_info = ActionInfoHelper(action=self.action, parser=self.parser)

        # Configure validation
        el = self.inner_elements.basic_element
        if isinstance(el, ValidationElement):
            # TODO: clean up
            def _input_element_validate(value: typing.Any) -> str | None:
                """Used by `_create_input_element_generic` as the validation function for the input element. Validates the value by trying to cast it to the action's type by default."""
                if action_info.action_nargs() == Nargs.OPTIONAL and value is None:
                    return "Value is required"
                try:
                    action_info.action_type()[1](value)
                    return None
                except Exception as e:
                    return str(e)

            el.without_auto_validation()
            el.validation = _input_element_validate
            el.error = None

        # Set default value
        if self.inner_elements.enable_box_element is None or self.inner_elements.enable_box_element.value:
            if self.inner_elements.nargs_wrapper_element.value is None:
                self.inner_elements.nargs_wrapper_element.value = action_info.action_default()

        # Bind the namespace value to the element which handles the value.
        self.namespace._nicegooey_state.events[self.action.dest].subscribe(callback=self.sync_from_namespace)

        # Sync the default value to the namespace, unless it was already set by an earlier action.
        if getattr(self.namespace, self.action.dest, None) is None:
            self.sync_to_namespace()
        else:
            self.sync_from_namespace()

    def delete(self) -> None:
        """Undoes any actions performed by this element and resets the namespace fields. Notably, this does not set the namespace field to the action's default but erases it completely."""
        setattr(self.namespace, self.action.dest, None)

    def _render_inner_elements(self) -> InnerElements:
        action_info = ActionInfoHelper(action=self.action, parser=self.parser)

        if self.action.option_strings:
            action_marker = self.action.option_strings[0].lstrip(self.parser.prefix_chars)
        else:
            action_marker = self.action.dest

        with ui.element().mark(f"ng-action-{action_marker}") as outmost:
            required_wrapper_element = self._action_type_input_required_wrapper(
                action_info,
                lambda: self._action_type_input_nargs_wrapper(
                    action_info, lambda: self._action_type_input_basic_element(action_info)
                ),
            )

        basic_element = _find_exactly_one_element(
            ElementFilter(marker=self.BASIC_ELEMENT_MARKER).within(instance=outmost), ValueElement
        )
        assert basic_element is not None
        nargs_wrapper_element = _find_exactly_one_element(
            ElementFilter(marker=self.NARGS_WRAPPER_MARKER).within(instance=outmost), ValueElement
        )
        assert nargs_wrapper_element is not None
        enable_box_element = _find_exactly_one_element(
            ElementFilter(marker=self.ENABLE_PARAMETER_BOX_MARKER).within(instance=outmost), ui.checkbox
        )

        return self.InnerElements(
            basic_element=basic_element,
            nargs_wrapper_element=nargs_wrapper_element,
            enable_box_element=enable_box_element,
            required_wrapper_element=required_wrapper_element,
        )

    @classmethod
    def _action_type_input_basic_element(cls, action_info: ActionInfoHelper) -> ValueElement:
        """Creates and returns an input element depending on just the type of this action."""
        basic_element: ValueElement
        if action_info.action.choices is not None:
            choices = list(action_info.action.choices)
            basic_element = MaxWidthSelect(options=choices, value=action_info.action.const or choices[0])
        else:
            _, action_type = action_info.action_type()
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
        basic_element.mark(cls.BASIC_ELEMENT_MARKER)
        return basic_element

    @classmethod
    def _list_element(
        cls,
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
                inner_element.mark(*(m + cls.LIST_INNER_ELEMENT_MARKER_SUFFIX for m in inner_element_markers))
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
                    ui.button(on_click=on_click).props("square padding=xs").mark(cls.ADD_BUTTON_MARKER)
                )
                add_button.set_icon("south")
            list_element = ui.input_chips(value=[])
            list_element.mark(*inner_element_markers)
        return list_element

    @classmethod
    def _action_type_input_nargs_wrapper(
        cls, action_info: ActionInfoHelper, basic_element: typing.Callable[[], ValueElement]
    ) -> ValueElement:
        """Creates and returns an element that wraps the basic element depending on the nargs of this action."""
        nargs = action_info.action_nargs()
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
                nargs_value_element = cls._list_element(basic_element)
            case Nargs.PARSER | Nargs.REMAINDER | Nargs.SUPPRESS:
                raise NotImplementedError(f"nargs value {nargs} are not supported in _action_type_input")
            case int(n):
                if n == 0:
                    nargs_value_element = ValueElement(value=None).mark(cls.BASIC_ELEMENT_MARKER)
                elif n == 1:
                    nargs_value_element = basic_element()
                else:
                    raise NotImplementedError("Only nargs 0 or 1 is supported in _action_type_input")
            case _:
                raise ValueError(f"Invalid nargs value: {nargs}")
        nargs_value_element.mark(cls.NARGS_WRAPPER_MARKER, *nargs_value_element._markers)
        return nargs_value_element

    @classmethod
    def _action_type_input_required_wrapper(
        cls, action_info: ActionInfoHelper, nargs_wrapper_element: typing.Callable[[], ValueElement]
    ) -> ui.element:
        """Creates and returns an element that wraps the nargs wrapper element depending on whether this action is required or optional."""
        with ui.element() as required_wrapper:
            if action_info.action.required:
                nargs_wrapper_element()
            else:
                with ui.row():
                    with ui.checkbox() as enable_box:
                        ui.tooltip("Enable")
                    enable_box.mark(cls.ENABLE_PARAMETER_BOX_MARKER)
                    with DisableableDiv() as nargs_wrapper:
                        nargs_wrapper_element()
                    nargs_wrapper.bind_enabled(enable_box, "value")

        required_wrapper.mark(cls.REQUIRED_WRAPPER_MARKER)
        return required_wrapper

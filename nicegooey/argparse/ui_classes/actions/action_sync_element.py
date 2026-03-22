import argparse
import builtins
import dataclasses
from typing import Any, Callable, Final, Type, override

from nicegui import ElementFilter, ui
from nicegui.elements.mixins.validation_element import ValidationElement
from nicegui.elements.mixins.value_element import ValueElement

from nicegooey.argparse.main import NiceGooeyNamespace, main_instance
from nicegooey.argparse.ui_classes.actions.action_info_helper import ActionInfoHelper
from nicegooey.argparse.ui_classes.util.disableable_div import DisableableDiv
from nicegooey.argparse.ui_classes.util.grouping_sync_ui import UiWrapperSyncElement
from nicegooey.argparse.ui_classes.util.max_width_select import MaxWidthSelect
from nicegooey.argparse.ui_classes.util.misc import Nargs, add_validation, clear_value_element
from nicegooey.argparse.ui_classes.util.optional_value_element import OptionalValidationElement
from nicegooey.argparse.ui_classes.util.sync_element import SyncElement
from nicegooey.argparse.ui_classes.util.validation_checkbox import ValidationCheckbox


def _find_exactly_one_element[T](filter: ElementFilter, typ: Type[T]) -> T | None:
    elements = list(filter)
    if not elements:
        return None
    assert len(elements) == 1
    e = elements[0]
    assert isinstance(e, typ)
    return e


class ActionSyncElement(SyncElement, UiWrapperSyncElement):
    """
    A group of UI elements that represent a single value of the argparse namespace.

    Offers functionality to automatically sync the element values to and from the namespace attribute.
    """

    action: argparse.Action
    parser: argparse.ArgumentParser

    @dataclasses.dataclass
    class InnerElements:
        basic_element: ValueElement
        basic_element_inner: ValueElement | None
        nargs_wrapper_element: ValueElement
        enable_box_element: ui.checkbox | None
        required_wrapper_element: ui.element

    inner_elements: InnerElements | None

    LIST_INNER_ELEMENT_MARKER_SUFFIX: Final[str] = "-inner"
    BASIC_ELEMENT_MARKER: Final[str] = "ng-action-type-input-basic"
    NARGS_WRAPPER_MARKER: Final[str] = "ng-action-type-input-nargs-wrapper"
    ENABLE_PARAMETER_BOX_MARKER: Final[str] = "ng-action-type-input-enable-parameter-box"
    REQUIRED_WRAPPER_MARKER: Final[str] = "ng-action-type-input-required-wrapper"
    ADD_BUTTON_MARKER: Final[str] = "ng-action-add-button"

    def __init__(self, action: argparse.Action, parser: argparse.ArgumentParser):
        super().__init__()
        self.action = action
        self.parser = parser
        self.inner_elements = None

    @property
    def action_info(self) -> ActionInfoHelper:
        return ActionInfoHelper(action=self.action, parser=self.parser)

    @property
    @override
    def namespace(self) -> NiceGooeyNamespace:
        return main_instance.namespace

    @property
    @override
    def dest(self) -> str:
        return self.action.dest

    @override
    def _ui_state_from_value(self, value: Any) -> None:
        assert self.inner_elements is not None

        # Evaluate whether the element should be disabled or enabled (if non-required).
        typ = self.action_info.action_type()[1]
        try:
            typ(value)
        except Exception:
            value_is_valid = False
        else:
            value_is_valid = True
        disable = value is None or not value_is_valid or value == self.action_info.action_default()

        # Set the values of the UI elements.
        if self.inner_elements.enable_box_element is not None:
            self.inner_elements.enable_box_element.value = not disable
        if value_is_valid and value is not None:
            self.inner_elements.nargs_wrapper_element.value = value
        else:
            clear_value_element(self.inner_elements.nargs_wrapper_element)

    @override
    def _ui_state_to_value(self) -> Any:
        assert self.inner_elements is not None

        if not self.is_enabled():
            value = self.action_info.action_default()
        else:
            value = self.inner_elements.nargs_wrapper_element.value
        return value

    def validate(self) -> bool:
        if not self.is_enabled():
            return True
        for el in [
            self.inner_elements.basic_element,
            self.inner_elements.nargs_wrapper_element,
            self.inner_elements.basic_element_inner,
            self.inner_elements.required_wrapper_element,
        ]:
            if isinstance(el, ValidationElement):
                if not el.validate():
                    return False
        return True

    def is_enabled(self) -> bool:
        if self.inner_elements is None:
            return False
        if self.inner_elements.enable_box_element is None:
            return True
        return self.inner_elements.enable_box_element.value

    def render(self) -> None:
        """Creates a ValueElement that represents the input of a single item matching the type of this action."""
        assert self.inner_elements is None
        self.inner_elements = self._render_inner_elements()

        action_info = self.action_info

        # Configure validation
        el = self.inner_elements.basic_element
        if isinstance(el, ValidationElement):

            def _input_element_validate(value: Any) -> str | None:
                """Used by `_create_input_element_generic` as the validation function for the input element. Validates the value by trying to cast it to the action's type by default."""
                if action_info.action_nargs() == Nargs.OPTIONAL and value is None:
                    return "Value is required"
                try:
                    action_info.action_type_with_nargs()(value)
                    return None
                except Exception as e:
                    return str(e)

            el.without_auto_validation()
            add_validation(el, _input_element_validate)

        # Set default values
        self.inner_elements.nargs_wrapper_element.value = (
            action_info.action_const()
            if action_info.action_nargs() == Nargs.OPTIONAL
            else action_info.action_default()
        )
        if self.action.choices:
            el = self.inner_elements.basic_element
            if not isinstance(el, ui.select):
                el = self.inner_elements.basic_element_inner
            assert isinstance(el, ui.select)
            el.value = action_info.action.const or next(iter(el.options))

        # Bind the namespace value to the element which handles the value.
        self.subscribe()

        # Sync the default value to the namespace, unless it was already set by an earlier action.
        if getattr(self.namespace, self.action.dest, None) is None:
            self.sync_to_namespace()
        else:
            self.sync_from_namespace()

        # Subscribe to propagate future changes from the elements to the namespace.
        self.inner_elements.basic_element.on_value_change(lambda ev: self.sync_to_namespace())
        self.inner_elements.nargs_wrapper_element.on_value_change(lambda ev: self.sync_to_namespace())
        if self.inner_elements.enable_box_element is not None:
            self.inner_elements.enable_box_element.on_value_change(lambda ev: self.sync_to_namespace())

    def deactivate(self) -> None:
        """Undoes any actions performed by this element and resets the namespace fields. Notably, this does not set the namespace field to the action's default but erases it completely."""
        setattr(self.namespace, self.action.dest, None)

    def _render_inner_elements(self) -> InnerElements:
        action_info = self.action_info

        if self.action.option_strings:
            action_marker = max(self.action.option_strings, key=len).lstrip(self.parser.prefix_chars)
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
        basic_element_inner = _find_exactly_one_element(
            ElementFilter(marker=self.BASIC_ELEMENT_MARKER + self.LIST_INNER_ELEMENT_MARKER_SUFFIX).within(
                instance=outmost
            ),
            ValueElement,
        )
        nargs_wrapper_element = _find_exactly_one_element(
            ElementFilter(marker=self.NARGS_WRAPPER_MARKER).within(instance=outmost), ValueElement
        )
        assert nargs_wrapper_element is not None
        enable_box_element = _find_exactly_one_element(
            ElementFilter(marker=self.ENABLE_PARAMETER_BOX_MARKER).within(instance=outmost), ui.checkbox
        )

        return self.InnerElements(
            basic_element=basic_element,
            basic_element_inner=basic_element_inner,
            nargs_wrapper_element=nargs_wrapper_element,
            enable_box_element=enable_box_element,
            required_wrapper_element=required_wrapper_element,
        )

    @classmethod
    def _action_type_input_basic_element(cls, action_info: ActionInfoHelper) -> ValidationElement:
        """Creates and returns an input element depending on just the type of this action."""
        basic_element: ValidationElement
        if action_info.action.choices is not None:
            choices = list(action_info.action.choices)
            basic_element = MaxWidthSelect(options=choices)
        else:
            _, action_type = action_info.action_type()
            match action_type:
                case builtins.bool:
                    basic_element = ValidationCheckbox()
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
        inner_element_f: Callable[[], ValueElement],
        on_add_button_click: Callable[[ValueElement, ValueElement, Any], None] | None = None,
    ) -> ValidationElement:
        """Creates and returns an element for inputting multiple items of the given inner element."""

        def on_add_button_click_default(
            list_element: ValueElement,
            inner_element: ValueElement,
            inner_element_default_value: Any,
        ) -> None:
            if isinstance(inner_element, ValidationElement):
                if not inner_element.validate():
                    return
            # sometimes, list_element.value is "" here and I couldn't find out why, so I just did a defensive `or []`
            list_element.set_value((list_element.value or []) + [inner_element.value])
            inner_element.set_value(inner_element_default_value)

        with ui.column():
            with ui.row(align_items="center"):
                # Create single-item add element
                inner_element = inner_element_f()
                inner_element_markers = inner_element._markers
                inner_element.mark(*(m + cls.LIST_INNER_ELEMENT_MARKER_SUFFIX for m in inner_element_markers))
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
        cls, action_info: ActionInfoHelper, basic_element: Callable[[], ValidationElement]
    ) -> ValidationElement:
        """Creates and returns an element that wraps the basic element depending on the nargs of this action."""
        nargs = action_info.action_nargs()
        nargs_value_element: ValidationElement
        match nargs:
            case Nargs.SINGLE_ELEMENT:
                nargs_value_element = basic_element()
            case Nargs.OPTIONAL:
                nargs_value_element = OptionalValidationElement(
                    inner=basic_element, none_value=action_info.action_const()
                )
            case Nargs.ZERO_OR_MORE:
                nargs_value_element = cls._list_element(basic_element)
            case Nargs.ONE_OR_MORE:
                nargs_value_element = cls._list_element(basic_element)
                nargs_value_element.without_auto_validation()
                add_validation(
                    nargs_value_element,
                    {"Must enter at least one value": lambda v: isinstance(v, list) and len(v) > 0},
                )
            case Nargs.PARSER | Nargs.REMAINDER | Nargs.SUPPRESS:
                raise NotImplementedError(f"nargs value {nargs} are not supported in _action_type_input")
            case int(n):
                if n == 0:
                    nargs_value_element = ValidationElement(validation=None, value=None, tag="q-field").mark(
                        cls.BASIC_ELEMENT_MARKER
                    )
                else:
                    nargs_value_element = cls._list_element(basic_element)
                    nargs_value_element.without_auto_validation()
                    add_validation(
                        nargs_value_element,
                        {f"Must enter exactly {n} values": lambda v: isinstance(v, list) and len(v) == n},
                    )
            case _:
                raise ValueError(f"Invalid nargs value: {nargs}")

        nargs_value_element.mark(cls.NARGS_WRAPPER_MARKER, *nargs_value_element._markers)
        return nargs_value_element

    @classmethod
    def _action_type_input_required_wrapper(
        cls, action_info: ActionInfoHelper, nargs_wrapper_element: Callable[[], ValueElement]
    ) -> ui.element:
        """Creates and returns an element that wraps the nargs wrapper element depending on whether this action is required or optional."""
        with ui.element() as required_wrapper:
            # Unlike the vanilla argparse, we consider positional arguments to be required in all cases.
            is_required = action_info.action.required or len(action_info.action.option_strings) == 0
            if is_required:
                nargs_wrapper_element()
            else:
                with ui.row():
                    with ui.checkbox(value=False) as enable_box:
                        ui.tooltip("Enable")
                    enable_box.mark(cls.ENABLE_PARAMETER_BOX_MARKER)
                    with DisableableDiv() as nargs_wrapper:
                        nargs_wrapper_element()
                    nargs_wrapper.bind_enabled_from(enable_box, "value")

        required_wrapper.mark(cls.REQUIRED_WRAPPER_MARKER)
        return required_wrapper

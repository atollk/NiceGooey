import abc
import argparse
import builtins
import dataclasses
from typing import override, Final, Callable, Any, cast

from nicegui import ui, ElementFilter
from nicegui.elements.mixins.validation_element import ValidationElement
from nicegui.elements.mixins.value_element import ValueElement

from ..util.disableable_div import DisableableDiv
from ..util.grouping_sync_ui import UiWrapperSyncElement
from ..util.max_width_select import MaxWidthSelect
from ..util.misc import Nargs, add_validation, q_field, clear_value_element
from ..util.optional_value_element import OptionalValidationElement
from ..util.sync_element import SyncElement
from ..util.ui_wrapper import UiWrapper
from ..util.validation_checkbox import ValidationCheckbox
from ...main import NiceGooeyMain, NiceGooeyNamespace, main_instance
from .action_info_helper import ActionInfoHelper


class ActionUiElement[ActionT: argparse.Action](UiWrapper, SyncElement, UiWrapperSyncElement, abc.ABC):
    """
    A group of UI elements representing one single action of the argument parser.
    """

    action: ActionT

    @dataclasses.dataclass
    class InnerElements:
        basic_element: ValidationElement
        basic_element_inner: ValidationElement | None
        nargs_wrapper_element: ValidationElement
        enable_box_element: ValueElement | None
        required_wrapper_element: ValidationElement
        outmost: ui.element

    inner_elements: InnerElements | None

    LIST_INNER_ELEMENT_MARKER_SUFFIX: Final[str] = "-inner"
    BASIC_ELEMENT_MARKER: Final[str] = "ng-action-element-basic"
    NARGS_WRAPPER_MARKER: Final[str] = "ng-action-element-nargs"
    ENABLE_PARAMETER_BOX_MARKER: Final[str] = "ng-action-element-parameter-box"
    REQUIRED_WRAPPER_MARKER: Final[str] = "ng-action-element-required"
    ADD_BUTTON_MARKER: Final[str] = "ng-action-add-button"

    @staticmethod
    def from_action(parent: NiceGooeyMain, action: argparse.Action) -> "ActionUiElement | None":
        from .standard_actions import (
            AppendActionUiElement,
            AppendConstActionUiElement,
            CountActionUiElement,
            ExtendActionUiElement,
            StoreActionUiElement,
            StoreConstActionUiElement,
        )

        assert parent.parent_parser is not None
        action_config = ActionInfoHelper(action=action, parser=parent.parent_parser).ng_config()
        if (override := action_config.element_override) is not None:
            return override(parent=parent, action=action)

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
        UiWrapper.__init__(self, parent)
        SyncElement.__init__(self)
        self.action = action
        self.inner_elements = None

    @property
    def _parser(self) -> argparse.ArgumentParser:
        assert self.parent.parent_parser is not None
        return self.parent.parent_parser

    @property
    def _action_info(self) -> ActionInfoHelper:
        return ActionInfoHelper(self.action, self._parser)

    @property
    @override
    def namespace(self) -> NiceGooeyNamespace:
        return main_instance.namespace

    @property
    @override
    def dest(self) -> str:
        return self.action.dest

    @override
    def render(self) -> ui.element:
        c = ui.column()
        with c:
            self._render_action_name()
            self._render_input_element()
        return c

    def _render_action_name(self):
        """Renders the name of this action (i.e. the metavar or dest) and a tooltip with the help text if it exists."""
        with ui.row(align_items="center"):
            if isinstance(self.action.metavar, str):
                name = self.action.metavar
            elif isinstance(self.action.metavar, tuple):
                name = self.action.metavar[0]
            elif self.action.option_strings:
                assert self._parser is not None
                name = max(self.action.option_strings, key=len).lstrip(self._parser.prefix_chars)
            else:
                name = self.action.dest
            ui.label(name).classes("font-bold")
            if self.action.help:
                with ui.button(icon="question_mark") as btn:
                    # Styling
                    btn.props("round padding=xs size=xs")
                    # Non-focusable with keyboard
                    btn.props("tabindex='-1'")
                    # Tooltip on hover
                    ui.tooltip(self.action.help)

    def _render_input_element(self) -> None:
        """Creates a ValueElement that represents the input of a single item matching the type of this action."""
        assert self.inner_elements is None
        self._render_inner_elements()
        assert self.inner_elements is not None

        action_info = self._action_info

        # Configure validation
        def _input_element_validate(value: Any) -> str | None:
            """Used by `_create_input_element_generic` as the validation function for the input element. Validates the value by trying to cast it to the action's type by default."""
            if action_info.nargs() == Nargs.OPTIONAL and value is None:
                return "Value is required"
            try:
                action_info.type_with_nargs()(value)
                return None
            except Exception as e:
                return str(e)

        el = self.inner_elements.basic_element
        el.without_auto_validation()
        add_validation(el, _input_element_validate)

        # Set default values
        self.inner_elements.nargs_wrapper_element.value = (
            action_info.const() if action_info.nargs() == Nargs.OPTIONAL else action_info.default()
        )
        if self.action.choices:
            el = self.inner_elements.basic_element_inner or self.inner_elements.basic_element
            assert hasattr(el, "options")
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

    @override
    def _ui_state_from_value(self, value: Any) -> None:
        assert self.inner_elements is not None

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
            self.inner_elements.nargs_wrapper_element.value = value
        else:
            clear_value_element(self.inner_elements.nargs_wrapper_element)

    @override
    def _ui_state_to_value(self) -> Any:
        assert self.inner_elements is not None

        if not self.is_enabled():
            value = self._action_info.default()
        else:
            value = self.inner_elements.nargs_wrapper_element.value
        return value

    def validate(self) -> bool:
        # If the element is disabled, it's always valid.
        if not self.is_enabled():
            return True

        # Otherwise, check every sub-element for validation.
        assert self.inner_elements is not None
        for el in [
            self.inner_elements.basic_element,
            self.inner_elements.nargs_wrapper_element,
            self.inner_elements.basic_element_inner,
            self.inner_elements.required_wrapper_element,
        ]:
            if el is not None and not el.validate():
                return False

        # Check custom user logic, if any.
        custom_validation = self._action_info.ng_config().validation
        if err := custom_validation(self._ui_state_to_value()):
            self.inner_elements.required_wrapper_element.error = err
            return False

        # Validation passed
        return True

    def is_enabled(self) -> bool:
        if self.inner_elements is None:
            return False
        if self.inner_elements.enable_box_element is None:
            return True
        return cast(bool, self.inner_elements.enable_box_element.value)

    def deactivate(self) -> None:
        """Undoes any actions performed by this element and resets the namespace fields. Notably, this does not set the namespace field to the action's default but erases it completely."""
        setattr(self.namespace, self.action.dest, None)

    def _render_inner_elements(self) -> None:
        """Renders all inner elements by calling the respective class functions, and sets the result to self.inner_elements."""
        action_info = self._action_info

        if self.action.option_strings:
            action_marker = max(self.action.option_strings, key=len).lstrip(self._parser.prefix_chars)
        else:
            action_marker = self.action.dest

        with ui.element().mark(f"ng-action-{action_marker}") as outmost:
            required_wrapper_element = self._render_action_required(
                action_info,
                lambda: self._render_action_nargs(
                    action_info, lambda: self._render_action_single(action_info)
                ),
            )

        basic_element = find_exactly_one_element(
            ElementFilter(marker=self.BASIC_ELEMENT_MARKER, kind=ValidationElement).within(instance=outmost)
        )
        assert basic_element is not None
        basic_element_inner = find_exactly_one_element(
            ElementFilter(
                marker=self.BASIC_ELEMENT_MARKER + self.LIST_INNER_ELEMENT_MARKER_SUFFIX,
                kind=ValidationElement,
            ).within(instance=outmost),
        )
        nargs_wrapper_element = find_exactly_one_element(
            ElementFilter(marker=self.NARGS_WRAPPER_MARKER, kind=ValidationElement).within(instance=outmost)
        )
        assert nargs_wrapper_element is not None
        enable_box_element = find_exactly_one_element(
            ElementFilter(marker=self.ENABLE_PARAMETER_BOX_MARKER, kind=ValueElement).within(instance=outmost)
        )

        self.inner_elements = self.InnerElements(
            basic_element=basic_element,
            basic_element_inner=basic_element_inner,
            nargs_wrapper_element=nargs_wrapper_element,
            enable_box_element=enable_box_element,
            required_wrapper_element=required_wrapper_element,
            outmost=outmost,
        )

    @classmethod
    def _render_action_single(cls, action_info: ActionInfoHelper) -> ValidationElement:
        """Creates and returns an input element depending on just the type of this action, ignoring 'required' and 'nargs'."""
        basic_element: ValidationElement
        if action_info.action.choices is not None:
            choices = list(action_info.action.choices)
            basic_element = MaxWidthSelect(options=choices)
        else:
            action_type = action_info.type()
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
    def _render_action_list[T: ValidationElement](
        cls,
        inner_element_f: Callable[[], T],
        on_add_button_click: Callable[[ui.input_chips, T, Any], None] | None = None,
    ) -> tuple[ui.input_chips, T, ui.button]:
        """
        Creates and returns an element for inputting multiple items of the given inner element.
        Returns a tuple of (outer list element, inner input element, add button).
        Notably, does not add any markers to the new elements - this has to be done outside of this function, if desired.
        """

        def on_add_button_click_default(
            list_element: ui.input_chips,
            inner_element: T,
            inner_element_default_value: Any,
        ) -> None:
            if not inner_element.validate():
                return
            # sometimes, list_element.value is "" here and I couldn't find out why, so I just did a defensive `or []`
            list_element.set_value((list_element.value or []) + [inner_element.value])
            inner_element.set_value(inner_element_default_value)

        with ui.column():
            with ui.row(align_items="center"):
                # Create single-item add element
                inner_element = inner_element_f()
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
                add_button = ui.button(on_click=on_click).props("square padding=xs")
                add_button.set_icon("south")
            list_element = ui.input_chips(value=[]).props("use-input=false")
        return list_element, inner_element, add_button

    @classmethod
    def _render_action_nargs(
        cls, action_info: ActionInfoHelper, basic_element: Callable[[], ValidationElement]
    ) -> ValidationElement:
        """Creates and returns an element that wraps the basic element depending on the nargs of this action."""
        nargs = action_info.nargs()
        nargs_value_element: ValidationElement
        inner_element = list_add_button = None
        match nargs:
            case Nargs.SINGLE_ELEMENT:
                nargs_value_element = basic_element()
            case Nargs.OPTIONAL:
                nargs_value_element = OptionalValidationElement(
                    inner=basic_element, none_value=action_info.const()
                )
            case Nargs.ZERO_OR_MORE:
                nargs_value_element, inner_element, list_add_button = cls._render_action_list(basic_element)
            case Nargs.ONE_OR_MORE:
                nargs_value_element, inner_element, list_add_button = cls._render_action_list(basic_element)
                nargs_value_element.without_auto_validation()
                add_validation(
                    nargs_value_element,
                    {"Must enter at least one value": lambda v: isinstance(v, list) and len(v) > 0},
                )
            case Nargs.PARSER | Nargs.REMAINDER | Nargs.SUPPRESS:
                raise NotImplementedError(f"nargs value {nargs} are not supported in _action_type_input")
            case int(n):
                if n == 0:
                    nargs_value_element = q_field().mark(cls.BASIC_ELEMENT_MARKER)
                else:
                    nargs_value_element, inner_element, list_add_button = cls._render_action_list(
                        basic_element
                    )
                    nargs_value_element.without_auto_validation()
                    add_validation(
                        nargs_value_element,
                        {f"Must enter exactly {n} values": lambda v: isinstance(v, list) and len(v) == n},
                    )
            case _:
                raise ValueError(f"Invalid nargs value: {nargs}")

        nargs_value_element.mark(cls.NARGS_WRAPPER_MARKER, *nargs_value_element._markers)
        if inner_element is not None and list_add_button is not None:
            inner_element_markers = inner_element._markers
            inner_element.mark(*(m + cls.LIST_INNER_ELEMENT_MARKER_SUFFIX for m in inner_element_markers))
            nargs_value_element.mark(
                cls.NARGS_WRAPPER_MARKER, *inner_element_markers, *nargs_value_element._markers
            )
            list_add_button.mark(cls.ADD_BUTTON_MARKER)
        else:
            nargs_value_element.mark(cls.NARGS_WRAPPER_MARKER, *nargs_value_element._markers)
        return nargs_value_element

    @classmethod
    def _render_action_required(
        cls, action_info: ActionInfoHelper, nargs_wrapper_element: Callable[[], ValidationElement]
    ) -> ValidationElement:
        """Creates and returns an element that wraps the nargs wrapper element depending on whether this action is required or optional."""
        with q_field() as required_wrapper:
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


def find_exactly_one_element[T: ui.element](filter: ElementFilter[T]) -> T | None:
    elements = list(filter)
    if not elements:
        return None
    assert len(elements) == 1
    return elements[0]

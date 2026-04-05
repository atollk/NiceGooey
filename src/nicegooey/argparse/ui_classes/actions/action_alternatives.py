"""A bunch of default implementations for action UI elements that can be used to override the default in certain cases."""

import os
from typing import Type, override, Callable

from nicegui import ui
from nicegui.elements.mixins.validation_element import ValidationElement

from nicegooey.argparse.ui_classes.actions.action_info_helper import ActionInfoHelper
from nicegooey.argparse.ui_classes.actions.standard_actions import (
    StoreActionUiElement,
    StoreConstActionUiElement,
)
from nicegooey.argparse.ui_classes.util.misc import q_field
from nicegooey.ui_util.disableable_div import DisableableDiv
from nicegooey.ui_util.local_file_picker import LocalFilePicker
from nicegooey.ui_util.validation_wrapper import ValidationWrapper
from nicegooey.ui_util.value_text_element import ValueLabel


def store_action_slider(min: float, max: float, step: float = 1) -> Type[StoreActionUiElement]:
    """Displays a numeric 'store' action with a slider element instead of the default number input."""

    class StoreActionSliderElement(StoreActionUiElement):
        @override
        @classmethod
        def _render_action_single(cls, action_info: ActionInfoHelper) -> ValidationElement:
            def slider():
                return (
                    ui.slider(min=min, max=max, step=step)
                    .classes("w-sm")
                    .props("label label-always markers snap")
                )

            basic_element = ValidationWrapper(validation={}, value_element=slider).classes("mt-4 -mb-10")
            basic_element.mark(cls.BASIC_ELEMENT_MARKER)
            return basic_element

    return StoreActionSliderElement


def store_action_radio() -> Type[StoreActionUiElement]:
    """Displays a 'store' action with choices with a radio element instead of the default select."""

    class StoreActionRadioElement(StoreActionUiElement):
        @override
        @classmethod
        def _render_action_single(cls, action_info: ActionInfoHelper) -> ValidationElement:
            options = list(action_info.action.choices or [])
            if not options:
                raise ValueError(
                    "store_action_radio can only be used when 'choices' are specified on the action."
                )
            basic_element = ValidationWrapper(
                validation={}, value_element=lambda: ui.radio(options=list(action_info.action.choices or []))
            )
            basic_element.mark(cls.BASIC_ELEMENT_MARKER)
            return basic_element

    return StoreActionRadioElement


def store_const_action_toggle() -> Type[StoreConstActionUiElement]:
    """Displays an optional 'store_const' action with a toggle element instead of the default checkbox."""

    class StoreActionToggleElement(StoreConstActionUiElement):
        @override
        @classmethod
        def _render_action_required(
            cls, action_info: ActionInfoHelper, nargs_wrapper_element: Callable[[], ValidationElement]
        ) -> ValidationElement:
            with q_field() as required_wrapper:
                # Unlike the vanilla argparse, we consider positional arguments to be required in all cases.
                is_required = action_info.action.required or len(action_info.action.option_strings) == 0
                if is_required:
                    nargs_wrapper_element()
                else:
                    with ui.row():
                        enable_box = ui.switch(value=False, text="Enable")
                        enable_box.mark(cls.ENABLE_PARAMETER_BOX_MARKER)
                        with DisableableDiv() as nargs_wrapper:
                            nargs_wrapper_element()
                        nargs_wrapper.bind_enabled_from(enable_box, "value")

            required_wrapper.mark(cls.REQUIRED_WRAPPER_MARKER)
            return required_wrapper

    return StoreActionToggleElement


def store_action_file() -> Type[StoreActionUiElement]:
    """Displays a string 'store' action with a file picker widget instead of a free text input."""

    class StoreActionFileElement(StoreActionUiElement):
        @override
        @classmethod
        def _render_action_single(cls, action_info: ActionInfoHelper) -> ValidationElement:
            async def pick_file():
                picker_dialog = LocalFilePicker(os.getcwd(), multiple=False)
                if result := await picker_dialog:
                    basic_element.value = result[0]

            with ui.row().classes("items-center"):
                ui.button("Browse files", on_click=pick_file, icon="folder_open")

            basic_element = ValidationWrapper(validation={}, value_element=lambda: ValueLabel(""))
            basic_element.mark(cls.BASIC_ELEMENT_MARKER)
            return basic_element

    return StoreActionFileElement

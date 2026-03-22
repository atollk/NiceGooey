"""A bunch of default implementations for action UI elements that can be used to override the default in certain cases."""

from typing import Type

from nicegui import ui
from nicegui.elements.mixins.validation_element import ValidationElement

from nicegooey.argparse.ui_classes.actions.action_info_helper import ActionInfoHelper
from nicegooey.argparse.ui_classes.actions.action_ui_element import ActionUiElement
from nicegooey.argparse.ui_classes.actions.standard_actions import StoreActionUiElement
from nicegooey.argparse.ui_classes.util.validation_wrapper import ValidationWrapper


def store_action_slider_element(min: float, max: float, step: float) -> Type[ActionUiElement]:
    class StoreActionSliderElement(StoreActionUiElement):
        @classmethod
        def _action_type_input_basic_element(cls, action_info: ActionInfoHelper) -> ValidationElement:
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

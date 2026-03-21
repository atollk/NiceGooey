from nicegui import ui
from nicegui.defaults import DEFAULT_PROPS
from nicegui.elements.mixins.validation_element import ValidationElement
from nicegui.events import Handler, ValueChangeEventArguments
from typing_extensions import override


class ValidationCheckbox(ui.checkbox, ValidationElement):
    @override
    def __init__(
        self,
        text: str = "",
        *,
        value: bool | None = DEFAULT_PROPS["model-value"] | False,
        on_change: Handler[ValueChangeEventArguments] | None = None,
    ) -> None:
        super().__init__(text, value=value, on_change=on_change)

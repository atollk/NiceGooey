from nicegui import ui
from nicegui.defaults import DEFAULT_PROPS
from nicegui.elements.mixins.validation_element import ValidationElement
from nicegui.events import Handler, ValueChangeEventArguments


class ValidationCheckbox(ValidationElement, ui.checkbox):
    # No @override because the constructor does not match ValidationElement
    def __init__(
        self,
        text: str = "",
        *,
        value: bool | None = DEFAULT_PROPS["model-value"] | False,
        on_change: Handler[ValueChangeEventArguments] | None = None,
    ) -> None:
        super().__init__(text=text, value=value, on_change=on_change, validation={})

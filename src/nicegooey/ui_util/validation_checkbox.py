from nicegui import ui
from nicegui.defaults import DEFAULT_PROPS
from nicegui.elements.mixins.validation_element import ValidationElement
from nicegui.events import Handler, ValueChangeEventArguments
from typing_extensions import override


# required because of https://github.com/zauberzeug/nicegui/issues/5947
class _ValidationElementWithDefault(ValidationElement):
    def __init__(self, validation=None, **kwargs) -> None:
        super().__init__(validation=validation if validation is not None else {}, **kwargs)


class ValidationCheckbox(ui.checkbox, _ValidationElementWithDefault):
    @override
    def __init__(
        self,
        text: str = "",
        *,
        value: bool | None = DEFAULT_PROPS["model-value"] | False,
        on_change: Handler[ValueChangeEventArguments] | None = None,
    ) -> None:
        super().__init__(text=text, value=value, on_change=on_change)

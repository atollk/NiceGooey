from typing import Any, cast

from nicegui import ui
from nicegui.elements.mixins.text_element import TextElement
from nicegui.elements.mixins.value_element import ValueElement


class ValueTextElement(ValueElement, TextElement):
    """A wrapper of TextElement which exposes the text field as a ValueElement value field."""

    def __init__(self, text: Any):
        ValueElement.__init__(self, value=text)
        TextElement.__init__(self, text=text)

    @property
    def value(self) -> str:  # pyrefly: ignore[bad-override]
        return cast(str, self.text)

    @value.setter
    def value(self, value: str) -> None:
        self.text = value


class ValueLabel(ValueTextElement, ui.label):
    pass

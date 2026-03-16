from nicegui.elements.mixins.value_element import ValueElement
from nicegui import ui
from typing import Any, Callable, Self

from nicegui.events import Handler, ValueChangeEventArguments

from nicegooey.argparse.ui_classes.util import clear_value_element
from nicegooey.argparse.ui_classes.util.disableable_div import DisableableDiv


class OptionalValueElement(ValueElement):
    """An element that can either have a value of a certain type or be None, with a checkbox to toggle between the two states."""

    none_value: Any
    inner_element: ValueElement
    checkbox: ui.checkbox

    def __init__(self, *, inner: Callable[[], ValueElement], none_value: Any) -> None:
        self.none_value = none_value
        with ui.row(align_items="center") as row:
            with DisableableDiv() as disableable_div:
                self.inner_element = inner()
            self.checkbox = ui.checkbox().props("dense")
        disableable_div.bind_enabled_from(self.checkbox, "value")
        super().__init__(value=none_value)
        row.move(self)

    @property
    def value(self) -> Any:
        if self.checkbox.value:
            return self.inner_element.value
        else:
            return self.none_value

    @value.setter
    def value(self, value: Any) -> None:
        if value is None or value == self.none_value:
            self.checkbox.value = False
            clear_value_element(self.inner_element)
        else:
            self.checkbox.value = True
            self.inner_element.value = value

    def on_value_change(self, callback: Handler[ValueChangeEventArguments]) -> Self:
        def wrapped_cb(ev: ValueChangeEventArguments) -> None:
            new_ev = ValueChangeEventArguments(
                value=self.value, previous_value=None, sender=ev.sender, client=ev.client
            )
            callback(new_ev)

        self.inner_element.on_value_change(wrapped_cb)
        self.checkbox.on_value_change(wrapped_cb)
        return self

    def bind_value_to(
        self,
        target_object: Any,
        target_name: str = "value",
        forward: Callable[[Any], Any] | None = None,
        *,
        strict: bool | None = None,
    ) -> Self:
        raise NotImplementedError("bind_value_to is not supported by OptionalValueElement")

    def bind_value_from(
        self,
        target_object: Any,
        target_name: str = "value",
        backward: Callable[[Any], Any] | None = None,
        *,
        strict: bool | None = None,
    ) -> Self:
        raise NotImplementedError("bind_value_from is not supported by OptionalValueElement")

    def bind_value(
        self,
        target_object: Any,
        target_name: str = "value",
        *,
        forward: Callable[[Any], Any] | None = None,
        backward: Callable[[Any], Any] | None = None,
        strict: bool | None = None,
    ) -> Self:
        raise NotImplementedError("bind_value is not supported by OptionalValueElement")

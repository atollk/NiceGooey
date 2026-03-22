from typing import Callable

from nicegui.elements.mixins.validation_element import ValidationElement, ValidationFunction, ValidationDict
from nicegui.elements.mixins.value_element import ValueElement


class ValidationWrapper(ValidationElement):
    """Wraps a `ValueElement` to support validation."""

    _value_element: ValueElement

    def __init__(
        self,
        validation: ValidationFunction | ValidationDict | None,
        value_element: Callable[[], ValueElement],
    ) -> None:
        super().__init__(validation=validation, value=None, tag="q-field")
        self.props("borderless")
        with self:
            self._value_element = value_element()

        self.on_value_change = self._value_element.on_value_change
        self.bind_value_to = self._value_element.bind_value_to
        self.bind_value_from = self._value_element.bind_value_from
        self.bind_value = self._value_element.bind_value
        self.set_value = self._value_element.set_value
        self._event_args_to_value = self._value_element._event_args_to_value
        self._value_to_model_value = self._value_element._value_to_model_value
        self._value_to_event_value = self._value_element._value_to_event_value

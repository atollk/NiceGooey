from typing import Callable, Any

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
        self._value_element = value_element()
        super().__init__(validation=validation, value=None, tag="q-field")
        self._value_element.move(self)
        self.props("borderless")

    def __getattr__(self, item: str) -> Any:
        try:
            return self.__getattribute__(item)
        except AttributeError:
            if item == "_value_element":
                raise
            return getattr(self._value_element, item)

    def __setattr__(self, key: str, value: Any) -> None:
        if key == "value":
            self._value_element.value = value
        super().__setattr__(key, value)

import abc
import argparse
import typing

from nicegui import ui
from nicegui.elements.mixins import value_element, validation_element

from .action_ui import ActionUi


class ActionUiElement[ActionT: argparse.Action](ActionUi[ActionT], abc.ABC):
    _UNSET = object()

    element: value_element.ValueElement | None = None

    @typing.override
    def validate(self) -> bool:
        if isinstance(self.element, validation_element.ValidationElement):
            return self.element.validate()
        return True

    def _validate_input_value(self, value: str) -> str | None:
        try:
            self._action_type()(value)
            return None
        except Exception as e:
            return str(e)

    def _create_input_element_generic(
        self,
        init: typing.Callable[[typing.Any], value_element.ValueElement],
        *,
        forward_transform: typing.Callable[[typing.Any], typing.Any] = lambda x: x,
        backward_transform: typing.Callable[[typing.Any], typing.Any] = lambda x: x,
        validation: validation_element.ValidationFunction | validation_element.ValidationDict | None = None,
        default: typing.Any = _UNSET,
    ) -> value_element.ValueElement:
        """
        Creates/Renders the input element for this action and stores it in `self.element`.
        :param init: The type/constructor to use for the input element.
        :param forward_transform: The forward transformation when binding the input element value to the respective namespace variable.
        :param backward_transform: The backward transformation when binding the input element value to the respective namespace variable.
        :param validation: Optional validation to apply to the input element.
        :param default: Optional default value for the input element. If not provided, the action's default or a type-based default will be used.
        :return `self.element`
        """
        el = init(default if default is not self._UNSET else self._action_default())
        if isinstance(el, validation_element.ValidationElement):
            el.without_auto_validation()
            if validation is not None:
                el.validation = validation
                el.error = None
        if not hasattr(self.parent.namespace, self.action.dest):
            setattr(self.parent.namespace, self.action.dest, self._action_default())
        el.bind_value(
            target_object=self.parent.namespace,
            target_name=self.action.dest,
            forward=forward_transform,
            backward=backward_transform,
        )
        self.element = el
        return self.element

    @abc.abstractmethod
    def _create_input_element(self) -> value_element.ValueElement:
        """Creates the input element for this action."""
        raise NotImplementedError()

    @typing.override
    def render(self) -> ui.element:
        c = ui.column()
        with c:
            self.render_action_name()
            self._create_input_element()
        return c

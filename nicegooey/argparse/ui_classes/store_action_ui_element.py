import argparse
import typing

from nicegui.elements.mixins import value_element

from .action_ui_element import ActionUiElement


class StoreActionUiElement(ActionUiElement[argparse._StoreAction]):
    @typing.override
    def _create_input_element(self) -> value_element.ValueElement:
        def forward_transform(v: typing.Any) -> typing.Any:
            ns = argparse.Namespace()
            ns.__setattr__(self.action.dest, getattr(self.parent.namespace, self.action.dest))
            try:
                cast = self._action_type()(v)
            except (TypeError, ValueError):
                pass
            else:
                assert self.parent.parent_parser is not None
                self.action(self.parent.parent_parser, ns, cast)
            return getattr(ns, self.action.dest)

        el = self._create_input_element_generic(
            lambda v: self._action_type_input(value=v),
            forward_transform=forward_transform,
            validation=self._validate_input_value,
        )
        return el

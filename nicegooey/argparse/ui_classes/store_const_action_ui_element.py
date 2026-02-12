import argparse
import typing

from nicegui import ui
from nicegui.elements.mixins import value_element

from .action_ui_element import ActionUiElement


class StoreConstActionUiElement(ActionUiElement[argparse._StoreConstAction]):
    @typing.override
    def _create_input_element(self) -> value_element.ValueElement:
        def forward_transform(v: typing.Any) -> typing.Any:
            if v is None:
                return None
            assert isinstance(v, bool)
            if v:
                ns = argparse.Namespace()
                assert self.parent.parent_parser is not None
                self.action(self.parent.parent_parser, ns, None)
                return getattr(ns, self.action.dest)
            else:
                return self._action_default()

        def backward_transform(v: typing.Any) -> bool | None:
            if v == self.action.const:
                return True
            elif v == self._action_default():
                return False
            else:
                return None

        return self._create_input_element_generic(
            ui.checkbox,
            forward_transform=forward_transform,
            backward_transform=backward_transform,
            default=False,
        )

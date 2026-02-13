import argparse
import typing

from nicegui import ui
from nicegui.elements.mixins import value_element

from .action_ui_element import ActionUiElement


class StoreConstActionUiElement(ActionUiElement[argparse._StoreConstAction]):
    @typing.override
    def _input_element_forward_transform(self, v: typing.Any) -> typing.Any:
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

    @typing.override
    def _input_element_backward_transform(self, v: typing.Any) -> bool | None:
        if v == self.action.const:
            return True
        elif v == self._action_default():
            return False
        else:
            return None

    @typing.override
    def _input_element_init(self, default: typing.Any) -> value_element.ValueElement:
        return ui.checkbox(default)

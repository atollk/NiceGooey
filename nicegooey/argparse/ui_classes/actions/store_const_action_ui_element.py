import argparse
import typing


from .action_ui_element import ActionUiElement


class StoreConstActionUiElement(ActionUiElement[argparse._StoreConstAction]):
    @typing.override
    def _input_element_forward_transform(self, v: typing.Any) -> typing.Any:
        # The value doesn't actually matter here, since the const value is always what's stored.
        ns = argparse.Namespace()
        assert self.parent.parent_parser is not None
        self.action(self.parent.parent_parser, ns, None)
        return getattr(ns, self.action.dest)

    @typing.override
    def _input_element_backward_transform(self, v: typing.Any) -> bool | None:
        # This logic doesn't matter because the value isn't actually used, but it's fun to have here :)
        if v == self.action.const:
            return True
        elif v == self._action_default():
            return False
        else:
            return None

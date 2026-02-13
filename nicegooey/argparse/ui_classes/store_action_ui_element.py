import argparse
import typing


from .action_ui_element import ActionUiElement


class StoreActionUiElement(ActionUiElement[argparse._StoreAction]):
    @typing.override
    def _input_element_forward_transform(self, v: typing.Any) -> typing.Any:
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

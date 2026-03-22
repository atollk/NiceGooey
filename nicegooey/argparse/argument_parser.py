import argparse
import copy
import dataclasses
from argparse import Namespace
from typing import Sequence, overload, TYPE_CHECKING

if TYPE_CHECKING:
    from nicegooey.argparse.ui_classes.actions.action_ui_element import ActionUiElement


@dataclasses.dataclass
class NiceGooeyConfig:
    """
    Configuration for the NiceGooey setup.

    Attributes:
        root_card_class (str): A space-separated list of Tailwind classes to be applied to the root of the argument UI.
            Especially useful to pass something like 'w-4xl' to limit the width on large screens.
        action_element_overrides (dict): A dict that maps parser action objects to `ActionUiElement` classes.
            Use this to customize what elements are used to render for certain actions.

    """

    root_card_class: str = "w-full"
    action_element_overrides: dict[argparse.Action, type["ActionUiElement"]] = dataclasses.field(
        default_factory=dict
    )


class NgArgumentParser(argparse.ArgumentParser):
    nicegooey_config: NiceGooeyConfig = NiceGooeyConfig()

    @staticmethod
    def from_argparse(parser: argparse.ArgumentParser) -> "NgArgumentParser":
        clone = copy.copy(parser)
        clone.__class__ = NgArgumentParser
        assert isinstance(clone, NgArgumentParser)
        clone.nicegooey_config = NiceGooeyConfig()
        return clone

    @overload
    def parse_args(self, args: Sequence[str] | None = None, namespace: None = None) -> Namespace: ...

    @overload
    def parse_args[_N](self, args: Sequence[str] | None, namespace: _N) -> _N: ...

    @overload
    def parse_args[N](self, *, namespace: N) -> N: ...

    def parse_args[N](self, args: Sequence[str] | None = None, namespace: N | None = None) -> N | Namespace:
        from nicegooey.argparse.main import main_instance

        if namespace is not None:
            raise NotImplementedError("Passing namespace to parse_args is not supported yet.")
        if args is not None:
            raise NotImplementedError("Passing args to parse_args is not supported yet.")
        return main_instance.parse_args(self)

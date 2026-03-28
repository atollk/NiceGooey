import argparse
import copy
import dataclasses
from argparse import Namespace
from collections import defaultdict
from typing import Sequence, overload, TYPE_CHECKING

if TYPE_CHECKING:
    from nicegooey.argparse.ui_classes.actions.action_ui_element import ActionUiElement


@dataclasses.dataclass
class NiceGooeyConfig:
    """
    Configuration for the NiceGooey setup.

    Attributes:
        root_card_class: A space-separated list of Tailwind classes to be applied to the root of the argument UI.
            Especially useful to pass something like 'w-4xl' to limit the width on large screens.
        action_config: A dict that maps parser action objects to `ActionConfig` classes.
            Use this to set configurations affecting individual actions.

    """

    @dataclasses.dataclass
    class ActionConfig:
        """
        Configuration for a single action.

        Attributes:
            element_override: If set, this class is instantiated to display the widget for this element in the UI
                instead of the default.
        """

        element_override: type["ActionUiElement"] | None = None

    root_card_class: str = "max-w-4xl"
    action_config: dict[argparse.Action, ActionConfig] = dataclasses.field(
        default_factory=lambda: defaultdict(NiceGooeyConfig.ActionConfig)
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

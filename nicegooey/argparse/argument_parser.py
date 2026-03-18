import argparse
import copy
import dataclasses
from argparse import Namespace
from typing import Sequence, overload


@dataclasses.dataclass
class ArgumentParserConfig:
    argument_vp_width: int | str = "w-full"


class NgArgumentParser(argparse.ArgumentParser):
    nicegooey_config: ArgumentParserConfig = ArgumentParserConfig()

    @staticmethod
    def from_argparse(parser: argparse.ArgumentParser) -> "NgArgumentParser":
        clone = copy.copy(parser)
        clone.__class__ = NgArgumentParser
        assert isinstance(clone, NgArgumentParser)
        clone.nicegooey_config = ArgumentParserConfig()
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

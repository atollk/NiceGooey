import argparse
import copy
from argparse import Namespace
from typing import Sequence, overload, TYPE_CHECKING

from nicegooey.argparse.config import NiceGooeyConfig

if TYPE_CHECKING:
    pass


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

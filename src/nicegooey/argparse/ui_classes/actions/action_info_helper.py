from nicegooey.argparse import NgArgumentParser
import argparse
import builtins
import dataclasses
import enum
import warnings
from typing import Any, Callable

from nicegooey.argparse import NiceGooeyConfig
from nicegooey.argparse.ui_classes.util.misc import Nargs


@dataclasses.dataclass
class ActionInfoHelper:
    action: argparse.Action
    parser: argparse.ArgumentParser

    class TypeCount(enum.Enum):
        Zero = "0"
        One = "1"
        Many = "*"

    def type_count(self) -> TypeCount:
        """Returns the number of elements represented by the type, if you follow the nargs of this action."""
        nargs = self.nargs()
        is_multiple = nargs in (Nargs.ZERO_OR_MORE, Nargs.ONE_OR_MORE) or (
            isinstance(nargs, int) and nargs > 0
        )
        if is_multiple:
            return self.TypeCount.Many
        elif nargs == 0:
            return self.TypeCount.Zero
        else:
            return self.TypeCount.One

    def type(self) -> Callable[[str], Any]:
        """Returns the type of this action, or a reasonable default if no type is set."""
        match self.action.type:
            case None:
                return str
            case argparse.FileType:
                raise NotImplementedError("argparse.FileType is deprecated and not supported.")
            case str():
                return self.parser._registry_get("type", self.action.type)
            case _:
                return self.action.type

    def type_with_nargs(self) -> Callable[[Any], Any]:
        """Like action_type, but also takes into considering the nargs of this action."""
        type_count = self.type_count()
        match type_count:
            case ActionInfoHelper.TypeCount.Zero:
                return lambda v: v
            case ActionInfoHelper.TypeCount.One:
                return self.type()
            case ActionInfoHelper.TypeCount.Many:
                return lambda v: list(v)
            case _:
                raise ValueError(f"Invalid type count {type_count}")

    def const(self) -> Any:
        return self.action.const

    def default(self) -> Any:
        """Returns the default value for this action, or a reasonable default if no default is set."""
        type_count = self.type_count()
        type_base = self.type()

        if self.action.default is not None:
            if type_count == self.TypeCount.Many and not isinstance(self.action.default, list):
                warnings.warn("Action expects multiple arguments but the default is not a list.")
                return [self.action.default]
            return self.action.default

        match type_count:
            case self.TypeCount.Zero:
                return None
            case self.TypeCount.One:
                match type_base:
                    case builtins.bool:
                        return False
                    case builtins.int | builtins.float:
                        return 0
                    case _:
                        return ""
            case self.TypeCount.Many:
                return []

    def nargs(self) -> int | Nargs:
        """Returns the nargs of this action, or a reasonable default if no nargs is set."""
        if isinstance(self.action.nargs, int):
            return self.action.nargs

        if self.action.nargs is not None:
            if self.action.nargs in ("?", "*", "+"):
                return Nargs(self.action.nargs)
            elif self.action.nargs in ("...", "A...", "==SUPPRESS=="):
                raise NotImplementedError(f"nargs value {self.action.nargs} not supported")
            else:
                raise ValueError(f"Unrecognized nargs value: {self.action.nargs}")

        return Nargs.SINGLE_ELEMENT

    def ng_config(self) -> NiceGooeyConfig.ActionConfig:
        """Returns the NiceGooey-specific config for this action that was set by the user."""
        if isinstance(self.parser, NgArgumentParser):
            return self.parser.nicegooey_config.action_config.get(self.action, NiceGooeyConfig.ActionConfig())
        else:
            return NiceGooeyConfig.ActionConfig()

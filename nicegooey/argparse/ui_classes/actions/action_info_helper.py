import argparse
import builtins
import dataclasses
import enum
import warnings
from typing import Any, Callable

from nicegooey.argparse.ui_classes.util.nargs import Nargs


@dataclasses.dataclass
class ActionInfoHelper:
    action: argparse.Action
    parser: argparse.ArgumentParser

    class TypeCount(enum.Enum):
        Zero = "0"
        One = "1"
        Many = "*"

    def _is_nargs_multiple(self) -> TypeCount:
        nargs = self.action_nargs()
        is_multiple = nargs in (Nargs.ZERO_OR_MORE, Nargs.ONE_OR_MORE) or (
            isinstance(nargs, int) and nargs > 0
        )
        if is_multiple:
            return self.TypeCount.Many
        elif nargs == 0:
            return self.TypeCount.Zero
        else:
            return self.TypeCount.One

    def action_type(self) -> tuple[TypeCount, Callable[[str], Any]]:
        """Returns the type of this action, or a reasonable default if no type is set."""
        base_type = None
        match self.action.type:
            case None:
                base_type = str
            case argparse.FileType:
                raise NotImplementedError("argparse.FileType is deprecated and not supported.")
            case str():
                base_type = self.parser._registry_get("type", self.action.type)
            case _:
                base_type = self.action.type
        return self._is_nargs_multiple(), base_type

    def action_type_with_nargs(self) -> Callable[[Any], Any]:
        type_count, type_base = self.action_type()
        match type_count:
            case ActionInfoHelper.TypeCount.Zero:
                return lambda v: v
            case ActionInfoHelper.TypeCount.One:
                return type_base
            case ActionInfoHelper.TypeCount.Many:
                return lambda v: list(v)
            case _:
                raise ValueError(f"Invalid type count {type_count}")

    def action_const(self) -> Any:
        return self.action.const

    def action_default(self) -> Any:
        """Returns the default value for this action, or a reasonable default if no default is set."""
        type_count, type_base = self.action_type()

        # ugly hack but I don't know a better solution
        if isinstance(self.action, argparse._AppendAction):
            return []

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

    def action_nargs(self) -> int | Nargs:
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

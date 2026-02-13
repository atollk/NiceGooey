import argparse
import builtins
import dataclasses
import typing

from nicegooey.argparse.ui_classes.util import Nargs


@dataclasses.dataclass
class ActionInfoHelper:
    action: argparse.Action
    parser: argparse.ArgumentParser

    def action_type(self) -> typing.Callable[[str], typing.Any]:
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

    def action_default(self) -> typing.Any:
        """Returns the default value for this action, or a reasonable default if no default is set."""
        if self.action.default is not None:
            return self.action.default
        if self.action.choices is not None:
            return []
        else:
            match self.action_type():
                case builtins.bool:
                    return False
                case builtins.int | builtins.float:
                    return 0
                case _:
                    return ""

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

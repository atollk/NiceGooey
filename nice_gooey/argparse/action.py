import enum
import typing

import nice_gooey.argparse


class Action:
    option_strings: list[str]
    dest: str
    nargs: int | str | None
    const: object | None
    default: object | None
    type: typing.Type | typing.Callable[[str], object] | None
    choices: typing.Sequence | None
    required: bool
    help: str | None
    metavar: str | None
    deprecated: bool = False

    container: nice_gooey.argparse.ArgumentParser

    def __init__(
        self,
        option_strings,
        dest,
        nargs=None,
        const=None,
        default=None,
        type=None,
        choices=None,
        required=False,
        help=None,
        metavar=None,
    ):
        pass

    def __call__(self, parser, namespace, values, option_string=None):
        pass

    def format_usage(self):
        pass


class BooleanOptionalAction(Action):
    pass


class PredefinedAction(enum.Enum):
    STORE = "store"
    STORE_CONST = "store_const"
    STORE_TRUE = "store_true"
    STORE_FALSE = "store_false"
    APPEND = "append"
    APPEND_CONST = "append_const"
    EXTEND = "extend"
    COUNT = "count"
    HELP = "help"
    VERSION = "version"

    Literals = typing.Literal[
        "store",
        "store_const",
        "store_true",
        "store_false",
        "append",
        "append_const",
        "extend",
        "count",
        "help",
        "version",
    ]
    _ignore_ = [Literals]

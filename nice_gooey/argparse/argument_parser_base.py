import dataclasses
import enum
import os
import re
import sys
import typing
from argparse import SUPPRESS, ArgumentError
from collections import defaultdict
from gettext import ngettext

from .file_type import FileType
from .formatter import HelpFormatter
from .action import Action, PredefinedAction
from .namespace import Namespace


class Nargs(enum.Enum):
    OPTIONAL = "?"
    ZERO_OR_MORE = "*"
    ONE_OR_MORE = "+"

    Literals = typing.Literal["?", "*", "+"]
    _ignore_ = [Literals]


@dataclasses.dataclass
class _BoolWrapper:
    value: bool


NEGATIVE_NUMBER_MATCHER: typing.Final[typing.Pattern[str]] = re.compile(r"^-\d+$|^-\d*\.\d+$")


class ArgumentParser:
    prog: str
    usage: str
    description: str
    epilog: str
    parents: list["ArgumentParser"]
    formatter_class: "HelpFormatter"
    prefix_chars: str
    fromfile_prefix_chars: str | None
    argument_default: object | None
    conflict_handler: str
    add_help: bool
    allow_abbrev: bool
    exit_on_error: bool
    suggest_on_error: bool
    color: bool

    _defaults: dict[str, object]
    _registries: dict[str, dict[typing.Hashable, object]]
    _actions: list[Action]
    _option_string_actions: dict[str, Action]
    _has_negative_number_optionals: _BoolWrapper

    def __init__(
        self,
        prog: str | None = None,
        usage: str | None = None,
        description: str | None = None,
        epilog: str | None = None,
        parents: list["ArgumentParser"] | None = None,
        formatter_class: HelpFormatter = HelpFormatter,
        prefix_chars: str = "-",
        fromfile_prefix_chars: str | None = None,
        argument_default: object | None = None,
        conflict_handler: str = "error",
        add_help: bool = True,
        allow_abbrev: bool = True,
        exit_on_error: bool = True,
        *,
        suggest_on_error: bool = False,
        color: bool = True,
    ) -> None:
        if prog is None:
            self.prog = os.path.basename(sys.argv[0])
        else:
            self.prog = prog

        self.usage = usage
        self.description = description
        self.epilog = epilog
        self.parents = parents or []
        self.formatter_class = formatter_class
        self.prefix_chars = prefix_chars
        self.fromfile_prefix_chars = fromfile_prefix_chars
        self.argument_default = argument_default
        self.conflict_handler = conflict_handler
        self.add_help = add_help
        self.allow_abbrev = allow_abbrev
        self.exit_on_error = exit_on_error
        self.suggest_on_error = suggest_on_error
        self.color = color

        self._defaults = dict()
        self._registries = defaultdict(dict)
        self._actions = []
        self._option_string_actions = dict()
        self._has_negative_number_optionals = _BoolWrapper(False)

        if self.add_help:
            default_prefix = "-" if "-" in prefix_chars else prefix_chars[0]
            self.add_argument(
                default_prefix + "h",
                default_prefix * 2 + "help",
                action="help",
                default=SUPPRESS,
                help="show this help message and exit",
            )

        for parent in parents:
            raise NotImplementedError()
            if not isinstance(parent, ArgumentParser):
                raise TypeError("parents must be a list of ArgumentParser")
            self._add_container_actions(parent)
            defaults = parent._defaults
            self._defaults.update(defaults)

    _option_strings = typing.NamedTuple(
        "_option_strings", [("option_strings", list[str]), ("dest", str), ("required", bool)]
    )

    def _get_option_strings(
        self, *args: str, nargs: int | Nargs.Literals | None, required: bool, dest: str | None
    ) -> _option_strings:
        # Check for positional arguments, if no arg names are provided or only a single one without prefix chars.
        chars = self.prefix_chars
        if not args or len(args) == 1 and args[0][0] not in chars:
            if args and dest is not None:
                raise ValueError("dest supplied twice for positional argument")
            if required:
                raise TypeError("'required' is an invalid argument for positionals")

            required = nargs not in (Nargs.OPTIONAL.value, Nargs.ZERO_OR_MORE.value, 0)
            option_strings = []
        else:
            # determine short and long option strings
            option_strings = []
            long_option_strings = []

            option_string = ""
            for option_string in args:
                # error on strings that don't start with an appropriate prefix
                if option_string[0] not in self.prefix_chars:
                    raise ValueError(
                        f"invalid option string {option_string!r}: must start with a character {self.prefix_chars!r}"
                    )

                # strings starting with two prefix characters are long options
                option_strings.append(option_string)
                if len(option_string) > 1 and option_string[1] in self.prefix_chars:
                    long_option_strings.append(option_string)

            # infer destination, '--foo-bar' -> 'foo_bar' and '-x' -> 'x'
            if dest is None:
                if long_option_strings:
                    dest_option_string = long_option_strings[0]
                else:
                    dest_option_string = option_strings[0]
                dest = dest_option_string.lstrip(self.prefix_chars)
                if not dest:
                    raise ValueError(f"dest= is required for options like {option_string!r}")
                dest = dest.replace("-", "_")

        return ArgumentParser._option_strings(option_strings=option_strings, dest=dest, required=required)

    def add_argument[T](
        self,
        *args: str,
        action: PredefinedAction.Literals | Action = "store",
        nargs: int | Nargs.Literals | None = None,
        const: object | None = None,
        default: T | None | str = None,
        type: typing.Type[T] | typing.Callable[[str], T] = str,
        choices: typing.Sequence[T] | None = None,
        required: bool = False,
        help: str = "TODO",
        metavar: str | None = None,
        dest: str | None = None,
        deprecated: bool = False,
    ) -> Action:
        option_strings, dest, required = self._get_option_strings(
            *args, nargs=nargs, required=required, dest=dest
        )

        if default is None:
            default = self._defaults.get(dest, self.argument_default)

        # create the action object, and add it to the parser
        action_class = self._registry_get("action", action, action)
        if not callable(action_class):
            raise ValueError(f'unknown action "{action_class}"')
        action_object = action_class(
            option_strings=option_strings,
            nargs=nargs,
            const=const,
            default=default,
            type=type,
            choices=choices,
            required=required,
            help=help,
            dest=dest,
            metavar=metavar,
            deprecated=deprecated,
        )
        assert isinstance(action_object, Action)

        type_func = self._registry_get("type", action_object.type, action_object.type)
        if not callable(type_func):
            raise ValueError(f"{type_func!r} is not callable")
        if type_func is FileType:
            raise ValueError(f"{type_func!r} is a FileType class object, instance of it must be passed")

        # raise an error if the metavar does not match the type
        if hasattr(self, "_get_formatter"):
            try:
                self._get_formatter()._format_args(action, None)
            except TypeError:
                raise ValueError("length of metavar tuple does not match nargs")

        return self._add_action(action_object)

    def _add_action(self, action: Action) -> Action:
        self._check_conflict(action)

        self._actions.append(action)
        action.container = self

        for option_string in action.option_strings:
            self._option_string_actions[option_string] = action
            if NEGATIVE_NUMBER_MATCHER.match(option_string):
                self._has_negative_number_optionals.value = True

        return action

    def _remove_action(self, action):
        self._actions.remove(action)

    def _check_conflict(self, action: Action) -> None:
        conflicting_optionals = [
            (option_string, conflicting_action)
            for option_string in action.option_strings
            if (conflicting_action := self._option_string_actions.get(option_string)) is not None
        ]
        if conflicting_optionals:
            if self.conflict_handler == "error":
                message = ngettext(
                    "conflicting option string: %s",
                    "conflicting option strings: %s",
                    len(conflicting_optionals),
                )
                conflict_string = ", ".join(
                    [option_string for option_string, action in conflicting_optionals]
                )
                raise ArgumentError(action, message % conflict_string)
            elif self.conflict_handler == "resolve":
                # remove all conflicting options
                for option_string, action in conflicting_optionals:
                    # remove the conflicting option
                    action.option_strings.remove(option_string)
                    self._option_string_actions.pop(option_string, None)

                    # if the option now has no option string, remove it from the
                    # container holding it
                    if not action.option_strings:
                        action.container._remove_action(action)
            else:
                handler_func_name = f"_handle_conflict_{self.conflict_handler}"
                try:
                    handler_func = getattr(self, handler_func_name)
                except AttributeError:
                    raise ValueError(f"invalid conflict_resolution value: {self.conflict_handler!r}")
                handler_func(action, conflicting_optionals)

    @typing.overload
    def parse_args(self, args: typing.Sequence[str] | None = None, namespace: None = None) -> Namespace: ...
    @typing.overload
    def parse_args[N](self, args: typing.Sequence[str] | None, namespace: N) -> N: ...
    @typing.overload
    def parse_args[N](self, *, namespace: N) -> N: ...

    def parse_args[N: Namespace](
        self, *args: None | str | typing.Sequence[str], namespace: None | N = None
    ) -> N:
        pass

    def add_subparsers(
        self, *, title, description, prog, parser_class, action, dest, required, help, metavar
    ):
        raise NotImplementedError()

    def add_argument_group(self, title=None, description=None, *, argument_default, conflict_handler):
        raise NotImplementedError()

    def add_mutually_exclusive_group(self, required):
        raise NotImplementedError()

    def set_defaults(self, **kwargs):
        raise NotImplementedError()

    def print_usage(self, file=None):
        raise NotImplementedError()

    def print_help(self, file=None):
        raise NotImplementedError()

    def format_usage(self):
        raise NotImplementedError()

    def format_help(self):
        raise NotImplementedError()

    def parse_known_args(self, args=None, namespace=None):
        raise NotImplementedError()

    def convert_arg_line_to_args(self, arg_line):
        raise NotImplementedError()

    def exit(self, status=0, message=None):
        raise NotImplementedError()

    def error(self, message):
        raise NotImplementedError()

    def parse_intermixed_args(self, args=None, namespace=None):
        raise NotImplementedError()

    def parse_known_intermixed_args(self, args=None, namespace=None):
        raise NotImplementedError()

    @typing.overload
    def register(
        self, registry_name: typing.Literal["action"], value: typing.Hashable, object: typing.Type[Action]
    ) -> None: ...

    @typing.overload
    def register(self, registry_name: str, value: typing.Hashable, object: object): ...

    def register(self, registry_name: str, value: typing.Hashable, object: object):
        self._registries[registry_name][value] = object

    def _registry_get(self, registry_name: str, value: typing.Hashable, default: object | None = None):
        return self._registries[registry_name].get(value, default)

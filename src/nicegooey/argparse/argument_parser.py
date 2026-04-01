import argparse
import copy
from argparse import Namespace
from collections.abc import Iterable
from typing import Sequence, overload, TYPE_CHECKING, Any, override, Type

from nicegooey.argparse.config import NiceGooeyConfig


class _NgActionsContainer(argparse._ActionsContainer):
    if TYPE_CHECKING:

        @override
        def add_argument[T](
            self,
            *name_or_flags: str,
            action: str | type[argparse.Action] = ...,
            nargs: int | str | None = None,
            const: Any = ...,
            default: Any = ...,
            type: argparse._ActionType = ...,
            choices: Iterable[T] | None = ...,
            required: bool = ...,
            help: str | None = ...,
            metavar: str | tuple[str, ...] | None = ...,
            dest: str | None = ...,
            version: str = ...,
            **kwargs: Any,
        ) -> "NgActionWrapper": ...

        @override
        def add_argument_group(
            self,
            title: str | None = None,
            description: str | None = None,
            *,
            prefix_chars: str = ...,
            argument_default: Any = ...,
            conflict_handler: str = ...,
        ) -> "NgArgumentGroup": ...

        @override
        def add_mutually_exclusive_group(self, *, required: bool = False) -> "NgMutualExclusiveGroup": ...
    else:

        @override
        def add_argument(self, *args, **kwargs) -> "NgActionWrapper":
            return _copy_as_type(super().add_argument(*args, **kwargs), NgActionWrapper)

        @override
        def add_argument_group(self, *args, **kwargs) -> "NgArgumentGroup":
            return _copy_as_type(super().add_argument_group(*args, **kwargs), NgArgumentGroup)

        @override
        def add_mutually_exclusive_group(self, *args, **kwargs) -> "NgMutualExclusiveGroup":
            return _copy_as_type(
                super().add_mutually_exclusive_group(*args, **kwargs), NgMutualExclusiveGroup
            )


class NgActionWrapper(argparse.Action):
    def __get_nicegooey_config(self) -> NiceGooeyConfig:
        import nicegooey.argparse.main

        return nicegooey.argparse.main.main_instance.parser_config

    @property
    def nicegooey_config(self) -> NiceGooeyConfig.ActionConfig:
        return self.__get_nicegooey_config().action_config.get(self, NiceGooeyConfig.ActionConfig())

    @nicegooey_config.setter
    def nicegooey_config(self, value: NiceGooeyConfig.ActionConfig) -> None:
        self.__get_nicegooey_config().action_config[self] = value

    def set_nicegooey_config(self, value: NiceGooeyConfig.ActionConfig) -> None:
        self.nicegooey_config = value


class NgArgumentGroup(_NgActionsContainer, argparse._ArgumentGroup):
    pass


class NgMutualExclusiveGroup(_NgActionsContainer, argparse._MutuallyExclusiveGroup):
    pass


class NgArgumentParser(_NgActionsContainer, argparse.ArgumentParser):
    nicegooey_config: NiceGooeyConfig = NiceGooeyConfig()

    @staticmethod
    def from_argparse(parser: argparse.ArgumentParser) -> "NgArgumentParser":
        clone = _copy_as_type(parser, NgArgumentParser)
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


def _copy_as_type[T](obj: Any, newtyp: Type[T]) -> T:
    clone = copy.copy(obj)
    clone.__class__ = newtyp
    assert isinstance(clone, newtyp)
    return clone

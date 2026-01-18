import argparse as std_argparse
import dataclasses
import typing
import nice_gooey.argparse as ng_argparse

Param = typing.ParamSpec("Param")
RetType = typing.TypeVar("RetType")
MainCallable = typing.Callable[Param, RetType]


@dataclasses.dataclass
class ArgparsePatchState:
    active: bool = False
    main_function: typing.Callable | None = None


patch_state = ArgparsePatchState()


@dataclasses.dataclass
class ArgparsePatchBackup:
    argument_parser: typing.Type[object]


def nice_gooey_argparse_main() -> typing.Callable[[MainCallable], MainCallable]:
    def decorator(func: MainCallable) -> MainCallable:
        def wrapper(*args: Param.args, **kwargs: Param.kwargs) -> RetType:
            global patch_state
            patch_state.active = True
            patch_state.main_function = func

            backup = ArgparsePatchBackup(argument_parser=std_argparse.ArgumentParser)
            std_argparse.ArgumentParser = ng_argparse.ArgumentParser

            try:
                result = func(*args, **kwargs)
                return result
            finally:
                std_argparse.ArgumentParser = backup.argument_parser

                patch_state.active = False
                patch_state.main_function = None

        return wrapper

    return decorator

import contextlib
import typing
from .main import NiceGooeyMain

Param = typing.ParamSpec("Param")
RetType = typing.TypeVar("RetType")
MainCallable = typing.Callable[Param, RetType]

main_instance = NiceGooeyMain()


@contextlib.contextmanager
def _argparse_patch_context(*, patch: bool) -> typing.Generator[None, None, None]:
    """Context manager to patch argparse.ArgumentParser with nice_gooey.argparse.ArgumentParser."""
    import argparse as std_argparse
    import nicegooey.argparse as ng_argparse

    argument_parser_backup = std_argparse.ArgumentParser
    if patch:
        std_argparse.ArgumentParser = ng_argparse.ArgumentParser
    try:
        yield
    finally:
        if patch:
            std_argparse.ArgumentParser = argument_parser_backup


@contextlib.contextmanager
def _active_main_function_context(main_func: MainCallable) -> typing.Generator[None, None, None]:
    if main_instance.main_func is not None:
        raise RuntimeError("Nested active_main_function_context is not allowed")
    main_instance.main_func = main_func
    try:
        yield
    finally:
        main_instance.main_func = None


def nice_gooey_argparse_main(patch_argparse: bool = True) -> typing.Callable[[MainCallable], MainCallable]:
    def decorator(func: MainCallable) -> MainCallable:
        def wrapper(*args: Param.args, **kwargs: Param.kwargs) -> RetType:
            with _argparse_patch_context(patch=patch_argparse), _active_main_function_context(main_func=func):
                return func(*args, **kwargs)

        return wrapper

    return decorator

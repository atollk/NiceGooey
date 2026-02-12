import contextlib
import typing

import nicegui.helpers
from .main import main_instance
from .argument_parser import NgArgumentParser
import functools
import argparse

Param = typing.ParamSpec("Param")
RetType = typing.TypeVar("RetType")
MainCallable = typing.Callable[Param, RetType]


@contextlib.contextmanager
def _argparse_patch_context(*, patch: bool) -> typing.Generator[None, None, None]:
    """Context manager to patch argparse.ArgumentParser with nice_gooey.argparse.ArgumentParser."""
    if not patch:
        yield
    else:
        original_parse_args = argparse.ArgumentParser.parse_args
        # pyrefly: ignore[bad-assignment]
        argparse.ArgumentParser.parse_args = NgArgumentParser.parse_args
        try:
            yield
        finally:
            argparse.ArgumentParser.parse_args = original_parse_args


@contextlib.contextmanager
def _active_main_function_context(main_func: MainCallable) -> typing.Generator[None, None, None]:
    if main_instance.main_func is not None:
        raise RuntimeError("Nested active_main_function_context is not allowed")
    main_instance.main_func = main_func
    try:
        yield
    finally:
        if not nicegui.helpers.is_user_simulation():
            main_instance.main_func = None


def nice_gooey_argparse_main(*, patch_argparse: bool = True) -> typing.Callable[[MainCallable], MainCallable]:
    def decorator(func: MainCallable) -> MainCallable:
        @functools.wraps(func)
        def wrapper(*args: Param.args, **kwargs: Param.kwargs) -> RetType:
            with _argparse_patch_context(patch=patch_argparse), _active_main_function_context(main_func=func):
                return func(*args, **kwargs)

        return wrapper

    return decorator

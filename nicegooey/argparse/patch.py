import argparse
import contextlib
import functools
from typing import Callable, Generator, ParamSpec, TypeVar

import nicegui.helpers

from .argument_parser import NgArgumentParser
from .main import main_instance

Param = ParamSpec("Param")
RetType = TypeVar("RetType")
MainCallable = Callable[Param, RetType]


@contextlib.contextmanager
def _argparse_patch_context(*, patch: bool) -> Generator[None, None, None]:
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
def _active_main_function_context(main_func: MainCallable) -> Generator[None, None, None]:
    if not nicegui.helpers.is_user_simulation():
        # In tests, this function is called multiple within a test due to how nicegui implements the simulation.
        if main_instance.main_func is not None:
            raise RuntimeError("Nested active_main_function_context is not allowed")
    main_instance.main_func = main_func
    try:
        yield
    finally:
        if not nicegui.helpers.is_user_simulation():
            # In tests, this function is called multiple within a test due to how nicegui implements the simulation.
            main_instance.main_func = None


def nice_gooey_argparse_main(*, patch_argparse: bool = True) -> Callable[[MainCallable], MainCallable]:
    def decorator(func: MainCallable) -> MainCallable:
        @functools.wraps(func)
        def wrapper(*args: Param.args, **kwargs: Param.kwargs) -> RetType:
            with _argparse_patch_context(patch=patch_argparse), _active_main_function_context(main_func=func):
                return func(*args, **kwargs)

        return wrapper

    return decorator

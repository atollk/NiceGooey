import argparse
import enum
from typing import Any

from nicegui.elements.mixins.validation_element import ValidationElement, ValidationDict, ValidationFunction
from nicegui.elements.mixins.value_element import ValueElement
from nicegui.helpers import is_coroutine_function


class Nargs(enum.Enum):
    OPTIONAL = argparse.OPTIONAL
    ZERO_OR_MORE = argparse.ZERO_OR_MORE
    ONE_OR_MORE = argparse.ONE_OR_MORE
    PARSER = argparse.PARSER
    REMAINDER = argparse.REMAINDER
    SUPPRESS = argparse.SUPPRESS
    SINGLE_ELEMENT = "1"


def clear_value_element(e: ValueElement) -> None:
    e.value = ""


def q_field() -> ValidationElement:
    return ValidationElement(value=None, validation={}, tag="q-field").props("borderless")


def add_validation(
    element: ValidationElement, validation: ValidationDict | ValidationFunction | None
) -> None:
    """Like ValidationElement.validation = x, but adds to the existing validation instead of overwriting it."""

    def convert_dict_to_func(d: ValidationDict, make_async: bool) -> ValidationFunction:
        def f(value: Any) -> str | None:
            for k, v in d.items():
                if not v(value):
                    return k
            return None

        if make_async:

            async def g(value: Any) -> str | None:
                return f(value)

            return g
        else:
            return f

    old_validation = element.validation

    if old_validation is None or validation is None:
        element.validation = validation or old_validation
        if not element._auto_validation:
            element.error = None
        return

    old_is_function = callable(old_validation)
    new_is_function = callable(validation)
    old_is_async_function = old_is_function and is_coroutine_function(old_validation)
    new_is_async_function = new_is_function and is_coroutine_function(validation)

    # If both are functions but exactly one is async, they cannot be combined smoothly.
    if old_is_function and new_is_function and (old_is_async_function != new_is_async_function):
        raise ValueError(
            "Cannot merge two validation functions, one of which is async, the other of which is sync."
        )

    if not old_is_function and not new_is_function:
        # Both are dicts: Simply merge them
        new_validation = {**old_validation, **validation}
    else:
        target_async = new_is_async_function if new_is_function else old_is_async_function

        # Make sure that both are functions.
        if old_is_function:
            old_f = old_validation
        else:
            old_f = convert_dict_to_func(old_validation, target_async)
        if new_is_function:
            new_f = validation
        else:
            new_f = convert_dict_to_func(validation, target_async)

        # Define the new function.
        if target_async:

            async def new_validation(v: Any) -> str | None:
                if (r := await old_f(v)) is not None:
                    return r
                return await new_f(v)
        else:

            def new_validation(v: Any) -> str | None:
                if (r := old_f(v)) is not None:
                    return r
                return new_f(v)

    element.validation = new_validation
    if not element._auto_validation:
        element.error = None

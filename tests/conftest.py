from typing import Iterable

import pytest


@pytest.fixture(autouse=True)
def reset_nicegooey_main():
    """Fixture to reset the main_instance before each test."""
    from nicegooey.argparse.main import main_instance

    main_instance.reset()
    yield


def exactly_one[T](iterable: Iterable[T]) -> T:
    i = iter(iterable)
    try:
        x = next(i)
    except StopIteration:
        raise AssertionError("Iterable does not contain any elements.")
    try:
        next(i)
    except StopIteration:
        return x
    else:
        raise AssertionError("Iterable contains more than one element.")

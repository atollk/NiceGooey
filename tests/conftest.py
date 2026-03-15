from typing import Iterable

import pytest
from nicegui import ElementFilter, ui
from nicegui.testing import UserInteraction
from nicegui.testing.user import User


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


def find_within[T, S](
    user: User,
    kind: type[T] | None = None,
    marker: str | list[str] | None = None,
    content: str | list[str] | None = None,
    within_kind: type[S] | None = None,
    within_marker: str | list[str] | None = None,
    within_instance: ui.element | list[ui.element] | None = None,
) -> UserInteraction[T]:
    with user:
        filter = ElementFilter(kind=kind, marker=marker, content=content).within(
            kind=within_kind, marker=within_marker, instance=within_instance
        )
        return UserInteraction(user=user, elements=set(filter), target=None)

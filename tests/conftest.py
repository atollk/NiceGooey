from typing import Iterable

import pytest
from nicegui import ElementFilter
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


def find_within[T](
    user: User,
    kind: type[T] | None = None,
    marker: str | list[str] | None = None,
    content: str | list[str] | None = None,
    within_marker: str | list[str] | None = None,
    within_outer_marker: str | list[str] | None = None,
) -> UserInteraction[T]:
    with user:
        filter = ElementFilter(kind=kind, marker=marker, content=content)
        if within_marker:
            filter = filter.within(marker=within_marker)
        if within_outer_marker:
            filter = filter.within(marker=within_outer_marker)
        interaction = UserInteraction(user=user, elements=set(filter), target=None)
    assert len(interaction.elements) == 1, (
        f"More/Less than one element found matching: kind={kind}, marker={marker}, content={content}, within_marker={within_marker}, within_outer_marker={within_outer_marker}"
    )
    return interaction

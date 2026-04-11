import asyncio
import sys
from typing import Iterable, overload, Any

import nicegui.context
import pytest
from nicegui import ElementFilter
from nicegui.testing import UserInteraction
from nicegui.testing.user import User

if sys.platform == "win32":
    # On Windows, nicegui's FilePersistentDict.backup() uses aiofiles (via the asyncio
    # executor) to write the storage file asynchronously. When the event loop shuts down
    # the executor before the aiofiles context manager can close its file handle, the
    # handle stays open and the subsequent unlink() in clear() raises WinError 32.
    # Fix: override backup() to always write synchronously in the test process so no
    # async file handle is ever left open.
    from nicegui import json as _nicegui_json
    from nicegui.persistence import file_persistent_dict as _fpd

    def _sync_backup(self: _fpd.FilePersistentDict) -> None:
        if not self.filepath.exists():
            if not self:
                return
            self.filepath.parent.mkdir(exist_ok=True)
        self.filepath.write_text(
            _nicegui_json.dumps(self, indent=self.indent),
            encoding=self.encoding,
        )

    _fpd.FilePersistentDict.backup = _sync_backup  # type: ignore[method-assign]


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


async def assert_has_validation_error(user: User) -> None:
    with user:
        scope = nicegui.context.slot.parent
    # The validation errors actually don't pop up immediately, so we have to do a retry-sleep-check here.
    for retry in range(3):
        for el in scope.descendants():
            if not el.props.get("error", False):
                continue
            if "error-message" in el.props:
                return
        await asyncio.sleep([0.1, 1, 0][retry])
    raise AssertionError("No validation error found")


@overload
def find_within(
    user: User,
    marker: str | list[str] | None = None,
    content: str | list[str] | None = None,
    within_marker: str | list[str] | None = None,
    within_outer_marker: str | list[str] | None = None,
    within_outest_marker: str | list[str] | None = None,
) -> UserInteraction[Any]: ...


@overload
def find_within[T](
    user: User,
    kind: type[T] | None = None,
    marker: str | list[str] | None = None,
    content: str | list[str] | None = None,
    within_marker: str | list[str] | None = None,
    within_outer_marker: str | list[str] | None = None,
    within_outest_marker: str | list[str] | None = None,
) -> UserInteraction[Any]: ...


def find_within[T](
    user: User,
    kind: type[T] | None = None,
    marker: str | list[str] | None = None,
    content: str | list[str] | None = None,
    within_marker: str | list[str] | None = None,
    within_outer_marker: str | list[str] | None = None,
    within_outest_marker: str | list[str] | None = None,
) -> UserInteraction[T]:
    with user:
        filter = ElementFilter(kind=kind, marker=marker, content=content)
        if within_marker:
            filter = filter.within(marker=within_marker)
            if within_outer_marker:
                filter = filter.within(marker=within_outer_marker)
                if within_outest_marker:
                    filter = filter.within(marker=within_outest_marker)
        interaction = UserInteraction(user=user, elements=set(filter), target=None)
    assert len(interaction.elements) == 1, (
        f"More/Less than one element found matching: kind={kind}, marker={marker}, content={content}, within_marker={within_marker}, within_outer_marker={within_outer_marker}, within_outest_marker={within_outest_marker}",
    )
    return interaction

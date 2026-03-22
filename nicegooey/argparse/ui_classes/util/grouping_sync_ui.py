import abc
from collections.abc import Iterable
from typing import Protocol, Any, override


from nicegooey.argparse.main import NiceGooeyNamespace
from nicegooey.argparse.ui_classes.util.sync_element import SyncElement
from nicegooey.argparse.ui_classes.util.ui_wrapper import UiWrapper

# TODO: the class names in this file suck


class UiWrapperSyncElement(Protocol):
    def deactivate(self) -> None: ...

    def validate(self) -> bool: ...

    def sync_to_namespace(self) -> None: ...


class GroupingSyncUi(UiWrapper, SyncElement, UiWrapperSyncElement):
    """A SyncElement mostly does its syncing logic by delegating to children."""

    @abc.abstractmethod
    def get_children(self) -> Iterable[UiWrapperSyncElement]: ...

    def deactivate(self) -> None:
        for child in self.get_children():
            child.deactivate()

    def validate(self) -> bool:
        children = list(c.validate() for c in self.get_children())
        return all(children)

    def sync_to_namespace(self) -> None:
        for child in self.get_children():
            child.sync_to_namespace()

    @override
    @property
    def namespace(self) -> NiceGooeyNamespace:
        raise NotImplementedError()

    @override
    @property
    def dest(self) -> str:
        raise NotImplementedError()

    @override
    def _ui_state_from_value(self, value: Any) -> None:
        raise NotImplementedError()

    @override
    def _ui_state_to_value(self) -> Any:
        raise NotImplementedError()

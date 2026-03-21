import abc
from typing import Any

from nicegooey.argparse.main import NiceGooeyNamespace


class SyncElement(abc.ABC):
    """An abstract base class for elements that hold a value which will be synced to a namespace field on change."""

    _disable_sync_to_namespace: bool
    _disable_sync_from_namespace: bool

    def __init__(self):
        self._disable_sync_to_namespace = False
        self._disable_sync_from_namespace = False

    def subscribe(self) -> None:
        self.namespace._nicegooey_state.events[self.dest].subscribe(callback=self.sync_from_namespace)

    @property
    @abc.abstractmethod
    def namespace(self) -> NiceGooeyNamespace: ...

    @property
    @abc.abstractmethod
    def dest(self) -> str: ...

    def sync_from_namespace(self) -> None:
        if self._disable_sync_from_namespace:
            return
        value = getattr(self.namespace, self.dest, None)
        try:
            self._disable_sync_to_namespace = True
            self._ui_state_from_value(value)
        finally:
            self._disable_sync_to_namespace = False

    @abc.abstractmethod
    def _ui_state_from_value(self, value: Any) -> None: ...

    def sync_to_namespace(self) -> None:
        if self._disable_sync_to_namespace:
            return
        value = self._ui_state_to_value()
        try:
            self._disable_sync_from_namespace = True
            setattr(self.namespace, self.dest, value)
        finally:
            self._disable_sync_from_namespace = False

    @abc.abstractmethod
    def _ui_state_to_value(self) -> Any: ...

import argparse
import io
import logging
from typing import Any, Callable, Iterable

from nicegui import binding

logger = logging.getLogger("nicegooey.argparse")


class BindingNamespace(argparse.Namespace):
    _bindings: dict[str, binding.BindableProperty]

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        super().__setattr__("_bindings", {})

    def __setattr__(self, key: str, value: Any) -> None:
        if isinstance(value, binding.BindableProperty):
            self._bindings[key] = value
        elif not key.startswith("___"):
            b = binding.BindableProperty()
            b.__set_name__(self, key)
            b.__set__(self, value)
            self._bindings[key] = b
        else:
            super().__setattr__(key, value)

    def __getattr__(self, name: str) -> Any:
        _bindings = super().__getattribute__("_bindings")
        if name in _bindings:
            return _bindings[name]
        else:
            return super().__getattribute__(name)

    def to_pure_namespace(self) -> argparse.Namespace:
        """Returns a pure `argparse.Namespace` with the same values as this `BindingNamespace`."""
        ns = argparse.Namespace()
        for key in self._bindings:
            v = getattr(self, key).__get__(self)
            setattr(ns, key, v)
        return ns


class CallbackWriter(io.StringIO):
    """a StringIO-based object that calls a function on every write."""

    def __init__(self, callback: Callable[[str], ...], *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.callback = callback

    def write(self, s: str) -> int:
        result = super().write(s)
        self.callback(s)
        return result

    def writelines(self, lines: Iterable[str]) -> None:
        for line in lines:
            self.write(line)

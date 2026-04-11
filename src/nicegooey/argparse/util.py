import argparse
import io
import logging
import re
from typing import Any, Callable, Iterable

from nicegui import binding, app

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

    def __init__(self, callback: Callable[[str], object], *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.callback = callback

    def write(self, s: str) -> int:
        result = super().write(s)
        self.callback(s)
        return result

    def writelines(self, lines: Iterable[str]) -> None:  # type: ignore[override]
        for line in lines:
            self.write(line)


def parse_quasar_theme_variables(scss: str) -> None:
    """
    Given a list of SCSS variables, e.g. created by https://www.quasarui.com/tools/theme-builder, parses them and sets
    them as the nicegui theme.
    """
    colors = {}
    for m in re.finditer(r"^\$(\S+)\s*:\s*(#[0-9a-f]{6});", scss, re.MULTILINE):
        colors[m.group(1)] = m.group(2)
    app.colors(**colors)

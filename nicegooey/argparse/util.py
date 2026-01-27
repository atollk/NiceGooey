import argparse
import io
import logging
import typing

from nicegui import binding

logger = logging.getLogger("nicegooey.argparse")


class BindingNamespace(argparse.Namespace):
    def __init__(self, **kwargs: typing.Any) -> None:
        super().__init__(**kwargs)
        self._bindings: dict[str, binding.BindableProperty] = {}

    def __setattr__(self, key: str, value: typing.Any) -> None:
        if isinstance(value, binding.BindableProperty):
            self._bindings[key] = value
        else:
            super().__setattr__(key, value)

    def __getattr__(self, name: str) -> typing.Any:
        _bindings = super().__getattribute__("_bindings")
        if name in _bindings:
            return _bindings[name].value
        else:
            return super().__getattribute__(name)


class CallbackWriter(io.StringIO):
    """a StringIO-based object that calls a function on every write."""

    def __init__(self, callback: typing.Callable[[str], ...], *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.callback = callback

    def write(self, s: str) -> int:
        result = super().write(s)
        self.callback(s)
        return result

    def writelines(self, lines: typing.Iterable[str]) -> None:
        for line in lines:
            self.write(line)

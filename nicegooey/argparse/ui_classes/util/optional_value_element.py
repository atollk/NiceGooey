import typing

from nicegui.binding import bindable_properties, _propagate
from nicegui.elements.mixins.value_element import ValueElement
from nicegui import ui
from typing import Any, Callable, ClassVar

from nicegooey.argparse.ui_classes.util import DisableableDiv


class _BindablePropertyProxy:
    """Helper class inspired by nicegui.BindableProperty to allow defining a property on OptionalValueElement that can be bound to other properties, even though the actual value is stored in the inner element."""

    _getter: Callable[[Any], Any]
    _setter: Callable[[Any, Any], None]
    _change_handler: Callable[[Any, Any], Any] | None
    name: str | None = None

    def __init__(
        self,
        getter: Callable[["OptionalValueElement"], Any],
        setter: Callable[["OptionalValueElement", Any], None],
        on_change: Callable[["OptionalValueElement", Any], Any] | None = None,
    ) -> None:
        self._getter = getter
        self._setter = setter
        self._change_handler = on_change

    def set_name(self, name: str) -> None:
        self.name = name

    def get(self, owner: "OptionalValueElement") -> Any:
        return self._getter(owner)

    def set(self, owner: "OptionalValueElement", value: Any) -> None:
        assert self.name is not None
        self._setter(owner, value)
        key = (id(owner), str(self.name))
        bindable_properties[key] = owner
        _propagate(owner, self.name)
        if self._change_handler is not None:
            self._change_handler(owner, value)


class OptionalValueElement(ValueElement):
    """An element that can either have a value of a certain type or be None, with a checkbox to toggle between the two states."""

    value_proxy: ClassVar[_BindablePropertyProxy]
    value_proxy_last_value: Any = None
    inner_element: ValueElement
    checkbox: ui.checkbox

    class _ValueElementCallable(typing.Protocol):
        def __call__(self, *, value: Any) -> ValueElement: ...

    def __init__(self, *, inner: Callable[[], ValueElement]) -> None:
        with ui.row(align_items="center"):
            with DisableableDiv() as disableable_div:
                self.inner_element = inner()
                super().__init__(value=None)
            self.checkbox = ui.checkbox().props("dense")
        self.inner_element.on_value_change(self._sync_from_inner)
        self.checkbox.on_value_change(self._sync_from_inner)
        disableable_div.bind_enabled_from(self.checkbox, "value")

    @property
    def value(self):
        return self.value_proxy.get(self)

    @value.setter
    def value(self, value):
        if value != self.value_proxy_last_value:
            self.value_proxy.set(self, value)
            self.value_proxy_last_value = value

    def get_value_proxy(self) -> Any:
        if self.checkbox.value:
            return self.inner_element.value
        else:
            return None

    def set_value_proxy(self, value) -> None:
        if value is None:
            self.checkbox.value = False
            self.inner_element.value = None
        else:
            self.checkbox.value = True
            self.inner_element.value = value

    def _sync_from_inner(self) -> None:
        self.value = self.get_value_proxy()


OptionalValueElement.value_proxy = _BindablePropertyProxy(
    OptionalValueElement.get_value_proxy,
    OptionalValueElement.set_value_proxy,
    on_change=lambda sender, value: sender._handle_value_change(value),
)
OptionalValueElement.value_proxy.set_name("value_proxy")

from typing import Any

from nicegui import ui
from nicegui.elements.mixins.disableable_element import DisableableElement


class DisableableDiv(DisableableElement):
    """A div that can be disabled, i.e. have a disabled style and prevent interaction with its children."""

    _inner_loading: ui.element

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.style("position: relative")  # contain the q-inner-loading overlay within this div

        self._inner_loading = ui.element(tag="q-inner-loading")
        self._inner_loading.move(self)
        self._inner_loading.style("z-index: 100")  # make sure the loading overlay is above all children

        # Make the overlay transparent - we'll style the children instead
        self._inner_loading.props("dark=false")
        self._inner_loading.style("background: transparent")

        self._handle_enabled_change(True)

    def _handle_enabled_change(self, enabled: bool) -> None:
        self._inner_loading.props.set_bool("showing", not enabled)
        if enabled:
            self.style(remove="filter: grayscale(0.7) opacity(0.5); cursor: not-allowed")
        else:
            self.style("filter: grayscale(0.7) opacity(0.5); cursor: not-allowed")

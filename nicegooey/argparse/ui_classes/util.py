import argparse
import enum
import typing

from nicegui import ui
from nicegui.elements.mixins.disableable_element import DisableableElement
from nicegui.elements.mixins.value_element import ValueElement

from ..argument_parser import ArgumentParserConfig

if typing.TYPE_CHECKING:
    from ..main import NiceGooeyMain


class Nargs(enum.Enum):
    OPTIONAL = argparse.OPTIONAL
    ZERO_OR_MORE = argparse.ZERO_OR_MORE
    ONE_OR_MORE = argparse.ONE_OR_MORE
    PARSER = argparse.PARSER
    REMAINDER = argparse.REMAINDER
    SUPPRESS = argparse.SUPPRESS
    SINGLE_ELEMENT = "1"


class Validator(typing.Protocol):
    def validate(self) -> bool: ...


class UiWrapper(Validator):
    """Generic base class for most UI elements."""

    parent: "NiceGooeyMain"

    def __init__(self, parent: "NiceGooeyMain") -> None:
        self.parent = parent

    @property
    def parser_config(self) -> ArgumentParserConfig:
        assert self.parent.parser_config is not None
        return self.parent.parser_config

    def render(self) -> ui.element:
        return ui.element()

    def validate(self) -> bool:
        return True


class MaxWidthSelect(ui.select):
    """A select element that is as wide as its longest option, but no wider."""

    def __init__(self, options: list[str], **kwargs):
        super().__init__(options, **kwargs)

        # Reparent: wrap self in an inline-block div after creation
        longest = max((str(opt) for opt in options), key=len)
        assert self.parent_slot is not None
        with self.parent_slot.parent:
            with ui.element("div").classes("relative inline-block") as wrapper:
                # Hidden sizer with only the longest label
                with ui.element("div").classes(
                    "flex flex-col invisible h-0 overflow-hidden text-base whitespace-nowrap pl-3 pr-10"
                ):
                    ui.label(longest).classes("block")

        self.move(wrapper)
        self.classes("w-full")


class DisableableDiv(DisableableElement):
    """A div that can be disabled, i.e. have a disabled style and prevent interaction with its children."""

    _inner_loading: ui.element

    def __init__(self, **kwargs: typing.Any) -> None:
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


def clear_value_element(e: ValueElement) -> None:
    e.value = ""

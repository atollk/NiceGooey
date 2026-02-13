import argparse
import enum
import typing

from nicegui import ui

from .. import ArgumentParserConfig

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
    def __init__(self, options: list[str], **kwargs):
        super().__init__(options, **kwargs)

        # Reparent: wrap self in an inline-block div after creation
        longest = max((str(opt) for opt in options), key=len)
        with self.parent_slot.parent:
            with ui.element("div").classes("relative inline-block") as wrapper:
                # Hidden sizer with only the longest label
                with ui.element("div").classes(
                    "flex flex-col invisible h-0 overflow-hidden text-base whitespace-nowrap pl-3 pr-10"
                ):
                    ui.label(longest).classes("block")

        self.move(wrapper)
        self.classes("w-full")

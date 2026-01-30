import typing

from nicegui import ui

from . import ArgumentParserConfig

if typing.TYPE_CHECKING:
    from .main import NiceGooeyMain


class Validator(typing.Protocol):
    def validate(self) -> bool: ...


class UiWrapper(Validator):
    parent: "NiceGooeyMain"

    def __init__(self, parent: "NiceGooeyMain") -> None:
        self.parent = parent

    @property
    def parser_config(self) -> ArgumentParserConfig:
        return self.parent.parser_config

    def render(self) -> ui.element:
        return ui.element()

    def validate(self) -> bool:
        return True

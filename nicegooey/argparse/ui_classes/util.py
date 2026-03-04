import argparse
import enum
import typing

from nicegui import ui
import nicegui.binding

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


def unbind_to(
    self_obj: typing.Any, self_name: str, other_obj: typing.Any, other_name: str, strict: bool = False
) -> None:
    """Undo a bind_to call of a nicegui element."""
    key = (id(self_obj), self_name)
    if key not in nicegui.binding.bindings:
        if strict:
            raise ValueError(f"No bindings found for {self_obj}.{self_name}")
    else:
        new_bindings = [
            x
            for x in nicegui.binding.bindings[key]
            if self_obj is x[0] and other_obj is x[1] and other_name is x[2]
        ]
        if len(new_bindings) == len(nicegui.binding.bindings[key]) and strict:
            raise ValueError(f"No binding found from {self_obj}.{self_name} to {other_obj}.{other_name}")
        nicegui.binding.bindings[key] = new_bindings

    if key in nicegui.binding.bindable_properties:
        nicegui.binding.active_links = [
            x
            for x in nicegui.binding.active_links
            if not (self_obj is x[0] and self_name is x[1] and other_obj is x[2] and other_name is x[3])
        ]


def unbind_from(
    self_obj: typing.Any, self_name: str, other_obj: typing.Any, other_name: str, strict: bool = False
) -> None:
    """Undo a bind_from call of a nicegui element."""
    key = (id(other_obj), other_name)
    if key not in nicegui.binding.bindings:
        if strict:
            raise ValueError(f"No bindings found for {other_obj}.{other_name}")
    else:
        new_bindings = [
            x
            for x in nicegui.binding.bindings[key]
            if other_obj is x[0] and self_obj is x[1] and self_name is x[2]
        ]
        if len(new_bindings) == len(nicegui.binding.bindings[key]) and strict:
            raise ValueError(f"No binding found from {other_obj}.{other_name} to {self_obj}.{self_name}")
        nicegui.binding.bindings[key] = new_bindings

    if key in nicegui.binding.bindable_properties:
        nicegui.binding.active_links = [
            x
            for x in nicegui.binding.active_links
            if not (other_obj is x[0] and self_name is x[1] and self_obj is x[2] and self_name is x[3])
        ]


def unbind(
    self_obj: typing.Any, self_name: str, other_obj: typing.Any, other_name: str, strict: bool = False
) -> None:
    """Undo a bind call of a nicegui element."""
    unbind_to(self_obj, self_name, other_obj, other_name, strict)
    unbind_from(self_obj, self_name, other_obj, other_name, strict)

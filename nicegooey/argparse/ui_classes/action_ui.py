import argparse
import builtins
import typing

from nicegui import ui
from nicegui.elements.mixins import value_element

from ..main import NiceGooeyMain
from .util import UiWrapper


class ActionUi[ActionT: argparse.Action](UiWrapper):
    action: ActionT

    @staticmethod
    def from_action(parent: NiceGooeyMain, action: argparse.Action) -> "ActionUi | None":
        from .store_action_ui_element import StoreActionUiElement
        from .store_const_action_ui_element import StoreConstActionUiElement
        from .extend_action_ui_element import ExtendActionUiElement
        from .append_action_ui_element import AppendActionUiElement
        from .append_const_action_ui_element import AppendConstActionUiElement
        from .count_action_ui_element import CountActionUiElement

        match action:
            case argparse._StoreAction():
                return StoreActionUiElement(parent=parent, action=action)
            case argparse._StoreConstAction():
                return StoreConstActionUiElement(parent=parent, action=action)
            case argparse._ExtendAction():
                return ExtendActionUiElement(parent=parent, action=action)
            case argparse._AppendAction():
                return AppendActionUiElement(parent=parent, action=action)
            case argparse._AppendConstAction():
                return AppendConstActionUiElement(parent=parent, action=action)
            case argparse._CountAction():
                return CountActionUiElement(parent=parent, action=action)
            case argparse._HelpAction() | argparse._VersionAction() | argparse._SubParsersAction():
                # handled differently
                return None
            case _:
                raise NotImplementedError(f"UI for action type {type(action)} not implemented")

    def __init__(self, parent: NiceGooeyMain, action: ActionT) -> None:
        super().__init__(parent)
        self.action = action

    def render_action_name(self):
        with ui.row(align_items="center").mark("ng-action-name"):
            if isinstance(self.action.metavar, str):
                name = self.action.metavar
            elif isinstance(self.action.metavar, tuple):
                name = self.action.metavar[0]
            else:
                name = self.action.dest
            ui.label(name).classes("font-bold")
            if self.action.help:
                with ui.button(icon="question_mark").props("round padding=xs size=xs"):
                    ui.tooltip(self.action.help)

    def _action_type(self) -> typing.Callable[[str], typing.Any]:
        match self.action.type:
            case None:
                return str
            case argparse.FileType:
                raise NotImplementedError("argparse.FileType is deprecated and not supported.")
            case str():
                assert self.parent.parent_parser is not None
                return self.parent.parent_parser._registry_get("type", self.action.type)
            case _:
                return self.action.type

    def _action_type_input(self, *args, **kwargs) -> value_element.ValueElement:
        """Creates a ValueElement that represents the input of a single item matching the type of this action."""
        el: value_element.ValueElement
        if self.action.choices is not None:
            # TODO: make the size consistent
            choices = list(self.action.choices)
            # pyrefly: ignore[bad-keyword-argument]
            el = ui.select(options=choices, *args, **kwargs)
        else:
            match self._action_type():
                case builtins.bool:
                    el = ui.checkbox(*args, **kwargs)
                case builtins.int:
                    el = ui.number(format="%d", *args, **kwargs).props("dense")
                case builtins.float:
                    el = ui.number(format="%f", *args, **kwargs).props("dense")
                case builtins.str:
                    el = ui.input(*args, **kwargs).props("dense")
                case _:
                    el = ui.input(*args, **kwargs).props("dense")
        el.mark("ng-action-type-input")
        return el

    def _action_default(self) -> typing.Any:
        if self.action.default is not None:
            return self.action.default
        if self.action.choices is not None:
            return []
        else:
            match self._action_type():
                case builtins.bool:
                    return False
                case builtins.int | builtins.float:
                    return 0
                case _:
                    return ""

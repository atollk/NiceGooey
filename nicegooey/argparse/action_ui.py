import argparse
import builtins
import typing

import nicegui.element
from nicegui import ui
from nicegui.elements.mixins import value_element, validation_element

from .main import NiceGooeyMain


class ActionUi[ActionT: argparse.Action]:
    parent: NiceGooeyMain
    action: ActionT

    @staticmethod
    def from_action(parent: NiceGooeyMain, action: argparse.Action) -> "ActionUiElement":
        match action:
            case argparse._StoreAction():
                return StoreActionUiElement(parent=parent, action=action)
            case argparse._StoreConstAction():
                return StoreConstActionUiElement(parent=parent, action=action)
            case argparse._ExtendAction():
                pass  # TODO
                raise NotImplementedError()
            case argparse._AppendAction():
                pass  # TODO
                raise NotImplementedError()
            case argparse._AppendConstAction():
                pass  # TODO
                raise NotImplementedError()
            case argparse._CountAction():
                pass  # TODO
                raise NotImplementedError()
            case argparse._HelpAction() | argparse._VersionAction():
                # help and version are handled differently
                return ActionUiElement(parent, action)
            case argparse._SubParsersAction():
                pass  # TODO
                raise NotImplementedError()
            case _:
                raise NotImplementedError(f"UI for action type {type(action)} not implemented")

    def __init__(self, parent: NiceGooeyMain, action: ActionT) -> None:
        self.parent = parent
        self.action = action

    def _action_type(self) -> typing.Callable[[str], typing.Any]:
        if self.action.type is None:
            return str
        else:
            return self.action.type

    def render_action_name(self):
        with ui.column():
            ui.label(self.action.dest)
            if self.action.help:
                ui.label(self.action.help).classes("text-caption text-secondary")

    def render(self) -> None:
        pass

    def validate(self) -> bool:
        return True


class ActionUiElement[ActionT: argparse.Action, ElementT: nicegui.element.Element](ActionUi[ActionT]):
    element: ElementT | None = None

    def validate(self) -> bool:
        if isinstance(self.element, validation_element.ValidationElement):
            return self.element.validate()
        return True

    def on_change(self) -> None:
        if self.element is None:
            raise RuntimeError("ActionUiElement not rendered yet")
        self.action(self.parent.parent_parser, self.parent.namespace, self.element.value)

    def _validate_input_value(self, value: str) -> str | None:
        try:
            self._action_type()(value)
            return None
        except Exception as e:
            return str(e)


class StoreActionUiElement(ActionUiElement[argparse._StoreAction, value_element.ValueElement]):
    def render(self) -> None:
        match self._action_type():
            case builtins.bool:
                with ui.row():
                    self.element = ui.checkbox(
                        text="", value=bool(self.action.default or False), on_change=self.on_change
                    )
            case builtins.int:
                with ui.row():
                    self.element = ui.number(
                        value=self.action.default, format="%d", on_change=self.on_change
                    ).without_auto_validation()
                    self.render_action_name()
            case builtins.float:
                with ui.row():
                    self.element = ui.number(
                        value=self.action.default, format="%f", on_change=self.on_change
                    ).without_auto_validation()
                    self.render_action_name()
            case builtins.str:
                with ui.row():
                    self.element = ui.input(
                        value=self.action.default, on_change=self.on_change
                    ).without_auto_validation()
                    self.render_action_name()
            case _:
                with ui.row():
                    self.element = ui.input(
                        value=self.action.default,
                        validation=self._validate_input_value,
                        oon_change=self.on_change,
                    ).without_auto_validation()
                    self.render_action_name()


class StoreConstActionUiElement(ActionUiElement[argparse._StoreConstAction, value_element.ValueElement]):
    def render(self) -> None:
        with ui.row():
            self.element = ui.checkbox(text="", value=False, on_change=self.on_change)
            self.render_action_name()


class AppendActionUiElement(ActionUiElement):
    action: argparse._AppendAction
    element: value_element.ValueElement | None = None

    def render(self) -> None:
        match self.action.type:
            case builtins.int:
                with ui.row():
                    self.element = ui.number(
                        value=0, format="%d", on_change=self.on_change
                    ).without_auto_validation()
                    self.render_action_name()
            case builtins.float:
                with ui.row():
                    self.element = ui.number(
                        value=0.0, format="%f", on_change=self.on_change
                    ).without_auto_validation()
                    self.render_action_name()
            case builtins.str | None:
                with ui.row():
                    self.element = ui.input(value="", on_change=self.on_change).without_auto_validation()
                    self.render_action_name()
            case _:
                with ui.row():
                    self.element = ui.input(
                        value="", validation=self._validate_input_value, on_change=self.on_change
                    ).without_auto_validation()
                    self.render_action_name()


class AppendConstActionUiElement(ActionUiElement):
    action: argparse._AppendConstAction
    element: value_element.ValueElement | None = None

    def render(self) -> None:
        with ui.row():
            self.element = ui.input_chips(
                "", value=self.action.default, on_change=self.on_change
            ).without_auto_validation()
            self.render_action_name()


class CountActionUiElement(ActionUiElement):
    action: argparse._CountAction
    element: value_element.ValueElement | None = None

    def render(self) -> None:
        with ui.row():
            self.element = ui.number(value=0, format="%d", on_change=self.on_change).without_auto_validation()
            self.render_action_name()

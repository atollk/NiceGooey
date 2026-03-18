import abc
import argparse
from typing import Type, override

from nicegui import ui

from .action_info_helper import ActionInfoHelper
from .action_sync_element import ActionSyncElement
from ..util.ui_wrapper import UiWrapper
from ...main import NiceGooeyMain


class ActionUiElement[ActionT: argparse.Action](UiWrapper, abc.ABC):
    _UNSET = object()

    action: ActionT
    element: ActionSyncElement | None = None

    @staticmethod
    def from_action(parent: NiceGooeyMain, action: argparse.Action) -> "ActionUiElement | None":
        from .action_impls import (
            StoreActionUiElement,
            StoreConstActionUiElement,
            ExtendActionUiElement,
            AppendActionUiElement,
            AppendConstActionUiElement,
            CountActionUiElement,
        )

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

    @override
    def render(self) -> ui.element:
        c = ui.column()
        with c:
            self._render_action_name()
            self._render_input_element()
        return c

    @override
    def validate(self) -> bool:
        return self.element.validate()

    def deactivate(self) -> None:
        """Undoes any actions performed by this element and resets the namespace fields."""
        self.element.deactivate()

    @property
    def _action_info(self) -> ActionInfoHelper:
        assert self.parent.parent_parser is not None
        return ActionInfoHelper(self.action, self.parent.parent_parser)

    def _render_action_name(self):
        """Renders the name of this action (i.e. the metavar or dest) and a tooltip with the help text if it exists."""
        with ui.row(align_items="center"):
            if isinstance(self.action.metavar, str):
                name = self.action.metavar
            elif isinstance(self.action.metavar, tuple):
                name = self.action.metavar[0]
            elif self.action.option_strings:
                name = self.action.option_strings[0].lstrip(self.parent.parent_parser.prefix_chars)
            else:
                name = self.action.dest
            ui.label(name).classes("font-bold")
            if self.action.help:
                with ui.button(icon="question_mark") as btn:
                    # Styling
                    btn.props("round padding=xs size=xs")
                    # Non-focusable with keyboard
                    btn.props("tabindex='-1'")
                    # Tooltip on hover
                    ui.tooltip(self.action.help)

    @classmethod
    def _action_sync_element(cls) -> Type[ActionSyncElement]:
        return ActionSyncElement

    def _render_input_element(self) -> ActionSyncElement:
        """
        Creates/Renders the input element for this action and stores it in `self.element`.
        :return `self.element`
        """
        assert self.parent.parent_parser is not None
        self.element = self._action_sync_element()(
            action=self.action,
            parser=self.parent.parent_parser,
        )
        self.element.render()
        self.element.configure()
        return self.element

import argparse
from typing import TYPE_CHECKING, override, Iterable

from nicegui import ui

from .argument_group_ui import ArgumentGroupUi
from nicegooey.argparse.ui_classes.util.grouping_sync_ui import GroupingSyncUi, UiWrapperSyncElement
from .subparsers_ui import SubparsersUi

if TYPE_CHECKING:
    from nicegooey.argparse.main import NiceGooeyMain


class ParserUi(GroupingSyncUi):
    action_groups: list[ArgumentGroupUi]
    subparsers_action: argparse._SubParsersAction | None
    subparsers: SubparsersUi | None

    def __init__(self, parent: "NiceGooeyMain", parser: argparse.ArgumentParser) -> None:
        super().__init__(parent)
        self.parser = parser

        self.action_groups = [
            ArgumentGroupUi(self.parent, action_group) for action_group in self.parser._action_groups
        ]
        self.subparsers_action = None
        self.subparsers = None

        # Find subparsers action
        subparser_group = self.parser._subparsers
        if subparser_group is not None:
            assert len(subparser_group._group_actions) == 1
            subparsers_action = subparser_group._group_actions[0]
            if not isinstance(subparsers_action, argparse._SubParsersAction):
                raise TypeError(
                    f"subparsers action must be of type argparse._SubParsersAction but is {type(subparsers_action)}"
                )
            self.subparsers_action = subparsers_action
            self.subparsers = SubparsersUi(parent=self.parent, subparsers_action=self.subparsers_action)

    @override
    def render(self) -> ui.element:
        with ui.column() as root:
            for child in self.action_groups:
                child.render()

            if self.subparsers:
                self.subparsers.render()
        return root

    @override
    def get_children(self) -> Iterable[UiWrapperSyncElement]:
        yield from self.action_groups
        if self.subparsers:
            yield self.subparsers

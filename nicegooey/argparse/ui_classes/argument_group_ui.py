import argparse
import typing

from nicegui import ui

from nicegooey.argparse.ui_classes.action_ui_element import ActionUiElement
from .util import UiWrapper

if typing.TYPE_CHECKING:
    from ..main import NiceGooeyMain
    from .mutually_exclusive_group_ui import MutuallyExclusiveGroupUi


class ArgumentGroupUi(UiWrapper):
    children: list["ActionUiElement | MutuallyExclusiveGroupUi"]
    group: argparse._ArgumentGroup

    def __init__(self, parent: "NiceGooeyMain", group: argparse._ArgumentGroup) -> None:
        from .mutually_exclusive_group_ui import MutuallyExclusiveGroupUi

        super().__init__(parent)
        self.group = group
        self.children = []

        mutually_exclusive_groups_done = set()
        for action in self.group._group_actions:
            me_group = next(
                (
                    me_group
                    for me_group in self.group._mutually_exclusive_groups
                    if action in me_group._group_actions
                ),
                None,
            )
            if me_group is None:
                ui_container = ActionUiElement.from_action(self.parent, action)
            else:
                if me_group in mutually_exclusive_groups_done:
                    continue
                mutually_exclusive_groups_done.add(me_group)
                ui_container = MutuallyExclusiveGroupUi(self.parent, me_group)
            if ui_container is not None:
                self.children.append(ui_container)

    @typing.override
    def validate(self) -> bool:
        validation_failed = False
        for child in self.children:
            validation_failed = child.validate() or validation_failed
        return not validation_failed

    def _render_action(self, action: argparse.Action) -> ui.element:
        ui_container = ActionUiElement.from_action(self.parent, action)
        if ui_container is not None:
            self.children.append(ui_container)
            with ui.item().classes("border-2"):
                return ui_container.render().mark(f"ng-action-{action.dest}")
        else:
            return ui.element()

    @typing.override
    def render(self) -> ui.element:
        if not self.children:
            return ui.element()
        with ui.card().classes("w-full").mark(f"ng-group-{self.group.title}") as root:
            ui.label(self.group.title or "").classes("text-lg font-bold mb-2")
            with ui.list().classes("flex justify-between"):
                for child in self.children:
                    if isinstance(child, ActionUiElement):
                        with ui.item().classes("border-2"):
                            child.render().mark(f"ng-action-{child.action.dest}")
                    else:
                        with ui.card():
                            child.render()
        return root

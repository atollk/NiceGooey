import argparse
from typing import TYPE_CHECKING, Literal, override, Iterable

import nicegui.events
from nicegui import ui

from nicegooey.argparse.ui_classes.actions.action_ui_element import ActionUiElement
from nicegooey.argparse.ui_classes.util.grouping_sync_ui import UiWrapperSyncElement, GroupingSyncUi

if TYPE_CHECKING:
    from nicegooey.argparse.main import NiceGooeyMain


class MutuallyExclusiveGroupUi(GroupingSyncUi):
    group: argparse._MutuallyExclusiveGroup
    active_element: ActionUiElement | None

    def __init__(self, parent: "NiceGooeyMain", group: argparse._MutuallyExclusiveGroup) -> None:
        super().__init__(parent)
        self.group = group
        self.active_element = None

    def _render_action(self, action: argparse.Action | Literal[""]) -> ui.element:
        if action == "":
            return ui.element()

        # "Patch" the action to have required=True. In the vanilla argparse, this is disallowed, but for the UI logic it actually makes sense as the selection process already covers the optionality.
        # If we wouldn't do this, there would be a checkbox to enable the argument after it has been selected.
        action.required = True

        ui_container = ActionUiElement.from_action(self.parent, action)
        self.active_element = ui_container
        if ui_container is not None:
            with ui.item().classes("border-2"):
                return ui_container.render().mark(f"ng-action-{action.dest}")
        else:
            return ui.element()

    def _build_action_choice_names(self) -> dict[argparse.Action, str]:
        choices: dict[argparse.Action, str] = {}
        for action in self.group._group_actions:
            if isinstance(action.metavar, str):
                action_name = action.metavar
            elif isinstance(action.metavar, tuple):
                action_name = action.metavar[0]
            elif len(action.option_strings) > 0:
                action_name = max(action.option_strings, key=len)
            else:
                action_name = action.dest
            choices[action] = action_name
        return choices

    @override
    def render(self) -> ui.element:
        render_action = ui.refreshable(self._render_action)
        choices = self._build_action_choice_names()

        def on_selector_change(ev: nicegui.events.ValueChangeEventArguments) -> None:
            # Undo the previous action
            if self.active_element is not None:
                self.active_element.deactivate()
            # Render the next action
            render_action.refresh(ev.value)

        with ui.row(align_items="center").mark("ng-me-group") as root:
            default_choice = self.group._group_actions[0]
            if not choices:
                raise RuntimeError(f"Mutually exclusive group must not be empty: {self.group}")
            if not self.group.required:
                choices = {**{"": "-"}, **choices}  # should be the first item
                default_choice = ""
            selector = ui.select(
                choices,
                value=default_choice,
                on_change=on_selector_change,
            )
            render_action(selector.value)
        return root

    @override
    def get_children(self) -> Iterable[UiWrapperSyncElement]:
        if self.active_element:
            yield self.active_element

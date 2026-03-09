import argparse
import typing

from nicegui import ui
import nicegui.events

from .actions.action_info_helper import ActionInfoHelper
from .actions.action_ui_element import ActionUiElement
from .util import UiWrapper

if typing.TYPE_CHECKING:
    from ..main import NiceGooeyMain


class MutuallyExclusiveGroupUi(UiWrapper):
    group: argparse._MutuallyExclusiveGroup
    active_element: UiWrapper | None

    def __init__(self, parent: "NiceGooeyMain", group: argparse._MutuallyExclusiveGroup) -> None:
        super().__init__(parent)
        self.group = group
        self.active_element = None

    @typing.override
    def validate(self) -> bool:
        return self.active_element is None or self.active_element.validate()

    def _render_action(self, action: argparse.Action | None) -> ui.element:
        if action is None:
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

    def _build_action_choice_names(self) -> dict[argparse.Action | None, str]:
        choices: dict[argparse.Action | None, str] = {}
        for action in self.group._group_actions:
            if isinstance(action.metavar, str):
                action_name = action.metavar
            elif isinstance(action.metavar, tuple):
                action_name = action.metavar[0]
            elif len(action.option_strings) > 0:
                action_name = action.option_strings[0]
            else:
                action_name = action.dest
            choices[action] = action_name
        return choices

    @typing.override
    def render(self) -> ui.element:
        render_action = ui.refreshable(self._render_action)
        choices = self._build_action_choice_names()

        def on_selector_change(ev: nicegui.events.ValueChangeEventArguments) -> None:
            # Undo the previous action
            previous_action = next(
                (action for action, label in choices.items() if label == ev.previous_value["label"]), None
            )
            if isinstance(previous_action, argparse.Action):
                setattr(
                    self.parent.namespace,
                    previous_action.dest,
                    ActionInfoHelper(
                        action=previous_action, parser=self.parent.parent_parser
                    ).action_default(),
                )
            # Render the next action
            render_action.refresh(ev.value)

        with ui.row(align_items="center").mark("ng-me-group") as root:
            default_choice = self.group._group_actions[0]
            if not choices:
                raise RuntimeError(f"Mutually exclusive group must not be empty: {self.group}")
            if not self.group.required:
                choices = {**{None: "-"}, **choices}  # should be the first item
                default_choice = None
            selector = ui.select(
                choices,
                value=default_choice,
                on_change=on_selector_change,
            )
            render_action(selector.value)
        return root

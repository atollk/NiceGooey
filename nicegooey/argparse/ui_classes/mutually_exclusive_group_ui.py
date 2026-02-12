import argparse
import typing

from nicegui import ui

from .util import UiWrapper
from .action_ui import ActionUi

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

    def _render_action(self, action: argparse.Action) -> ui.element:
        ui_container = ActionUi.from_action(self.parent, action)
        self.active_element = ui_container
        if ui_container is not None:
            with ui.item().classes("border-2"):
                return ui_container.render().mark(f"ng-action-{action.dest}")
        else:
            return ui.element()

    @typing.override
    def render(self) -> ui.element:
        render_action = ui.refreshable(self._render_action)

        with ui.row(align_items="center").mark("ng-me-group") as root:
            choices = {action: (action.metavar or action.dest) for action in self.group._group_actions}
            if not choices:
                raise RuntimeError(f"Mutually exclusive group must not be empty: {self.group}")
            selector = ui.select(
                choices,
                value=self.group._group_actions[0],
                on_change=lambda val: render_action.refresh(val.value),
            )
            render_action(selector.value)
        return root

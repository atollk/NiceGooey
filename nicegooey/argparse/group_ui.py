import argparse
import typing

from nicegui import ui

from .ui_util import UiWrapper
from .action_ui import ActionUi

if typing.TYPE_CHECKING:
    from .main import NiceGooeyMain


class RootUi(UiWrapper):
    children: list["ArgumentGroupUi"]

    def __init__(self, parent: "NiceGooeyMain") -> None:
        super().__init__(parent)
        self.children = []

    @typing.override
    def render(self) -> ui.element:
        with ui.column(align_items="center").props("data-testid=ng-root") as root:
            # TODO: dark mode to save my eyes
            dark = ui.dark_mode(True)
            with ui.row():
                ui.label("Switch mode:")
                ui.button("Dark", on_click=dark.enable)
                ui.button("Light", on_click=dark.disable)

            width = (
                self.parser_config.argument_vp_width
                if isinstance(self.parser_config.argument_vp_width, str)
                else f"w-{self.parser_config.argument_vp_width}"
            )
            parent_parser = self.parent.parent_parser
            assert parent_parser is not None
            with ui.column().classes(width):
                for action_group in parent_parser._action_groups:
                    action_group = ArgumentGroupUi(self.parent, action_group)
                    self.children.append(action_group)
                    action_group.render()
            on_submit = self.parent.submit
            ui.button("Submit").on_click(on_submit)
        return root

    @typing.override
    def validate(self) -> bool:
        validation_failed = False
        for child in self.children:
            validation_failed = child.validate() or validation_failed
        return not validation_failed


class ArgumentGroupUi(UiWrapper):
    children: list[UiWrapper]
    group: argparse._ArgumentGroup

    def __init__(self, parent: "NiceGooeyMain", group: argparse._ArgumentGroup) -> None:
        super().__init__(parent)
        self.children = []
        self.group = group

    @typing.override
    def validate(self) -> bool:
        validation_failed = False
        for child in self.children:
            validation_failed = child.validate() or validation_failed
        return not validation_failed

    def _render_action(self, action: argparse.Action) -> ui.element:
        ui_container = ActionUi.from_action(self.parent, action)
        if ui_container is not None:
            self.children.append(ui_container)
            with ui.item().classes("border-2"):
                return ui_container.render().props(f"data-testid=ng-action-{action.dest}")
        else:
            return ui.element()

    @typing.override
    def render(self) -> ui.element:
        mutually_exclusive_groups_done = set()
        with ui.card().classes("w-full").props(f"data-testid=ng-group-{self.group.title}") as root:
            ui.label(self.group.title or "").classes("text-lg font-bold mb-2")
            with ui.list().classes("flex justify-between"):
                for action in self.group._group_actions:
                    # If this action is part of a mutually exclusive group, render that entire group at this point, if it has not been rendered already.
                    me_group = next(
                        (
                            me_group
                            for me_group in self.group._mutually_exclusive_groups
                            if action in me_group._group_actions
                        ),
                        None,
                    )
                    if me_group is None:
                        self._render_action(action)
                    else:
                        if me_group in mutually_exclusive_groups_done:
                            continue
                        mutually_exclusive_groups_done.add(me_group)
                        me_group_ui = MutuallyExclusiveGroupUi(self.parent, me_group)
                        self.children.append(me_group_ui)
                        me_group_ui.render()
        return root


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
                return ui_container.render().props(f"data-testid=ng-action-{action.dest}")
        else:
            return ui.element()

    @typing.override
    def render(self) -> ui.element:
        render_action = ui.refreshable_method(self._render_action)

        with ui.row(align_items="center").props("data-testid=ng-me-group") as root:
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

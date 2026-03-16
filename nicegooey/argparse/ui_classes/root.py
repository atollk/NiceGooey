import argparse
import typing

from nicegui import ui

from .groupings.argument_group_ui import ArgumentGroupUi
from .groupings.subparsers_ui import SubparsersUi
from .util.ui_wrapper import UiWrapper

if typing.TYPE_CHECKING:
    from ..main import NiceGooeyMain


class RootUi(UiWrapper):
    action_groups: list[ArgumentGroupUi]
    subparsers_action: argparse._SubParsersAction | None
    subparsers: SubparsersUi | None

    def __init__(self, parent: "NiceGooeyMain") -> None:
        super().__init__(parent)

        parent_parser = self.parent.parent_parser
        assert parent_parser is not None

        self.action_groups = [
            ArgumentGroupUi(self.parent, action_group) for action_group in parent_parser._action_groups
        ]
        self.subparsers_action = None
        self.subparsers = None

        # Find subparsers action
        subparser_group = parent_parser._subparsers
        if subparser_group is not None:
            assert len(subparser_group._group_actions) == 1
            subparsers_action = subparser_group._group_actions[0]
            if not isinstance(subparsers_action, argparse._SubParsersAction):
                raise TypeError(
                    f"subparsers action must be of type argparse._SubParsersAction but is {type(subparsers_action)}"
                )
            self.subparsers_action = subparsers_action
            self.subparsers = SubparsersUi(parent=self.parent, subparsers_action=self.subparsers_action)

    @typing.override
    def render(self) -> ui.element:
        with ui.column().mark("ng-root") as root:
            with ui.column(align_items="center"):
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
                with ui.card():
                    with ui.column().classes(width):
                        for child in self.action_groups:
                            child.render()

                        if self.subparsers:
                            self.subparsers.render()

                    # Submit button
                    on_submit = self.parent.submit
                    ui.button("Submit").on_click(on_submit)

            with ui.column(align_items="end"):
                # TODO: nicer license info
                ui.link("License", "/license")
        return root

    @typing.override
    def validate(self) -> bool:
        group_validations = [group.validate() for group in self.action_groups]
        subparsers_validation = self.subparsers.validate() if self.subparsers is not None else True
        return all(group_validations) and subparsers_validation

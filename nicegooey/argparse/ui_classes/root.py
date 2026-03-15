import argparse
import typing

from nicegui import ui

from .argument_group_ui import ArgumentGroupUi
from .subparser_ui import SubparserUi
from .util.ui_wrapper import UiWrapper

if typing.TYPE_CHECKING:
    from ..main import NiceGooeyMain


class RootUi(UiWrapper):
    action_groups: list[ArgumentGroupUi]
    subparsers_action: argparse._SubParsersAction | None
    subparsers: list[SubparserUi]

    def __init__(self, parent: "NiceGooeyMain") -> None:
        super().__init__(parent)

        parent_parser = self.parent.parent_parser
        assert parent_parser is not None

        self.action_groups = [
            ArgumentGroupUi(self.parent, action_group) for action_group in parent_parser._action_groups
        ]
        self.subparsers_action = None
        self.subparsers = []

        # Collect subparsers
        subparser_group = parent_parser._subparsers
        if subparser_group is not None:
            assert len(subparser_group._group_actions) == 1
            subparsers_action = subparser_group._group_actions[0]
            if not isinstance(subparsers_action, argparse._SubParsersAction):
                raise TypeError(
                    f"subparsers action must be of type argparse._SubParsersAction but is {type(subparsers_action)}"
                )
            self.subparsers_action = subparsers_action
            subparsers = self.subparsers_action.choices
            assert isinstance(subparsers, dict)
            self.subparsers = [
                SubparserUi(self.parent, title, subparser) for title, subparser in subparsers.items()
            ]

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
                            self._render_subparsers()

                    # Submit button
                    on_submit = self.parent.submit
                    ui.button("Submit").on_click(on_submit)

            with ui.column(align_items="end"):
                # TODO: nicer license info
                ui.link("License", "/license")
        return root

    def _render_subparsers(self) -> None:
        assert self.subparsers is not None
        assert self.subparsers_action is not None
        none_tab = None
        with ui.tabs() as ui_tabs:
            if not self.subparsers_action.required:
                none_tab = ui.tab("-")
            for child in self.subparsers:
                child.render_tab()
        with ui.tab_panels(ui_tabs, value=self.subparsers[0].tab if none_tab is None else none_tab):
            if none_tab is not None:
                ui.tab_panel(none_tab)
            for child in self.subparsers:
                child.render_tab_panel()

    @typing.override
    def validate(self) -> bool:
        group_validations = [group.validate() for group in self.action_groups]
        subparser_validations = [subparser.validate() for subparser in self.subparsers]
        return all(group_validations) and all(subparser_validations)

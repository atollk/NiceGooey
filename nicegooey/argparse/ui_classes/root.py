import argparse
import typing

from nicegui import ui

from .group import ArgumentGroupUi
from .util import UiWrapper

if typing.TYPE_CHECKING:
    from ..main import NiceGooeyMain


class RootUi(UiWrapper):
    action_groups: list[ArgumentGroupUi]
    subparsers_action: argparse._SubParsersAction | None
    subparsers: list["SubparserUi"]

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
            with ui.card():
                with ui.column().classes(width):
                    for child in self.action_groups:
                        child.render()

                    if self.subparsers:
                        none_tab = None
                        with ui.tabs() as ui_tabs:
                            if not self.subparsers_action.required:
                                none_tab = ui.tab("-")
                            for child in self.subparsers:
                                child.render_tab()
                        with ui.tab_panels(
                            ui_tabs, value=self.subparsers[0].tab if none_tab is None else none_tab
                        ):
                            if none_tab is not None:
                                ui.tab_panel(none_tab)
                            for child in self.subparsers:
                                child.render_tab_panel()

                # Submit button
                on_submit = self.parent.submit
                ui.button("Submit").on_click(on_submit)
        return root

    @typing.override
    def validate(self) -> bool:
        validation_failed = False
        for group in self.action_groups:
            validation_failed = group.validate() or validation_failed
        for subparser in self.subparsers:
            validation_failed = subparser.validate() or validation_failed
        return not validation_failed


class SubparserUi(UiWrapper):
    title: str
    subparser: argparse.ArgumentParser
    tab: ui.tab | None
    action_groups: list[ArgumentGroupUi]

    def __init__(self, parent: "NiceGooeyMain", title: str, subparser: argparse.ArgumentParser) -> None:
        super().__init__(parent)
        self.title = title
        self.subparser = subparser
        self.tab = None
        self.action_groups = [
            ArgumentGroupUi(self.parent, action_group) for action_group in self.subparser._action_groups
        ]

    def render_tab(self) -> ui.tab:
        self.tab = ui.tab(self.subparser.prog).props(f"data-testid=ng-subparser-tab-{self.title}")
        return self.tab

    def render_tab_panel(self) -> ui.tab_panel:
        assert self.tab is not None
        panel = ui.tab_panel(self.tab).props(f"data-testid=ng-subparser-tabpanel-{self.title}")
        with panel:
            for group in self.action_groups:
                group.render()
        return panel

    @typing.override
    def render(self) -> ui.element:
        raise NotImplementedError("use render_tab and render_tab_panel")

    @typing.override
    def validate(self) -> bool:
        assert self.tab is not None
        assert self.tab.parent_slot is not None
        tabs = self.tab.parent_slot.parent
        if not isinstance(tabs, ui.tabs):
            raise TypeError(f"expected tabs to be of type ui.tabs but is {type(tabs)}")
        if tabs.value != self.tab:
            return True

        validation_failed = False
        for group in self.action_groups:
            validation_failed = group.validate() or validation_failed
        return not validation_failed

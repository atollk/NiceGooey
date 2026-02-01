import argparse
import typing

from nicegui import ui

from .group import ArgumentGroupUi
from .util import UiWrapper

if typing.TYPE_CHECKING:
    from ..main import NiceGooeyMain


class RootUi(UiWrapper):
    action_groups: list[ArgumentGroupUi]
    subparsers: list["SubparserUi"]

    def __init__(self, parent: "NiceGooeyMain") -> None:
        super().__init__(parent)
        self.action_groups = []
        self.subparsers = []

    @typing.override
    def render(self) -> ui.element:
        with ui.column(align_items="center").props("data-testid=ng-root") as root:
            # TODO: dark mode to save my eyes
            dark = ui.dark_mode(True)
            with ui.row():
                ui.label("Switch mode:")
                ui.button("Dark", on_click=dark.enable)
                ui.button("Light", on_click=dark.disable)

            parent_parser = self.parent.parent_parser
            assert parent_parser is not None

            # Collect action groups
            self.action_groups = [
                ArgumentGroupUi(self.parent, action_group) for action_group in parent_parser._action_groups
            ]

            # Collect subparsers
            subparser_group = parent_parser._subparsers
            if subparser_group is not None:
                assert len(subparser_group._group_actions) == 1
                subparsers_action = subparser_group._group_actions[0]
                subparsers = subparsers_action.choices
                assert isinstance(subparsers, dict)
                self.subparsers = [
                    SubparserUi(self.parent, title, subparser) for title, subparser in subparsers.items()
                ]

            # Render everything
            width = (
                self.parser_config.argument_vp_width
                if isinstance(self.parser_config.argument_vp_width, str)
                else f"w-{self.parser_config.argument_vp_width}"
            )
            with ui.card():
                with ui.column().classes(width):
                    for child in self.action_groups:
                        child.render()
                    with ui.tabs() as ui_tabs:
                        for child in self.subparsers:
                            child.render_tab()
                    # TODO: support optional subparsers
                    with ui.tab_panels(ui_tabs, value=self.subparsers[0].tab):
                        for child in self.subparsers:
                            child.render_tab_panel()

                # Submit button
                on_submit = self.parent.submit
                ui.button("Submit").on_click(on_submit)
        return root

    @typing.override
    def validate(self) -> bool:
        validation_failed = False
        for child in self.action_groups:
            validation_failed = child.validate() or validation_failed
        return not validation_failed


class SubparserUi(UiWrapper):
    title: str
    subparser: argparse.ArgumentParser
    tab: ui.tab | None

    def __init__(self, parent: "NiceGooeyMain", title: str, subparser: argparse.ArgumentParser) -> None:
        super().__init__(parent)
        self.title = title
        self.subparser = subparser
        self.tab = None

    def render_tab(self) -> ui.tab:
        self.tab = ui.tab(self.subparser.prog)
        return self.tab

    def render_tab_panel(self) -> ui.tab_panel:
        assert self.tab is not None
        panel = ui.tab_panel(self.tab)
        with panel:
            ui.label("TODO")
        return panel

    @typing.override
    def render(self) -> ui.element:
        raise NotImplementedError("use render_tab and render_tab_panel")

    @typing.override
    def validate(self) -> bool:
        # TODO
        return True

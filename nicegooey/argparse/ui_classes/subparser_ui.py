import argparse
import typing

from nicegui import ui

from .util import UiWrapper
from .argument_group_ui import ArgumentGroupUi

if typing.TYPE_CHECKING:
    from ..main import NiceGooeyMain


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
        self.tab = ui.tab(self.subparser.prog).mark(f"ng-subparser-tab-{self.title}")
        return self.tab

    def render_tab_panel(self) -> ui.tab_panel:
        assert self.tab is not None
        panel = ui.tab_panel(self.tab).mark(f"ng-subparser-tabpanel-{self.title}")
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

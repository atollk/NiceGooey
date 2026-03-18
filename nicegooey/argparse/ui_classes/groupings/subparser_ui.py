import argparse
from typing import TYPE_CHECKING, Final, override, Iterable

from nicegui import ui


from .argument_group_ui import ArgumentGroupUi
from ..util.grouping_sync_ui import UiWrapperSyncElement, GroupingSyncUi

if TYPE_CHECKING:
    from nicegooey.argparse.main import NiceGooeyMain
    from .parser_ui import ParserUi


class SubparserUi(GroupingSyncUi):
    TAB_MARKER_PREFIX: Final[str] = "ng-subparser-tab-"
    TABPANEL_MARKER_PREFIX: Final[str] = "ng-subparser-tabpanel-"

    title: str
    subparser: argparse.ArgumentParser
    tab: ui.tab | None
    parser_ui: "ParserUi"
    action_groups: list[ArgumentGroupUi]

    def __init__(self, parent: "NiceGooeyMain", title: str, subparser: argparse.ArgumentParser) -> None:
        from .parser_ui import ParserUi

        super().__init__(parent)
        self.title = title
        self.subparser = subparser
        self.tab = None
        self.parser_ui = ParserUi(parent=parent, parser=self.subparser)

    def render_tab(self) -> ui.tab:
        self.tab = ui.tab(self.title).mark(f"{SubparserUi.TAB_MARKER_PREFIX}{self.title}")
        return self.tab

    def render_tab_panel(self) -> ui.tab_panel:
        assert self.tab is not None
        panel = ui.tab_panel(self.tab).mark(f"{SubparserUi.TABPANEL_MARKER_PREFIX}{self.title}")
        with panel:
            self.parser_ui.render()
        return panel

    @override
    def render(self) -> ui.element:
        raise NotImplementedError("use render_tab and render_tab_panel")

    @override
    def validate(self) -> bool:
        assert self.tab is not None
        assert self.tab.parent_slot is not None
        tabs = self.tab.parent_slot.parent
        if not isinstance(tabs, ui.tabs):
            raise TypeError(f"expected tabs to be of type ui.tabs but is {type(tabs)}")
        if tabs.value != self.tab:
            return True

        return self.parser_ui.validate()

    @override
    def get_children(self) -> Iterable[UiWrapperSyncElement]:
        yield self.parser_ui

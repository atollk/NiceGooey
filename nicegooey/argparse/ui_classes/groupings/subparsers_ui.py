import argparse
from typing import TYPE_CHECKING, Any, override

import nicegui.events
from nicegui import ui

from nicegooey.argparse.ui_classes.util.sync_element import SyncElement
from nicegooey.argparse.ui_classes.util.ui_wrapper import UiWrapper

from .subparser_ui import SubparserUi

if TYPE_CHECKING:
    from nicegooey.argparse.main import NiceGooeyMain, NiceGooeyNamespace


class SubparsersUi(UiWrapper, SyncElement):
    subparsers_action: argparse._SubParsersAction
    subparsers: list[SubparserUi]
    ui_tabs: ui.tabs | None
    ui_tab_panels: ui.tab_panels | None
    active_tab_title: str | None

    def __init__(self, parent: "NiceGooeyMain", subparsers_action: argparse._SubParsersAction) -> None:
        UiWrapper.__init__(self, parent)
        SyncElement.__init__(self)
        self.subparsers_action = subparsers_action

        subparsers: dict[str, argparse.ArgumentParser] = self.subparsers_action.choices
        assert isinstance(subparsers, dict)
        self.subparsers = [
            SubparserUi(
                parent=self.parent, title=title, get_parent_tabs=lambda: self.ui_tabs, subparser=subparser
            )
            for title, subparser in subparsers.items()
        ]

        self.ui_tabs = None
        self.ui_tab_panels = None

    @override
    @property
    def namespace(self) -> "NiceGooeyNamespace":
        return self.parent.namespace

    @override
    @property
    def dest(self) -> str:
        return self.subparsers_action.dest

    @override
    def _ui_state_from_value(self, value: Any) -> None:
        assert self.ui_tab_panels is not None
        self.ui_tab_panels.value = value

    @override
    def _ui_state_to_value(self) -> Any:
        return self.active_tab_title

    def _render_tab_panels(self, none_tab: ui.tab | None):
        def on_tab_change(ev: nicegui.events.ValueChangeEventArguments) -> None:
            # Deactivate the previous tab
            child: SubparserUi | None = None
            if self.active_tab_title is not None:
                child = next(p for p in self.subparsers if p.title == self.active_tab_title)
                child.deactivate()
            # Memorize the next tab
            self.active_tab_title = ev.value
            # Store in namespace
            self.sync_to_namespace()
            if child is not None:
                child.sync_to_namespace()

        if none_tab is not None:
            self.active_tab_title = None
            init_panel = none_tab
        else:
            self.active_tab_title = self.subparsers[0].title
            init_panel = self.subparsers[0].tab
        with ui.tab_panels(self.ui_tabs, value=init_panel) as self.ui_tab_panels:
            if none_tab is not None:
                ui.tab_panel(none_tab)
            for child in self.subparsers:
                child.render_tab_panel()
        self.ui_tab_panels.on_value_change(callback=on_tab_change)

    @override
    def render(self) -> ui.element:
        assert self.subparsers is not None
        assert self.subparsers_action is not None

        none_tab = None
        with ui.element() as root:
            with ui.tabs() as self.ui_tabs:
                # Required row wrapper so that too many tabs don't overflow but wrap around to a new line instead.
                with ui.row():
                    tab_list: list[ui.tab] = []
                    if not self.subparsers_action.required:
                        none_tab = ui.tab("-")
                        tab_list.append(none_tab)
                    for child in self.subparsers:
                        t = child.render_tab()
                        tab_list.append(t)

                    # https://github.com/zauberzeug/nicegui/issues/5885#issuecomment-4105965436
                    for t in tab_list:
                        t.tabs = self.ui_tabs

            self._render_tab_panels(none_tab)

        self.subscribe()
        self.sync_to_namespace()
        return root

    def deactivate(self) -> None:
        for subp in self.subparsers:
            subp.deactivate()

    @override
    def validate(self) -> bool:
        # Use a list rather than a generator to prevent lazy evaluation.
        return all([subparser.validate() for subparser in self.subparsers])

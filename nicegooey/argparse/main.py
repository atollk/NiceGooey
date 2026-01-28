import argparse
import contextlib
import typing

import nicegui.run
from nicegui import ui
from nicegui.elements.mixins import validation_element

if typing.TYPE_CHECKING:
    from .action_ui import ActionUi

from .util import BindingNamespace, logger, CallbackWriter
from .argument_parser import ArgumentParserConfig, NgArgumentParser


class NiceGooeyMain:
    # State
    parent_parser: argparse.ArgumentParser | None
    main_func: typing.Callable | None
    is_running: bool
    parser_config: ArgumentParserConfig

    # Argument values
    namespace: BindingNamespace

    # UI elements
    action_elements: dict[argparse.Action, "ActionUi"]

    def __init__(self):
        self.parent_parser = None
        self.main_func = None
        self.is_running = False
        self.namespace = BindingNamespace()
        self.action_elements = {}

    def parse_args(
        self,
        argument_parser: argparse.ArgumentParser,
    ) -> argparse.Namespace | typing.Never:
        if self.is_running:
            return self._get_namespace()
        else:
            self.is_running = True
            self.parent_parser = argument_parser
            if isinstance(self.parent_parser, NgArgumentParser):
                self.parser_config = self.parent_parser.nicegooey_config
            else:
                self.parser_config = ArgumentParserConfig()
            ui.run(root=self._ui_root, reload=False)
            raise AssertionError("nicegui.ui.run should not return")

    def _get_namespace(self) -> argparse.Namespace:
        if self.parent_parser is None:
            raise RuntimeError("NiceGooeyMain has no parent parser set")
        return self.namespace

    async def _submit(self) -> None:
        # Validate
        validation_error = False
        for action, element in self.action_elements.items():
            # TODO: failed validation isn't visible in the UI
            validation_error = validation_element or not element.validate()
        if validation_error:
            logger.warning(f"Validation error: {validation_error}")
            return

        # Process result
        assert self.main_func is not None
        dialog = ui.dialog()
        with dialog:
            with ui.card():
                terminal = ui.xterm()
                finish_button = ui.button("Close", on_click=dialog.close)
        finish_button.disable()
        dialog.open()
        write_terminal: typing.Callable[[str], typing.Any] = terminal.write
        file_buffer = CallbackWriter(write_terminal)
        with contextlib.redirect_stdout(file_buffer):
            await nicegui.run.io_bound(self.main_func)
        finish_button.enable()

    def _ui_root(self) -> None:
        if self.main_func is None:
            raise RuntimeError("NiceGooeyMain.parse_args called outside of nice_gooey_argparse_main")

        with ui.column(align_items="center").props("data-testid=ng-root"):
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
            assert self.parent_parser is not None
            with ui.column().classes(width):
                for action_group in self.parent_parser._action_groups:
                    self._render_action_group(action_group)
            ui.button("Submit").on("click", self._submit)

    def _render_action_group(self, action_group: argparse._ArgumentGroup) -> None:
        mutually_exclusive_groups_done = set()
        with ui.card().classes("w-full").props(f"data-testid=ng-group-{action_group.title}"):
            ui.label(action_group.title or "").classes("text-lg font-bold mb-2")
            with ui.list().classes("flex justify-between"):
                for action in action_group._group_actions:
                    # If this action is part of a mutually exclusive group, render that entire group at this point, if it has not been rendered already.
                    me_group = next(
                        (
                            me_group
                            for me_group in self.parent_parser._mutually_exclusive_groups
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
                        self._render_mutually_exclusive_group(me_group)

    def _render_mutually_exclusive_group(
        self, mutually_exclusive_group: argparse._MutuallyExclusiveGroup
    ) -> None:
        render_action = ui.refreshable_method(self._render_action)

        with ui.row(align_items="center").props("data-testid=ng-me-group"):
            choices = {
                action: (action.metavar or action.dest) for action in mutually_exclusive_group._group_actions
            }
            if not choices:
                raise RuntimeError(f"Mutually exclusive group must not be empty: {mutually_exclusive_group}")
            selector = ui.select(
                choices,
                value=mutually_exclusive_group._group_actions[0],
                on_change=lambda val: render_action.refresh(val.value),
            )
            render_action(selector.value)

    def _render_action(self, action: argparse.Action) -> ui.element:
        from .action_ui import ActionUi

        ui_container = ActionUi.from_action(self, action)
        self.action_elements[action] = ui_container
        if ui_container is not None:
            with ui.item().classes("border-2"):
                return ui_container.render().props(f"data-testid=ng-action-{action.dest}")
        else:
            return ui.element()


main_instance = NiceGooeyMain()

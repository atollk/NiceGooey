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
            assert self.parent_parser is not None
            with ui.column().classes(width):
                for action_group in self.parent_parser._action_groups:
                    self._render_action_group(action_group)
            ui.button("Submit").on("click", self._submit)

    def _render_action_group(self, action_group: argparse._ArgumentGroup) -> None:
        from .action_ui import ActionUi

        # Find relevant actions for this group
        actions = []
        for action in action_group._actions:
            container = getattr(action, "container", None)
            if container is None:
                logger.warning(f"Action {action} has no container attribute")
            else:
                if container is action_group:
                    actions.append(action)

        if not actions:
            return

        # Render
        with ui.card().classes("w-full"):
            ui.label(action_group.title or "").classes("text-lg font-bold mb-2")
            with ui.list().classes("flex justify-between"):
                for action in actions:
                    element = ActionUi.from_action(self, action)
                    if element is not None:
                        with ui.item().classes("border-2"):
                            element.render()


main_instance = NiceGooeyMain()

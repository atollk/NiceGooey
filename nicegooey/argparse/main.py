import argparse
import contextlib
import typing

import nicegui.run
import nicegui.helpers
from nicegui import ui
from .util import BindingNamespace, logger, CallbackWriter
from .argument_parser import ArgumentParserConfig, NgArgumentParser

if typing.TYPE_CHECKING:
    from .ui_classes.root import RootUi


class NiceGooeyMain:
    # State
    parent_parser: argparse.ArgumentParser | None = None
    main_func: typing.Callable | None = None
    is_running: bool = False
    parser_config: ArgumentParserConfig | None = None

    # Argument values
    namespace: BindingNamespace = BindingNamespace()

    # UI elements
    ui_root: "RootUi | None" = None

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
            if nicegui.helpers.is_user_simulation():
                return argparse.Namespace()
            else:
                raise AssertionError("nicegui.ui.run should not return")

    def _get_namespace(self) -> argparse.Namespace:
        if self.parent_parser is None:
            raise RuntimeError("NiceGooeyMain has no parent parser set")
        return self.namespace

    async def submit(self) -> None:
        # Validate
        assert self.ui_root is not None
        if not self.ui_root.validate():
            logger.warning("Validation error")
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
        from .ui_classes.root import RootUi

        if self.main_func is None:
            raise RuntimeError("NiceGooeyMain.parse_args called outside of nice_gooey_argparse_main")

        self.ui_root = RootUi(self)
        self.ui_root.render()


main_instance = NiceGooeyMain()

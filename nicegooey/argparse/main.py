import argparse
import typing

from nicegui import ui
from nicegui.elements.mixins import validation_element

if typing.TYPE_CHECKING:
    from .argument_parser import ArgumentParser
    from .action_ui import ActionUi


class NiceGooeyMain:
    parent_parser: "ArgumentParser | None" = None
    main_func: typing.Callable | None = None
    is_running: bool = False

    namespace: argparse.Namespace = argparse.Namespace()

    action_elements: dict[argparse.Action, "ActionUi"] = {}

    def parse_args(
        self, argument_parser: "ArgumentParser", *args, **kwargs
    ) -> argparse.Namespace | typing.Never:
        if self.is_running:
            return self._get_namespace()
        else:
            self.is_running = True
            self.parent_parser = argument_parser
            self._run(*args, **kwargs)

    def _run(self, *args, **kwargs) -> typing.Never:
        # TODO: make reload work
        ui.run(root=self.ui_root, reload=False)
        raise AssertionError("nicegui.ui.run should not return")

    def _get_namespace(self) -> argparse.Namespace:
        if self.parent_parser is None:
            raise RuntimeError("NiceGooeyMain has no parent parser set")
        return self.namespace

    def _submit(self) -> None:
        validation_error = False
        for action, element in self.action_elements.items():
            validation_error = validation_element or not element.validate()
        if not validation_error:
            assert self.main_func is not None
            self.main_func()

    def ui_root(self) -> None:
        if self.main_func is None:
            raise RuntimeError("NiceGooeyMain.parse_args called outside of nice_gooey_argparse_main")
        parser_actions = self.parent_parser._actions
        with ui.list().props("dense separator"):
            for action in parser_actions:
                with ui.item():
                    self._ui_action(action)
        ui.button("Submit").on("click", self._submit)

    def _ui_action(self, action: argparse.Action) -> None:
        from .action_ui import ActionUi

        element = ActionUi.from_action(self, action)
        element.render()

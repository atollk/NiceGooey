import argparse
import logging
import typing

from nicegui import ui, binding
from nicegui.elements.mixins import validation_element

if typing.TYPE_CHECKING:
    from .action_ui import ActionUi

logger = logging.getLogger("nicegooey.argparse")


class BindingNamespace(argparse.Namespace):
    def __init__(self, **kwargs: typing.Any) -> None:
        super().__init__(**kwargs)
        self._bindings: dict[str, binding.BindableProperty] = {}

    def __setattr__(self, key: str, value: typing.Any) -> None:
        if isinstance(value, binding.BindableProperty):
            self._bindings[key] = value
        else:
            super().__setattr__(key, value)

    def __getattr__(self, item: str) -> typing.Any:
        _bindings = super().__getattribute__("_bindings")
        if item in _bindings:
            return _bindings[item].value
        else:
            return super().__getattribute__(item)


class HotReloadException(Exception):
    """Exception to signal hot-reload in nicegooey.argparse."""

    pass


class NiceGooeyMain:
    # State
    parent_parser: argparse.ArgumentParser | None
    main_func: typing.Callable | None
    is_running: bool

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
        self, argument_parser: argparse.ArgumentParser, *args, **kwargs
    ) -> argparse.Namespace | typing.Never:
        if self.is_running:
            return self._get_namespace()
        else:
            self.is_running = True
            self.parent_parser = argument_parser
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

        # TODO: dark mode to save my eyes
        dark = ui.dark_mode(True)
        ui.label("Switch mode:")
        ui.button("Dark", on_click=dark.enable)
        ui.button("Light", on_click=dark.disable)

        for action_group in self.parent_parser._action_groups:
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
                continue

            # Render
            with ui.card().classes("w-full"):
                ui.label(action_group.title).classes("text-lg font-bold mb-2")
                with ui.list().props("bordered separator"):
                    for action in actions:
                        with ui.item():
                            self._ui_action(action)
        ui.button("Submit").on("click", self._submit)

    def _ui_action(self, action: argparse.Action) -> None:
        from .action_ui import ActionUi

        element = ActionUi.from_action(self, action)
        element.render()


main_instance = NiceGooeyMain()

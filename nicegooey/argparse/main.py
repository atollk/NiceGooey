import argparse
import typing

import nicegui.ui

if typing.TYPE_CHECKING:
    from .argument_parser import ArgumentParser


class NiceGooeyMain:
    parent_parser: "ArgumentParser | None" = None
    main_func: typing.Callable | None = None
    is_running: bool = False

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
        nicegui.ui.run(root=self.ui_root, reload=False)
        raise AssertionError("nicegui.ui.run should not return")

    def _get_namespace(self) -> argparse.Namespace:
        if self.parent_parser is None:
            raise RuntimeError("NiceGooeyMain has no parent parser set")
        ns = argparse.Namespace()
        ns.name = "foo"
        return ns

    def ui_root(self) -> None:
        if self.main_func is None:
            raise RuntimeError("NiceGooeyMain.parse_args called outside of nice_gooey_argparse_main")
        nicegui.ui.label("foo")
        nicegui.ui.button("Execute Main Function").on_click(self.main_func)

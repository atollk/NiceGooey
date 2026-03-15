import argparse
from typing import override, Type

from .action_sync_element import ActionSyncElement
from .action_ui_element import ActionUiElement


class CountActionUiElement(ActionUiElement[argparse._CountAction]):
    """Count actions are a special case because they differ very much between UI and CLI usage. In the UI, they are just a number widget."""

    class _ActionSyncElement(ActionSyncElement):
        @override
        def __init__(self, action: argparse.Action, parser: argparse.ArgumentParser):
            super().__init__(self._create_pseudo_action(action), parser)

        @staticmethod
        def _create_pseudo_action(action: argparse.Action) -> argparse.Action:
            """Create a pseudo action that behaves like the count action but can be used to initialize the input element."""
            # TODO: if the original is required, the min count should be 1
            return argparse._StoreAction(
                option_strings=action.option_strings,
                dest=action.dest,
                nargs=None,
                default=0,
                type=int,
                required=True,
                help=action.help,
                metavar=action.metavar,
                deprecated=action.deprecated if hasattr(action, "deprecated") else False,
            )

    @override
    @classmethod
    def _action_sync_element(cls) -> Type[ActionSyncElement]:
        return cls._ActionSyncElement

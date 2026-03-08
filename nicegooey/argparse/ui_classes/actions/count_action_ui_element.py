import argparse
import typing


from .action_input_base import ActionInputBaseElement
from .action_ui_element import ActionUiElement


class CountActionUiElement(ActionUiElement[argparse._CountAction]):
    """Count actions are a special case because they differ very much between UI and CLI usage. In the UI, they are just a number widget."""

    def __pseudo_action(self) -> argparse.Action:
        """Create a pseudo action that behaves like the count action but can be used to initialize the input element."""
        # TODO: if the original is required, the min count should be 1
        return argparse._StoreAction(
            option_strings=self.action.option_strings,
            dest=self.action.dest,
            nargs=None,
            default=0,
            type=int,
            required=True,
            help=self.action.help,
            metavar=self.action.metavar,
            deprecated=self.action.deprecated if hasattr(self.action, "deprecated") else False,
        )

    @typing.override
    def _input_element_init(self, default: typing.Any) -> ActionInputBaseElement:
        assert self.parent.parent_parser is not None
        input_base = ActionInputBaseElement(
            action=self.__pseudo_action(), parser=self.parent.parent_parser, init_value=default
        )
        return input_base

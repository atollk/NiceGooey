import argparse
import typing


from .list_action_ui_element import ListActionUiElement


class AppendConstActionUiElement(ListActionUiElement[argparse._AppendConstAction]):
    @typing.override
    def _input_element_default(self) -> None:
        return None

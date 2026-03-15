import argparse
from typing import Any, Type, override

from .action_info_helper import ActionInfoHelper
from .action_sync_element import ActionSyncElement
from .action_ui_element import ActionUiElement


class StoreConstActionUiElement(ActionUiElement[argparse._StoreConstAction]):
    class _ActionSyncElement(ActionSyncElement):
        @override
        def _ui_state_from_value(self, value: Any) -> None:
            el = self.inner_elements.enable_box_element
            if el is None:
                # The element is required, so we can't do anything.
                return
            # This logic doesn't matter because the value isn't actually used, but it's fun to have here :)
            if value == self.action.const:
                el.value = True
            elif value == ActionInfoHelper(action=self.action, parser=self.parser).action_default():
                el.value = False
            else:
                el.value = None

        @override
        def _ui_state_to_value(self) -> Any:
            if self.inner_elements.enable_box_element is None or self.inner_elements.enable_box_element.value:
                ns = argparse.Namespace()
                assert self.parser is not None
                self.action(self.parser, ns, None)
                return getattr(ns, self.action.dest)
            else:
                return ActionInfoHelper(action=self.action, parser=self.parser).action_default()

    @classmethod
    @override
    def _action_sync_element(cls) -> Type[ActionSyncElement]:
        return cls._ActionSyncElement

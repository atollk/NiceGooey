import argparse
from typing import Type, Any, override

from .action_info_helper import ActionInfoHelper
from .action_sync_element import ActionSyncElement
from .action_ui_element import ActionUiElement


class StoreActionUiElement(ActionUiElement[argparse._StoreAction]):
    class _ActionSyncElement(ActionSyncElement):
        @override
        def _ui_state_to_value(self) -> Any:
            v = self.inner_elements.nargs_wrapper_element.value
            ns = argparse.Namespace()
            ns.__setattr__(self.action.dest, getattr(self.namespace, self.action.dest))
            try:
                action_info = ActionInfoHelper(action=self.action, parser=self.parser)
                t = action_info.action_type_with_nargs()
                cast = t(v)
            except (TypeError, ValueError):
                pass
            else:
                assert self.parser is not None
                self.action(self.parser, ns, cast)
            return getattr(ns, self.action.dest)

    @classmethod
    def _action_sync_element(cls) -> Type[ActionSyncElement]:
        return cls._ActionSyncElement

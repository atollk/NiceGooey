import argparse
import dataclasses
from collections import defaultdict
from typing import TYPE_CHECKING, Callable, Any

if TYPE_CHECKING:
    from nicegooey.argparse.ui_classes.actions.action_ui_element import ActionUiElement


@dataclasses.dataclass
class NiceGooeyConfig:
    """
    Configuration for the NiceGooey setup.

    Attributes:
        root_card_class: A space-separated list of Tailwind classes to be applied to the root of the argument UI.
            Especially useful to pass something like 'w-4xl' to limit the width on large screens.
        action_config: A dict that maps parser action objects to `ActionConfig` classes.
            Use this to set configurations affecting individual actions.

    """

    @dataclasses.dataclass
    class ActionConfig:
        """
        Configuration for a single action.

        Attributes:
            element_override: If set, this class is instantiated to display the widget for this element in the UI
                instead of the default. For example, use this to render a slider with min and max limits, instead
                of a numeric input field.
                Look at nicegooey.argparse.ui_classes.actions.action_alternatives for predefined options.
            validation: A callable that is run when "Submit" is pressed. The value of the action is passed as the
                argument. If the function returns a string, the process is stopped and the string is shown as an error.
        """

        element_override: type["ActionUiElement[argparse.Action]"] | None = None
        validation: Callable[[Any], str | None] = lambda v: None

    root_card_class: str = "max-w-4xl"
    action_config: dict[argparse.Action, ActionConfig] = dataclasses.field(
        default_factory=lambda: defaultdict(NiceGooeyConfig.ActionConfig)
    )

import argparse
import dataclasses
import enum
from collections import defaultdict
from typing import TYPE_CHECKING, Callable, Any, Type

if TYPE_CHECKING:
    from nicegooey.argparse.ui_classes.actions.action_ui_element import ActionUiElement


def foo():
    return defaultdict(NiceGooeyConfig.ActionConfig)


@dataclasses.dataclass
class NiceGooeyConfig:
    """
    Configuration for the NiceGooey setup.

    Attributes:
        root_card_class: A space-separated list of Tailwind classes to be applied to the root of the argument UI.
            Especially useful to pass something like 'w-4xl' to limit the width on large screens.
        action_card_class: A space-separated list of Tailwind classes to be applied to each widget representing
            a parser action. For example, use "max-w-1/3" to always show up to three actions on one row.
        display_help: Whether and how to display the help text of arguments. The default is to show it as a tooltip.
        require_all_with_default: If True, arguments with a default value are always treated as "required".
            This can be overwritten for individual actions.
        action_config: A dict that maps parser action objects to `ActionConfig` classes.
            Use this to set configurations affecting individual actions.
        nicegui_run_kwargs: A dict of keyword-arguments that is passed to ui.run.

    """

    class DisplayHelp(enum.Enum):
        NoDisplay = enum.auto()
        Tooltip = enum.auto()
        Label = enum.auto()

    root_card_class: str = "max-w-4xl"
    action_card_class: str = ""
    display_help: DisplayHelp = DisplayHelp.Tooltip
    require_all_with_default: bool = False
    nicegui_run_kwargs: dict[str, Any] = dataclasses.field(default_factory=dict)

    @dataclasses.dataclass
    class ActionConfig:
        """
        Configuration for a single action.

        Attributes:
            display_name: Override the name of the action as shown in the UI.
                By default, the name is derived from the option strings, dest, or metavar.
            element_override: If set, this class is instantiated to display the widget for this element in the UI
                instead of the default. For example, use this to render a slider with min and max limits, instead
                of a numeric input field.
                Look at nicegooey.argparse.ui_classes.actions.action_alternatives for predefined options.
            validation: A callable that is run when "Submit" is pressed. The value of the action is passed as the
                argument. If the function returns a string, the process is stopped and the string is shown as an error.
            override_required: Overrides the "required" field of the action.
            override_type: Overrides the "type" field. This is especially useful if the action has a non-standard type,
                e.g. to do some validation, but you want to render a specific widget, like a number input.
            number_precision: If the action is numeric, this defines the number of post-decimal precision digits
                that are shown in the input field. Raises an error for non-numeric actions.
        """

        display_name: str | None = None
        element_override: type["ActionUiElement[argparse.Action]"] | None = None
        validation: Callable[[Any], str | None] = lambda v: None
        override_required: bool | None = None
        override_type: Type | None = None
        number_precision: int | None = None

    action_config: dict[argparse.Action, ActionConfig] = dataclasses.field(default_factory=foo)

    def get_action_config(self, action: argparse.Action) -> ActionConfig:
        config = self.action_config.get(action, None)
        if config is None:
            config = self.ActionConfig()
            self.action_config[action] = config
        return config

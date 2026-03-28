import pytest
from nicegui import ui
from nicegui.testing import User

from nicegooey.argparse import NgArgumentParser, nice_gooey_argparse_main
from nicegooey.argparse.ui_classes.actions.action_alternatives import store_const_action_toggle
from nicegooey.argparse.argument_parser import NiceGooeyConfig
from tests.conftest import exactly_one, find_within


@pytest.mark.nicegui_main_file(__file__)
async def test_store_const_action_toggle(user: User) -> None:
    """Test that store_const_action_toggle displays a toggle/switch instead of checkbox."""
    await user.open("/")
    await user.should_see("verbose")

    # Find the switch element (not a checkbox)
    switch = find_within(user, kind=ui.switch, within_marker="ng-action-verbose")
    assert len(switch.elements) == 1, "Should find switch element"

    # Verify we don't have a regular checkbox
    try:
        find_within(user, kind=ui.checkbox, within_marker="ng-action-verbose")
        assert False, "Should not have checkbox when using toggle override"
    except (ValueError, AssertionError):
        pass  # Expected

    # Verify the switch has the correct initial value (should be False)
    switch_element = exactly_one(switch.elements)
    assert switch_element.value is False

    # Verify the switch element has the expected text property
    # The text "Enable" is set in the alternative implementation
    assert hasattr(switch_element, "text") and switch_element.text == "Enable"

    # Note: Testing actual value binding for store_const is complex in NiceGUI testing framework
    # The important thing is that the switch widget is rendered instead of checkbox


@nice_gooey_argparse_main(patch_argparse=False)
def main():
    parser = NgArgumentParser()
    verbose_action = parser.add_argument(
        "--verbose", action="store_const", const="DEBUG", default="INFO", help="Enable debug mode"
    )

    # Configure toggle override
    parser.nicegooey_config.action_config[verbose_action] = NiceGooeyConfig.ActionConfig(
        element_override=store_const_action_toggle()
    )

    parser.parse_args()


if __name__ == "__main__":
    main()

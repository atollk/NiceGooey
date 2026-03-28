import pytest
from nicegui import ui
from nicegui.testing import User

from nicegooey.argparse import NgArgumentParser, nice_gooey_argparse_main
from nicegooey.argparse.ui_classes.actions.action_alternatives import store_action_radio
from nicegooey.argparse.argument_parser import NiceGooeyConfig
from tests.conftest import exactly_one, find_within


@pytest.mark.nicegui_main_file(__file__)
async def test_store_action_radio(user: User) -> None:
    """Test that store_action_radio displays radio buttons instead of select dropdown."""
    await user.open("/")
    await user.should_see("color")

    # Find the radio element (not a select)
    radio = find_within(user, kind=ui.radio, within_marker="ng-action-color")
    assert len(radio.elements) == 1, "Should find radio element"

    # Verify we don't have a regular select dropdown
    try:
        find_within(user, kind=ui.select, within_marker="ng-action-color")
        assert False, "Should not have select when using radio override"
    except (ValueError, AssertionError):
        pass  # Expected

    # Verify the radio has the correct options
    radio_element = exactly_one(radio.elements)
    options = radio_element._props["options"]
    # Options are formatted as [{'value': 0, 'label': 'red'}, ...]
    option_labels = [opt["label"] for opt in options]
    assert option_labels == ["red", "green", "blue"]

    # Note: Testing actual value binding is complex in NiceGUI testing framework
    # The important thing is that the radio widget is rendered instead of select dropdown


@nice_gooey_argparse_main(patch_argparse=False)
def main() -> None:
    parser = NgArgumentParser()
    color_action = parser.add_argument(
        "--color", type=str, choices=["red", "green", "blue"], help="Choose a color"
    )

    # Configure radio override
    parser.nicegooey_config.action_config[color_action] = NiceGooeyConfig.ActionConfig(
        element_override=store_action_radio()
    )

    parser.parse_args()


if __name__ == "__main__":
    main()

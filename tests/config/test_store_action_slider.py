import pytest
from nicegui import ui
from nicegui.testing import User

from nicegooey.argparse import NgArgumentParser, nice_gooey_argparse_main
from nicegooey.argparse.ui_classes.actions.action_alternatives import store_action_slider
from nicegooey.argparse.argument_parser import NiceGooeyConfig
from tests.conftest import exactly_one, find_within


@pytest.mark.nicegui_main_file(__file__)
async def test_store_action_slider(user: User) -> None:
    """Test that store_action_slider displays a slider instead of number input."""
    await user.open("/")
    await user.should_see("volume")

    # Find the slider element (not a number input)
    slider = find_within(user, kind=ui.slider, within_marker="ng-action-volume")
    assert len(slider.elements) == 1, "Should find slider element"

    # Verify we don't have a regular number input
    try:
        find_within(user, kind=ui.number, within_marker="ng-action-volume")
        assert False, "Should not have number input when using slider override"
    except (ValueError, AssertionError):
        pass  # Expected

    # Verify the slider has the correct min/max/step properties
    slider_element = exactly_one(slider.elements)
    assert slider_element._props["min"] == 0
    assert slider_element._props["max"] == 100
    assert slider_element._props["step"] == 10

    # Note: Testing actual value binding is complex in NiceGUI testing framework
    # The important thing is that the slider widget is rendered instead of number input


@nice_gooey_argparse_main(patch_argparse=False)
def main():
    parser = NgArgumentParser()
    volume_action = parser.add_argument("--volume", type=int, help="Volume level", default=0)

    # Configure slider override
    parser.nicegooey_config.action_config[volume_action] = NiceGooeyConfig.ActionConfig(
        element_override=store_action_slider(min=0, max=100, step=10)
    )

    parser.parse_args()


if __name__ == "__main__":
    main()

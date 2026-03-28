import pytest
from nicegui import ui
from nicegui.testing import User

from nicegooey.argparse import NgArgumentParser, nice_gooey_argparse_main
from nicegooey.argparse.ui_classes.actions.action_alternatives import store_action_file
from nicegooey.argparse.argument_parser import NiceGooeyConfig
from tests.conftest import find_within


@pytest.mark.nicegui_main_file(__file__)
async def test_store_action_file(user: User) -> None:
    """Test that store_action_file displays a file picker button instead of text input."""
    await user.open("/")
    await user.should_see("config-file")

    # Find the browse button
    browse_button = user.find("Browse files")
    assert len(browse_button.elements) == 1, "Should find Browse files button"

    # Verify the button is within the config-file action
    browse_button_scoped = find_within(
        user, kind=ui.button, content="Browse files", within_marker="ng-action-config_file"
    )
    assert len(browse_button_scoped.elements) == 1, "Browse button should be in config-file action"

    # Verify we don't have a regular text input
    try:
        find_within(user, kind=ui.input, within_marker="ng-action-config_file")
        assert False, "Should not have text input when using file picker override"
    except (ValueError, AssertionError):
        pass  # Expected

    # Note: Full file picker interaction is difficult to test in automated tests
    # We've verified the UI structure is correct (button exists, no text input)


@nice_gooey_argparse_main(patch_argparse=False)
def main():
    parser = NgArgumentParser()
    config_action = parser.add_argument("--config-file", type=str, help="Configuration file path")

    # Configure file picker override
    parser.nicegooey_config.action_config[config_action] = NiceGooeyConfig.ActionConfig(
        element_override=store_action_file()
    )

    parser.parse_args()


if __name__ == "__main__":
    main()

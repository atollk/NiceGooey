import pytest
from nicegui import ui
from nicegui.testing import User

from nicegooey.argparse import NgArgumentParser, NiceGooeyConfig, nice_gooey_argparse_main
from nicegooey.argparse.ui_classes.actions.action_alternatives import store_action_file
from tests.conftest import find_within


@pytest.mark.nicegui_main_file(__file__)
async def test_store_action_file_read_file_or_dir(user: User) -> None:
    """Test that store_action_file(mode='read_file_or_dir') renders a Browse files button."""

    await user.open("/")
    await user.should_see("input-path")

    # Browse button must be present within the action
    find_within(user, kind=ui.button, content="Browse files", within_marker="ng-action-input_path")

    # No plain text input
    with pytest.raises(AssertionError):
        find_within(user, kind=ui.input, within_marker="ng-action-input_path")


@nice_gooey_argparse_main(patch_argparse=False)
def main() -> None:
    parser = NgArgumentParser()
    input_action = parser.add_argument("--input-path", type=str, help="Input file or directory")
    input_action.nicegooey_config = NiceGooeyConfig.ActionConfig(
        element_override=store_action_file(mode="read_file_or_dir")
    )
    parser.parse_args()


if __name__ == "__main__":
    main()

import pytest
from nicegui import ui
from nicegui.testing import User

from nicegooey.argparse import NgArgumentParser, NiceGooeyConfig, nice_gooey_argparse_main
from tests.conftest import find_within


@pytest.mark.nicegui_main_file(__file__)
async def test_display_help_label(user: User) -> None:
    """Test that Label mode renders help text as a label beneath the action name."""

    await user.open("/")
    await user.should_see("output")

    # A standalone label with the help text must be present
    await user.should_see("Output file path")

    # No question-mark icon button
    with pytest.raises(AssertionError):
        find_within(user, kind=ui.button, within_marker="ng-action-output")


@nice_gooey_argparse_main(patch_argparse=False)
def main() -> None:
    parser = NgArgumentParser()
    parser.nicegooey_config.display_help = NiceGooeyConfig.DisplayHelp.Label
    parser.add_argument("--output", type=str, help="Output file path", required=True)
    parser.parse_args()


if __name__ == "__main__":
    main()

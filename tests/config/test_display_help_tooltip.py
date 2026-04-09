import pytest
from nicegui import ui
from nicegui.testing import User

from nicegooey.argparse import NgArgumentParser, nice_gooey_argparse_main
from tests.conftest import find_within


@pytest.mark.nicegui_main_file(__file__)
async def test_display_help_tooltip(user: User) -> None:
    """Test that Tooltip mode (default) shows a question-mark icon button and no standalone help label."""

    await user.open("/")
    await user.should_see("output")

    # A question-mark icon button should be present
    find_within(user, kind=ui.button, within_marker="ng-action-output")

    # No standalone ui.label with the help text (it should only be inside a tooltip)
    with pytest.raises(AssertionError):
        find_within(user, kind=ui.label, content="Output file path", within_marker="ng-action-output")


@nice_gooey_argparse_main(patch_argparse=False)
def main() -> None:
    parser = NgArgumentParser()
    # display_help defaults to Tooltip
    parser.add_argument("--output", type=str, help="Output file path", required=True)
    parser.parse_args()


if __name__ == "__main__":
    main()

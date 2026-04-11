import pytest
from nicegui import ui
from nicegui.testing import User

from nicegooey.argparse import NgArgumentParser, NiceGooeyConfig, nice_gooey_argparse_main


@pytest.mark.nicegui_main_file(__file__)
async def test_display_help_no_display(user: User) -> None:
    """Test that NoDisplay mode shows no tooltip button and no help label."""

    await user.open("/")
    await user.should_see("output")

    # No tooltip / question-mark button
    with pytest.raises(AssertionError):
        user.find(kind=ui.button, marker="icon=question_mark")

    # Action name label is still rendered
    await user.should_see("output")

    # No standalone help label with the help text
    with pytest.raises(AssertionError):
        user.find(content="Output file path")


@nice_gooey_argparse_main(patch_argparse=False)
def main() -> None:
    parser = NgArgumentParser()
    parser.nicegooey_config.display_help = NiceGooeyConfig.DisplayHelp.NoDisplay
    parser.add_argument("--output", type=str, help="Output file path", required=True)
    parser.parse_args()


if __name__ == "__main__":
    main()

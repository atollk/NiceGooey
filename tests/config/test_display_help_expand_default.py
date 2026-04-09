import pytest
from nicegui.testing import User

from nicegooey.argparse import NgArgumentParser, NiceGooeyConfig, nice_gooey_argparse_main


@pytest.mark.nicegui_main_file(__file__)
async def test_display_help_expand_default(user: User) -> None:
    """Test that %(default)s in help strings is expanded when rendered as a Label."""

    await user.open("/")
    await user.should_see("count")

    # Expanded help text must appear in the UI
    await user.should_see("Count (default: 5)")

    # The unexpanded format string must NOT appear
    with pytest.raises(AssertionError):
        user.find(content="%(default)s")


@nice_gooey_argparse_main(patch_argparse=False)
def main() -> None:
    parser = NgArgumentParser()
    parser.nicegooey_config.display_help = NiceGooeyConfig.DisplayHelp.Label
    parser.add_argument("--count", type=int, default=5, help="Count (default: %(default)s)")
    parser.parse_args()


if __name__ == "__main__":
    main()

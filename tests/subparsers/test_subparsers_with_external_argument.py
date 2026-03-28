import pytest
from nicegui.testing import User

from nicegooey.argparse import NgArgumentParser, nice_gooey_argparse_main
from nicegooey.argparse.ui_classes.groupings.subparser_ui import SubparserUi


@pytest.mark.nicegui_main_file(__file__)
async def test_subparsers_with_external_argument(user: User) -> None:
    """Test subparsers with an argument defined outside subparsers (always visible)."""

    await user.open("/")

    await user.should_see("global-option")

    await user.should_see("cmd1")
    await user.should_see("cmd2")

    # Click "cmd1" tab and verify its option is visible
    cmd1_tab = user.find(marker=f"{SubparserUi.TAB_MARKER_PREFIX}cmd1")
    cmd1_tab.click()
    await user.should_see("cmd1-option")

    # Click "cmd2" tab and verify both global-option and cmd2-option are visible
    cmd2_tab = user.find(marker=f"{SubparserUi.TAB_MARKER_PREFIX}cmd2")
    cmd2_tab.click()
    await user.should_see("global-option")
    await user.should_see("cmd2-option")


@nice_gooey_argparse_main(patch_argparse=False)
def main() -> None:
    parser = NgArgumentParser()

    parser.add_argument("--global-option", type=str, help="Global option visible everywhere")

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    parser_cmd1 = subparsers.add_parser("cmd1", help="Command 1")
    parser_cmd1.add_argument("--cmd1-option", type=str, help="Command 1 option")

    parser_cmd2 = subparsers.add_parser("cmd2", help="Command 2")
    parser_cmd2.add_argument("--cmd2-option", type=int, help="Command 2 option")

    parser.parse_args()


if __name__ == "__main__":
    main()

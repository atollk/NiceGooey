import pytest
from nicegui import ui
from nicegui.testing import User

from nicegooey.argparse import NgArgumentParser, nice_gooey_argparse_main
from nicegooey.argparse.main import main_instance
from nicegooey.argparse.ui_classes.groupings.subparser_ui import SubparserUi


@pytest.mark.nicegui_main_file(__file__)
async def test_optional_subparsers_with_dash_tab(user: User) -> None:
    """Test optional subparsers which show a '-' tab for no subparser selection."""

    await user.open("/")

    await user.should_see("-")
    await user.should_see("cmd1")
    await user.should_see("cmd2")

    # Verify that all tabs exist
    dash_tab = user.find(kind=ui.tab, content="-")
    cmd1_tab = user.find(marker=f"{SubparserUi.TAB_MARKER_PREFIX}cmd1")
    cmd2_tab = user.find(marker=f"{SubparserUi.TAB_MARKER_PREFIX}cmd2")
    assert len(dash_tab.elements) > 0
    assert len(cmd1_tab.elements) > 0
    assert len(cmd2_tab.elements) > 0

    # Click '-' tab and verify namespace.command is None
    dash_tab.click()
    assert main_instance.namespace.command in (None, "-")


@nice_gooey_argparse_main(patch_argparse=False)
def main():
    parser = NgArgumentParser()

    subparsers = parser.add_subparsers(dest="command", required=False, help="Optional commands")

    parser_cmd1 = subparsers.add_parser("cmd1", help="Command 1")
    parser_cmd1.add_argument("--opt1", type=str, help="Option 1")

    parser_cmd2 = subparsers.add_parser("cmd2", help="Command 2")
    parser_cmd2.add_argument("--opt2", type=str, help="Option 2")

    parser.parse_args()


if __name__ == "__main__":
    main()

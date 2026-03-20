import pytest
from nicegui.testing import User

from nicegooey.argparse import NgArgumentParser, nice_gooey_argparse_main
from nicegooey.argparse.main import main_instance
from nicegooey.argparse.ui_classes.groupings.subparser_ui import SubparserUi

from nicegui import ui

from tests.conftest import find_within


@pytest.mark.nicegui_main_file(__file__)
async def test_nested_subparser_structure(user: User) -> None:
    """Test complex nested subparser structure with multiple levels."""

    await user.open("/")

    await user.should_see("verbose")
    await user.should_see("remote")

    # Click on the "remote" tab
    remote_tab = user.find(marker=f"{SubparserUi.TAB_MARKER_PREFIX}remote")
    remote_tab.click()

    # Verify command is set
    assert main_instance.namespace.command == "remote"

    # Verify nested subparser tabs are visible
    await user.should_see("add")
    await user.should_see("remove")

    # Click on the "add" tab
    add_tab = user.find(marker=f"{SubparserUi.TAB_MARKER_PREFIX}add")
    add_tab.click()

    # Verify remote_command is set
    assert main_instance.namespace.remote_command == "add"

    # Verify --name and --url fields are visible
    await user.should_see("name")
    await user.should_see("url")

    # Fill in the fields
    name_input = find_within(
        user,
        kind=ui.input,
        within_marker="ng-action-name",
        within_outer_marker=f"{SubparserUi.TABPANEL_MARKER_PREFIX}add",
    )
    url_input = find_within(
        user,
        kind=ui.input,
        within_marker="ng-action-url",
        within_outer_marker=f"{SubparserUi.TABPANEL_MARKER_PREFIX}add",
    )

    name_input.type("origin")
    url_input.type("https://github.com")

    # Verify namespace values
    assert main_instance.namespace.name == "origin"
    assert main_instance.namespace.url == "https://github.com"


@nice_gooey_argparse_main(patch_argparse=False)
def main():
    parser = NgArgumentParser()

    parser.add_argument("--verbose", action="store_true", help="Verbose mode")

    subparsers = parser.add_subparsers(dest="command", help="Main commands")

    parser_remote = subparsers.add_parser("remote", help="Remote operations")
    remote_subparsers = parser_remote.add_subparsers(dest="remote_command", help="Remote commands")

    parser_remote_add = remote_subparsers.add_parser("add", help="Add remote")
    parser_remote_add.add_argument("--name", type=str, help="Remote name", required=True)
    parser_remote_add.add_argument("--url", type=str, help="Remote URL", required=True)

    parser_remote_remove = remote_subparsers.add_parser("remove", help="Remove remote")
    parser_remote_remove.add_argument("--name", type=str, help="Remote name to remove", required=True)

    parser.parse_args()


if __name__ == "__main__":
    main()

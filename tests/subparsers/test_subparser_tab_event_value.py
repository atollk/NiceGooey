"""Test that subparser tab change events use correct value type.

This test verifies TODO at subparsers_ui.py:64 - confirms that ev.value
is a string (tab name) and not a Tab object.
"""

import os

import pytest
from nicegui.testing import User

from nicegooey.argparse.argument_parser import NgArgumentParser
from nicegooey.argparse.main import main_instance
from nicegooey.argparse.patch import nice_gooey_argparse_main
from nicegooey.argparse.ui_classes.groupings.subparser_ui import SubparserUi
from nicegooey.argparse.ui_classes.groupings.subparsers_ui import SubparsersUi
from tests.conftest import find_within


@pytest.mark.nicegui_main_file(__file__)
async def test_subparser_tab_event_value_is_string(user: User) -> None:
    """Test that tab change events provide string values (tab names)."""
    await user.open("/")

    await user.should_see("cmd1")
    await user.should_see("cmd2")

    # Verify initial state
    subparsers_ui = main_instance.ui_root.parser.subparsers
    assert isinstance(subparsers_ui, SubparsersUi)
    assert isinstance(subparsers_ui.active_tab_title, str), "active_tab_title should be a string"
    assert subparsers_ui.active_tab_title == "cmd1", "Initial tab should be cmd1"

    # Switch to cmd2
    cmd2_tab = find_within(user, marker=f"{SubparserUi.TAB_MARKER_PREFIX}cmd2")
    cmd2_tab.click()

    # Verify active tab is now cmd2 and is a string
    assert isinstance(subparsers_ui.active_tab_title, str), (
        "active_tab_title should remain a string after tab change"
    )
    assert subparsers_ui.active_tab_title == "cmd2", "Active tab should be cmd2 after click"

    # Verify namespace also contains the string
    assert main_instance.namespace.command == "cmd2"
    assert isinstance(main_instance.namespace.command, str), "Namespace command should be a string"

    # Switch back to cmd1
    cmd1_tab = find_within(user, marker=f"{SubparserUi.TAB_MARKER_PREFIX}cmd1")
    cmd1_tab.click()

    # Verify it's still a string
    assert isinstance(subparsers_ui.active_tab_title, str), "active_tab_title should remain a string"
    assert subparsers_ui.active_tab_title == "cmd1", "Active tab should be cmd1 after click"
    assert isinstance(main_instance.namespace.command, str), "Namespace command should remain a string"


@nice_gooey_argparse_main(patch_argparse=False)
def main():
    parser = NgArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    parser_cmd1 = subparsers.add_parser("cmd1", help="Command 1")
    parser_cmd1.add_argument("--arg1", type=str, help="Argument for cmd1")

    parser_cmd2 = subparsers.add_parser("cmd2", help="Command 2")
    parser_cmd2.add_argument("--arg2", type=int, help="Argument for cmd2")

    args = parser.parse_args()

    if not os.environ["PYTEST_CURRENT_TEST"].endswith("(setup)"):
        print(f"Command: {args.command}")


if __name__ == "__main__":
    main()

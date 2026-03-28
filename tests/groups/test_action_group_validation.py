"""Test that validation cascades correctly through action groups.

This test verifies the BUG at grouping_sync_ui.py:31-32 - validate() should
call validate() on all children, not just check if children exist.
"""

from typing import Any

import pytest
from nicegui import ui
from nicegui.testing import User

from nicegooey.argparse.argument_parser import NgArgumentParser
from nicegooey.argparse.patch import nice_gooey_argparse_main
from tests.conftest import find_within, assert_has_validation_error


@pytest.mark.nicegui_main_file(__file__)
async def test_action_group_validates_children(user: User) -> None:
    """Test that action groups properly validate their child actions."""
    await user.open("/")

    # Submit without filling required field in action group
    submit_button = user.find("Submit")
    submit_button.click()

    # Should fail validation (required field is empty)
    await assert_has_validation_error(user)

    # Fill required field in the user group
    name_input = find_within(user, kind=ui.input, within_marker="ng-action-name")
    name_input.type("test")

    # Now submit should pass
    submit_button.click()
    await user.should_see(kind=ui.xterm)


@nice_gooey_argparse_main(patch_argparse=False)
def main() -> None:
    parser = NgArgumentParser()

    # Create an argument group with a required field
    def nonempty_str(v: Any) -> str:
        result = str(v)
        if not result:
            raise ValueError()
        else:
            return result

    user_group = parser.add_argument_group("User Information", "Information about the user")
    user_group.add_argument("--name", type=nonempty_str, required=True, help="User's name")

    parser.parse_args()


if __name__ == "__main__":
    main()

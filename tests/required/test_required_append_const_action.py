"""
Test that append_const actions work with required=True.
"""

import pytest
from nicegui import ui
from nicegui.testing import User

from nicegooey.argparse.argument_parser import NgArgumentParser
from nicegooey.argparse.main import main_instance
from nicegooey.argparse.patch import nice_gooey_argparse_main
from nicegooey.argparse.ui_classes.actions.action_sync_element import ActionSyncElement
from tests.conftest import assert_has_validation_error, find_within


@pytest.mark.nicegui_main_file(__file__)
async def test_required_append_const_basic(user: User) -> None:
    """Test that required append_const actions work."""
    await user.open("/")
    await user.should_see("verbose")

    # Verify no enable checkbox
    with pytest.raises(AssertionError):
        user.find(kind=ui.checkbox, marker=ActionSyncElement.ENABLE_PARAMETER_BOX_MARKER)

    # List should be empty initially
    assert main_instance.namespace.verbose == []

    # Try to submit without clicking - should fail
    submit_button = user.find("Submit")
    submit_button.click()
    await assert_has_validation_error(user)

    # Click the button once
    verbose_button = find_within(
        user, marker=ActionSyncElement.ADD_BUTTON_MARKER, within_marker="ng-action-verbose"
    )
    verbose_button.click()

    assert main_instance.namespace.verbose == ["INFO"]

    # Now submit should pass
    submit_button.click()
    await user.should_see(kind=ui.xterm)


@nice_gooey_argparse_main(patch_argparse=False)
def main():
    parser = NgArgumentParser()
    parser.add_argument(
        "--verbose",
        "-v",
        action="append_const",
        const="INFO",
        dest="verbose",
        required=True,
        help="Add verbose",
    )
    parser.parse_args()


if __name__ == "__main__":
    main()

"""
Test that append actions work with required=True.
This test verifies required list actions should work without raising NotImplementedError.
"""

import os

import pytest
from nicegui import ui
from nicegui.testing import User

from nicegooey.argparse.argument_parser import NgArgumentParser
from nicegooey.argparse.main import main_instance
from nicegooey.argparse.patch import nice_gooey_argparse_main
from nicegooey.argparse.ui_classes.actions.action_sync_element import ActionSyncElement


@pytest.mark.nicegui_main_file(__file__)
async def test_required_append_validation(user: User) -> None:
    """Test that required append actions validate properly."""
    await user.open("/")
    await user.should_see("tags")

    # Verify no enable checkbox for required append action
    with pytest.raises(AssertionError):
        user.find(kind=ui.checkbox, marker=ActionSyncElement.ENABLE_PARAMETER_BOX_MARKER)

    # List should be empty initially
    assert main_instance.namespace.tags == []

    # Try to submit without adding items - should fail
    submit_button = user.find("Submit")
    submit_button.click()
    with pytest.raises(AssertionError):
        user.find(kind=ui.xterm)

    # Add one item
    input_field = user.find(
        marker=ActionSyncElement.BASIC_ELEMENT_MARKER + ActionSyncElement.LIST_INNER_ELEMENT_MARKER_SUFFIX
    )
    add_button = user.find(marker=ActionSyncElement.ADD_BUTTON_MARKER)
    input_field.type("python")
    add_button.click()

    assert main_instance.namespace.tags == ["python"]

    # Now submit should pass
    submit_button.click()
    await user.should_see(kind=ui.xterm)


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
    with pytest.raises(AssertionError):
        user.find(kind=ui.xterm)

    # Click the button once
    verbose_button = user.find("Add verbose")
    verbose_button.click()

    assert main_instance.namespace.verbose == ["INFO"]

    # Now submit should pass
    submit_button.click()
    await user.should_see(kind=ui.xterm)


@pytest.mark.nicegui_main_file(__file__)
async def test_required_extend_basic(user: User) -> None:
    """Test that required extend actions work."""
    await user.open("/")
    await user.should_see("items")

    # Verify no enable checkbox
    with pytest.raises(AssertionError):
        user.find(kind=ui.checkbox, marker=ActionSyncElement.ENABLE_PARAMETER_BOX_MARKER)

    # List should be empty initially
    assert main_instance.namespace.items == []

    # Try to submit without adding - should fail
    submit_button = user.find("Submit")
    submit_button.click()
    with pytest.raises(AssertionError):
        user.find(kind=ui.xterm)

    # Add items (extend adds multiple at once)
    input_field = user.find(
        marker=ActionSyncElement.BASIC_ELEMENT_MARKER + ActionSyncElement.LIST_INNER_ELEMENT_MARKER_SUFFIX
    )
    add_button = user.find(marker=ActionSyncElement.ADD_BUTTON_MARKER)
    input_field.type("a,b,c")
    add_button.click()

    assert main_instance.namespace.items == ["a", "b", "c"]

    # Now submit should pass
    submit_button.click()
    await user.should_see(kind=ui.xterm)


# Test function for test_required_append_validation
@nice_gooey_argparse_main(patch_argparse=False)
def main():
    parser = NgArgumentParser()

    # Determine which test is running
    test_name = os.environ.get("PYTEST_CURRENT_TEST", "")

    if "test_required_append_validation" in test_name:
        parser.add_argument("--tag", action="append", type=str, dest="tags", required=True, help="Add tags")
    elif "test_required_append_const_basic" in test_name:
        parser.add_argument(
            "--verbose",
            "-v",
            action="append_const",
            const="INFO",
            dest="verbose",
            required=True,
            help="Add verbose",
        )
    elif "test_required_extend_basic" in test_name:
        parser.add_argument(
            "--items",
            action="extend",
            nargs="+",
            type=str,
            required=True,
            help="Extend items (comma-separated)",
        )

    args = parser.parse_args()

    if not test_name.endswith("(setup)"):
        if "test_required_append_validation" in test_name:
            print(f"Tags: {args.tags}")
        elif "test_required_append_const_basic" in test_name:
            print(f"Verbose: {args.verbose}")
        elif "test_required_extend_basic" in test_name:
            print(f"Items: {args.items}")


if __name__ == "__main__":
    main()

"""
Test that append actions work with required=True.
"""

import pytest
from nicegui import ui
from nicegui.testing import User

from nicegooey.argparse.argument_parser import NgArgumentParser
from nicegooey.argparse.main import main_instance
from nicegooey.argparse.patch import nice_gooey_argparse_main
from nicegooey.argparse.ui_classes.actions.action_ui_element import ActionUiElement
from tests.conftest import assert_has_validation_error


@pytest.mark.nicegui_main_file(__file__)
async def test_required_append_validation(user: User) -> None:
    """Test that required append actions validate properly."""
    await user.open("/")
    await user.should_see("tags")

    # Verify no enable checkbox for required append action
    with pytest.raises(AssertionError):
        user.find(kind=ui.checkbox, marker=ActionUiElement.ENABLE_PARAMETER_BOX_MARKER)

    # List should be empty initially
    assert main_instance.namespace.tags == []

    # Try to submit without adding items - should fail
    submit_button = user.find("Submit")
    submit_button.click()
    await assert_has_validation_error(user)

    # Add one item
    input_field = user.find(
        marker=ActionUiElement.BASIC_ELEMENT_MARKER + ActionUiElement.LIST_INNER_ELEMENT_MARKER_SUFFIX
    )
    add_button = user.find(marker=ActionUiElement.ADD_BUTTON_MARKER)
    input_field.type("python")
    add_button.click()

    assert main_instance.namespace.tags == ["python"]

    # Now submit should pass
    submit_button.click()
    await user.should_see(kind=ui.xterm)


@nice_gooey_argparse_main(patch_argparse=False)
def main():
    parser = NgArgumentParser()
    parser.add_argument("--tag", action="append", type=str, dest="tags", required=True, help="Add tags")
    parser.parse_args()


if __name__ == "__main__":
    main()

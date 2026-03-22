import pytest
from nicegui import ui
from nicegui.testing import User

from nicegooey.argparse import NgArgumentParser, nice_gooey_argparse_main
from nicegooey.argparse.main import main_instance
from nicegooey.argparse.ui_classes.actions.action_ui_element import ActionUiElement
from tests.conftest import assert_has_validation_error


@pytest.mark.nicegui_main_file(__file__)
async def test_nargs_specific_number_validation(user: User) -> None:
    """Test that nargs with specific number enforces exactly that many values."""

    await user.open("/")

    await user.should_see("rgb")

    # Verify initial namespace
    assert main_instance.namespace.rgb in (None, [], [0, 0, 0])

    # Add three RGB values
    basic_element = user.find(
        marker=ActionUiElement.BASIC_ELEMENT_MARKER + ActionUiElement.LIST_INNER_ELEMENT_MARKER_SUFFIX
    )
    add_button = user.find(marker=ActionUiElement.ADD_BUTTON_MARKER)

    # Get submit button for validation tests
    submit_button = user.find("Submit")

    # Add first value (R)
    basic_element.type("255")
    add_button.click()
    # Verify validation failure - need exactly 3 values
    submit_button.click()
    await assert_has_validation_error(user)

    # Add second value (G)
    basic_element.type("128")
    add_button.click()
    # Verify validation failure - still need 3 values
    submit_button.click()
    await assert_has_validation_error(user)

    # Add third value (B)
    basic_element.type("64")
    add_button.click()
    # Verify validation pass - now we have exactly 3 values
    submit_button.click()
    await user.should_see(kind=ui.xterm)

    # Verify namespace contains all three values
    assert main_instance.namespace.rgb == [255, 128, 64]


@pytest.mark.nicegui_main_file(__file__)
async def test_nargs_three_submit_validation(user: User) -> None:
    """Test that submitting with wrong count fails validation for nargs=3."""
    await user.open("/")

    basic_element = user.find(
        marker=ActionUiElement.BASIC_ELEMENT_MARKER + ActionUiElement.LIST_INNER_ELEMENT_MARKER_SUFFIX
    )
    add_button = user.find(marker=ActionUiElement.ADD_BUTTON_MARKER)
    submit_button = user.find("Submit")

    # Add only 2 items
    basic_element.type("255")
    add_button.click()
    basic_element.type("128")
    add_button.click()

    # Should fail validation (need exactly 3)
    submit_button.click()
    await assert_has_validation_error(user)

    # Add third item
    basic_element.type("64")
    add_button.click()

    # Should pass validation
    submit_button.click()
    await user.should_see(kind=ui.xterm)

    # Verify namespace
    assert main_instance.namespace.rgb == [255, 128, 64]


@nice_gooey_argparse_main(patch_argparse=False)
def main():
    parser = NgArgumentParser()
    parser.add_argument("--rgb", nargs=3, type=int, help="RGB color (3 integers)", required=True)
    parser.parse_args()


if __name__ == "__main__":
    main()

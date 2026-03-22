import pytest
from nicegui.testing import User

from nicegooey.argparse import NgArgumentParser, nice_gooey_argparse_main
from nicegooey.argparse.main import main_instance
from nicegooey.argparse.ui_classes.actions.action_ui_element import ActionUiElement


@pytest.mark.nicegui_main_file(__file__)
async def test_nargs_plus(user: User) -> None:
    """Test nargs='+' - one or more values (at least one required)."""

    await user.open("/")

    await user.should_see("required-items")

    assert main_instance.namespace.required_items in (None, [])

    # Add first item
    basic_element = user.find(
        marker=ActionUiElement.BASIC_ELEMENT_MARKER + ActionUiElement.LIST_INNER_ELEMENT_MARKER_SUFFIX
    )
    add_button = user.find(marker=ActionUiElement.ADD_BUTTON_MARKER)
    basic_element.type("required_item1")
    add_button.click()

    # Verify namespace is updated correctly
    assert main_instance.namespace.required_items == ["required_item1"]

    # Add a second item
    basic_element.type("required_item2")
    add_button.click()

    # Verify namespace now contains both values
    assert main_instance.namespace.required_items == ["required_item1", "required_item2"]


@nice_gooey_argparse_main(patch_argparse=False)
def main():
    parser = NgArgumentParser()
    parser.add_argument(
        "--required-items", nargs="+", type=str, help="One or more items (required)", required=True
    )
    parser.parse_args()


if __name__ == "__main__":
    main()

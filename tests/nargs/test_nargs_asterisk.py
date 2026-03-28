import pytest
from nicegui.testing import User

from nicegooey.argparse import NgArgumentParser, nice_gooey_argparse_main
from nicegooey.argparse.main import main_instance
from nicegooey.argparse.ui_classes.actions.action_ui_element import ActionUiElement


@pytest.mark.nicegui_main_file(__file__)
async def test_nargs_asterisk(user: User) -> None:
    """Test nargs='*' - zero or more values (list)."""

    await user.open("/")

    await user.should_see("items")

    assert main_instance.namespace.items in (None, [])

    # Add first item
    basic_element = user.find(
        marker=ActionUiElement.BASIC_ELEMENT_MARKER + ActionUiElement.LIST_INNER_ELEMENT_MARKER_SUFFIX
    )
    add_button = user.find(marker=ActionUiElement.ADD_BUTTON_MARKER)
    basic_element.type("item1")
    add_button.click()

    # Verify namespace is updated correctly
    assert main_instance.namespace.items == ["item1"]

    # Add a second item
    basic_element.type("item2")
    add_button.click()

    # Verify namespace now contains both values
    assert main_instance.namespace.items == ["item1", "item2"]


@nice_gooey_argparse_main(patch_argparse=False)
def main() -> None:
    parser = NgArgumentParser()
    parser.add_argument("--items", nargs="*", type=str, help="Zero or more items", required=True)
    parser.parse_args()


if __name__ == "__main__":
    main()

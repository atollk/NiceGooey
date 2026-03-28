import pytest
from nicegui.testing import User

from nicegooey.argparse import NgArgumentParser, nice_gooey_argparse_main
from nicegooey.argparse.main import main_instance
from nicegooey.argparse.ui_classes.actions.action_ui_element import ActionUiElement


@pytest.mark.nicegui_main_file(__file__)
async def test_nargs_three(user: User) -> None:
    """Test nargs=3 - exactly three values expected."""

    await user.open("/")

    await user.should_see("coords")

    assert main_instance.namespace.coords in (None, [], [0, 0, 0])

    # Add three float values
    basic_element = user.find(
        marker=ActionUiElement.BASIC_ELEMENT_MARKER + ActionUiElement.LIST_INNER_ELEMENT_MARKER_SUFFIX
    )
    add_button = user.find(marker=ActionUiElement.ADD_BUTTON_MARKER)

    # Add first value
    basic_element.type("1.0")
    add_button.click()

    # Add second value
    basic_element.type("2.5")
    add_button.click()

    # Add third value
    basic_element.type("3.7")
    add_button.click()

    # Verify namespace contains all three values
    assert main_instance.namespace.coords == [1.0, 2.5, 3.7]


@nice_gooey_argparse_main(patch_argparse=False)
def main() -> None:
    parser = NgArgumentParser()
    parser.add_argument("--coords", nargs=3, type=float, help="Three coordinates (x, y, z)", required=True)
    parser.parse_args()


if __name__ == "__main__":
    main()

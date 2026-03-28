import pytest
from nicegui.testing import User

from nicegooey.argparse import NgArgumentParser, nice_gooey_argparse_main
from nicegooey.argparse.main import main_instance
from nicegooey.argparse.ui_classes.actions.action_ui_element import ActionUiElement
from nicegooey.argparse.ui_classes.actions.standard_actions import ListActionUiElement


@pytest.mark.nicegui_main_file(__file__)
async def test_append_action_with_int(user: User) -> None:
    """Test append action with int type."""

    await user.open("/")
    await user.should_see("numbers")

    assert main_instance.namespace.numbers == []

    number_input = user.find(marker=ActionUiElement.BASIC_ELEMENT_MARKER)
    assert len(number_input.elements) == 1
    add_button = user.find(marker=ListActionUiElement.LIST_ADD_BUTTON_MARKER)
    assert len(add_button.elements) == 1

    number_input.type("42")
    add_button.click()
    assert main_instance.namespace.numbers == [42]

    number_input.type("100")
    add_button.click()
    assert main_instance.namespace.numbers == [42, 100]

    number_input.type("7")
    add_button.click()
    assert main_instance.namespace.numbers == [42, 100, 7]


@nice_gooey_argparse_main(patch_argparse=False)
def main() -> None:
    parser = NgArgumentParser()
    parser.add_argument("--number", action="append", type=int, dest="numbers", help="Add numbers")
    parser.parse_args()


if __name__ == "__main__":
    main()

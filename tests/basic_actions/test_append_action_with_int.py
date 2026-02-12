import pytest
from nicegui import ui
from nicegui.testing import User

from nicegooey.argparse import nice_gooey_argparse_main, NgArgumentParser
from nicegooey.argparse.main import main_instance


@pytest.mark.nicegui_main_file(__file__)
async def test_append_action_with_int(user: User) -> None:
    """Test append action with int type."""

    await user.open("/")
    await user.should_see("numbers")

    assert main_instance.namespace.numbers == []

    number_input = user.find(ui.number)
    add_button = user.find(ui.button).filter(
        lambda x: x.element.props.get("data-testid") == "ng-action-add-button"
    )

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
def main():
    parser = NgArgumentParser()
    parser.add_argument("--number", action="append", type=int, dest="numbers", help="Add numbers")
    parser.parse_args()


if __name__ == "__main__":
    main()

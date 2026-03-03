import pytest
from nicegui.testing import User

from nicegooey.argparse import nice_gooey_argparse_main, NgArgumentParser
from nicegooey.argparse.main import main_instance
from tests.conftest import input_number


@pytest.mark.nicegui_main_file(__file__)
async def test_append_action_with_int(user: User) -> None:
    """Test append action with int type."""

    await user.open("/")
    await user.should_see("numbers")

    assert main_instance.namespace.numbers == []

    number_input = user.find(marker="ng-action-type-input-basic")
    assert len(number_input.elements) == 1
    add_button = user.find(marker="ng-action-add-button")
    assert len(add_button.elements) == 1

    input_number(number_input, 42)
    add_button.click()
    assert main_instance.namespace.numbers == [42]

    input_number(number_input, 100)
    add_button.click()
    assert main_instance.namespace.numbers == [42, 100]

    input_number(number_input, 7)
    add_button.click()
    assert main_instance.namespace.numbers == [42, 100, 7]


@nice_gooey_argparse_main(patch_argparse=False)
def main():
    parser = NgArgumentParser()
    parser.add_argument("--number", action="append", type=int, dest="numbers", help="Add numbers")
    parser.parse_args()


if __name__ == "__main__":
    main()

import pytest
from nicegui import ui
from nicegui.testing import User

from nicegooey.argparse import NgArgumentParser, nice_gooey_argparse_main
from nicegooey.argparse.main import main_instance
from nicegooey.argparse.ui_classes.actions.action_ui_element import ActionUiElement
from tests.conftest import exactly_one, find_within


@pytest.mark.nicegui_main_file(__file__)
async def test_string_action_with_choices_const(user: User) -> None:
    """Test that when a const is specified it takes priority as the initial value."""

    await user.open("/")
    await user.should_see("fruit")
    await user.should_see("required_fruit")

    assert main_instance.namespace.fruit == "apple"
    assert main_instance.namespace.required_fruit == "orange"

    fruit_select = exactly_one(find_within(user, kind=ui.select, within_marker="ng-action-fruit").elements)
    required_fruit_select = exactly_one(
        find_within(user, kind=ui.select, within_marker="ng-action-required_fruit").elements
    )
    assert fruit_select.value == "orange"
    assert required_fruit_select.value == "orange"

    enable_checkbox = user.find(kind=ui.checkbox, marker=ActionUiElement.ENABLE_PARAMETER_BOX_MARKER)
    enable_checkbox.click()
    assert main_instance.namespace.fruit == "orange"


@nice_gooey_argparse_main(patch_argparse=False)
def main() -> None:
    parser = NgArgumentParser()
    parser.add_argument(
        "--fruit",
        choices=["apple", "banana", "orange"],
        const="orange",
        default="apple",
        nargs="?",
        help="Pick a fruit",
    )
    parser.add_argument(
        "--required_fruit",
        choices=["apple", "banana", "orange"],
        const="orange",
        default="apple",
        help="Pick a fruit",
        required=True,
        nargs="?",
    )
    parser.parse_args()


if __name__ == "__main__":
    main()
